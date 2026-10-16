"""Read-only checks for explicitly rooted formal Markdown artifacts."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import re
import stat
import subprocess
import unicodedata
from dataclasses import asdict, dataclass, replace
from pathlib import Path, PurePosixPath
from typing import Literal
from urllib.parse import unquote, urlsplit

from artifact_io import (
    Artifact, ArtifactInputError, PathInput, SourceLocation, _ANCHOR, _INLINE_CODE, _resolve_file,
    _resolve_root, iter_markdown_lines, parse_artifact,
)


@dataclass(frozen=True, slots=True)
class Finding:
    code: str
    path: str
    line: int
    owner: str | None
    target: str | None
    message: str
    related: SourceLocation | None = None


@dataclass(frozen=True, slots=True)
class InputFile:
    path: str
    sha256: str
    size: int
    role: Literal["formal", "guide", "reference"]
    owner: str | None = None


@dataclass(frozen=True, slots=True)
class BaseFile:
    path: str
    blob: str
    sha256: str
    size: int
    formal: bool


@dataclass(frozen=True, slots=True)
class Change:
    path: str
    status: Literal["added", "modified", "deleted"]
    base_blob: str | None
    before_sha256: str | None
    after_sha256: str | None


@dataclass(frozen=True, slots=True)
class Baseline:
    root: str
    target: Literal["working-tree"]
    base_sha: str | None
    base_tree: str | None
    comparison_complete: bool | None
    snapshot_sha256: str
    files: tuple[InputFile, ...]
    base_files: tuple[BaseFile, ...]
    changes: tuple[Change, ...]


@dataclass(frozen=True, slots=True)
class Exclusion:
    path: str
    reason: str


@dataclass(frozen=True, slots=True)
class CheckReport:
    status: Literal["clean", "invalid", "input-error", "empty"]
    findings: tuple[Finding, ...]
    checked_count: int
    baseline: Baseline | None
    excluded: tuple[Exclusion, ...]
    attempted_count: int

    def to_dict(self) -> dict:
        result = asdict(self)
        for finding in result["findings"]:
            if finding["related"] is not None:
                finding["related"]["path"] = str(finding["related"]["path"])
        return result


@dataclass(frozen=True, slots=True)
class Inventory:
    """The report and its actual read snapshot for bounded downstream tools."""

    report: CheckReport
    artifacts: tuple[Artifact, ...]
    raw_files: tuple[tuple[Path, bytes], ...]
    base_raw_files: tuple[tuple[str, bytes], ...]


_FORMAL_NAME = re.compile(r"^[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+(?=[-.\s:：]|$)")
_METADATA_MARKER = re.compile(
    r"""(?:^|[{,])[ \t]*["']?(?:schemaVersion|id|kind|scope|contentState|upstream|targets|confirmation)["']?(?=[: \t]|$)"""
)
_HEADING = re.compile(r" {0,3}(#{1,6})(?:[ \t]+(.*)|$)")
_PLACEHOLDER = re.compile(
    r"待填写|(?<![A-Za-z0-9])(?:(?i:NNN)|TODO|TBD|PROJECT)(?![A-Za-z0-9])"
    r"|(?i:<(?:slug|project|context|id)>)|\{\{[^{}\n]+\}\}",
)
_DESTINATION = r"""(?:<[^>\n]*>|(?:\\.|[^\s()\\]|\([^()\n]*\))+)"""
_OPTIONAL_TITLE = r"""(?:[ \t]+(?:"[^"\n]*"|'[^'\n]*'))?"""
_INLINE_LINK = re.compile(
    r"(?<!\\)!?\[[^\]\n]*\]\([ \t]*(" + _DESTINATION + ")" + _OPTIONAL_TITLE + r"[ \t]*\)"
)
_DEFINITION = re.compile(
    r" {0,3}\[([^\]\n]+)\]:[ \t]*(" + _DESTINATION + ")" + _OPTIONAL_TITLE + r"[ \t]*$"
)
_REFERENCE = re.compile(r"(?<!\\)!?\[([^\]\n]+)\](?:\[([^\]\n]*)\])?")
_TOOL_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__", ".pytest_cache",
              ".mypy_cache", ".tox", ".nox"}
_NATIVE_DIRS = ("skills", "instructions", "agents", "prompts", "workflows")
_ACQUISITION_ERRORS = {
    "FILE_READ_ERROR", "FILE_NOT_FOUND", "DIRECTORY_READ_ERROR", "INVALID_PATH",
    "OUTSIDE_ROOT", "EXCLUDED_TARGET", "INPUT_CHANGED",
}


def _network_path(value: str) -> bool:
    return value.startswith(("\\\\", "//"))


def _local_root(root: PathInput) -> Path:
    if isinstance(root, (str, os.PathLike)):
        value = os.fspath(root)
        if isinstance(value, str) and (_network_path(value) or "://" in value):
            raise ArtifactInputError("INVALID_ROOT", str(root), 1, "Select a local filesystem root, not a network/URL path")
    return _resolve_root(root, str(root))


