"""Read explicitly selected Markdown artifacts. No scanning, writes or execution."""

from __future__ import annotations

import json
import os
import re
import stat
from collections.abc import Iterable
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any, Literal, NoReturn, cast

import yaml
from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError
from referencing import Registry
from referencing.exceptions import NoSuchResource
from yaml.nodes import MappingNode, Node, ScalarNode, SequenceNode


PathInput = str | os.PathLike[str]
ContentState = Literal["draft", "confirmed", "retired"]
MetadataPath = tuple[str | int, ...]


class ArtifactInputError(ValueError):
    """Stable code and 1-based source location; the original exception stays chained."""

    def __init__(self, code: str, path: Path | str, line: int, message: str) -> None:
        self.code = code
        self.path = path
        self.line = line
        self.message = message
        super().__init__(f"{code}: {path}:{line}: {message}")


@dataclass(frozen=True, slots=True)
class SourceLocation:
    path: Path
    line: int


@dataclass(frozen=True, slots=True)
class Target:
    target: str
    criterion_anchor: str
    test_id: str | None
    location: SourceLocation
    criterion_location: SourceLocation


@dataclass(frozen=True, slots=True)
class Confirmation:
    by: str
    reference: str
    baseline: str
    location: SourceLocation


@dataclass(frozen=True, slots=True)
class Anchor:
    name: str
    location: SourceLocation


@dataclass(frozen=True, slots=True)
class Acceptance:
    id: str
    owner: str
    anchor: str
    location: SourceLocation
    anchor_location: SourceLocation

    @property
    def reference(self) -> str:
        return f"{self.owner}#{self.anchor}"


@dataclass(frozen=True, slots=True)
class Artifact:
    schema_version: int
    id: str
    kind: str
    scope: str
    content_state: ContentState
    upstream: tuple[str, ...]
    targets: tuple[Target, ...]
    confirmation: Confirmation | None
    path: Path
    relative_path: str
    location: SourceLocation
    id_location: SourceLocation
    body_start_line: int
    source: str
    body: str
    anchors: tuple[Anchor, ...]
    acceptances: tuple[Acceptance, ...]

    @property
    def key(self) -> str:
        return f"{self.scope}/{self.id}"

    @property
    def acceptance_ids(self) -> tuple[str, ...]:
        return tuple(item.reference for item in self.acceptances)


def _path(value: PathInput, code: str, context: Path | str) -> Path:
    if not isinstance(value, (str, os.PathLike)) or isinstance(value, bytes):
        raise ArtifactInputError(code, context, 1, f"Expected a string or path, got {value!r}")
    if isinstance(value, str) and not value.strip():
        raise ArtifactInputError(code, context, 1, "An explicit nonempty path is required")
    try:
        return Path(value)
    except (TypeError, ValueError) as error:
        raise ArtifactInputError(code, context, 1, str(error)) from error


def _resolve_root(root: PathInput, context: Path | str) -> Path:
    requested = _path(root, "INVALID_ROOT", context)
    try:
        resolved = requested.resolve(strict=True)
        mode = resolved.stat().st_mode
    except (OSError, ValueError, RuntimeError) as error:
        raise ArtifactInputError("INVALID_ROOT", context, 1, f"Root {root!r}: {error}") from error
    if not stat.S_ISDIR(mode):
        raise ArtifactInputError("INVALID_ROOT", context, 1, f"Root is not a directory: {resolved}")
    return resolved


def _resolve_file(path: PathInput, root: Path) -> Path:
    requested = _path(path, "INVALID_PATH", str(path))
    if requested.anchor and not requested.is_absolute():
        raise ArtifactInputError("INVALID_PATH", str(path), 1, "Drive-relative/rooted paths are ambiguous")
    try:
        resolved = (root / requested).resolve()
    except (OSError, ValueError, RuntimeError) as error:
        raise ArtifactInputError("INVALID_PATH", str(path), 1, str(error)) from error
    if not resolved.is_relative_to(root):
        raise ArtifactInputError(
            "OUTSIDE_ROOT", str(path), 1, f"Resolved file {resolved} is outside root {root}",
        )
    try:
        mode = resolved.stat().st_mode
    except FileNotFoundError as error:
        raise ArtifactInputError("FILE_NOT_FOUND", resolved, 1, str(error)) from error
    except (OSError, ValueError) as error:
        raise ArtifactInputError("FILE_READ_ERROR", resolved, 1, str(error)) from error
    if not stat.S_ISREG(mode):
        raise ArtifactInputError("INVALID_PATH", resolved, 1, "Input is not a regular file")
    return resolved


