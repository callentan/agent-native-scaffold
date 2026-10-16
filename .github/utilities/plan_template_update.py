"""Read-only three-way update proposals; never apply, fetch or publish."""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass, replace
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat

from artifact_io import ArtifactInputError, PathInput, load_yaml_mapping
from check_artifacts import Exclusion, _commit_tree, _git, _local_root, _output_path, _TOOL_DIRS


@dataclass(frozen=True, slots=True)
class TreeSource:
    """One explicit local tree, with an optional exact version and file scope."""
    root: PathInput
    version: str | None = None
    files: tuple[str, ...] | None = None


@dataclass(frozen=True, slots=True)
class FileIdentity:
    path: str
    source: str
    version: str
    sha256: str | None
    size: int | None


@dataclass(frozen=True, slots=True)
class TreeIdentity:
    role: str
    root: str
    version: str
    snapshot: str
    files: tuple[FileIdentity, ...]
    excluded: tuple[Exclusion, ...]
    selection: tuple[str, ...] | None

@dataclass(frozen=True, slots=True)
class UpdateItem:
    path: str
    action: str
    reason: str
    base: FileIdentity
    local: FileIdentity
    candidate: FileIdentity


@dataclass(frozen=True, slots=True)
class UpdatePlan:
    changes: tuple[UpdateItem, ...]
    conflicts: tuple[UpdateItem, ...]
    preserved: tuple[UpdateItem, ...]
    sources: tuple[TreeIdentity, ...]

    @property
    def status(self) -> str:
        return "conflict" if self.conflicts else "proposed" if self.changes else "no-change"

    def to_dict(self) -> dict:
        return {"status": self.status, **asdict(self)}


@dataclass(frozen=True, slots=True)
class ProposalProblem:
    code: str
    path: str
    line: int
    message: str


@dataclass(frozen=True, slots=True)
class FileMapping:
    scenario: str
    source: str
    target: str


@dataclass(frozen=True, slots=True)
class TargetProposal:
    id: str
    repository: str | None
    scope: str | None
    status: str
    mappings: tuple[FileMapping, ...]
    plan: UpdatePlan | None
    findings: tuple[ProposalProblem, ...]


@dataclass(frozen=True, slots=True)
class BatchPlan:
    source_repository: str
    registration_path: str
    registration_sha256: str
    targets: tuple[TargetProposal, ...]

    @property
    def status(self) -> str:
        states = {target.status for target in self.targets}
        return ("input-error" if "unavailable" in states else "conflict" if "conflict" in states
                else "proposed" if "proposed" in states else "no-change")

    def to_dict(self) -> dict:
        return {
            "status": self.status, "source_repository": self.source_repository,
            "registration": {"path": self.registration_path, "sha256": self.registration_sha256},
            "targets": [{**asdict(target), "plan": target.plan.to_dict() if target.plan else None}
                        for target in self.targets],
        }


@dataclass(frozen=True, slots=True)
class _Snapshot:
    root: Path
    identity: TreeIdentity
    raw: tuple[tuple[str, bytes], ...]
    directories: tuple[str, ...]


def _sha(raw: bytes) -> str:
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def _root(value: PathInput) -> Path:
    if not isinstance(value, (str, os.PathLike)) or isinstance(value, bytes):
        raise ArtifactInputError("INVALID_ROOT", "root", 1, "An explicit local directory is required")
    try:
        text = os.fspath(value)
        if isinstance(text, str) and (text.startswith(("//", "\\\\")) or "://" in text):
            raise ArtifactInputError("INVALID_ROOT", "root", 1, "Select a local directory, not a network/URL input")
        requested = Path(value)
        if not os.fspath(value).strip() or requested.anchor and not requested.is_absolute():
            raise ArtifactInputError("INVALID_ROOT", "root", 1, "An unambiguous local directory is required")
        # Keep the lexical location for the alias check; do not traverse a link
        # and then reinterpret its destination as a newly authorized source.
        lexical = Path(os.path.abspath(requested))
        actual = _local_root(value)
        if lexical != actual or actual.parent == actual:
            raise ArtifactInputError("UNSAFE_ROOT", str(value), 1, "Root aliases and filesystem roots are not update inputs")
        return actual
    except (OSError, ValueError, RuntimeError) as error:
        if isinstance(error, ArtifactInputError):
            raise
        raise ArtifactInputError("INVALID_ROOT", "root", 1, "Cannot resolve the explicit local directory") from error


