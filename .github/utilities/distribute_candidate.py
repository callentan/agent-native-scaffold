"""Copy or verify the exact DDD candidate manifest using portable file I/O.

This maker-side utility is not included downstream. It copies only listed file
bytes, records local Git provenance, and never installs or executes candidate
content. Outputs must be new and explicitly authorized. Partial outputs are
retained on failure. Ordinary link checks are not a concurrent-filesystem
sandbox; use a source and destination that are not being modified during copy.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import stat
import subprocess
from typing import Any


from check_artifacts import _git_environment


MANIFEST_PATH = "docs/distribution-manifest.json"


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


def _is_link(path: Path) -> bool:
    try:
        info = path.lstat()
    except FileNotFoundError:
        return False
    # lstat also exposes Windows junction/reparse attributes on Python 3.11.
    return stat.S_ISLNK(info.st_mode) or bool(getattr(info, "st_file_attributes", 0) & 0x400)


def _absolute_path(value: str, label: str) -> Path:
    _reject_network(value, label)
    path = Path(value)
    if not path.is_absolute():
        raise CandidateError("ABSOLUTE_PATH_REQUIRED", f"{label} must be absolute")
    if ".." in path.parts:
        raise CandidateError("UNSAFE_PATH", f"{label} must not contain parent traversal")
    return path


def _local_directory(value: str, label: str) -> Path:
    path = _absolute_path(value, label)
    if _is_link(path):
        raise CandidateError("UNSAFE_PATH", f"{label} must not itself be a link")
    try:
        # Resolve ordinary ancestor aliases, including macOS /var -> /private/var.
        resolved = path.resolve(strict=True)
    except OSError as error:
        raise CandidateError("PATH_NOT_FOUND", f"{label} must be an existing directory") from error
    if not resolved.is_dir():
        raise CandidateError("INVALID_DIRECTORY", f"{label} must be an existing directory")
    return resolved


def _inside_output_root(path: Path, allowed_roots: tuple[Path, ...]) -> None:
    if not any(path.parent.is_relative_to(root) for root in allowed_roots):
        raise CandidateError("OUTPUT_OUTSIDE_ALLOWED_ROOT",
                             "Output must be inside an explicitly allowed output root")


def _local_new_file(value: str, label: str, allowed_roots: tuple[Path, ...],
                    *, suffix: str | None = None) -> Path:
    path = _absolute_path(value, label)
    if suffix is not None and path.suffix.lower() != suffix:
        raise CandidateError("INVALID_OUTPUT_SUFFIX", f"{label} must use the {suffix} extension")
    parent = _local_directory(str(path.parent), f"{label} parent")
    resolved = parent / path.name
    if os.path.lexists(resolved):
        raise CandidateError("OUTPUT_CONFLICT", f"{label} already exists",
                             path=path.name, status="conflict", exit_code=1)
    _inside_output_root(resolved, allowed_roots)
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


def _file_path(root: Path, relative: str) -> Path:
    path = root
    for component in PurePosixPath(_safe_relative(relative)).parts:
        path = path / component
        if _is_link(path):
            raise CandidateError("UNSAFE_PATH", "Links are not candidate files or directories", path=relative)
    return path


def _source_bytes(root: Path, relative: str) -> bytes:
    try:
        path = _file_path(root, relative)
        if not path.exists():
            raise CandidateError("SOURCE_FILE_MISSING", "A listed file is missing", path=relative)
        if not path.is_file():
            raise CandidateError("SOURCE_NOT_REGULAR", "A listed file is not a regular file", path=relative)
        return path.read_bytes()
    except OSError as error:
        raise CandidateError("SOURCE_READ_ERROR", "A listed file cannot be read", path=relative) from error


def _duplicate_reject(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise CandidateError("DUPLICATE_MANIFEST_KEY", "Manifest JSON contains a duplicate object key")
        result[key] = value
    return result


def _read_manifest(root: Path) -> tuple[dict[str, Any], bytes, str]:
    try:
        raw = _source_bytes(root, MANIFEST_PATH)
        manifest = json.loads(raw.decode("utf-8"), object_pairs_hook=_duplicate_reject,
                              parse_constant=lambda value: (_ for _ in ()).throw(
                                  CandidateError("INVALID_MANIFEST", "Manifest contains a non-finite number")))
    except CandidateError:
        raise
    except (UnicodeError, json.JSONDecodeError) as error:
        raise CandidateError("INVALID_MANIFEST", "The distribution manifest must be UTF-8 JSON",
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
        if not isinstance(entry["component"], str) or entry["component"] not in components:
            raise CandidateError("INVALID_MANIFEST", "File references an undeclared owner component", path=relative)
    raw_paths = {entry["path"] for entry in files}
    if MANIFEST_PATH not in raw_paths:
        raise CandidateError("MANIFEST_NOT_SELF_DESCRIBING", "The manifest must itself be a listed file",
                             path=MANIFEST_PATH)
    for relative in raw_paths:
        parent = PurePosixPath(relative).parent
        while str(parent) != ".":
            if parent.as_posix().casefold() in seen:
                raise CandidateError("MANIFEST_PATH_COLLISION", "A file path is also a parent directory",
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
        _safe_relative(path_value, directory=isinstance(path_value, str) and path_value.endswith("/"))
        if path_value.casefold() in excluded_seen:
            raise CandidateError("DUPLICATE_EXCLUSION", "Manifest has duplicate exclusion paths", path=path_value)
        excluded_seen.add(path_value.casefold())
        if not isinstance(exclusion["reason"], str) or not exclusion["reason"].strip():
            raise CandidateError("INVALID_MANIFEST", "Each exclusion needs a reason", path=path_value)
    return manifest, raw, _sha256(raw)


def _git(root: Path, *arguments: str) -> bytes:
    result = subprocess.run(
        ["git", "--no-pager", "-c", "core.quotepath=false", "-c", "core.fsmonitor=false", *arguments],
        cwd=root, env=_git_environment(root), shell=False, capture_output=True, check=False,
    )
    if result.returncode:
        raise CandidateError("GIT_PROVENANCE_UNAVAILABLE",
                             "Local Git provenance could not be read; no branch or network fallback is used")
    return result.stdout


def _git_provenance(root: Path) -> tuple[str, list[dict[str, str]], list[str]]:
    try:
        top = _git(root, "rev-parse", "--show-toplevel").decode("utf-8").strip()
        if Path(top).resolve(strict=True) != root:
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


def _excluded_reason(relative: str, manifest: dict[str, Any]) -> str:
    for exclusion in manifest["excluded"]:
        path = exclusion["path"]
        if (path.endswith("/") and relative.startswith(path)) or relative == path:
            return exclusion["reason"]
    return "NOT_ALLOWLISTED"


def _validate_sources(root: Path):
    manifest, manifest_raw, manifest_sha = _read_manifest(root)
    commit, dirty, source_paths = _git_provenance(root)
    snapshots = {
        entry["path"]: _source_bytes(root, entry["path"])
        for entry in sorted(manifest["files"], key=lambda item: item["path"])
    }
    if snapshots[MANIFEST_PATH] != manifest_raw:
        raise CandidateError("MANIFEST_CHANGED", "Manifest bytes changed while its inventory was read",
                             path=MANIFEST_PATH)
    # Files outside the allowlist are not copied, and do not block a DDD export.
    excluded = [
        {"path": relative, "reason": _excluded_reason(relative, manifest)}
        for relative in source_paths if relative not in snapshots
    ]
    return manifest, manifest_sha, snapshots, excluded, commit, dirty, source_paths


def _output_roots(values: list[str]) -> tuple[Path, ...]:
    if not values:
        raise CandidateError("OUTPUT_ROOT_REQUIRED", "Supply at least one explicitly authorized output root")
    return tuple(dict.fromkeys(_local_directory(value, "Allowed output root") for value in values))


def _path_reference(path: Path, root: Path, allowed_roots: tuple[Path, ...]) -> str:
    if path.is_relative_to(root):
        return path.relative_to(root).as_posix()
    for allowed in allowed_roots:
        if path.is_relative_to(allowed):
            return f"external:{allowed.name}/{path.relative_to(allowed).as_posix()}"
    return "external"


def _target_directory(value: str, root: Path, allowed_roots: tuple[Path, ...],
                      *, must_exist: bool) -> Path:
    requested = _absolute_path(value, "Candidate path")
    if requested == Path(requested.anchor):
        raise CandidateError("UNSAFE_CANDIDATE_PATH", "Candidate must be a child of an authorized output root")
    if must_exist:
        resolved = _local_directory(str(requested), "Candidate")
    else:
        resolved = _local_directory(str(requested.parent), "Candidate parent") / requested.name
        if os.path.lexists(resolved):
            raise CandidateError("TARGET_CONFLICT", "Candidate already exists; no owner content was changed",
                                 path=_path_reference(resolved, root, allowed_roots),
                                 status="conflict", exit_code=1)
    _inside_output_root(resolved, allowed_roots)
    if resolved.is_relative_to(root) or root.is_relative_to(resolved):
        raise CandidateError("SOURCE_TREE_OUTPUT_REFUSED", "Source and candidate directories must not overlap")
    return resolved


def _provenance_record(commit: str, dirty: list[dict[str, str]],
                       source_paths: list[str]) -> dict[str, Any]:
    return {
        "source_commit": commit,
        "dirty_scope": dirty,
        "source_inventory_sha256": _sha256("\n".join(source_paths).encode("utf-8")),
    }


def _walk_candidate(candidate: Path) -> tuple[list[str], list[str], list[dict[str, str]]]:
    files: list[str] = []
    directories: list[str] = []
    findings: list[dict[str, str]] = []

    def visit(directory: Path) -> None:
        try:
            entries = sorted(directory.iterdir())
        except OSError:
            findings.append({"code": "DIRECTORY_READ_ERROR",
                             "path": directory.relative_to(candidate).as_posix(),
                             "message": "A candidate directory could not be read"})
            return
        for entry in entries:
            relative = entry.relative_to(candidate).as_posix()
            try:
                if _is_link(entry):
                    findings.append({"code": "UNSAFE_ENTRY", "path": relative,
                                     "message": "Links are not candidate entries"})
                elif entry.is_dir():
                    directories.append(relative)
                    if entry.name in {".git", ".venv", "__pycache__"}:
                        findings.append({"code": "FORBIDDEN_DIRECTORY", "path": relative,
                                         "message": "Git, runtime, and cache directories are excluded"})
                    visit(entry)
                elif entry.is_file():
                    files.append(relative)
                else:
                    findings.append({"code": "UNSAFE_ENTRY", "path": relative,
                                     "message": "Candidate entry is not a regular file or directory"})
            except OSError:
                findings.append({"code": "FILE_READ_ERROR", "path": relative,
                                 "message": "A candidate entry could not be inspected"})

    visit(candidate)
    return sorted(files), sorted(directories), findings


def _copy_receipt(root: Path, target: Path, manifest: dict[str, Any],
                  manifest_sha: str, snapshots: dict[str, bytes],
                  excluded: list[dict[str, str]], commit: str,
                  dirty: list[dict[str, str]], source_paths: list[str],
                  allowed_roots: tuple[Path, ...]) -> dict[str, Any]:
    files = []
    components = {entry["path"]: entry["component"] for entry in manifest["files"]}
    try:
        for relative, raw in snapshots.items():
            destination = _file_path(target, relative)
            destination.parent.mkdir(parents=True, exist_ok=True)
            with destination.open("xb") as output:
                output.write(raw)
            copied = _source_bytes(target, relative)
            if copied != raw:
                raise CandidateError("COPY_BYTES_MISMATCH", "Candidate bytes differ from the preflight source",
                                     path=relative)
            files.append({
                "path": relative, "component": components[relative], "size": len(raw),
                "source_sha256": _sha256(raw), "candidate_sha256": _sha256(copied),
            })
        for relative, original in snapshots.items():
            if _source_bytes(root, relative) != original:
                raise CandidateError("SOURCE_CHANGED", "A listed source changed during candidate copy", path=relative)
        if _git_provenance(root) != (commit, dirty, source_paths):
            raise CandidateError("SOURCE_SCOPE_CHANGED", "Git source identity or dirty scope changed during copy")
        actual_files, _, findings = _walk_candidate(target)
        if findings or set(actual_files) != set(snapshots):
            raise CandidateError("TARGET_CHANGED", "Candidate inventory changed during copy")
    except FileExistsError as error:
        raise CandidateError("OUTPUT_CONFLICT", "A candidate file already exists; partial output was retained",
                             status="conflict", exit_code=1) from error
    except OSError as error:
        raise CandidateError("COPY_IO_ERROR",
                             "Candidate copy stopped; the partial candidate was retained for inspection",
                             path=_path_reference(target, root, allowed_roots)) from error
    return {
        "schemaVersion": 1, "status": "copied", "exit_code": 0,
        "manifest_sha256": manifest_sha,
        "provenance": {"source_root": ".", **_provenance_record(commit, dirty, source_paths)},
        "target": _path_reference(target, root, allowed_roots),
        "allowed_output_roots": [_path_reference(item, root, allowed_roots) for item in allowed_roots],
        "copied_count": len(files), "excluded_count": len(excluded),
        "files": files, "excluded_files": excluded, "findings": [],
    }


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
    expected_directories = {
        parent.as_posix() for relative in expected_files
        for parent in PurePosixPath(relative).parents if str(parent) != "."
    }
    for relative in sorted(set(actual_directories) - expected_directories):
        if relative not in {item["path"] for item in findings}:
            findings.append({"code": "EXTRA_DIRECTORY", "path": relative,
                             "message": "Candidate contains an unowned directory"})
    candidate_bytes: dict[str, bytes] = {}
    for relative in sorted(expected_files & actual_set):
        try:
            raw = _source_bytes(candidate, relative)
        except CandidateError as error:
            code = {"UNSAFE_PATH": "UNSAFE_ENTRY", "SOURCE_FILE_MISSING": "MISSING_FILE"}.get(
                error.code, "FILE_READ_ERROR",
            )
            findings.append({"code": code, "path": relative, "message": str(error)})
            continue
        candidate_bytes[relative] = raw
        if _sha256(raw) != _sha256(snapshots[relative]):
            findings.append({"code": "HASH_MISMATCH", "path": relative,
                             "message": "Candidate raw bytes differ from the current listed source"})
    findings.sort(key=lambda item: (item["path"], item["code"]))
    components = {entry["path"]: entry["component"] for entry in manifest["files"]}
    return {
        "schemaVersion": 1, "status": "valid" if not findings else "invalid",
        "exit_code": 0 if not findings else 1, "manifest_sha256": manifest_sha,
        "provenance": {"source_root": ".", **_provenance_record(commit, dirty, source_paths)},
        "candidate": _path_reference(candidate, root, allowed_roots),
        "allowed_output_roots": [_path_reference(item, root, allowed_roots) for item in allowed_roots],
        "verified_count": len(candidate_bytes), "excluded_count": len(excluded),
        "files": [
            {
                "path": relative, "component": components[relative],
                "size": len(snapshots[relative]), "source_sha256": _sha256(snapshots[relative]),
                "candidate_sha256": _sha256(candidate_bytes[relative]) if relative in candidate_bytes else None,
            }
            for relative in sorted(expected_files)
        ],
        "excluded_files": excluded, "findings": findings,
    }


def _report_path(value: str | None, root: Path, allowed_roots: tuple[Path, ...]) -> Path | None:
    if value is None:
        return None
    path = _local_new_file(value, "Report path", allowed_roots, suffix=".json")
    if path.is_relative_to(root):
        raise CandidateError("OUTPUT_OVERLAP", "A report must be outside the source tree")
    return path


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
        raise CandidateError("REPORT_WRITE_ERROR", "Report write failed; any partial report was retained",
                             path=path.name) from error
    return report


def _failure(error: CandidateError, root: Path | None, allowed_roots: tuple[Path, ...],
             report_path: Path | None) -> dict[str, Any]:
    payload = {
        "schemaVersion": 1, "status": error.status, "exit_code": error.exit_code,
        "findings": [{"code": error.code, "path": error.path, "message": str(error)}],
        "allowed_output_roots": [
            _path_reference(path, root, allowed_roots) if root is not None else path.name
            for path in allowed_roots
        ],
    }
    if report_path is not None:
        payload["report_output"] = {"path": report_path.name, "written": False}
    return payload


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
        allowed_roots = _output_roots(arguments.allow_output_root)
        report_path = _report_path(arguments.report, root, allowed_roots)
        value = arguments.target if arguments.target is not None else arguments.verify
        candidate = _target_directory(value, root, allowed_roots,
                                      must_exist=arguments.target is None)
        if report_path is not None and (report_path == candidate or report_path.is_relative_to(candidate)):
            raise CandidateError("OUTPUT_OVERLAP", "Candidate and report destinations must be separate")
        source_data = _validate_sources(root)
        if arguments.target is not None:
            try:
                candidate.mkdir()
            except FileExistsError as error:
                raise CandidateError("TARGET_CONFLICT", "Candidate already exists; it was not overwritten",
                                     status="conflict", exit_code=1) from error
            payload = _copy_receipt(root, candidate, *source_data, allowed_roots)
        else:
            payload = _verify_receipt(root, candidate, *source_data, allowed_roots)
        if report_path is not None:
            payload = _write_report(report_path, payload)
            summary = {
                "status": payload["status"], "exit_code": payload["exit_code"],
                "report_output": payload["report_output"],
                "copied_count": payload.get("copied_count"),
                "verified_count": payload.get("verified_count"),
                "excluded_count": payload.get("excluded_count"), "findings": payload["findings"],
            }
            print(json.dumps(summary, ensure_ascii=True, sort_keys=True))
        else:
            print(_json_bytes(payload).decode("utf-8"), end="")
        return payload["exit_code"]
    except CandidateError as error:
        print(json.dumps(_failure(error, root, allowed_roots, report_path),
                         ensure_ascii=True, sort_keys=True))
        return error.exit_code
    except (OSError, UnicodeError):
        failure = CandidateError("LOCAL_IO_ERROR",
                                 "A local operation failed; any newly created partial output was retained")
        print(json.dumps(_failure(failure, root, allowed_roots, report_path),
                         ensure_ascii=True, sort_keys=True))
        return failure.exit_code


if __name__ == "__main__":
    raise SystemExit(main())
