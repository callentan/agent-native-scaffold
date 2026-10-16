"""Shared BC mapping, exact commit and live domain bytes; no setup side effects."""

from __future__ import annotations

import os
from pathlib import Path
import re

from artifact_io import ArtifactInputError, _schema_validator
from check_artifacts import _commit_tree, _exclusion, _fixed_file, _git


def validate_mapping(data: dict, name: str, path: Path) -> None:
    contract = Path(__file__).resolve().parents[1] / "contracts" / (name + ".schema.json")
    try:
        validator = _schema_validator(contract.read_bytes(), contract)
    except OSError as error:
        raise ArtifactInputError("CONTRACT_ERROR", contract, 1, str(error)) from error
    if not isinstance(data, dict) or type(data.get("schemaVersion")) is not int or data["schemaVersion"] != 1:
        raise ArtifactInputError("UNSUPPORTED_SCHEMA_VERSION", path, 1, "Expected integer schemaVersion 1")
    violation = next(validator.iter_errors(data), None)
    if violation:
        raise ArtifactInputError("INVALID_METADATA", path, 1,
                                 f"{name} schema violation at {list(violation.absolute_path)} ({violation.validator})")


def relative_path(value: str, context: Path, *, directory: bool = False) -> str:
    if directory and value == ".":
        return value
    if (not isinstance(value, str) or not value or value.strip() != value
            or re.search(r"[\\:#\x00-\x1f]", value) or value.startswith("/") or value.endswith("/")
            or any(part in ("", ".", "..") for part in value.split("/"))):
        raise ArtifactInputError("INVALID_PATH", context, 1, "Use an explicit local root-relative path")
    if _exclusion(value) == "TOOL_DATA":
        raise ArtifactInputError("EXCLUDED_TARGET", context, 1, "Git, environment and dependency data are not sources")
    return value


class Commit:
    """One immutable object's blobs. No worktree snapshot, checkout or execution."""

    def __init__(self, root: Path, object_sha: str) -> None:
        self.root = root
        self.sha, _, manifest = _commit_tree(root, object_sha)
        self.files: dict[str, tuple[str, str, str]] = {}
        self.raw: dict[str, bytes] = {}
        try:
            for entry in manifest.split(b"\0"):
                if entry:
                    header, name = entry.split(b"\t", 1)
                    self.files[name.decode("utf-8")] = tuple(header.decode("ascii").split())
        except (UnicodeError, ValueError) as error:
            raise ArtifactInputError("BASE_UNAVAILABLE", root, 1, "Unreadable exact Git manifest") from error

    def read(self, relative: str) -> bytes:
        relative_path(relative, self.root)
        record = self.files.get(relative)
        if record is None:
            raise ArtifactInputError("OBJECT_PATH_MISSING", self.root / relative, 1, "File is absent at the selected commit")
        mode, kind, blob = record
        if mode not in ("100644", "100755") or kind != "blob":
            raise ArtifactInputError("INVALID_OBJECT_FILE", self.root / relative, 1, "Source must be a regular Git blob")
        if relative not in self.raw:
            self.raw[relative] = _git(self.root, "cat-file", "blob", blob)
        return self.raw[relative]

    def directory(self, relative: str) -> bool:
        return relative == "." or any(name.startswith(relative + "/") for name in self.files)


def domain_files(source_root: Path, relative: str, baseline: str, read) -> tuple[dict[Path, bytes], bool]:
    """The collector's fixed root/path comparison, shared with explicit setup.

    The caller owns acquisition/protection and supplies read(path, source_root).
    SHA256 identifies one raw file; a commit identifies one file or the exact
    directory file set, excluding only its .git metadata.
    """
    path = source_root / relative
    if baseline.startswith("sha256:"):
        raw = read(path, source_root)
        _fixed_file(source_root, path, raw, baseline)
        return {path: raw}, False
    source_object = Commit(source_root, baseline)
    directory = relative not in source_object.files
    if not directory:
        names = [relative]
    else:
        names = sorted(name for name in source_object.files if relative == "." or name.startswith(relative + "/"))
        if not names:
            raise ArtifactInputError("OBJECT_PATH_MISSING", path, 1, "Domain path is absent at its fixed commit")
        actual_names = set()

        def walk_error(error):
            raise ArtifactInputError("DIRECTORY_READ_ERROR", path, 1, str(error)) from error

        for current, dirs, filenames in os.walk(path, followlinks=False, onerror=walk_error):
            dirs[:] = [name for name in dirs if name != ".git"]
            for name in [*dirs, *filenames]:
                item = Path(current) / name
                if item.resolve() != item:
                    raise ArtifactInputError("OUTSIDE_ROOT", item, 1, "Linked domain entries are unsupported")
            actual_names.update((Path(current) / name).relative_to(source_root).as_posix()
                                for name in filenames if name != ".git")
        if set(names) != actual_names:
            raise ArtifactInputError("BASE_MISMATCH", path, 1, "Domain file set differs from its fixed commit")
    files = {}
    for name in names:
        expected = source_object.read(name)
        actual = read(source_root / name, source_root)
        if actual != expected:
            raise ArtifactInputError("BASE_MISMATCH", source_root / name, 1, "Domain bytes differ from the fixed commit")
        files[source_root / name] = actual
    return files, directory
