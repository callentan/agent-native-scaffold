"""Create and verify a local candidate from the exact file-level manifest.

This maker-side utility is deliberately not part of the downstream candidate.
It copies no directories, initializes no repository, and performs no install or
publication operation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import stat
import subprocess
import sys
from typing import Any


MANIFEST_PATH = "docs/distribution-manifest.json"
_REPARSE = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)


class CandidateError(ValueError):
    def __init__(self, code: str, message: str, *, path: str | None = None,
                 status: str = "input-error", exit_code: int = 2):
        super().__init__(message)
        self.code = code
        self.path = path
        self.status = status
        self.exit_code = exit_code


def _sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=True, sort_keys=True, indent=2) + "\n").encode("utf-8")


def _reject_network(value: str, label: str) -> None:
    if not value.strip() or "://" in value or value.startswith(("//", "\\\\")):
        raise CandidateError("LOCAL_PATH_REQUIRED", f"{label} must be an explicit local path")


def _is_reparse(path: Path) -> bool:
    try:
        info = os.lstat(path)
    except OSError:
        return False
    return stat.S_ISLNK(info.st_mode) or bool(getattr(info, "st_file_attributes", 0) & _REPARSE)


def _assert_no_reparse_components(path: Path, *, allow_missing_final: bool = False) -> None:
    if not path.is_absolute() or ".." in path.parts:
        raise CandidateError("UNSAFE_PATH", "Path must be absolute and contain no parent traversal")
    current = Path(path.anchor)
    components = path.parts[1:]
    for index, component in enumerate(components):
        current = current / component
        if not os.path.lexists(current):
            if allow_missing_final and index == len(components) - 1:
                return
            raise CandidateError("PATH_NOT_FOUND", "A declared path component does not exist")
        if _is_reparse(current):
            raise CandidateError("UNSAFE_PATH", "Reparse points and symbolic links are not allowed")


def _local_directory(value: str, label: str) -> Path:
    _reject_network(value, label)
    path = Path(value)
    if not path.is_absolute():
        raise CandidateError("ABSOLUTE_PATH_REQUIRED", f"{label} must be absolute")
    _assert_no_reparse_components(path)
    resolved = path.resolve(strict=True)
    if not resolved.is_dir():
        raise CandidateError("INVALID_DIRECTORY", f"{label} must be an existing directory")
    return resolved


def _local_new_file(value: str, label: str, allowed_roots: tuple[Path, ...],
                    *, suffix: str | None = None) -> Path:
    _reject_network(value, label)
    path = Path(value)
    if not path.is_absolute() or ".." in path.parts or path.name in ("", ".", ".."):
        raise CandidateError("UNSAFE_OUTPUT", f"{label} must be an absolute, non-traversing file path")
    if suffix is not None and path.suffix.lower() != suffix:
        raise CandidateError("INVALID_OUTPUT_SUFFIX", f"{label} must use the {suffix} extension")
    _assert_no_reparse_components(path.parent)
    parent = path.parent.resolve(strict=True)
    if not parent.is_dir():
        raise CandidateError("INVALID_OUTPUT_PARENT", f"{label} parent must be an existing directory")
    resolved = parent / path.name
    if os.path.lexists(resolved):
        raise CandidateError("OUTPUT_CONFLICT", f"{label} already exists",
                             path=path.name, status="conflict", exit_code=1)
    if not any(resolved.parent.is_relative_to(root) for root in allowed_roots):
        raise CandidateError("OUTPUT_OUTSIDE_ALLOWED_ROOT",
                             f"{label} must be inside an explicitly allowed output root")
    return resolved


def _safe_relative(value: Any, *, directory: bool = False) -> str:
    if not isinstance(value, str) or not value or "\\" in value or ":" in value:
        raise CandidateError("INVALID_MANIFEST_PATH", "Manifest paths must be explicit relative POSIX paths")
    if any(character in value for character in "*?[]{}"):
        raise CandidateError("INVALID_MANIFEST_PATH", "Manifest paths may not contain glob or pattern syntax")
    if any(ord(character) < 32 for character in value):
        raise CandidateError("INVALID_MANIFEST_PATH", "Manifest path contains a control character")
    if value.startswith("/") or value.endswith("/") != directory:
        raise CandidateError("INVALID_MANIFEST_PATH", "Manifest path has an invalid root or trailing separator")
    parts = value[:-1].split("/") if directory else value.split("/")
    if any(part in ("", ".", "..") for part in parts):
        raise CandidateError("INVALID_MANIFEST_PATH", "Manifest path contains an empty or traversal segment")
    return value


def _duplicate_reject(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise CandidateError("DUPLICATE_MANIFEST_KEY", "Manifest JSON contains a duplicate object key")
        result[key] = value
    return result


def _read_manifest(root: Path) -> tuple[dict[str, Any], bytes, str]:
    path = root / MANIFEST_PATH
    _assert_no_reparse_components(path)
    try:
        raw = path.read_bytes()
        manifest = json.loads(raw.decode("utf-8"), object_pairs_hook=_duplicate_reject,
                              parse_constant=lambda value: (_ for _ in ()).throw(
                                  CandidateError("INVALID_MANIFEST", "Manifest contains a non-finite number")))
    except CandidateError:
        raise
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise CandidateError("INVALID_MANIFEST", "The explicit distribution manifest cannot be read as UTF-8 JSON",
                             path=MANIFEST_PATH) from error
    if not isinstance(manifest, dict) or set(manifest) != {"schemaVersion", "components", "files", "excluded"}:
        raise CandidateError("INVALID_MANIFEST", "Manifest has an unexpected top-level shape", path=MANIFEST_PATH)
    if type(manifest["schemaVersion"]) is not int or manifest["schemaVersion"] != 1:
        raise CandidateError("INVALID_MANIFEST", "Manifest schemaVersion must be integer 1", path=MANIFEST_PATH)
    components = manifest["components"]
    if not isinstance(components, dict) or not components:
        raise CandidateError("INVALID_MANIFEST", "Manifest requires component ownership descriptions")
    if any(not isinstance(key, str) or not key.strip() or not isinstance(value, str) or not value.strip()
           for key, value in components.items()):
        raise CandidateError("INVALID_MANIFEST", "Each component requires a nonempty id and description")
    files = manifest["files"]
    if not isinstance(files, list) or not files:
        raise CandidateError("INVALID_MANIFEST", "Manifest requires explicit file entries")
    seen: set[str] = set()
    for entry in files:
        if not isinstance(entry, dict) or set(entry) != {"path", "component"}:
            raise CandidateError("INVALID_MANIFEST", "Each file entry must contain only path and component")
        relative = _safe_relative(entry["path"])
        folded = relative.casefold()
        if folded in seen:
            raise CandidateError("DUPLICATE_MANIFEST_PATH", "Manifest contains a duplicate or case-alias path",
                                 path=relative)
        seen.add(folded)
        if entry["component"] not in components:
            raise CandidateError("INVALID_MANIFEST", "File references an undeclared owner component", path=relative)
    raw_paths = [entry["path"] for entry in files]
    if MANIFEST_PATH not in raw_paths:
        raise CandidateError("MANIFEST_NOT_SELF_DESCRIBING", "The exact manifest must be listed as a candidate file",
                             path=MANIFEST_PATH)
    # A file may not also be another listed file's parent.
    exact = set(raw_paths)
    for relative in raw_paths:
        parent = PurePosixPath(relative).parent
        while str(parent) != ".":
            if parent.as_posix() in exact:
                raise CandidateError("MANIFEST_PATH_COLLISION", "Manifest path is both a file and a parent directory",
                                     path=relative)
            parent = parent.parent
    exclusions = manifest["excluded"]
    if not isinstance(exclusions, list):
        raise CandidateError("INVALID_MANIFEST", "Manifest exclusions must be a list")
    excluded_seen: set[str] = set()
    for exclusion in exclusions:
        if not isinstance(exclusion, dict) or set(exclusion) != {"path", "reason"}:
            raise CandidateError("INVALID_MANIFEST", "Each exclusion must contain only path and reason")
        path_value = exclusion["path"]
        is_directory = isinstance(path_value, str) and path_value.endswith("/")
        _safe_relative(path_value, directory=is_directory)
        if path_value.casefold() in excluded_seen:
            raise CandidateError("DUPLICATE_EXCLUSION", "Manifest has duplicate exclusion paths", path=path_value)
        excluded_seen.add(path_value.casefold())
        if not isinstance(exclusion["reason"], str) or not exclusion["reason"].strip():
            raise CandidateError("INVALID_MANIFEST", "Each exclusion needs an explicit reason", path=path_value)
    return manifest, raw, _sha256(raw)


def _git(root: Path, *arguments: str) -> bytes:
    environment = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    environment.update({
        "GIT_CONFIG_GLOBAL": os.devnull,
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_OPTIONAL_LOCKS": "0",
    })
    command = [
        "git", "--no-pager", "-c", "core.quotepath=false", "-c", "core.fsmonitor=false",
        *arguments,
    ]
    result = subprocess.run(
        command, cwd=root, env=environment, shell=False,
        capture_output=True, check=False,
    )
    if result.returncode:
        raise CandidateError("GIT_PROVENANCE_UNAVAILABLE",
                             "Local Git provenance could not be read; no branch or network fallback is used")
    return result.stdout


def _git_provenance(root: Path) -> tuple[str, list[dict[str, str]], list[str]]:
    try:
        top = _git(root, "rev-parse", "--show-toplevel").decode("utf-8").strip()
        top_path = Path(top).resolve(strict=True)
        if top_path != root:
            raise CandidateError("SOURCE_ROOT_NOT_GIT_TOP", "Source root must be the exact local Git checkout root")
        commit = _git(root, "rev-parse", "--verify", "HEAD").decode("ascii").strip()
        if len(commit) not in (40, 64) or any(character not in "0123456789abcdef" for character in commit):
            raise CandidateError("SOURCE_COMMIT_INVALID", "Git HEAD is not a complete commit object id")
        status_raw = _git(root, "status", "--porcelain=v1", "--untracked-files=all",
                          "--ignore-submodules=all").decode("utf-8").splitlines()
        dirty = []
        for line in status_raw:
            if len(line) < 4:
                raise CandidateError("GIT_STATUS_INVALID", "Git returned an unrecognized local status record")
            dirty.append({"status": line[:2], "path": line[3:]})
        inventory_raw = _git(root, "ls-files", "--cached", "--others", "--exclude-standard",
                             "--full-name", "-z")
        paths = [item.decode("utf-8") for item in inventory_raw.split(b"\0") if item]
        return commit, dirty, sorted(set(paths))
    except UnicodeDecodeError as error:
        raise CandidateError("GIT_PROVENANCE_INVALID", "Local Git paths are not valid UTF-8") from error


def _excluded_reason(relative: str, manifest: dict[str, Any]) -> str | None:
    for exclusion in manifest["excluded"]:
        path = exclusion["path"]
        if path.endswith("/") and relative.startswith(path):
            return exclusion["reason"]
        if relative == path:
            return exclusion["reason"]
    return None


def _inventory(root: Path, manifest: dict[str, Any], included: set[str],
               source_paths: list[str]) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    excluded: list[dict[str, str]] = []
    unclassified: list[dict[str, str]] = []
    for relative in source_paths:
        if relative in included:
            continue
        reason = _excluded_reason(relative, manifest)
        if reason is None:
            unclassified.append({"path": relative, "reason": "No explicit allowlist entry or exclusion rule"})
        else:
            excluded.append({"path": relative, "reason": reason})
    return excluded, unclassified


def _source_bytes(root: Path, relative: str) -> bytes:
    path = root.joinpath(*PurePosixPath(relative).parts)
    try:
        _assert_no_reparse_components(path)
        info = os.stat(path, follow_symlinks=False)
        if not stat.S_ISREG(info.st_mode):
            raise CandidateError("SOURCE_NOT_REGULAR", "Listed source must be a regular file", path=relative)
        raw = path.read_bytes()
        after = os.stat(path, follow_symlinks=False)
        if (info.st_size, info.st_mtime_ns, info.st_ino) != (after.st_size, after.st_mtime_ns, after.st_ino):
            raise CandidateError("SOURCE_CHANGED", "Listed source changed while it was read", path=relative)
        return raw
    except CandidateError:
        raise
    except OSError as error:
        code = "SOURCE_FILE_MISSING" if not path.exists() else "SOURCE_READ_ERROR"
        raise CandidateError(code, "A listed source file is missing or unreadable", path=relative) from error


def _output_roots(root: Path, values: list[str]) -> tuple[Path, ...]:
    if not values:
        raise CandidateError("OUTPUT_ROOT_REQUIRED", "Supply at least one explicitly authorized output root")
    roots = []
    for value in values:
        resolved = _local_directory(value, "Allowed output root")
        if resolved not in roots:
            roots.append(resolved)
    return tuple(roots)


def _path_reference(path: Path, root: Path, allowed_roots: tuple[Path, ...]) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        for allowed in allowed_roots:
            try:
                return f"external:{allowed.name}/{path.relative_to(allowed).as_posix()}"
            except ValueError:
                continue
    return "external"


def _target_directory(value: str, root: Path, allowed_roots: tuple[Path, ...],
                      *, must_exist: bool) -> Path:
    _reject_network(value, "Candidate path")
    requested = Path(value)
    if not requested.is_absolute() or ".." in requested.parts or requested.name in ("", ".", ".."):
        raise CandidateError("UNSAFE_CANDIDATE_PATH", "Candidate path must be absolute and contain no traversal")
    if must_exist:
        _assert_no_reparse_components(requested)
        resolved = requested.resolve(strict=True)
        if not resolved.is_dir():
            raise CandidateError("INVALID_CANDIDATE_ROOT", "Candidate must be an existing directory")
    else:
        _assert_no_reparse_components(requested.parent)
        parent = requested.parent.resolve(strict=True)
        resolved = parent / requested.name
        if os.path.lexists(resolved):
            raise CandidateError("TARGET_CONFLICT", "Candidate target already exists; no owner content was changed",
                                 path=_path_reference(resolved, root, allowed_roots),
                                 status="conflict", exit_code=1)
    if not any(resolved.parent.is_relative_to(allowed) for allowed in allowed_roots):
        raise CandidateError("OUTPUT_OUTSIDE_ALLOWED_ROOT", "Candidate must be inside an explicitly allowed output root")
    try:
        relative = resolved.relative_to(root)
        if relative.parts and relative.parts[0] != ".venv":
            raise CandidateError("SOURCE_TREE_OUTPUT_REFUSED",
                                 "A candidate under the source checkout is allowed only in its ignored .venv fixture root")
    except ValueError:
        pass
    return resolved


def _provenance_record(commit: str, dirty: list[dict[str, str]],
                       source_paths: list[str]) -> dict[str, Any]:
    return {
        "source_commit": commit,
        "dirty_scope": dirty,
        "source_inventory_sha256": _sha256("\n".join(source_paths).encode("utf-8")),
    }


def _validate_sources(root: Path) -> tuple[dict[str, Any], bytes, str, dict[str, bytes],
                                              list[dict[str, str]], list[dict[str, str]],
                                              str, list[dict[str, str]], list[str]]:
    manifest, manifest_raw, manifest_sha = _read_manifest(root)
    commit, dirty, source_paths = _git_provenance(root)
    entries = sorted(manifest["files"], key=lambda item: item["path"])
    included = {entry["path"] for entry in entries}
    excluded, unclassified = _inventory(root, manifest, included, source_paths)
    if unclassified:
        raise CandidateError("UNCLASSIFIED_SOURCE_FILE",
                             "Every local source file must be explicitly allowlisted or have an exclusion reason",
                             path=unclassified[0]["path"])
    snapshots = {entry["path"]: _source_bytes(root, entry["path"]) for entry in entries}
    if snapshots.get(MANIFEST_PATH) != manifest_raw:
        raise CandidateError("MANIFEST_CHANGED", "Manifest bytes changed while its inventory was read",
                             path=MANIFEST_PATH)
    return manifest, manifest_raw, manifest_sha, snapshots, excluded, dirty, commit, [
        {"path": item, "reason": _excluded_reason(item, manifest) or "NOT_ALLOWLISTED"}
        for item in source_paths if item not in included
    ], source_paths


def _copy_receipt(root: Path, target: Path, manifest: dict[str, Any], manifest_sha: str,
                  snapshots: dict[str, bytes], excluded: list[dict[str, str]],
                  commit: str, dirty: list[dict[str, str]], source_paths: list[str],
                  allowed_roots: tuple[Path, ...]) -> dict[str, Any]:
    files = []
    components = {entry["path"]: entry["component"] for entry in manifest["files"]}
    try:
        target.mkdir()
        for relative in sorted(snapshots):
            destination = target.joinpath(*PurePosixPath(relative).parts)
            destination.parent.mkdir(parents=True, exist_ok=True)
            _assert_no_reparse_components(destination.parent)
            raw = snapshots[relative]
            with destination.open("xb") as output:
                output.write(raw)
            copied = destination.read_bytes()
            if copied != raw:
                raise CandidateError("COPY_BYTES_MISMATCH", "Candidate bytes differ from the preflight source",
                                     path=relative)
            files.append({
                "path": relative,
                "component": components[relative],
                "size": len(raw),
                "source_sha256": _sha256(raw),
                "candidate_sha256": _sha256(copied),
            })
        for relative, original in snapshots.items():
            if _source_bytes(root, relative) != original:
                raise CandidateError("SOURCE_CHANGED", "A listed source changed during candidate copy",
                                     path=relative)
        commit_after, dirty_after, paths_after = _git_provenance(root)
        if (commit_after, dirty_after, paths_after) != (commit, dirty, source_paths):
            raise CandidateError("SOURCE_SCOPE_CHANGED", "Git source identity or dirty scope changed during copy")
    except CandidateError:
        raise
    except OSError as error:
        raise CandidateError("COPY_IO_ERROR",
                             "Candidate copy stopped; any newly created partial candidate is retained for inspection",
                             path=_path_reference(target, root, allowed_roots)) from error
    return {
        "schemaVersion": 1,
        "status": "copied",
        "exit_code": 0,
        "manifest_sha256": manifest_sha,
        "provenance": {"source_root": ".", **_provenance_record(commit, dirty, source_paths)},
        "target": _path_reference(target, root, allowed_roots),
        "allowed_output_roots": [_path_reference(item, root, allowed_roots) for item in allowed_roots],
        "copied_count": len(files),
        "excluded_count": len(excluded),
        "files": files,
        "excluded_files": excluded,
        "findings": [],
    }


def _walk_candidate(candidate: Path) -> tuple[list[str], list[str], list[dict[str, str]]]:
    files: list[str] = []
    directories: list[str] = []
    findings: list[dict[str, str]] = []
    stack = [candidate]
    while stack:
        current = stack.pop()
        try:
            children = sorted(os.scandir(current), key=lambda item: item.name, reverse=True)
        except OSError:
            findings.append({"code": "DIRECTORY_READ_ERROR",
                             "path": current.relative_to(candidate).as_posix() or ".",
                             "message": "Candidate directory cannot be enumerated"})
            continue
        for child in children:
            path = Path(child.path)
            relative = path.relative_to(candidate).as_posix()
            if child.is_symlink() or _is_reparse(path):
                findings.append({"code": "UNSAFE_ENTRY", "path": relative,
                                 "message": "Symbolic links and reparse entries are not candidate files"})
                continue
            try:
                if child.is_dir(follow_symlinks=False):
                    directories.append(relative)
                    if child.name in {".git", ".venv", "__pycache__"}:
                        findings.append({"code": "FORBIDDEN_DIRECTORY", "path": relative,
                                         "message": "Git, runtime, and cache directories are excluded"})
                    stack.append(path)
                elif child.is_file(follow_symlinks=False):
                    info = os.stat(path, follow_symlinks=False)
                    if not stat.S_ISREG(info.st_mode):
                        findings.append({"code": "UNSAFE_ENTRY", "path": relative,
                                         "message": "Candidate entry is not a regular file"})
                    else:
                        files.append(relative)
                else:
                    findings.append({"code": "UNSAFE_ENTRY", "path": relative,
                                     "message": "Candidate entry is not a regular file or directory"})
            except OSError:
                findings.append({"code": "ENTRY_READ_ERROR", "path": relative,
                                 "message": "Candidate entry cannot be inspected"})
    return sorted(files), sorted(directories), findings


def _verify_receipt(root: Path, candidate: Path, manifest: dict[str, Any],
                    manifest_sha: str, snapshots: dict[str, bytes], excluded: list[dict[str, str]],
                    commit: str, dirty: list[dict[str, str]], source_paths: list[str],
                    allowed_roots: tuple[Path, ...]) -> dict[str, Any]:
    actual_files, actual_directories, findings = _walk_candidate(candidate)
    expected_files = set(snapshots)
    actual_set = set(actual_files)
    for relative in sorted(expected_files - actual_set):
        findings.append({"code": "MISSING_FILE", "path": relative,
                         "message": "An explicitly listed candidate file is missing"})
    for relative in sorted(actual_set - expected_files):
        findings.append({"code": "EXTRA_FILE", "path": relative,
                         "message": "Candidate contains a file not present in the exact allowlist"})
    expected_directories = set()
    for relative in expected_files:
        parent = PurePosixPath(relative).parent
        while str(parent) != ".":
            expected_directories.add(parent.as_posix())
            parent = parent.parent
    for relative in sorted(set(actual_directories) - expected_directories):
        if relative not in {item["path"] for item in findings}:
            findings.append({"code": "EXTRA_DIRECTORY", "path": relative,
                             "message": "Candidate contains an unowned directory"})
    for relative in sorted(expected_files & actual_set):
        actual = candidate.joinpath(*PurePosixPath(relative).parts)
        try:
            raw = actual.read_bytes()
        except OSError:
            findings.append({"code": "FILE_READ_ERROR", "path": relative,
                             "message": "Candidate file cannot be read"})
            continue
        expected = snapshots[relative]
        if raw != expected:
            findings.append({"code": "HASH_MISMATCH", "path": relative,
                             "message": "Candidate raw bytes differ from the current listed source"})
    findings.sort(key=lambda item: (item["path"], item["code"]))
    status = "valid" if not findings else "invalid"
    return {
        "schemaVersion": 1,
        "status": status,
        "exit_code": 0 if not findings else 1,
        "manifest_sha256": manifest_sha,
        "provenance": {"source_root": ".", **_provenance_record(commit, dirty, source_paths)},
        "candidate": _path_reference(candidate, root, allowed_roots),
        "allowed_output_roots": [_path_reference(item, root, allowed_roots) for item in allowed_roots],
        "verified_count": len(expected_files & actual_set),
        "excluded_count": len(excluded),
        "files": [
            {
                "path": relative,
                "component": next(entry["component"] for entry in manifest["files"]
                                  if entry["path"] == relative),
                "size": len(snapshots[relative]),
                "source_sha256": _sha256(snapshots[relative]),
                "candidate_sha256": _sha256(
                    candidate.joinpath(*PurePosixPath(relative).parts).read_bytes()
                ) if relative in actual_set else None,
            }
            for relative in sorted(expected_files)
        ],
        "excluded_files": excluded,
        "findings": findings,
    }


def _write_report(path: Path | None, payload: dict[str, Any]) -> dict[str, Any]:
    if path is None:
        return payload
    report = dict(payload)
    report["report_output"] = {"path": path.name, "written": True}
    try:
        with path.open("xb") as output:
            output.write(_json_bytes(report))
    except FileExistsError as error:
        raise CandidateError("REPORT_CONFLICT", "Report path already exists; it was not overwritten",
                             path=path.name, status="conflict", exit_code=1) from error
    except OSError as error:
        raise CandidateError("REPORT_WRITE_ERROR", "New report could not be written") from error
    return report


def _failure(error: CandidateError, root: Path | None, allowed_roots: tuple[Path, ...],
             report_path: Path | None) -> dict[str, Any]:
    payload = {
        "schemaVersion": 1,
        "status": error.status,
        "exit_code": error.exit_code,
        "findings": [{
            "code": error.code,
            "path": error.path,
            "message": str(error),
        }],
        "allowed_output_roots": [
            _path_reference(path, root, allowed_roots) if root is not None else path.name
            for path in allowed_roots
        ],
    }
    if report_path is not None:
        payload["report_output"] = {"path": report_path.name, "written": False}
    return payload


def _report_path(value: str | None, root: Path, allowed_roots: tuple[Path, ...]) -> Path | None:
    if value is None:
        return None
    return _local_new_file(value, "Report path", allowed_roots, suffix=".json")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, help="Exact local maker checkout root")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--target", help="New candidate directory; it must not already exist")
    mode.add_argument("--verify", help="Existing candidate directory to compare against the allowlist")
    parser.add_argument("--allow-output-root", action="append", default=[],
                        help="Explicit existing local root for the candidate or new report; repeat as needed")
    parser.add_argument("--report", help="Optional new local JSON receipt; existing files are never overwritten")
    arguments = parser.parse_args(argv)
    root: Path | None = None
    allowed_roots: tuple[Path, ...] = ()
    report_path: Path | None = None
    try:
        root = _local_directory(arguments.root, "Source root")
        allowed_roots = _output_roots(root, arguments.allow_output_root)
        report_path = _report_path(arguments.report, root, allowed_roots)
        manifest, _, manifest_sha, snapshots, excluded, dirty, commit, actual_excluded, source_paths = \
            _validate_sources(root)
        if arguments.target is not None:
            target = _target_directory(arguments.target, root, allowed_roots, must_exist=False)
            if report_path is not None and (
                report_path == target or report_path.is_relative_to(target)
            ):
                raise CandidateError("OUTPUT_OVERLAP", "Candidate and report destinations must be separate")
            payload = _copy_receipt(root, target, manifest, manifest_sha, snapshots,
                                    excluded, commit, dirty, source_paths, allowed_roots)
        else:
            candidate = _target_directory(arguments.verify, root, allowed_roots, must_exist=True)
            payload = _verify_receipt(root, candidate, manifest, manifest_sha, snapshots,
                                      excluded, commit, dirty, source_paths, allowed_roots)
        payload["excluded_files"] = actual_excluded
        if report_path is not None:
            payload = _write_report(report_path, payload)
            summary = {
                "status": payload["status"],
                "exit_code": payload["exit_code"],
                "report_output": payload["report_output"],
                "copied_count": payload.get("copied_count"),
                "verified_count": payload.get("verified_count"),
                "excluded_count": payload.get("excluded_count"),
                "findings": payload["findings"],
            }
            print(json.dumps(summary, ensure_ascii=True, sort_keys=True))
        else:
            print(_json_bytes(payload).decode("utf-8"), end="")
        return payload["exit_code"]
    except CandidateError as error:
        payload = _failure(error, root, allowed_roots, report_path)
        print(json.dumps(payload, ensure_ascii=True, sort_keys=True))
        return error.exit_code
    except (OSError, UnicodeError) as error:
        failure = CandidateError("LOCAL_IO_ERROR", "A local candidate input/output operation failed")
        print(json.dumps(_failure(failure, root, allowed_roots, report_path),
                         ensure_ascii=True, sort_keys=True))
        return failure.exit_code


if __name__ == "__main__":
    raise SystemExit(main())