def _checked_location(value: PathInput, *, missing_ok: bool = False) -> Path:
    """Verify raw traversal before canonicalization, including canceled prefixes."""
    if not isinstance(value, (str, os.PathLike)) or isinstance(value, bytes):
        raise ArtifactInputError("INVALID_ROOT", "root", 1, "An explicit local directory is required")
    try:
        text = os.fspath(value)
        if isinstance(text, str) and (text.startswith(("//", "\\\\")) or "://" in text):
            raise ArtifactInputError("INVALID_ROOT", "root", 1, "Select a local directory, not a network/URL input")
        requested = Path(value)
        if not os.fspath(value).strip() or requested.anchor and not requested.is_absolute():
            raise ArtifactInputError("INVALID_ROOT", "root", 1, "An unambiguous local directory is required")
        requested = requested if requested.is_absolute() else Path.cwd() / requested
        current = Path(requested.anchor)
        parts = requested.parts[1:]
        for index, part in enumerate(parts):
            if part == "..":
                current = current.parent
                continue
            current = current / part
            try:
                info = current.lstat()
            except FileNotFoundError as error:
                if not missing_ok:
                    raise ArtifactInputError("INVALID_ROOT", "root", 1,
                                             "A declared traversal prefix does not exist") from error
                remaining = parts[index + 1:]
                if ".." in remaining:
                    raise ArtifactInputError("UNSAFE_ROOT", "root", 1,
                                             "Cannot verify parent traversal through a missing prefix") from error
                current = current.joinpath(*remaining)
                break
            if (stat.S_ISLNK(info.st_mode)
                    or getattr(info, "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT):
                raise ArtifactInputError("UNSAFE_ROOT", "root", 1,
                                         "Declared traversal cannot pass through a link/reparse point")
            if index < len(parts) - 1 and not stat.S_ISDIR(info.st_mode):
                raise ArtifactInputError("INVALID_ROOT", "root", 1,
                                         "A declared traversal prefix is not a directory")
        actual = current.resolve(strict=not missing_ok)
        if actual != current:
            raise ArtifactInputError("UNSAFE_ROOT", "root", 1, "Declared traversal resolves through an alias")
        return actual
    except (OSError, ValueError, RuntimeError) as error:
        if isinstance(error, ArtifactInputError):
            raise
        raise ArtifactInputError("INVALID_ROOT", "root", 1, "Cannot resolve the explicit local directory") from error


def _git_metadata_bytes(path: PathInput) -> bytes | None:
    """Read only a regular, explicitly local metadata file; never follow a pointer."""
    value = os.fspath(path)
    if _network_path(value) or "://" in value:
        raise ArtifactInputError("GIT_CONFIG_UNSAFE", "Git metadata", 1, "Network metadata locations are unsupported")
    actual = Path(path)
    try:
        actual = _checked_location(actual, missing_ok=True)
        if not actual.exists():
            return None
        if not stat.S_ISREG(actual.stat().st_mode):
            raise ValueError("Metadata must be a regular file")
        return actual.read_bytes()
    except (OSError, ValueError, RuntimeError) as error:
        raise ArtifactInputError("GIT_CONFIG_UNSAFE", actual, 1,
                                 "Git metadata must be a readable local regular file without aliases") from error


def _git_config_file(path: PathInput) -> None:
    """Refuse include declarations without asking Git to parse/follow them.

    This is only an exposure guard, not a Git-config interpreter. Remove quoted
    strings/comments and escaped characters before recognizing section headers;
    includeIf conditions and include paths themselves are never evaluated.
    """
    raw = _git_metadata_bytes(path)
    if raw is None:
        return
    logical = re.sub(rb"\\\r?\n", b"", raw.removeprefix(b"\xef\xbb\xbf"))
    visible = bytearray()
    quoted = comment = escaped = False
    for character in logical:
        if comment:
            if character in (10, 13):
                comment = False
                visible.append(character)
        elif escaped:
            escaped = False
            if not quoted:
                visible.append(32)
        elif character == 92:
            escaped = True
        elif character == 34:
            quoted = not quoted
            visible.append(32)
        elif not quoted and character in (35, 59):
            comment = True
        elif not quoted:
            visible.append(character)
    if re.search(rb"(?:^|[\r\n\]])[ \t\r\v\f]*\[[ \t\r\v\f]*(?:include|includeif)(?=[ \t\r\v\f.\]])",
                 visible, re.I):
        raise ArtifactInputError("GIT_CONFIG_INCLUDES_UNSUPPORTED", path, 1,
                                 "Repository-local include/includeIf configuration is unsupported for bounded local Git")


def _git_config_guard(root: PathInput, *, required: bool = True) -> None:
    """Check local Gitfile/common/worktree configuration BEFORE a Git invocation."""
    actual = _local_root(_checked_location(root))
    marker = actual / ".git"
    try:
        marker = _checked_location(marker, missing_ok=True)
        if not marker.exists():
            if required:
                raise ArtifactInputError("BASE_UNAVAILABLE", actual, 1, "The explicit checkout metadata is absent")
            return  # No Git discovery/ancestor borrowing for a plain local source.

        def pointer(raw: bytes, parent: Path, context: Path, *, prefix: str = "") -> Path:
            text = raw.decode("utf-8").strip()
            if prefix:
                if not text.startswith(prefix):
                    raise ValueError("Unsupported Gitfile")
                text = text[len(prefix):]
            text = text.strip()
            if (not text or _network_path(text) or "://" in text or re.search(r"[\x00-\x1f]", text)
                    or re.match(r"^[A-Za-z][A-Za-z0-9+.-]+:", text)):
                raise ValueError("Unsupported metadata pointer")
            # The pointer was rejected as text before any resolve/stat/open of it.
            return _checked_location(parent / text)

        if marker.is_dir():
            directory = marker
        else:
            directory = pointer(_git_metadata_bytes(marker) or b"", marker.parent, marker, prefix="gitdir: ")
        common_data = _git_metadata_bytes(directory / "commondir")
        common = directory if common_data is None else pointer(common_data, directory, directory / "commondir")
        head = (_git_metadata_bytes(directory / "HEAD") or b"").strip()
        if not ((head.startswith(b"ref:") and head[4:].strip().startswith(b"refs/"))
                or re.fullmatch(rb"(?:[0-9a-fA-F]{40}|[0-9a-fA-F]{64})", head)):
            raise ArtifactInputError("BASE_UNAVAILABLE", marker, 1,
                                     "Incomplete explicit checkout metadata cannot use ancestor Git discovery")
        for name in ("objects", "refs"):
            if not _checked_location(common / name).is_dir():
                raise ValueError("Git storage metadata is not a regular local directory")
        _git_config_file(common / "config")
        _git_config_file(directory / "config.worktree")
    except (OSError, ValueError, RuntimeError) as error:
        if isinstance(error, ArtifactInputError) and error.code in (
                "BASE_UNAVAILABLE", "GIT_CONFIG_INCLUDES_UNSUPPORTED", "GIT_CONFIG_UNSAFE"):
            raise
        raise ArtifactInputError("GIT_CONFIG_UNSAFE", marker, 1,
                                 "Gitfile/common/worktree metadata must be regular, local and safely readable") from error


def _domain_location(root: Path, source_root: str, relative: str) -> tuple[Path, Path]:
    """Resolve a declared local domain root/path, without requiring its existence.

    Writers reserve this location before any baseline/dereference can fail.
    Readers separately require existence, regular bytes and the declared basis.
    """
    if (not isinstance(source_root, str) or not source_root or source_root.strip() != source_root
            or _network_path(source_root) or re.search(r"[\\:\x00-\x1f$%~]", source_root)
            or Path(source_root).is_absolute()):
        raise ArtifactInputError("INVALID_ROOT", root, 1, "Use an explicit local relative domain root")
    if (not isinstance(relative, str) or not relative or relative.strip() != relative
            or re.search(r"[\\:#\x00-\x1f]", relative) or relative.startswith("/") or relative.endswith("/")
            or relative != "." and any(part in ("", ".", "..") for part in relative.split("/"))):
        raise ArtifactInputError("INVALID_PATH", root, 1, "Use an explicit path within the domain source root")
    if _exclusion(source_root) == "TOOL_DATA" or _exclusion(relative) == "TOOL_DATA":
        raise ArtifactInputError("EXCLUDED_TARGET", root, 1, "Tool data cannot be a domain input")
    try:
        actual_root = (root / source_root).resolve()
        lexical = actual_root / relative
        path = lexical.resolve()
    except (OSError, ValueError, RuntimeError) as error:
        raise ArtifactInputError("INVALID_PATH", root, 1, "Cannot resolve the declared domain location") from error
    if not path.is_relative_to(actual_root) or path != lexical:
        raise ArtifactInputError("OUTSIDE_ROOT", lexical, 1, "Domain paths cannot traverse links or escape their source root")
    return actual_root, path


def _exclusion(relative: str) -> str | None:
    """Rules are relative to the selected root, never to its ancestors."""
    parts = PurePosixPath(relative).parts
    if any(part in _TOOL_DIRS for part in parts):
        return "TOOL_DATA"
    if parts[:1] == ("_templates",) or relative == ".github/pull_request_template.md":
        return "TEMPLATE"
    if (len(parts) >= 2 and parts[0] == ".github" and parts[1] in _NATIVE_DIRS
            or relative == ".github/copilot-instructions.md"):
        return "NATIVE_METADATA"
    if len(parts) >= 2 and parts[0] == "docs" and parts[1] in ("design", "plan", "research"):
        return "MAKER_DATA"
    if any(part in ("tests", "test", "fixtures") for part in parts):
        return "TEST_FIXTURE"
    return None


def _formal(relative: str, source: str) -> bool:
    # Selection signals only, not another YAML/frontmatter parser. All actual
    # field validation and owner acceptance parsing belong to artifact_io.
    if _FORMAL_NAME.match(PurePosixPath(relative).stem):
        return True
    lines = source.splitlines()
    if lines and lines[0] == "---":
        for line in lines[1:]:
            if line == "---":
                break
            if _METADATA_MARKER.search(line):
                return True
    preamble = True
    for number, line in iter_markdown_lines(source):
        if line is None:
            preamble = False
            continue
        # A recognizable first delimiter keeps the metadata preamble open.
        # Only the parser decides whether its whitespace is actually valid.
        if number == 1 and re.fullmatch(r" {0,3}---[ \t]*", line):
            continue
        if preamble and _METADATA_MARKER.search(line):
            return True
        heading = _HEADING.fullmatch(line)
        if heading and heading[1] == "#" and _FORMAL_NAME.match(heading[2] or ""):
            return True
        if line.strip():
            preamble = False
    return False


def _error(error: ArtifactInputError, artifact: Artifact | None = None,
           line: int | None = None, target: str | None = None) -> Finding:
    return Finding(
        error.code, str(artifact.path if artifact else error.path),
        line if line is not None else error.line, artifact.key if artifact else None,
        target, error.message,
    )


def _walk(root: Path, excluded: list[Exclusion], errors: list[Finding]) -> list[Path]:
    paths: list[Path] = []

    def visit(directory: Path) -> None:
        try:
            with os.scandir(directory) as entries:
                children = sorted(entries, key=lambda entry: entry.name)
        except OSError as error:
            errors.append(Finding("DIRECTORY_READ_ERROR", str(directory), 1, None, None, str(error)))
            return
        for child in children:
            path = Path(child.path)
            relative = path.relative_to(root).as_posix()
            try:
                mode = child.stat(follow_symlinks=False).st_mode
                reason = _exclusion(relative)
                if reason is not None:
                    excluded.append(Exclusion(relative + ("/" if stat.S_ISDIR(mode) else ""), reason))
                    continue
                actual = path.resolve(strict=True)
                if not actual.is_relative_to(root):
                    raise ArtifactInputError("OUTSIDE_ROOT", path, 1, "Directory/file link leaves the explicit root")
                is_directory = actual.is_dir()
                if is_directory:
                    if actual != path:
                        excluded.append(Exclusion(relative + "/", "DIRECTORY_ALIAS"))
                    else:
                        visit(actual)
                elif path.suffix.lower() != ".md":
                    excluded.append(Exclusion(relative, "NON_MARKDOWN"))
                elif stat.S_ISLNK(mode) or not stat.S_ISREG(mode):
                    raise ArtifactInputError("INVALID_PATH", path, 1, "Formal input must be a regular, non-symlink file")
                else:
                    paths.append(path)
            except ArtifactInputError as error:
                errors.append(_error(error))
            except (OSError, ValueError, RuntimeError) as error:
                errors.append(Finding("FILE_READ_ERROR", str(path), 1, None, None, str(error)))
    visit(root)
    return sorted(paths)


def _read(path: Path, root: Path, raw_files: dict[Path, bytes],
          records: dict[Path, InputFile], role: Literal["formal", "guide", "reference"]) -> bytes:
    actual = _resolve_file(path, root)
    try:
        raw = actual.read_bytes()
    except OSError as error:
        raise ArtifactInputError("FILE_READ_ERROR", actual, 1, str(error)) from error
    if actual in raw_files and raw_files[actual] != raw:
        raise ArtifactInputError("INPUT_CHANGED", actual, 1, "Input changed during this check; rerun on stable files")
    raw_files[actual] = raw
    if actual not in records:
        records[actual] = InputFile(
            actual.relative_to(root).as_posix(), hashlib.sha256(raw).hexdigest(), len(raw), role,
        )
    elif role == "formal":
        records[actual] = replace(records[actual], role=role)
    return raw


def _decode(raw: bytes, path: Path) -> str:
    try:
        return raw.decode("utf-8-sig")
    except UnicodeDecodeError as error:
        line = error.object[:error.start].count(b"\n") + 1
        raise ArtifactInputError("INVALID_ENCODING", path, line, str(error)) from error


def _git_environment() -> dict[str, str]:
    env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    env.update(
        GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1", GIT_TERMINAL_PROMPT="0",
        GIT_OPTIONAL_LOCKS="0", GIT_NO_REPLACE_OBJECTS="1", GIT_NO_LAZY_FETCH="1",
    )
    return env


def _git(root: Path, *arguments: str) -> bytes:
    _git_config_guard(root)
    try:
        result = subprocess.run(
            ["git", "--no-pager", "--no-replace-objects", "-c", "core.fsmonitor=false",
             "-c", "protocol.allow=never", *arguments],
            cwd=root, env=_git_environment(), shell=False, capture_output=True, timeout=60,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        raise ArtifactInputError("BASE_UNAVAILABLE", root, 1, str(error)) from error
    if result.returncode:
        message = result.stderr.decode("utf-8", errors="replace").strip()
        raise ArtifactInputError("BASE_UNAVAILABLE", root, 1, f"Git read exit {result.returncode}: {message}")
    return result.stdout


def _commit_tree(root: Path, base_sha: str) -> tuple[str, str, bytes]:
    """Exact readable local commit and raw manifest, without checkout or filters."""
    if not isinstance(base_sha, str) or not re.fullmatch(r"(?:[0-9a-fA-F]{40}|[0-9a-fA-F]{64})", base_sha):
        raise ArtifactInputError("INVALID_BASE", root, 1, "Base must be a full 40- or 64-hex Git commit ID")
    base_sha = base_sha.lower()
    try:
        top = Path(_git(root, "rev-parse", "--show-toplevel").decode("utf-8").strip()).resolve()
        if top != root:
            raise ArtifactInputError("BASE_UNAVAILABLE", root, 1, "Base mode requires the explicit checkout root, not an ancestor repository")
        if _git(root, "cat-file", "-t", base_sha).strip() != b"commit":
            raise ArtifactInputError("BASE_UNAVAILABLE", root, 1, "The exact supplied object is not a commit")
        tree = _git(root, "rev-parse", f"{base_sha}^{{tree}}").decode("ascii").strip()
        entries = _git(root, "ls-tree", "-r", "-z", "--full-tree", base_sha)
        return base_sha, tree, entries
    except (UnicodeError, ValueError) as error:
        if isinstance(error, ArtifactInputError):
            raise
        raise ArtifactInputError("BASE_UNAVAILABLE", root, 1, f"Unreadable Git manifest: {error}") from error


def _fixed_file(root: Path, path: Path, raw: bytes, baseline: str) -> None:
    """Verify acquired file bytes against a raw digest or exact local commit/blob."""
    if not isinstance(baseline, str) or not re.fullmatch(r"(?:[0-9a-f]{40}|[0-9a-f]{64}|sha256:[0-9a-f]{64})", baseline):
        raise ArtifactInputError("INVALID_BASE", path, 1, "A full local Git object or raw sha256 is required")
    if baseline.startswith("sha256:"):
        if baseline != "sha256:" + hashlib.sha256(raw).hexdigest():
            raise ArtifactInputError("BASE_MISMATCH", path, 1, "Source bytes differ from the supplied sha256")
        return
    top = Path(_git(root, "rev-parse", "--show-toplevel").decode("utf-8").strip()).resolve()
    if top != root:
        raise ArtifactInputError("BASE_UNAVAILABLE", path, 1, "Source Git objects require the explicit checkout root")
    kind = _git(root, "cat-file", "-t", baseline).strip()
    blob = baseline
    if kind == b"commit":
        relative = path.relative_to(root).as_posix()
        entries = [entry for entry in _git(root, "--literal-pathspecs", "ls-tree", "-r", "-z",
                                          "--full-tree", baseline, "--", relative).split(b"\0") if entry]
        if len(entries) != 1:
            raise ArtifactInputError("BASE_UNAVAILABLE", path, 1, "Source path is absent/ambiguous at the exact commit")
        header, name = entries[0].split(b"\t", 1)
        mode, object_kind, object_id = header.decode("ascii").split()
        if name.decode("utf-8") != relative or object_kind != "blob" or mode not in ("100644", "100755"):
            raise ArtifactInputError("BASE_UNAVAILABLE", path, 1, "Exact commit source is not a regular blob")
        blob = object_id
    elif kind != b"blob":
        raise ArtifactInputError("BASE_UNAVAILABLE", path, 1, "Source baseline must be an exact commit or blob")
    if _git(root, "cat-file", "blob", blob) != raw:
        raise ArtifactInputError("BASE_MISMATCH", path, 1, "Source bytes differ from the exact local Git blob")


def _base(root: Path, base_sha: str, *,
          raw_files: dict[str, bytes] | None = None) -> tuple[str, str, tuple[BaseFile, ...]]:
    base_sha, tree, entries = _commit_tree(root, base_sha)
    try:
        files = []
        for entry in entries.split(b"\0"):
            if not entry:
                continue
            header, name = entry.split(b"\t", 1)
            _, kind, blob = header.decode("ascii").split()
            relative = name.decode("utf-8")
            if _exclusion(relative) or PurePosixPath(relative).suffix.lower() != ".md":
                continue
            if kind != "blob":
                raise ArtifactInputError("BASE_UNAVAILABLE", root, 1, f"Not a historical file: {relative}")
            raw = _git(root, "cat-file", "blob", blob)
            if raw_files is not None:
                raw_files[relative] = raw
            # Historical bytes are comparison evidence, not newer-schema inputs.
            files.append(BaseFile(relative, blob, hashlib.sha256(raw).hexdigest(), len(raw),
                                  _formal(relative, raw.decode("utf-8-sig", errors="replace"))))
    except (UnicodeError, ValueError) as error:
        if isinstance(error, ArtifactInputError):
            raise
        raise ArtifactInputError("BASE_UNAVAILABLE", root, 1, f"Unreadable Git manifest: {error}") from error
    return base_sha, tree, tuple(sorted(files, key=lambda item: item.path))


def _mask_code(line: str) -> str:
    return _INLINE_CODE.sub(lambda match: " " * len(match[0]), line)


def _document_findings(artifact: Artifact) -> list[Finding]:
    findings: list[Finding] = []

    def add(code: str, line: int, target: str | None, message: str) -> None:
        findings.append(Finding(code, str(artifact.path), line, artifact.key, target, message))

    titles = []
    for number, line in iter_markdown_lines(artifact.body, artifact.body_start_line):
        if line is None:
            continue
        heading = _HEADING.fullmatch(line)
        if heading and heading[1] == "#":
            titles.append(number)
            if not (heading[2] or "").strip(" \t#"):
                add("EMPTY_TITLE", number, None, "H1 needs a nonempty title")
            if len(titles) > 1:
                add("MULTIPLE_TITLES", number, None, f"Only one H1 is supported; first on line {titles[0]}")
        for marker in _PLACEHOLDER.finditer(_mask_code(line)):
            add("INCOMPLETE_ARTIFACT", number, marker[0], "Residual formal placeholder; supply a fact or state the specific unresolved question")
    if not titles:
        add("MISSING_TITLE", artifact.body_start_line, None, "Formal body needs one H1 title")

    locations = dict(artifact.metadata_locations)
    values = [(("id",), artifact.id), (("scope",), artifact.scope)]
    values.extend((("upstream", index), value) for index, value in enumerate(artifact.upstream))
    for index, target in enumerate(artifact.targets):
        values.extend(((("targets", index, "target"), target.target),
                       (("targets", index, "criterionAnchor"), target.criterion_anchor)))
        if target.test_id is not None:
            values.append((("targets", index, "testId"), target.test_id))
    if artifact.confirmation is not None:
        for key in ("by", "reference", "baseline"):
            values.append((("confirmation", key), getattr(artifact.confirmation, key)))
    for field, value in values:
        if _PLACEHOLDER.search(value):
            location = locations.get(field, artifact.location)
            add("INCOMPLETE_ARTIFACT", location.line, value, f"Residual placeholder in {'.'.join(map(str, field))}")
    return findings


def _anchors(source: str, artifact: Artifact | None = None) -> set[str]:
    # Owner-qualified acceptances/explicit formal anchors come from the parser.
    anchors = {anchor.name for anchor in artifact.anchors} if artifact else set()
    used_headings: set[str] = set()
    body = artifact.body if artifact else source
    for _, line in iter_markdown_lines(body):
        if line is None:
            continue
        if artifact is None:
            anchor = _ANCHOR.fullmatch(line)
            if anchor:
                anchors.add(anchor[2])
        heading = _HEADING.fullmatch(line)
        if heading and heading[2]:
            title = re.sub(r"[ \t]+#+[ \t]*$", "", heading[2])
            title = _INLINE_LINK.sub(lambda match: match[0].split("]", 1)[0].lstrip("!["), title)
            title = re.sub(r"<[^>]*>", "", title)
            title = html.unescape(title).lower()
            slug = "".join(char for char in title
                           if char in " _-" or unicodedata.category(char)[0] in "LN")
            slug = slug.replace(" ", "-")
            candidate = slug
            count = 0
            while candidate in used_headings:
                count += 1
                candidate = f"{slug}-{count}"
            used_headings.add(candidate)
            anchors.add(candidate)
    return anchors


def _links(artifact: Artifact) -> tuple[list[tuple[int, str]], list[Finding]]:
    lines = [(number, _mask_code(line)) for number, line in
             iter_markdown_lines(artifact.body, artifact.body_start_line) if line is not None]
    definitions: dict[str, str] = {}
    links: list[tuple[int, str]] = []
    findings: list[Finding] = []

    def label(value: str) -> str:
        return " ".join(value.split()).casefold()

    for _, line in lines:
        match = _DEFINITION.fullmatch(line)
        if match:
            definitions.setdefault(label(match[1]), match[2])
    for number, line in lines:
        if _DEFINITION.fullmatch(line):
            continue
        for match in _INLINE_LINK.finditer(line):
            links.append((number, match[1]))
        remaining = _INLINE_LINK.sub(lambda match: " " * len(match[0]), line)
        for match in _REFERENCE.finditer(remaining):
            key = label(match[2] or match[1])
            if key in definitions:
                links.append((number, definitions[key]))
            elif match[2] is not None:
                findings.append(Finding("UNRESOLVED_REFERENCE", str(artifact.path), number,
                                        artifact.key, key, "No local reference-link definition"))
    return links, findings


def _link_findings(artifact: Artifact, root: Path, artifacts: dict[Path, Artifact],
                   raw_files: dict[Path, bytes], records: dict[Path, InputFile]) -> tuple[list[Finding], list[Finding]]:
    links, findings = _links(artifact)
    errors: list[Finding] = []
    for number, target in links:
        destination = html.unescape(target.removeprefix("<").removesuffix(">"))
        try:
            if _network_path(destination):
                raise ArtifactInputError("OUTSIDE_ROOT", artifact.path, number, "UNC/network paths are not local references")
            destination = re.sub(r"\\([\\`*{}\[\]()#+.!_<> -])", r"\1", destination)
            parsed = urlsplit(destination)
            if parsed.scheme and parsed.scheme != "file" and len(parsed.scheme) != 1:
                continue  # External addresses are never fetched.
            if parsed.netloc and (parsed.scheme != "file" or parsed.netloc != "localhost"):
                raise ArtifactInputError("OUTSIDE_ROOT", artifact.path, number, "Network/UNC file references are outside root")
            name = unquote(parsed.path, errors="strict")
            fragment = unquote(parsed.fragment, errors="strict")
            if parsed.scheme == "file" and re.match(r"^/[A-Za-z]:/", name):
                name = name[1:]
            if len(parsed.scheme) == 1:
                name = unquote(destination.split("#", 1)[0], errors="strict")
            if _network_path(name):
                raise ArtifactInputError("OUTSIDE_ROOT", artifact.path, number, "Encoded UNC/network path is outside root")
            path = artifact.path if not name else artifact.path.parent / name
            lexical = Path(os.path.abspath(path))
            if not lexical.is_relative_to(root):
                raise ArtifactInputError("OUTSIDE_ROOT", artifact.path, number, "Local reference leaves the explicit root")
            if _exclusion(lexical.relative_to(root).as_posix()) == "TOOL_DATA":
                raise ArtifactInputError("EXCLUDED_TARGET", lexical, 1, "Git, environment and dependency data are not link-read inputs")
            actual = _resolve_file(path, root)
            if _exclusion(actual.relative_to(root).as_posix()) == "TOOL_DATA":
                raise ArtifactInputError("EXCLUDED_TARGET", actual, 1, "Git, environment and dependency data are not link-read inputs")
            raw = _read(actual, root, raw_files, records, "reference")
            if fragment:
                if actual.suffix.lower() != ".md":
                    findings.append(Finding("UNSUPPORTED_FRAGMENT", str(artifact.path), number,
                                            artifact.key, target, "Fragments are supported only for local Markdown files"))
                elif fragment not in _anchors(_decode(raw, actual), artifacts.get(actual)):
                    findings.append(Finding("BROKEN_ANCHOR", str(artifact.path), number,
                                            artifact.key, target, "Local Markdown fragment is absent"))
        except ArtifactInputError as error:
            if error.code == "FILE_NOT_FOUND":
                findings.append(Finding("BROKEN_LINK", str(artifact.path), number,
                                        artifact.key, target, error.message))
            else:
                errors.append(_error(error, artifact, number, target))
        except (ValueError, UnicodeError) as error:
            findings.append(Finding("INVALID_LINK", str(artifact.path), number,
                                    artifact.key, target, str(error)))
    return findings, errors


def _baseline(root: Path, selected_base: str | None, tree: str | None,
              records: dict[Path, InputFile], base_files: tuple[BaseFile, ...],
              complete: bool) -> Baseline:
    files = tuple(sorted(records.values(), key=lambda item: item.path))
    current = {item.path: item for item in files}
    previous = {item.path: item for item in base_files}
    changes = []
    if selected_base is not None:
        scope = {item.path for item in files if item.role == "formal"}
        scope.update(item.path for item in base_files if item.formal)
        for path in sorted(scope):
            before, after = previous.get(path), current.get(path)
            if after is None and not complete:
                continue  # An unavailable input must never masquerade as a deletion.
            if before is not None and after is not None and before.sha256 == after.sha256:
                continue
            changes.append(Change(
                path, "added" if before is None else "deleted" if after is None else "modified",
                before.blob if before else None, before.sha256 if before else None,
                after.sha256 if after else None,
            ))
    identity = json.dumps([asdict(item) for item in files], sort_keys=True, separators=(",", ":"))
    return Baseline(str(root), "working-tree", selected_base, tree,
                    complete if selected_base is not None else None,
                    hashlib.sha256(identity.encode("utf-8")).hexdigest(), files, base_files, tuple(changes))


def read_inventory(root: PathInput, base_sha: str | None = None, *,
                   _base_root: PathInput | None = None) -> Inventory:
    """Keep one checked read set; consumers must not reparse mutable source files."""
    base_raw_files: dict[str, bytes] = {}
    try:
        actual_root = _local_root(root)
        # The native hook's private snapshot adapter supplies the original Git
        # root for raw history only. Current files still come solely from root.
        history_root = actual_root if _base_root is None else _local_root(_base_root)
        selected_base, tree, base_files = (_base(history_root, base_sha, raw_files=base_raw_files) if base_sha is not None
                                            else (None, None, ()))
    except ArtifactInputError as error:
        return Inventory(CheckReport("input-error", (_error(error),), 0, None, (), 0), (), (), ())
    findings: list[Finding] = []
    errors: list[Finding] = []
    excluded: list[Exclusion] = []
    raw_files: dict[Path, bytes] = {}
    records: dict[Path, InputFile] = {}
    artifacts: dict[Path, Artifact] = {}
    owners: dict[str, Artifact] = {}
    prior_formal = {item.path for item in base_files if item.formal}
    attempted = 0
    paths = _walk(actual_root, excluded, errors)
    for path in paths:
        relative = path.relative_to(actual_root).as_posix()
        formal = bool(_FORMAL_NAME.match(path.stem)) or relative in prior_formal
        try:
            raw = _read(path, actual_root, raw_files, records, "formal" if formal else "guide")
            source = _decode(raw, path)
            formal = formal or _formal(relative, source)
            if not formal:
                excluded.append(Exclusion(relative, "LIGHTWEIGHT_GUIDE"))
                continue
            artifact = parse_artifact(path, actual_root)
            _read(path, actual_root, raw_files, records, "formal")
            if artifact.source != source:
                raise ArtifactInputError("INPUT_CHANGED", path, 1, "Parser read a different snapshot")
            artifacts[path] = artifact
            records[path] = replace(records[path], owner=artifact.key)
            if artifact.key in owners:
                first = owners[artifact.key].id_location
                errors.append(Finding(
                    "DUPLICATE_ARTIFACT_ID", str(path), artifact.id_location.line,
                    artifact.key, artifact.key, f"First definition at {first.path}:{first.line}", first,
                ))
            else:
                owners[artifact.key] = artifact
            findings.extend(_document_findings(artifact))
        except ArtifactInputError as error:
            errors.append(_error(error))
        finally:
            if formal:
                attempted += 1
                if path in records:
                    records[path] = replace(records[path], role="formal")
    for artifact in artifacts.values():
        violations, input_errors = _link_findings(artifact, actual_root, artifacts, raw_files, records)
        findings.extend(violations)
        errors.extend(input_errors)
    complete = not any(error.code in _ACQUISITION_ERRORS for error in errors)
    baseline = _baseline(actual_root, selected_base, tree, records, base_files, complete)
    status = "input-error" if errors else "invalid" if findings else "clean" if artifacts else "empty"
    report = CheckReport(
        status, tuple(sorted([*errors, *findings], key=lambda item: (item.path, item.line, item.code, item.target or ""))),
        len(artifacts), baseline, tuple(sorted(excluded, key=lambda item: (item.path, item.reason))), attempted,
    )
    return Inventory(report, tuple(artifacts.values()), tuple(sorted(raw_files.items())),
                     tuple(sorted(base_raw_files.items())))


def run_check(root: PathInput, base_sha: str | None = None) -> CheckReport:
    """Validate the complete current inventory; a base adds comparison, not filtering."""
    return read_inventory(root, base_sha).report


def _report_path(value: str, root: str) -> Path:
    return _output_path(value, root, (".json",))


def _output_path(value: str, root: str, suffixes: tuple[str, ...]) -> Path:
    try:
        if _network_path(value) or "://" in value:
            raise ArtifactInputError("REPORT_CONFLICT", value, 1, "The report destination must be local")
        path = Path(value)
        if not value.strip() or path.anchor and not path.is_absolute():
            raise ArtifactInputError("REPORT_CONFLICT", value, 1, "An unambiguous explicit report path is required")
        if not path.is_absolute():
            path = _local_root(root) / path
        if path.exists() or path.is_symlink():
            raise ArtifactInputError("REPORT_CONFLICT", path, 1, "A report may not replace any existing file or directory")
        path = path.resolve()
        if path.suffix.lower() not in suffixes:
            raise ArtifactInputError("REPORT_CONFLICT", path, 1, f"An explicit new file with suffix {suffixes} is required")
        return path
    except (OSError, ValueError, RuntimeError) as error:
        if isinstance(error, ArtifactInputError):
            raise
        raise ArtifactInputError("REPORT_WRITE_ERROR", value, 1, str(error)) from error


def _write_report(payload: dict, value: str, root: str) -> None:
    """Shared protected JSON output only; no CLI dispatch or source execution."""
    output = _report_path(value, root)
    payload["report_output"] = {"path": str(output), "written": True}
    try:
        with output.open("x", encoding="utf-8", newline="\n") as destination:
            destination.write(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    except FileExistsError as error:
        raise ArtifactInputError("REPORT_CONFLICT", output, 1, str(error)) from error
    except OSError as error:
        raise ArtifactInputError("REPORT_WRITE_ERROR", output, 1, str(error)) from error


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True)
    parser.add_argument("--base")
    parser.add_argument("--report")
    arguments = parser.parse_args()
    report = run_check(arguments.root, arguments.base)
    payload = report.to_dict()
    if arguments.report is not None:
        try:
            _write_report(payload, arguments.report, arguments.root)
        except ArtifactInputError as error:
            report = replace(report, status="input-error", findings=(*report.findings, _error(error)))
            payload = report.to_dict()
            payload["report_output"] = {"path": str(error.path), "written": False}
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return {"clean": 0, "empty": 0, "invalid": 1, "input-error": 2}[report.status]


if __name__ == "__main__":
    raise SystemExit(main())
