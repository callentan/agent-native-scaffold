"""Optional native hooks: raw Git index acquisition, shared checks, text policy.

No source/index/config writes, source execution, filters, submodule updates or
network. Temporary regular files and Git tree objects are private to this run.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
import tempfile
import unicodedata


HOOKS = ("pre-commit", "commit-msg")
MANAGED_DIRS = {
    "domain-model", "stakeholder-requirements", "software-requirements",
    "user-stories", "architecture", "verification",
}
MANAGED_FILES = {"bc-config.yaml", "model-sources.yaml", "model.yaml", "model.json"}
EXIT = {"clean": 0, "empty": 0, "invalid": 1, "input-error": 2}
# Distribution name -> import name. requirements.lock records the tested set;
# any importable compatible version is accepted and only reported.
REQUIRED_DEPENDENCIES = {"PyYAML": "yaml", "jsonschema": "jsonschema"}


class HookInputError(ValueError):
    def __init__(self, code, path, message):
        self.code, self.path, self.message = code, str(path), message
        super().__init__(message)

    def finding(self):
        return {"code": self.code, "path": self.path, "line": 1,
                "owner": None, "target": None, "message": self.message, "related": None}


def _check_runtime(runtime, *, selected_python=None, selected_prefix=None):
    """One startup contract for installer probes and both hook entry points.

    Any Python 3.11+ interpreter (venv, conda or system) that can import the
    validator dependencies is accepted. Launcher selections, prefix and
    installed versions are report facts only, never refusal reasons.
    """
    executable = str(Path(sys.executable).absolute())
    runtime.update(executable=executable, version=sys.version,
                   version_info=list(sys.version_info[:3]), prefix=sys.prefix)
    if selected_python is not None:
        runtime["selected_executable"] = str(selected_python)
    if selected_prefix is not None:
        runtime["selected_prefix"] = str(selected_prefix)
    recovery = ("Use a Python 3.11+ interpreter (venv, conda or system) that can import the "
                "dependencies listed in .github/utilities/requirements.lock; "
                "explicitly reinstall hooks if the selected interpreter changed.")
    if sys.version_info[:2] < (3, 11):
        raise HookInputError("INTERPRETER_UNAVAILABLE", executable, recovery)
    try:
        import yaml  # noqa: F401
        import jsonschema  # noqa: F401
    except ImportError as error:
        raise HookInputError("DEPENDENCY_UNAVAILABLE", executable, f"{recovery} {error}") from error
    versions = {}
    for name in REQUIRED_DEPENDENCIES:
        try:
            versions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            versions[name] = None
    runtime["dependencies"] = versions


def git_environment(overrides=None):
    # Shared Git context, keeping a caller-selected config file (e.g. a fixture's
    # isolation). Imported lazily: the runtime check runs before dependencies load.
    # The native GIT_INDEX_FILE is captured explicitly by acquire_index.
    from check_artifacts import _git_environment
    return _git_environment(keep_config=True, overrides=overrides)


def git_read(root, *arguments, input=None, overrides=None, allowed=(0,), code="INDEX_UNAVAILABLE"):
    try:
        result = subprocess.run(
            ["git", "--no-pager", "--no-replace-objects", "-c", "core.fsmonitor=false",
             "-c", "protocol.allow=never", *arguments],
            cwd=root, env=git_environment(overrides), shell=False, input=input,
            capture_output=True, timeout=60,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        raise HookInputError(code, root, str(error)) from error
    if result.returncode not in allowed:
        raise HookInputError(code, root, f"Git exit {result.returncode}: "
                             + result.stderr.decode("utf-8", errors="replace").strip())
    return result


def git_scope(root):
    value = os.fspath(root)
    if (not value.strip() or value.startswith(("//", "\\\\")) or "://" in value
            or any(ord(c) < 32 for c in value)):
        raise HookInputError("INVALID_ROOT", value, "Select an explicit local checkout root")
    actual = Path(value).resolve(strict=True)
    top = Path(git_read(actual, "rev-parse", "--show-toplevel").stdout.decode("utf-8").strip()).resolve()
    if top != actual:
        raise HookInputError("INVALID_ROOT", actual, "Root must be the exact checkout top, not a subdirectory")
    def location(flag):
        return str(Path(git_read(actual, "rev-parse", "--path-format=absolute", flag)
                        .stdout.decode("utf-8").strip()).resolve())
    return {
        "root": str(actual), "git_dir": location("--git-dir"), "common_dir": location("--git-common-dir"),
        "object_format": git_read(actual, "rev-parse", "--show-object-format").stdout.decode("ascii").strip(),
    }


def _parent(root):
    result = git_read(root, "rev-parse", "--verify", "--quiet", "HEAD^{commit}", allowed=(0, 1))
    if result.returncode == 0:
        return result.stdout.decode("ascii").strip()
    symbolic = git_read(root, "symbolic-ref", "--quiet", "HEAD", allowed=(0, 1))
    if symbolic.returncode == 0:
        ref = symbolic.stdout.decode("utf-8").strip()
        if ref.startswith("refs/heads/"):
            exists = git_read(root, "show-ref", "--verify", "--quiet", ref, allowed=(0, 1))
            if exists.returncode == 1:
                return None  # A genuinely absent branch ref, not a failed base lookup.
    raise HookInputError("BASE_UNAVAILABLE", root, "HEAD is not a readable commit or a genuinely unborn branch")


def _safe_name(name):
    if (not name or name.startswith("/") or re.search(r'[\\:\x00-\x1f\x7f<>|?*"]', name)
            or any(part in ("", ".", "..") or part.casefold() == ".git"
                   or part.endswith((" ", "."))
                   or re.fullmatch(r"(?i:con|prn|aux|nul|com[1-9]|lpt[1-9])(?:\..*)?", part)
                   for part in name.split("/"))):
        raise HookInputError("UNSAFE_INDEX_ENTRY", name, "Index path cannot be safely materialized as a local regular file")


def _index_bytes(path):
    if not path.exists() and not path.is_symlink():
        return None
    if path.is_symlink() or path.resolve() != path or not stat.S_ISREG(path.stat().st_mode):
        raise HookInputError("INDEX_UNAVAILABLE", path, "Selected index must be a local regular file, not a link")
    return path.read_bytes()


def _entries(raw, *, staged):
    result = []
    seen = set()
    aliases = {}
    for record in raw.split(b"\0"):
        if not record:
            continue
        header, raw_name = record.split(b"\t", 1)
        mode, middle, last = header.decode("ascii").split()
        name = raw_name.decode("utf-8")
        if staged:
            blob, stage = middle, last
            if stage != "0":
                raise HookInputError("UNMERGED_INDEX", name, "Resolve index conflict stages before validation")
            _safe_name(name)
            parts = name.split("/")
            for length in range(1, len(parts) + 1):
                prefix = "/".join(parts[:length])
                key = unicodedata.normalize("NFC", prefix).casefold()
                if key in aliases and aliases[key] != prefix:
                    raise HookInputError("UNSAFE_INDEX_ENTRY", name, "Directory case/Unicode aliases cannot share the snapshot")
                aliases[key] = prefix
            folded = unicodedata.normalize("NFC", name).casefold()
            if folded in seen:
                raise HookInputError("UNSAFE_INDEX_ENTRY", name, "Case/Unicode aliases cannot share the temporary snapshot")
            seen.add(folded)
            if mode not in ("100644", "100755"):
                raise HookInputError("UNSAFE_INDEX_ENTRY", name, f"Unsupported index mode {mode}; no links or gitlinks are read")
        else:
            blob = last
        result.append({"path": name, "mode": mode, "blob": blob})
    return sorted(result, key=lambda entry: entry["path"])


def _changes(before, after):
    previous = {entry["path"]: entry for entry in before}
    current = {entry["path"]: entry for entry in after}
    return [
        {"path": path, "status": "added" if path not in previous else
         "deleted" if path not in current else "modified",
         "before": previous.get(path), "after": current.get(path)}
        for path in sorted(previous.keys() | current.keys())
        if previous.get(path) != current.get(path)
    ]


def acquire_index(root, base, snapshot):
    scope = git_scope(root)
    root = Path(scope["root"])
    selected = os.environ.get("GIT_INDEX_FILE")
    index = Path(selected) if selected else Path(
        git_read(root, "rev-parse", "--path-format=absolute", "--git-path", "index")
        .stdout.decode("utf-8").strip())
    if not index.is_absolute():
        index = root / index
    index = Path(os.path.abspath(index))
    if str(index).startswith(("//", "\\\\")):
        raise HookInputError("INDEX_UNAVAILABLE", index, "Network indexes are not supported")
    raw_index = _index_bytes(index)
    env = {"GIT_INDEX_FILE": str(index)}
    raw = git_read(root, "ls-files", "--stage", "-z", overrides=env).stdout
    parent = _parent(root)
    snapshot.update(scope, target="git-index", parent=parent, unborn=parent is None,
                    head=parent, base_origin="explicit" if base is not None else
                    "head-at-invocation" if parent is not None else "unborn",
                    base_sha=base if base is not None else parent,
                    index_path=str(index), index_sha256=hashlib.sha256(raw_index).hexdigest() if raw_index is not None else None,
                    index_manifest_sha256=hashlib.sha256(raw).hexdigest())
    # Use the local checker's exact-commit rule; explicit invalid input never falls back.
    from check_artifacts import _commit_tree
    if snapshot["base_sha"] is not None:
        exact, tree, _ = _commit_tree(root, snapshot["base_sha"])
        snapshot.update(base_sha=exact, base_tree=tree)
    else:
        snapshot["base_tree"] = None
    entries = _entries(raw, staged=True)
    snapshot["entries"] = entries
    # Git exposes intent-to-add as empty blobs in ls-files, but does not commit
    # them. Refuse rather than accidentally validating a different file set.
    diff = ("diff", "--cached", "--name-only", "-z", "--no-renames", "--no-ext-diff", "--no-textconv")
    visible = git_read(root, *diff, "--ita-visible-in-index", overrides=env).stdout
    invisible = git_read(root, *diff, "--ita-invisible-in-index", overrides=env).stdout
    if visible != invisible:
        raise HookInputError("INTENT_TO_ADD", index, "Stage file contents or remove intent-to-add entries explicitly")
    previous = _entries(git_read(root, "ls-tree", "-r", "-z", "--full-tree", parent).stdout,
                        staged=False) if parent else []
    snapshot["changes"] = _changes(previous, entries)
    return root, index, raw_index, raw, env, entries


def _blobs(root, entries):
    ids = sorted({entry["blob"] for entry in entries})
    if not ids:
        return {}
    data = git_read(root, "cat-file", "--batch", input=("".join(oid + "\n" for oid in ids)).encode("ascii")).stdout
    blobs = {}
    offset = 0
    algorithm = "sha256" if len(ids[0]) == 64 else "sha1"
    for expected in ids:
        end = data.index(b"\n", offset)
        header = data[offset:end].decode("ascii").split()
        if len(header) != 3 or header[:2] != [expected, "blob"]:
            raise HookInputError("INDEX_UNAVAILABLE", root, f"Index blob {expected} is missing or not a blob")
        size = int(header[2])
        raw = data[end + 1:end + 1 + size]
        offset = end + 2 + size
        actual = hashlib.new(algorithm, b"blob " + str(size).encode("ascii") + b"\0" + raw).hexdigest()
        if len(raw) != size or data[offset - 1:offset] != b"\n" or actual != expected:
            raise HookInputError("INDEX_UNAVAILABLE", root, f"Index blob {expected} could not be verified")
        blobs[expected] = raw
    if offset != len(data):
        raise HookInputError("INDEX_UNAVAILABLE", root, "Unexpected bytes in raw Git blob response")
    return blobs


def _tree(root, entries, objects):
    """Let Git encode/sort/hash trees; writes are confined to private objects."""
    hierarchy = {}
    for entry in entries:
        node = hierarchy
        parts = entry["path"].split("/")
        for part in parts[:-1]:
            if part in node and not isinstance(node[part], dict):
                raise HookInputError("UNSAFE_INDEX_ENTRY", entry["path"], "Index file/directory collision")
            node = node.setdefault(part, {})
        if parts[-1] in node:
            raise HookInputError("UNSAFE_INDEX_ENTRY", entry["path"], "Index file/directory collision")
        node[parts[-1]] = (entry["mode"], entry["blob"])
    objects.mkdir()
    def build(node):
        records = []
        for name, value in node.items():
            mode, kind, oid = ("040000", "tree", build(value)) if isinstance(value, dict) else (value[0], "blob", value[1])
            records.append(f"{mode} {kind} {oid}\t{name}\0".encode("utf-8"))
        return git_read(root, "mktree", "-z", "--missing", input=b"".join(records),
                        overrides={"GIT_OBJECT_DIRECTORY": str(objects)}).stdout.decode("ascii").strip()
    return build(hierarchy)


def _remap(value, temporary, root):
    if isinstance(value, dict):
        return {key: _remap(item, temporary, root) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_remap(item, temporary, root) for item in value]
    if isinstance(value, str):
        # OS exception strings may contain repr-escaped Windows paths.
        return value.replace(str(temporary).replace("\\", "\\\\"),
                             str(root).replace("\\", "\\\\")).replace(str(temporary), str(root))
    return value


def _checked(payload, snapshot_root, root, base):
    from check_artifacts import read_inventory
    from check_traceability import _trace_inventory
    inventory = read_inventory(snapshot_root, base, _base_root=root)
    delivery = sorted(entry.reference for artifact in inventory.artifacts for entry in artifact.acceptances)
    coverage = _trace_inventory(inventory, delivery, allow_empty=True)
    def report(value):
        result = _remap(value.to_dict(), snapshot_root, root)
        if result["baseline"] is not None:
            result["baseline"]["target"] = "git-index"
        return result
    artifact_report, coverage_report = report(inventory.report), report(coverage)
    coverage_status = ("not-run" if inventory.report.status == "input-error" else
                       "invalid" if coverage.status == "invalid" else
                       "not-applicable" if not delivery else coverage.status)
    payload.update(status=coverage.status, findings=coverage_report["findings"],
                   checked_count=coverage.checked_count, attempted_count=coverage.attempted_count,
                   checks={"artifacts": artifact_report, "coverage": {
                       "status": coverage_status, "acceptance_count": len(delivery),
                       "delivery_ids": delivery, "report": coverage_report,
                   }})


def _message_policy(payload, path, root, snapshot):
    if path is None:
        raise HookInputError("INVALID_MESSAGE", root, "commit-msg requires Git's supplied message path")
    message = Path(path)
    if not message.is_absolute():
        message = root / message
    if message.is_symlink() or not message.is_file() or message.resolve() != message:
        raise HookInputError("INVALID_MESSAGE", message, "Message must be a readable regular file, not a link")
    raw = message.read_bytes()
    text = raw.decode("utf-8-sig")
    managed = [
        change["path"] for change in snapshot["changes"]
        if change["path"] in MANAGED_FILES or
        (change["path"].split("/")[0] in MANAGED_DIRS
         and Path(change["path"]).suffix.lower() in (".md", ".feature", ".yaml", ".yml", ".json"))
    ]
    policy = {
        "name": "managed-reviewed-by-text-v1", "required": bool(managed),
        "managed_paths": managed, "authenticated": False,
        "message_path": str(message), "message_sha256": hashlib.sha256(raw).hexdigest(),
    }
    payload["policy"] = policy
    if managed:
        from check_artifacts import _PLACEHOLDER
        declared = re.findall(r"(?im)^reviewed-by:[ \t]*(.*)$", text)
        placeholders = {"reviewer", "name", "none", "n/a", "unknown", "pending", "not-run", "tbd", "to be confirmed"}
        invalid = any(
            len(value.strip()) < 2 or value.strip().casefold() in placeholders
            or _PLACEHOLDER.search(value) or re.search(r"<(?:name|reviewer)>", value, re.I)
            or not any(c.isalpha() for c in value)
            for value in declared
        )
        if not declared or invalid:
            error = HookInputError(
                "INVALID_REVIEWED_BY" if declared else "MISSING_REVIEWED_BY", message,
                "Managed staged paths require a non-placeholder 'Reviewed-by: name' line. "
                "This checks text only, never identity or approval; no message is changed.",
            )
            payload.update(status="invalid", findings=[error.finding()])


def _tool_sources():
    utilities = Path(__file__).resolve().parent
    tool_root = utilities.parent.parent
    paths = [utilities / name for name in
             ("hook_checks.py", "artifact_io.py", "check_artifacts.py", "check_traceability.py")]
    paths.append(tool_root / ".github/contracts/artifact.schema.json")
    entry = Path(sys.argv[0]).resolve()
    if entry.is_file() and entry.is_relative_to(tool_root):
        paths.append(entry)
    return {path.relative_to(tool_root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted(set(paths))}


def run_hook(hook, root, *, base=None, message=None, selected_python=None, selected_prefix=None):
    payload = {"hook": hook, "status": "clean", "exit_code": 0, "findings": [],
               "checked_count": 0, "attempted_count": 0, "snapshot": {}, "startup_validated": False,
               "runtime": {"executable": str(Path(sys.executable).absolute()), "version": sys.version,
                           "prefix": sys.prefix}}
    try:
        # Refuse an unusable interpreter before importing validators or
        # acquiring any source/index input.
        _check_runtime(payload["runtime"], selected_python=selected_python, selected_prefix=selected_prefix)
        payload["startup_validated"] = True
        import artifact_io
        import check_artifacts
        from check_traceability import _trace_inventory  # noqa: F401
        payload["runtime"]["tool_root"] = str(Path(__file__).resolve().parents[2])
        payload["runtime"]["tool_sources"] = _tool_sources()
        actual, *_, entries = acquire_index(root, base, payload["snapshot"])
        if hook == "pre-commit":
            with tempfile.TemporaryDirectory(prefix="artifact-index-") as name:
                temporary = Path(name).resolve()
                snapshot_root = temporary / "files"
                snapshot_root.mkdir()
                payload["snapshot"]["index_tree"] = _tree(actual, entries, temporary / "objects")
                blobs = _blobs(actual, entries)
                for entry in entries:
                    raw = blobs[entry["blob"]]
                    entry.update(sha256=hashlib.sha256(raw).hexdigest(), size=len(raw))
                    path = snapshot_root / entry["path"]
                    path.parent.mkdir(parents=True, exist_ok=True)
                    with path.open("xb") as output:
                        output.write(raw)
                _checked(payload, snapshot_root, actual, payload["snapshot"]["base_sha"])
        elif hook == "commit-msg":
            _message_policy(payload, message, actual, payload["snapshot"])
        else:
            raise HookInputError("INVALID_HOOK", hook, "Select pre-commit or commit-msg")
    except ImportError as error:
        failure = HookInputError("DEPENDENCY_UNAVAILABLE", sys.executable,
                                 "Restore matching distributed tool modules and the selected interpreter "
                                 f"from requirements.lock: {error}")
        payload.update(status="input-error", findings=[*payload["findings"], failure.finding()])
    except HookInputError as error:
        payload.update(status="input-error", findings=[*payload["findings"], error.finding()])
    except (OSError, UnicodeError, ValueError) as error:
        # Preserve the checker's exact codes, including INVALID_BASE and
        # BASE_UNAVAILABLE. Other acquisition/decoding errors cannot be empty.
        finding = {"code": getattr(error, "code", "INDEX_UNAVAILABLE"),
                   "path": str(getattr(error, "path", root)), "line": getattr(error, "line", 1),
                   "owner": None, "target": None, "message": getattr(error, "message", str(error)), "related": None}
        payload.update(status="input-error", findings=[*payload["findings"], finding])
    payload["exit_code"] = EXIT[payload["status"]]
    return payload


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("hook", choices=HOOKS)
    parser.add_argument("--root", required=True)
    parser.add_argument("--base")
    parser.add_argument("--report")
    parser.add_argument("--selected-python", help="Installed launcher's selected executable (report fact only)")
    parser.add_argument("--selected-prefix", help="Installed launcher's selected environment prefix (report fact only)")
    parser.add_argument("message", nargs="?")
    # Native Git supplies the optional message after --root. Python 3.11's
    # parse_args otherwise consumes this positional as absent before the option.
    args = parser.parse_intermixed_args(argv)
    payload = run_hook(args.hook, args.root, base=args.base, message=args.message,
                       selected_python=args.selected_python, selected_prefix=args.selected_prefix)
    if args.report and not payload["startup_validated"]:
        # A startup refusal must stay independent of validator imports, even
        # when output was requested. Do not open or inspect the requested path.
        payload["report_output"] = {"path": args.report, "written": False, "reason": "startup-refused"}
    elif args.report:
        try:
            from check_artifacts import _write_report
            _write_report(payload, args.report, args.root)
        except (ImportError, OSError, ValueError) as error:
            payload.update(status="input-error", exit_code=2)
            payload["findings"].append({
                "code": getattr(error, "code", "REPORT_WRITE_ERROR"),
                "path": str(getattr(error, "path", args.report)), "line": 1,
                "owner": None, "target": None, "message": str(error), "related": None,
            })
            payload["report_output"] = {"path": args.report, "written": False}
    print(json.dumps(payload, ensure_ascii=True, separators=(",", ":")))
    return payload["exit_code"]


if __name__ == "__main__":
    raise SystemExit(main())