class _DuplicateKeyError(yaml.constructor.ConstructorError):
    pass


class _UniqueSafeLoader(yaml.SafeLoader):
    def construct_object(self, node: Node, deep: bool = False) -> Any:
        try:
            return super().construct_object(node, deep=deep)
        except (ValueError, KeyError, OverflowError, IndexError, AttributeError) as error:
            # SafeLoader's scalar constructors can leak built-in exceptions for
            # malformed explicit !!int/!!bool/!!timestamp values. Locate the
            # failure at this YAML node, retaining the original cause and detail.
            raise yaml.constructor.ConstructorError(
                "while constructing a safe YAML value", node.start_mark,
                f"{node.tag}: {error}", node.start_mark,
            ) from error

    def construct_mapping(self, node: Node, deep: bool = False) -> dict:
        if not isinstance(node, MappingNode):
            raise yaml.constructor.ConstructorError(
                None, None, f"Expected a mapping node, got {node.id}", node.start_mark,
            )
        # Flattening also exposes duplicates introduced by YAML merge/override syntax.
        self.flatten_mapping(node)
        result = {}
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            if not isinstance(key, str):
                raise yaml.constructor.ConstructorError(
                    "while reading metadata", node.start_mark,
                    "Mapping keys must be strings", key_node.start_mark,
                )
            if key in result:
                raise _DuplicateKeyError(
                    "while reading metadata", node.start_mark,
                    f"Duplicate YAML key: {key!r}", key_node.start_mark,
                )
            result[key] = self.construct_object(value_node, deep=deep)
        return result


def _check_yaml_graph(node: Node, active: set[int], visited: set[int]) -> None:
    identity = id(node)
    if identity in active:
        raise yaml.constructor.ConstructorError(
            None, None, "Recursive YAML aliases are not metadata", node.start_mark,
        )
    if identity in visited:
        return
    active.add(identity)
    if isinstance(node, MappingNode):
        # Check the raw graph before SafeLoader normalizes ANY merge node, including
        # nested nodes which flatten_mapping consumes without construct_mapping.
        original_keys: set[str] = set()
        for key, value in node.value:
            if isinstance(key, ScalarNode):
                if key.value in original_keys:
                    raise _DuplicateKeyError(
                        "while reading metadata", node.start_mark,
                        f"Duplicate YAML key: {key.value!r}", key.start_mark,
                    )
                original_keys.add(key.value)
            _check_yaml_graph(key, active, visited)
            _check_yaml_graph(value, active, visited)
    elif isinstance(node, SequenceNode):
        for value in node.value:
            _check_yaml_graph(value, active, visited)
    active.remove(identity)
    visited.add(identity)


def _locations(node: Node, path: Path) -> dict[MetadataPath, SourceLocation]:
    result: dict[MetadataPath, SourceLocation] = {}

    def visit(current: Node, parts: MetadataPath) -> None:
        result.setdefault(parts, SourceLocation(path, current.start_mark.line + 2))
        if isinstance(current, MappingNode):
            for key, value in current.value:
                child = (*parts, key.value)
                result[child] = SourceLocation(path, key.start_mark.line + 2)
                visit(value, child)
        elif isinstance(current, SequenceNode):
            for index, value in enumerate(current.value):
                visit(value, (*parts, index))
    visit(node, ())
    return result


def _load_metadata(text: str, path: Path) -> tuple[dict[str, Any], dict[MetadataPath, SourceLocation]]:
    loader = None
    try:
        loader = _UniqueSafeLoader(text)
        node = loader.get_single_node()
        if node is not None:
            _check_yaml_graph(node, set(), set())
        data = loader.construct_document(node) if node is not None else None
        if not isinstance(data, dict):
            raise ArtifactInputError("INVALID_METADATA", path, 2, "Frontmatter must be a mapping")
        return data, _locations(node, path)
    except yaml.YAMLError as error:
        mark = getattr(error, "problem_mark", None)
        line = mark.line + 2 if mark else text[:getattr(error, "position", 0)].count("\n") + 2
        code = "DUPLICATE_YAML_KEY" if isinstance(error, _DuplicateKeyError) else "INVALID_YAML"
        raise ArtifactInputError(code, path, line, str(error)) from error
    except RecursionError as error:
        raise ArtifactInputError("INVALID_YAML", path, 2, f"YAML nesting exceeds parser limits: {error}") from error
    finally:
        if loader is not None:
            loader.dispose()


def _deny_external_schema(uri: str) -> NoReturn:
    raise NoSuchResource(ref=uri)