def _exclusion(name: str) -> str | None:
    if name.casefold() in _TOOL_DIRS:
        return "TOOL_DATA"
    if name.casefold() in ("test", "tests", "fixtures"):
        return "TEST_FIXTURE"
    return None


def _selection(files: tuple[str, ...] | None) -> tuple[str, ...] | None:
    if files is None:
        return None
    if not isinstance(files, tuple) or not files:
        raise ArtifactInputError("INVALID_SCOPE", "files", 1, "Use a nonempty tuple of explicit relative files")
    seen = set()
    for relative in files:
        if (not isinstance(relative, str) or not relative or relative.strip() != relative
                or re.search(r"[\\:#\x00-\x1f]", relative)
                or any(part in ("", ".", "..") for part in relative.split("/"))
                or any(_exclusion(part) for part in relative.split("/"))
                or relative.casefold() in seen):
            raise ArtifactInputError("INVALID_SCOPE", "files", 1, "File scopes require unique, nonexcluded local relative paths")
        seen.add(relative.casefold())
    return tuple(sorted(files))


def _snapshot(root: Path, role: str, selection: tuple[str, ...] | None = None) -> _Snapshot:
    raw, directories, excluded = {}, [], []

    def visit(directory: Path) -> None:
        try:
            with os.scandir(directory) as entries:
                children = sorted(entries, key=lambda entry: entry.name)
        except OSError as error:
            raise ArtifactInputError("DIRECTORY_READ_ERROR", role, 1, "Cannot enumerate the selected tree") from error
        for child in children:
            path = Path(child.path)
            relative = path.relative_to(root).as_posix()
            try:
                info = child.stat(follow_symlinks=False)
                reason = _exclusion(child.name)
                if reason:
                    excluded.append(Exclusion(relative + ("/" if stat.S_ISDIR(info.st_mode) else ""), reason))
                    continue
                if (stat.S_ISLNK(info.st_mode)
                        or getattr(info, "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT
                        or path.resolve(strict=True) != path):
                    raise ArtifactInputError("UNSAFE_PATH", relative, 1, "Input links/reparse points are not followed")
                if stat.S_ISDIR(info.st_mode):
                    directories.append(relative)
                    visit(path)
                elif stat.S_ISREG(info.st_mode):
                    raw[relative] = path.read_bytes()
                else:
                    raise ArtifactInputError("UNSAFE_PATH", relative, 1, "Input is not a regular file or directory")
            except (OSError, ValueError, RuntimeError) as error:
                if isinstance(error, ArtifactInputError):
                    raise
                raise ArtifactInputError("FILE_READ_ERROR", relative, 1, "Cannot read the selected input file") from error

    if selection is None:
        visit(root)
    else:
        # Even a selection whose files are all absent needs a readable root.
        try:
            with os.scandir(root):
                pass
        except OSError as error:
            raise ArtifactInputError("DIRECTORY_READ_ERROR", role, 1, "Cannot enumerate the selected tree") from error
        for relative in selection:
            current = root
            for index, part in enumerate(relative.split("/")):
                current = current / part
                try:
                    info = current.lstat()
                except FileNotFoundError:
                    break  # Only a missing directory entry is verified absence.
                except (OSError, ValueError) as error:
                    raise ArtifactInputError("FILE_READ_ERROR", relative, 1, "Cannot inspect the selected input file") from error
                try:
                    if (stat.S_ISLNK(info.st_mode)
                            or getattr(info, "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT
                            or current.resolve(strict=True) != current):
                        raise ArtifactInputError("UNSAFE_PATH", relative, 1, "Selected input paths cannot traverse links")
                    if index < len(relative.split("/")) - 1:
                        if not stat.S_ISDIR(info.st_mode):
                            raise ArtifactInputError("PATH_TYPE_CONFLICT", relative, 1, "A file blocks a selected parent directory")
                        directories.append(current.relative_to(root).as_posix())
                    elif stat.S_ISREG(info.st_mode):
                        raw[relative] = current.read_bytes()
                    else:
                        raise ArtifactInputError("PATH_TYPE_CONFLICT", relative, 1, "Selected file is not a regular file")
                except (OSError, ValueError, RuntimeError) as error:
                    if isinstance(error, ArtifactInputError):
                        raise
                    raise ArtifactInputError("FILE_READ_ERROR", relative, 1, "Cannot read the selected input file") from error
    records = [{"path": path, "sha256": _sha(content), "size": len(content)}
               for path, content in sorted(raw.items())]
    version = _sha(json.dumps({"files": records, "selection": selection}, sort_keys=True,
                              separators=(",", ":")).encode("utf-8"))
    identity = TreeIdentity(
        role, str(root), version, version,
        tuple(FileIdentity(record["path"], role, version, record["sha256"], record["size"])
              for record in records),
        tuple(sorted(excluded, key=lambda entry: entry.path)),
        selection,
    )
    return _Snapshot(root, identity, tuple(sorted(raw.items())), tuple(sorted(set(directories))))


def _verify_version(snapshot: _Snapshot, version: str | None) -> _Snapshot:
    if version is None:
        return snapshot
    if not isinstance(version, str) or not re.fullmatch(r"(?:sha256:[0-9a-f]{64}|[0-9a-f]{40}|[0-9a-f]{64})", version):
        raise ArtifactInputError("INVALID_BASE", snapshot.identity.role, 1, "Version must be an exact commit or scoped sha256")
    if version.startswith("sha256:"):
        if version != snapshot.identity.snapshot:
            raise ArtifactInputError("BASE_MISMATCH", snapshot.identity.role, 1, "Actual scoped bytes/file set differ from the supplied digest")
    else:
        _, _, entries = _commit_tree(snapshot.root, version)
        expected = {}
        try:
            for entry in entries.split(b"\0"):
                if not entry:
                    continue
                header, name = entry.split(b"\t", 1)
                mode, kind, blob = header.decode("ascii").split()
                relative = name.decode("utf-8")
                if snapshot.identity.selection is not None and relative not in snapshot.identity.selection:
                    continue
                if any(_exclusion(part) for part in relative.split("/")):
                    continue
                if kind != "blob" or mode not in ("100644", "100755"):
                    raise ArtifactInputError("BASE_UNAVAILABLE", relative, 1, "Exact Git scope contains a nonregular file")
                expected[relative] = _git(snapshot.root, "cat-file", "blob", blob)
        except (UnicodeError, ValueError) as error:
            if isinstance(error, ArtifactInputError):
                raise
            raise ArtifactInputError("BASE_UNAVAILABLE", snapshot.identity.role, 1, "Cannot read the exact local Git file set") from error
        if expected != dict(snapshot.raw):
            raise ArtifactInputError("BASE_MISMATCH", snapshot.identity.role, 1, "Actual scoped bytes/file set differ from the exact commit")
    identity = replace(snapshot.identity, version=version,
                       files=tuple(replace(file, version=version) for file in snapshot.identity.files))
    return replace(snapshot, identity=identity)


def _nonoverlapping(roots: tuple[Path, ...]) -> None:
    for index, root in enumerate(roots):
        for other in roots[index + 1:]:
            if root.is_relative_to(other) or other.is_relative_to(root):
                raise ArtifactInputError("OVERLAPPING_ROOTS", "roots", 1, "Select distinct, non-overlapping source trees")


def _stable(snapshots: tuple[_Snapshot, ...]) -> None:
    for before in snapshots:
        try:
            root = _root(before.root)
            after = _snapshot(root, before.identity.role, before.identity.selection)
        except ArtifactInputError as error:
            raise ArtifactInputError("INPUT_CHANGED", before.identity.role, 1,
                                     "Input became unavailable or unsafe during planning") from error
        if (before.raw != after.raw or before.directories != after.directories
                or before.identity.snapshot != after.identity.snapshot
                or before.identity.excluded != after.identity.excluded):
            raise ArtifactInputError("INPUT_CHANGED", before.identity.role, 1,
                                     "Input bytes or file/directory set changed during planning")


def _compare(snapshots: tuple[_Snapshot, ...],
             mappings: tuple[FileMapping, ...] | None = None) -> UpdatePlan:
    trees = [dict(snapshot.raw) for snapshot in snapshots]
    changes, conflicts, preserved = [], [], []
    rows = ([(path, path, path, path) for path in sorted(set().union(*trees))] if mappings is None
            else sorted((item.target, item.source, item.target, item.source) for item in mappings))
    folded = {}
    for path, *locations in rows:
        if path.casefold() in folded and folded[path.casefold()] != path:
            raise ArtifactInputError("PATH_COLLISION", path, 1, "Case-only path aliases require explicit owner resolution")
        folded[path.casefold()] = path
        for location, snapshot, tree in zip(locations, snapshots, trees):
            if location in snapshot.directories or any(parent.as_posix() in tree for parent in PurePosixPath(location).parents if parent.as_posix() != "."):
                raise ArtifactInputError("PATH_TYPE_CONFLICT", path, 1, "File/directory topology differs across the selected trees")
    for path, *locations in rows:
        old, owner, new = states = tuple(tree.get(location) for tree, location in zip(trees, locations))
        if owner == new:
            action = "preserve"
            reason = ("BOTH_DELETED" if owner is None else "SAME_ADDITION" if old is None
                      else "UNCHANGED" if old == owner else "ALREADY_ALIGNED")
        elif new == old:
            action = "preserve"
            reason = "LOCAL_ONLY" if old is None else "LOCAL_DELETED" if owner is None else "LOCAL_MODIFIED"
        elif owner == old:
            action = "add" if old is None else "delete" if new is None else "modify"
            reason = {"add": "CANDIDATE_ADDED", "delete": "CANDIDATE_DELETED", "modify": "CANDIDATE_MODIFIED"}[action]
        else:
            action = "conflict"
            reason = ("ADD_ADD" if old is None else "DELETE_MODIFY" if new is None
                      else "MODIFY_DELETE" if owner is None else "BOTH_MODIFIED")
        identities = tuple(
            FileIdentity(location, snapshot.identity.role, snapshot.identity.version,
                         None if content is None else _sha(content),
                         None if content is None else len(content))
            for snapshot, content, location in zip(snapshots, states, locations)
        )
        item = UpdateItem(path, action, reason, *identities)
        if action == "conflict":
            conflicts.append(item)
        elif action == "preserve":
            preserved.append(item)
        else:
            changes.append(item)
    return UpdatePlan(tuple(changes), tuple(conflicts), tuple(preserved),
                      tuple(snapshot.identity for snapshot in snapshots))


def plan_update(base: PathInput | TreeSource, local: PathInput | TreeSource,
                candidate: PathInput | TreeSource) -> UpdatePlan:
    """Compare the three actual trees. Missing/unreadable roots are not absence."""
    sources = tuple(value if isinstance(value, TreeSource) else TreeSource(value)
                    for value in (base, local, candidate))
    selections = tuple(_selection(source.files) for source in sources)
    if len(set(selections)) != 1:
        raise ArtifactInputError("INVALID_SCOPE", "files", 1, "Three-way scopes must select the same relative files")
    roots = tuple(_root(source.root) for source in sources)
    _nonoverlapping(roots)
    snapshots = tuple(_verify_version(_snapshot(root, role, selection), source.version)
                      for root, role, selection, source in
                      zip(roots, ("base", "local", "candidate"), selections, sources))
    result = _compare(snapshots)
    _stable(snapshots)
    return result


_ID = r"[A-Za-z0-9][A-Za-z0-9._-]*"
_PAIR = re.compile(_ID + "/" + _ID)
_SCENARIO = re.compile(_ID + "/" + _ID + "/" + _ID + r"#[A-Za-z][A-Za-z0-9._:-]*")
_VERSION = re.compile(r"(?:sha256:[0-9a-f]{64}|[0-9a-f]{40}|[0-9a-f]{64})")


def _shape(value, fields: set[str], code: str, location: str) -> None:
    if not isinstance(value, dict) or set(value) != fields:
        raise ArtifactInputError(code, location, 1, "Registration has missing or unknown fields")


def _pair(value) -> bool:
    return isinstance(value, str) and _PAIR.fullmatch(value) is not None


def _declared_root(parent: Path, value, code: str) -> Path:
    if (not isinstance(value, str) or not value or value.strip() != value
            or re.search(r"[\\:\x00-\x1f$%~]", value) or value.startswith("/")
            or value != "." and any(part in ("", ".") for part in value.split("/"))):
        raise ArtifactInputError(code, "root", 1, "Declare an explicit local root relative to the registration")
    return Path(os.path.abspath(parent / value))


def _location(parent: Path, value, code: str) -> Path:
    _shape(value, {"root", "version"}, code, "location")
    if not isinstance(value["version"], str) or not _VERSION.fullmatch(value["version"]):
        raise ArtifactInputError(code, "version", 1, "Registration requires an exact Git/content version")
    return _declared_root(parent, value["root"], code)


def _registration_bytes(path: Path) -> bytes:
    try:
        _root(path.parent)
        info = path.lstat()
        if (not stat.S_ISREG(info.st_mode) or path.resolve(strict=True) != path
                or getattr(info, "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT):
            raise ArtifactInputError("UNSAFE_PATH", path.name, 1, "Registration must be a regular local file, not an alias")
        return path.read_bytes()
    except (OSError, ValueError, RuntimeError) as error:
        if isinstance(error, ArtifactInputError):
            raise
        raise ArtifactInputError("REGISTRATION_UNAVAILABLE", path.name, 1, "Cannot read the explicit registration") from error


def _registration(value: PathInput) -> tuple[Path, bytes, dict]:
    if (not isinstance(value, (str, os.PathLike)) or isinstance(value, bytes)
            or not os.fspath(value).strip() or str(value).startswith(("//", "\\\\"))
            or "://" in str(value)):
        raise ArtifactInputError("REGISTRATION_UNAVAILABLE", "registration", 1, "Select an explicit local registration file")
    requested = Path(value)
    if requested.anchor and not requested.is_absolute():
        raise ArtifactInputError("REGISTRATION_UNAVAILABLE", "registration", 1, "Registration path is ambiguous")
    path = Path(os.path.abspath(requested))
    raw = _registration_bytes(path)
    try:
        data, _ = load_yaml_mapping(raw.decode("utf-8-sig"), path)
    except UnicodeError as error:
        raise ArtifactInputError("INVALID_ENCODING", path.name, 1, "Registration must be UTF-8") from error
    except ArtifactInputError as error:
        # SafeLoader diagnostics can contain source excerpts. Keep its code and
        # line, but do not publish arbitrary registration values in a report.
        raise ArtifactInputError(error.code, path.name, error.line, "Registration is not a safe, unique-key YAML/JSON mapping") from error
    code = "INVALID_REGISTRATION"
    _shape(data, {"schemaVersion", "source", "targets"}, code, path.name)
    if type(data["schemaVersion"]) is not int or data["schemaVersion"] != 1:
        raise ArtifactInputError(code, path.name, 1, "Expected integer schemaVersion 1")
    source = data["source"]
    _shape(source, {"repository", "base", "candidate", "files"}, code, "source")
    if not _pair(source["repository"]):
        raise ArtifactInputError(code, "source.repository", 1, "Use a portable owner/repository identity, not a URL")
    _location(path.parent, source["base"], code)
    _location(path.parent, source["candidate"], code)
    if not isinstance(source["files"], list) or not source["files"]:
        raise ArtifactInputError(code, "source.files", 1, "Register a nonempty explicit .feature file set")
    scenarios, paths = set(), []
    for entry in source["files"]:
        _shape(entry, {"scenario", "path"}, code, "source.files")
        if (not isinstance(entry["scenario"], str) or not _SCENARIO.fullmatch(entry["scenario"])
                or entry["scenario"] in scenarios):
            raise ArtifactInputError(code, "source.files", 1, "Scenario references must be explicit and unique")
        scenarios.add(entry["scenario"])
        paths.append(entry["path"])
    try:
        _selection(tuple(paths))
    except ArtifactInputError as error:
        raise ArtifactInputError(code, "source.files", 1, "Source files must be unique, safe relative paths") from error
    if any(PurePosixPath(relative).suffix.lower() != ".feature" for relative in paths):
        raise ArtifactInputError(code, "source.files", 1, "Fan-out only selects .feature files, not model/whole repositories")
    if not isinstance(data["targets"], list) or not data["targets"]:
        raise ArtifactInputError(code, "targets", 1, "Register explicit target identities")
    seen = set()
    for target in data["targets"]:
        if (not isinstance(target, dict) or not isinstance(target.get("id"), str)
                or not re.fullmatch(_ID, target["id"]) or target["id"] in seen):
            raise ArtifactInputError(code, "targets", 1, "Target IDs must be valid and unique")
        seen.add(target["id"])
    return path, raw, data


def _target_ids(values) -> tuple[str, ...]:
    if isinstance(values, (str, bytes)) or values is None:
        raise ArtifactInputError("INVALID_TARGETS", "targets", 1, "Explicit target IDs are required; no default fan-out")
    try:
        values = tuple(values)
    except TypeError as error:
        raise ArtifactInputError("INVALID_TARGETS", "targets", 1, "Target IDs must be a nonempty iterable") from error
    if (not values or any(not isinstance(value, str) or not re.fullmatch(_ID, value) for value in values)
            or len(set(values)) != len(values)):
        raise ArtifactInputError("INVALID_TARGETS", "targets", 1, "Select nonempty, valid, unique target IDs")
    return tuple(sorted(values))


def _problem(error: ArtifactInputError, location: str) -> ProposalProblem:
    return ProposalProblem(error.code, location, error.line,
                           "Selected local input/registration cannot be used; no proposal was applied")


def _registered_snapshot(parent: Path, declaration: dict, role: str,
                         selection: tuple[str, ...]) -> _Snapshot:
    try:
        root = _root(_declared_root(parent, declaration["root"], "INVALID_REGISTRATION"))
        snapshot = _verify_version(_snapshot(root, role, selection), declaration["version"])
    except ArtifactInputError as error:
        raise ArtifactInputError(error.code, role, error.line,
                                 "Selected local snapshot cannot be verified") from error
    return replace(snapshot, identity=replace(snapshot.identity, root=declaration["root"]))


def _target_mappings(target: dict, source: dict) -> tuple[FileMapping, ...]:
    code = "INVALID_TARGET_REGISTRATION"
    _shape(target, {"id", "repository", "scope", "local", "files"}, code, "target")
    if not _pair(target["repository"]) or not _pair(target["scope"]):
        raise ArtifactInputError(code, "target", 1, "Target repository and project/context must be explicit")
    if not isinstance(target["files"], list) or not target["files"]:
        raise ArtifactInputError(code, "target.files", 1, "Register a nonempty explicit target file scope")
    allowed = {entry["path"]: entry["scenario"] for entry in source["files"]}
    mappings = []
    for entry in target["files"]:
        _shape(entry, {"source", "path"}, code, "target.files")
        if not isinstance(entry["source"], str) or entry["source"] not in allowed:
            raise ArtifactInputError("TARGET_FILE_NOT_ALLOWED", "target.files", 1, "Target file is not selected by the source registration")
        mappings.append(FileMapping(allowed[entry["source"]], entry["source"], entry["path"]))
    try:
        _selection(tuple(item.target for item in mappings))
    except ArtifactInputError as error:
        raise ArtifactInputError(code, "target.files", 1, "Target paths must be unique, safe relative files") from error
    if any(PurePosixPath(item.target).suffix.lower() != ".feature" for item in mappings):
        raise ArtifactInputError(code, "target.files", 1, "Feature propagation requires explicit .feature destinations")
    return tuple(sorted(mappings, key=lambda item: item.target))


def _batch(registration: PathInput, target_ids) -> tuple[BatchPlan, tuple[Path, ...], bool]:
    selected = _target_ids(target_ids)
    path, raw, data = _registration(registration)
    source = data["source"]
    targets = {entry["id"]: entry for entry in data["targets"]}
    roots = [path, *(_declared_root(path.parent, source[role]["root"], "INVALID_REGISTRATION")
                     for role in ("base", "candidate"))]
    reservation_complete = True
    # Reserve ALL declared target locations before version/read errors. A
    # missing or invalid root cannot be guessed just to enable report output.
    for target in targets.values():
        try:
            local = target.get("local")
            if not isinstance(local, dict) or "root" not in local:
                raise ArtifactInputError("INVALID_TARGET_REGISTRATION", "root", 1, "Missing target root")
            roots.append(_declared_root(path.parent, local["root"], "INVALID_TARGET_REGISTRATION"))
        except ArtifactInputError:
            reservation_complete = False
    source_error, source_snapshots = None, ()
    try:
        files = tuple(sorted(entry["path"] for entry in source["files"]))
        source_snapshots = tuple(_registered_snapshot(path.parent, source[role], role, files)
                                 for role in ("base", "candidate"))
        _nonoverlapping(tuple(snapshot.root for snapshot in source_snapshots))
        if any(file not in dict(source_snapshots[0].raw) and file not in dict(source_snapshots[1].raw)
               for file in files):
            raise ArtifactInputError("SOURCE_FILE_MISSING", "source.files", 1, "Registered scenario is absent from both source versions")
    except ArtifactInputError as error:
        source_error = error
    results, accepted = [], {}
    for name in selected:
        target = targets.get(name)
        repository = target.get("repository") if target and _pair(target.get("repository")) else None
        scope = target.get("scope") if target and _pair(target.get("scope")) else None
        mappings = ()
        origin = f"targets/{name}"
        try:
            if target is None:
                raise ArtifactInputError("UNKNOWN_TARGET", name, 1, "Target is not registered")
            mappings = _target_mappings(target, source)
            _location(path.parent, target["local"], "INVALID_TARGET_REGISTRATION")
            if source_error is not None:
                origin = f"source/{source_error.path}"
                raise source_error
            origin += "/local"
            local = _registered_snapshot(path.parent, target["local"], "local",
                                         tuple(item.target for item in mappings))
            snapshots = (source_snapshots[0], local, source_snapshots[1])
            _nonoverlapping(tuple(snapshot.root for snapshot in snapshots))
            plan = _compare(snapshots, mappings)
            accepted[name] = local
            results.append(TargetProposal(name, repository, scope, plan.status, mappings, plan, ()))
        except ArtifactInputError as error:
            results.append(TargetProposal(name, repository, scope, "unavailable", mappings, None,
                                          (_problem(error, origin),)))
    if source_error is None:
        try:
            _stable(source_snapshots)
        except ArtifactInputError as error:
            results = [replace(result, status="unavailable", plan=None,
                               findings=(*result.findings, _problem(error, f"source/{error.path}")))
                       for result in results]
        else:
            for index, result in enumerate(results):
                if result.id in accepted:
                    try:
                        _stable((accepted[result.id],))
                    except ArtifactInputError as error:
                        results[index] = replace(result, status="unavailable", plan=None,
                                                 findings=(_problem(error, f"targets/{result.id}/local"),))
    try:
        if _registration_bytes(path) != raw:
            raise ArtifactInputError("INPUT_CHANGED", path.name, 1, "Registration changed during planning")
    except ArtifactInputError as error:
        raise ArtifactInputError("INPUT_CHANGED", path.name, 1, "Registration changed or became unreadable during planning") from error
    result = BatchPlan(source["repository"], path.name, _sha(raw), tuple(results))
    return result, tuple(roots), reservation_complete


def plan_batch(registration: PathInput, target_ids) -> BatchPlan:
    """Read explicit local .feature mappings; retain every selected target result."""
    return _batch(registration, target_ids)[0]


def _proposal_path(value: str, roots: tuple[PathInput, ...]) -> Path:
    try:
        output = _output_path(value, str(Path.cwd()), (".json",))
    except ArtifactInputError as error:
        # A rejected URI may carry caller-supplied userinfo. Reuse the helper's
        # code, not its raw value/OS diagnostic, in this proposal's public output.
        raise ArtifactInputError(error.code, "output", error.line,
                                 "Output requires a new, unambiguous local JSON file") from error
    lexical = Path(os.path.abspath(value))
    if lexical != output or output.parent.resolve() != output.parent:
        raise ArtifactInputError("REPORT_CONFLICT", "output", 1, "Output cannot traverse a directory alias")
    for value in roots:
        # Reserve the entire declaration, including missing paths and caches.
        try:
            root = Path(os.path.abspath(value)).resolve()
        except (OSError, ValueError, RuntimeError) as error:
            raise ArtifactInputError("REPORT_CONFLICT", "output", 1,
                                     "Cannot safely reserve every declared source location") from error
        if output.is_relative_to(root):
            raise ArtifactInputError("REPORT_CONFLICT", "output", 1, "Output cannot occupy a source tree")
    return output


def _write_proposal(payload: dict, output: Path) -> None:
    payload["report_output"] = {"path": str(output), "written": True}
    try:
        with output.open("x", encoding="utf-8", newline="\n") as destination:
            destination.write(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    except FileExistsError as error:
        raise ArtifactInputError("REPORT_CONFLICT", "output", 1, "Output already exists") from error
    except OSError as error:
        raise ArtifactInputError("REPORT_WRITE_ERROR", "output", 1,
                                 "Cannot create the new report; a partial new file may remain") from error


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base")
    parser.add_argument("--local")
    parser.add_argument("--candidate")
    parser.add_argument("--base-version")
    parser.add_argument("--local-version")
    parser.add_argument("--candidate-version")
    parser.add_argument("--registration")
    parser.add_argument("--target", action="append")
    parser.add_argument("--output")
    args = parser.parse_args(argv)
    single = (args.base, args.local, args.candidate, args.base_version, args.local_version, args.candidate_version)
    if args.registration:
        if any(value is not None for value in single) or not args.target:
            parser.error("Registration mode requires explicit --target selection and excludes single-tree arguments")
    elif args.target or not all(value is not None for value in (args.base, args.local, args.candidate)):
        parser.error("Supply all three roots, or --registration with explicit --target")
    payload = {}
    try:
        if args.registration:
            batch, roots, reservation_complete = _batch(args.registration, args.target)
            payload = batch.to_dict()
            if args.output is not None and not reservation_complete:
                raise ArtifactInputError("REPORT_CONFLICT", "output", 1, "Cannot prove output isolation from every declared source location")
        else:
            roots = (args.base, args.local, args.candidate)
            payload = plan_update(
                TreeSource(args.base, args.base_version), TreeSource(args.local, args.local_version),
                TreeSource(args.candidate, args.candidate_version),
            ).to_dict()
        output = _proposal_path(args.output, roots) if args.output is not None else None
        if output is not None:
            _write_proposal(payload, output)
    except ArtifactInputError as error:
        payload.update(status="input-error", findings=[{
            "code": error.code, "path": str(error.path), "line": error.line, "message": error.message,
        }])
        if args.output is not None:
            payload["report_output"] = {"written": False}
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return {"no-change": 0, "proposed": 0, "conflict": 1, "input-error": 2}[payload["status"]]


if __name__ == "__main__":
    raise SystemExit(main())