@lru_cache(maxsize=1)
def _artifact_validator() -> Draft202012Validator:
    path = Path(__file__).resolve().parents[1] / "contracts" / "artifact.schema.json"
    try:
        schema = json.loads(path.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)

        def check_local_refs(node: object) -> None:
            if isinstance(node, dict):
                for key, value in node.items():
                    if key in ("$ref", "$dynamicRef"):
                        if not isinstance(value, str) or not value.startswith("#/"):
                            raise ValueError(f"Only local JSON pointers are supported: {value!r}")
                        target = schema
                        for part in value[2:].split("/"):
                            target = target[part.replace("~1", "/").replace("~0", "~")]
                    check_local_refs(value)
            elif isinstance(node, list):
                for value in node:
                    check_local_refs(value)
        check_local_refs(schema)
    except (OSError, UnicodeError, ValueError, KeyError, TypeError, SchemaError) as error:
        raise ArtifactInputError("CONTRACT_ERROR", path, 1, str(error)) from error
    return Draft202012Validator(schema, registry=Registry(retrieve=_deny_external_schema))


def _validate_metadata(
    data: dict[str, Any], locations: dict[MetadataPath, SourceLocation], path: Path,
) -> None:
    validator = _artifact_validator()
    if "schemaVersion" in data and (type(data["schemaVersion"]) is not int or data["schemaVersion"] != 1):
        raise ArtifactInputError(
            "UNSUPPORTED_SCHEMA_VERSION", path, locations[("schemaVersion",)].line,
            f"Expected integer schemaVersion 1, got {data['schemaVersion']!r}",
        )
    for field, allowed, code in (
        ("kind", validator.schema["$defs"]["kind"]["enum"], "INVALID_KIND"),
        ("contentState", ("draft", "confirmed", "retired"), "INVALID_CONTENT_STATE"),
    ):
        if field in data and data[field] not in allowed:
            raise ArtifactInputError(code, path, locations[(field,)].line, f"Unsupported {field}: {data[field]!r}")
    error = next(validator.iter_errors(data), None)
    if error is not None:
        parts = tuple(error.absolute_path)
        while parts not in locations:
            parts = parts[:-1]
        field = ".".join(map(str, error.absolute_path)) or "frontmatter"
        raise ArtifactInputError("INVALID_METADATA", path, locations[parts].line,
                                 f"{field}: {error.message}") from error


_ANCHOR = re.compile(r""" {0,3}<a[ \t]+id=(["'])([A-Za-z][A-Za-z0-9._:-]*)\1[ \t]*></a>[ \t]*$""")
_FENCE = re.compile(r" {0,3}(`{3,}|~{3,})(.*)$")


def _without_comments(line: str, in_comment: bool) -> tuple[str, bool]:
    result = ""
    while line:
        if in_comment:
            end = line.find("-->")
            if end < 0:
                return result, True
            line, in_comment = line[end + 3:], False
        else:
            start = line.find("<!--")
            if start < 0:
                return result + line, False
            result += line[:start]
            line, in_comment = line[start + 4:], True
    return result, in_comment


def _body_entries(
    body: str, path: Path, start: int, artifact_id: str, owner: str,
) -> tuple[tuple[Anchor, ...], tuple[Acceptance, ...]]:
    heading = re.compile(
        r" {0,3}#{1,6}[ \t]+(" + re.escape(artifact_id) + r"-(?:AC|VC)-[0-9]+)(?=$|[ \t:：])"
    )
    anchors: dict[str, Anchor] = {}
    acceptances: list[Acceptance] = []
    pending: Anchor | None = None
    fence: tuple[str, int] | None = None
    in_comment = False
    for number, raw in enumerate(body.splitlines(), start):
        if fence is not None:
            if re.fullmatch(r" {0,3}" + re.escape(fence[0]) + "{" + str(fence[1]) + r",}[ \t]*", raw):
                fence = None
            continue
        line, in_comment = _without_comments(raw, in_comment)
        opener = _FENCE.fullmatch(line)
        if opener and not (opener[1][0] == "`" and "`" in opener[2]):
            fence = (opener[1][0], len(opener[1]))
            pending = None
            continue
        anchor_match = _ANCHOR.fullmatch(line)
        if anchor_match:
            name = anchor_match[2]
            if name in anchors:
                raise ArtifactInputError(
                    "DUPLICATE_ANCHOR", path, number,
                    f"Duplicate anchor {name!r}; first defined on line {anchors[name].location.line}",
                )
            pending = Anchor(name, SourceLocation(path, number))
            anchors[name] = pending
            continue
        item = heading.match(line)
        if item:
            identifier = item[1]
            if pending is None or pending.name != identifier.lower():
                raise ArtifactInputError(
                    "MISSING_ACCEPTANCE_ANCHOR", path, number,
                    f"Owner heading {identifier} needs its preceding explicit anchor {identifier.lower()!r}",
                )
            acceptances.append(Acceptance(
                identifier, owner, pending.name, SourceLocation(path, number), pending.location,
            ))
        if line.strip():
            pending = None
    return tuple(anchors.values()), tuple(acceptances)


def parse_artifact(path: PathInput, root: PathInput) -> Artifact:
    """Parse one explicitly selected local file; relative paths are relative to root."""
    actual_root = _resolve_root(root, str(root))
    actual = _resolve_file(path, actual_root)
    try:
        raw = actual.read_bytes()
    except OSError as error:
        raise ArtifactInputError("FILE_READ_ERROR", actual, 1, str(error)) from error
    try:
        source = raw.decode("utf-8-sig")
    except UnicodeDecodeError as error:
        # utf-8-sig removes the BOM before decoding; offsets refer to error.object.
        line = error.object[:error.start].count(b"\n") + 1
        raise ArtifactInputError("INVALID_ENCODING", actual, line, str(error)) from error
    lines = source.splitlines(keepends=True)
    if not lines or lines[0].rstrip("\r\n") != "---":
        raise ArtifactInputError("MISSING_FRONTMATTER", actual, 1, "File must begin with a YAML --- delimiter")
    closing = next((i for i in range(1, len(lines)) if lines[i].rstrip("\r\n") == "---"), None)
    if closing is None:
        raise ArtifactInputError("UNTERMINATED_FRONTMATTER", actual, 1, "Missing closing YAML --- delimiter")
    data, locations = _load_metadata("".join(lines[1:closing]), actual)
    _validate_metadata(data, locations, actual)
    body = "".join(lines[closing + 1:])
    body_start = closing + 2
    owner = f"{data['scope']}/{data['id']}"
    anchors, acceptances = _body_entries(body, actual, body_start, data["id"], owner)
    anchor_names = {anchor.name for anchor in anchors}
    targets = []
    for index, record in enumerate(data.get("targets", [])):
        criterion_location = locations[("targets", index, "criterionAnchor")]
        if record["criterionAnchor"] not in anchor_names:
            raise ArtifactInputError(
                "MISSING_CRITERION_ANCHOR", actual, criterion_location.line,
                f"Local criterion anchor {record['criterionAnchor']!r} is absent from the body",
            )
        targets.append(Target(
            record["target"], record["criterionAnchor"], record.get("testId"),
            locations[("targets", index)], criterion_location,
        ))
    declaration = data.get("confirmation")
    confirmation = None if declaration is None else Confirmation(
        declaration["by"], declaration["reference"], declaration["baseline"], locations[("confirmation",)],
    )
    return Artifact(
        schema_version=data["schemaVersion"], id=data["id"], kind=data["kind"], scope=data["scope"],
        content_state=cast(ContentState, data["contentState"]), upstream=tuple(data.get("upstream", [])),
        targets=tuple(targets), confirmation=confirmation, path=actual,
        relative_path=actual.relative_to(actual_root).as_posix(), location=SourceLocation(actual, 1),
        id_location=locations[("id",)], body_start_line=body_start, source=source, body=body,
        anchors=anchors, acceptances=acceptances,
    )


def parse_artifacts(paths: Iterable[PathInput], root: PathInput) -> tuple[Artifact, ...]:
    """Parse only the supplied paths, in order, rejecting duplicate scope/id."""
    actual_root = _resolve_root(root, str(root))  # Validate even an empty selection.
    if isinstance(paths, (str, bytes, os.PathLike)):
        raise ArtifactInputError("INVALID_PATH", str(paths), 1, "Expected a collection, not one path")
    try:
        selected = iter(paths)
    except TypeError as error:
        raise ArtifactInputError("INVALID_PATH", str(root), 1, str(error)) from error
    seen: dict[str, Artifact] = {}
    result = []
    for path in selected:
        artifact = parse_artifact(path, actual_root)
        if artifact.key in seen:
            first = seen[artifact.key].id_location
            raise ArtifactInputError(
                "DUPLICATE_ARTIFACT_ID", artifact.path, artifact.id_location.line,
                f"Duplicate {artifact.key}; first defined at {first.path}:{first.line}",
            )
        seen[artifact.key] = artifact
        result.append(artifact)
    return tuple(result)
