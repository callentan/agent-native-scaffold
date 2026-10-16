"""Inspect a fixed local domain source; explicitly register OR materialize it.

No network, checkout/filter execution, implicit staging, commit or push.
Submodule materialization is a separate, explicitly index-consented operation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import tempfile

import yaml

from artifact_io import ArtifactInputError, _resolve_file, load_yaml_mapping
from check_artifacts import (
    _anchors, _checked_location, _decode, _domain_location, _git, _git_environment,
    _local_root, _TOOL_DIRS,
)
from source_baseline import Commit, domain_files, relative_path, validate_mapping


_FIELDS = ("id", "kind", "root", "path", "baseline", "readOnly")
_CONFLICTS = {
    "BASE_MISMATCH", "SOURCE_ID_CONFLICT", "DUPLICATE_DOMAIN_SOURCE", "SOURCE_ALIAS",
    "SOURCE_OUTPUT_OVERLAP", "TARGET_CONFLICT", "SUBMODULE_CONFLICT", "INDEX_CONFLICT",
    "INPUT_CHANGED", "SHARED_METADATA",
}


def _sha(raw):
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def _network(value):
    return isinstance(value, str) and (
        value.startswith(("//", "\\\\")) or "://" in value
        or re.match(r"^(?:[^/\\:]+@[^/\\:]+:|[A-Za-z][A-Za-z0-9+.-]{1,}:)", value) is not None
    )


def _fail(code, path, message):
    raise ArtifactInputError(code, path, 1, message)


def _report(operation):
    return {
        "status": "unavailable", "exit_code": 2, "operation": operation, "outcome": "not-applied",
        "source": None, "location": None, "config": None, "target": None,
        "ownership": {"readOnly": None, "source_writes": False, "os_enforced": False},
        "actions": [], "written": [], "native": [], "findings": [], "preflight": None,
    }


def _problem(result, error):
    code = getattr(error, "code", "SETUP_IO_ERROR")
    conflict = code in _CONFLICTS
    result.update(status="conflict" if conflict else "unavailable", exit_code=1 if conflict else 2)
    result["findings"].append({
        "code": code, "path": str(getattr(error, "path", "local setup")), "line": getattr(error, "line", 1),
        "message": error.message if isinstance(error, ArtifactInputError) else
        "Local setup I/O failed; inspect the exact retained paths before recovery",
    })


def _source(value):
    if not isinstance(value, dict):
        _fail("INVALID_SOURCE_CONFIG", "domainSource", "Supply the explicit v1 domainSource mapping")
    if _network(value.get("root")):
        _fail("NETWORK_NOT_AUTHORIZED", "domainSource.root",
              "Network sources are unavailable/proposal-only. Supply an authorized local checkout and fixed baseline; "
              "no fetch, credential discovery or remote fallback is attempted")
    # Validate the original v1 source definition, not a second source schema.
    try:
        validate_mapping({
            "schemaVersion": 1, "projectId": "source-check", "boundedContexts": [{"id": "source-check"}],
            "domainSources": [value], "developmentRegistration": "docs/development.md#project-registration",
        }, "bc-config", Path("domainSource"))
    except ArtifactInputError as error:
        if error.code == "CONTRACT_ERROR":
            raise
        _fail("INVALID_SOURCE_CONFIG", "domainSource",
              "Expected exactly id/kind/root/path/baseline/readOnly with a supported full fixed baseline")
    return dict(value)


def _relative(value, root, *, directory=False):
    relative_path(value, root, directory=directory)
    if any(part.casefold() in _TOOL_DIRS for part in value.split("/")):
        _fail("EXCLUDED_TARGET", root, "Tool/Git metadata is not a source or materialization target")
    # Portable regular-file names, including Git paths later written natively.
    if any(part.endswith((" ", ".")) and part != "." or re.search(r'[\x7f<>|?*"]', part)
           or re.fullmatch(r"(?i:con|prn|aux|nul|com[1-9]|lpt[1-9])(?:\..*)?", part)
           for part in value.split("/")):
        _fail("INVALID_PATH", root, "The relative path cannot safely name portable regular files")
    return value


def _read_file(path, *, optional=False):
    actual = _checked_location(path, missing_ok=optional)
    try:
        if optional and not actual.exists():
            return None
        if not stat.S_ISREG(actual.stat().st_mode):
            _fail("INVALID_PATH", path, "A regular local file is required")
        return actual.read_bytes()
    except FileNotFoundError as error:
        raise ArtifactInputError("FILE_NOT_FOUND", path, 1, "The explicit local file is absent") from error
    except OSError as error:
        raise ArtifactInputError("FILE_READ_ERROR", path, 1, "Cannot read the explicit local file") from error


def _file_identity(path):
    raw = _read_file(path, optional=True)
    return {"path": str(path), "sha256": None if raw is None else _sha(raw),
            "mode": None if raw is None else stat.S_IMODE(path.stat().st_mode)}


def _repo(root):
    marker = root / ".git"
    if not marker.exists() and not marker.is_symlink():
        return None
    _checked_location(marker)
    top = Path(_git(root, "rev-parse", "--show-toplevel").decode("utf-8").strip())
    if top != root:
        _fail("BASE_UNAVAILABLE", root, "Git identity belongs to a different checkout root")
    directory, common = (
        _checked_location(Path(_git(root, "rev-parse", "--path-format=absolute", flag).decode("utf-8").strip()))
        for flag in ("--git-dir", "--git-common-dir")
    )
    files = [directory / "HEAD", directory / "index", common / "config", common / "packed-refs",
             directory / "config.worktree"]
    return {
        "root": str(root), "git_dir": str(directory), "common_dir": str(common),
        "object_format": _git(root, "rev-parse", "--show-object-format").decode("ascii").strip(),
        "files": [_file_identity(path) for path in files],
        "refs": _git(root, "for-each-ref", "--format=%(refname) %(objectname)").decode("utf-8"),
    }


def _config(root, relative):
    _relative(relative, root)
    path = _checked_location(root / relative)
    raw = _read_file(path)
    data, locations = load_yaml_mapping(_decode(raw, path), path)
    ids = [entry["id"] for entry in data.get("domainSources", [])
           if isinstance(entry, dict) and isinstance(entry.get("id"), str)] \
        if isinstance(data.get("domainSources"), list) else []
    if len(ids) != len(set(ids)):
        _fail("DUPLICATE_DOMAIN_SOURCE", path, "Source IDs collide; no entry is selected or overwritten")
    validate_mapping(data, "bc-config", path)
    registration, anchor = data["developmentRegistration"].split("#")
    registration_path = _resolve_file(registration, root)
    if anchor not in _anchors(_decode(_read_file(registration_path), registration_path)):
        _fail("BROKEN_ANCHOR", registration_path, "The configured development registration anchor is absent")
    return path, raw, data, locations, _file_identity(registration_path)


def _config_add(path, raw, data, locations, source):
    """Edit only the existing domainSources block; preserve all other raw bytes."""
    text = _decode(raw, path)
    lines = text.splitlines(keepends=True)
    start = locations[("domainSources",)].line - 1
    header = lines[start]
    newline = "\r\n" if header.endswith("\r\n") else "\n"
    block = yaml.safe_dump([source], sort_keys=False, allow_unicode=True).splitlines()
    if not data["domainSources"]:
        match = re.fullmatch(r"(domainSources:[ \t]*)\[\]([ \t]*(?:#[^\r\n]*)?)(?:\r?\n)?", header)
        if not match:
            _fail("CONFIG_EDIT_UNSUPPORTED", path, "Registration requires a standalone domainSources: [] block")
        lines[start] = match[1].rstrip() + match[2] + newline
        lines[start + 1:start + 1] = ["  " + line + newline for line in block]
    else:
        if not re.fullmatch(r"domainSources:[ \t]*(?:#[^\r\n]*)?(?:\r?\n)?", header):
            _fail("CONFIG_EDIT_UNSUPPORTED", path, "Only the explicit block-style domainSources list is editable")
        first = lines[locations[("domainSources", 0)].line - 1]
        indent = len(first) - len(first.lstrip(" "))
        if not first.lstrip(" ").startswith("- "):
            _fail("CONFIG_EDIT_UNSUPPORTED", path, "The source list has no safely appendable block layout")
        end = min((location.line - 1 for key, location in locations.items()
                   if len(key) == 1 and location.line > start + 1), default=len(lines))
        if end and not lines[end - 1].endswith("\n"):
            lines[end - 1] += newline
        lines[end:end] = [" " * indent + line + newline for line in block]
    updated = (b"\xef\xbb\xbf" if raw.startswith(b"\xef\xbb\xbf") else b"") + "".join(lines).encode("utf-8")
    check, _ = load_yaml_mapping(_decode(updated, path), path)
    expected = dict(data, domainSources=[*data["domainSources"], source])
    if check != expected:
        _fail("CONFIG_EDIT_UNSUPPORTED", path, "The exact source-list edit cannot preserve the original mapping")
    validate_mapping(check, "bc-config", path)
    return updated


def _overlap(left, right):
    # Conservative case handling also catches aliases on case-insensitive hosts.
    a, b = str(left).replace("\\", "/").casefold(), str(right).replace("\\", "/").casefold()
    return a == b or a.startswith(b.rstrip("/") + "/") or b.startswith(a.rstrip("/") + "/")


def _native(root, *args, payload=None, input=None, allowed=(0,), local_clone=False):
    command = [
        "git", "--no-pager", "--no-replace-objects", "-c", "core.fsmonitor=false",
        "-c", "core.hooksPath=" + os.devnull, "-c", "core.autocrlf=false",
        "-c", "protocol.allow=never",
    ]
    if local_clone:
        command += ["-c", "protocol.file.allow=always"]  # Exact local clone only; never config --global.
    if os.name == "nt":
        command += ["-c", "core.longpaths=true"]  # Scoped Git-for-Windows support, not owner config.
    command += list(args)
    try:
        run = subprocess.run(command, cwd=root, env=_git_environment(), input=input,
                             shell=False, capture_output=True, timeout=60)
    except (OSError, subprocess.TimeoutExpired) as error:
        _fail("NATIVE_GIT_ERROR", root, "The explicit local native Git operation could not complete")
    if payload is not None:
        payload["native"].append({
            "argv": command, "cwd": str(root), "returncode": run.returncode,
            "stdout": run.stdout.decode("utf-8", errors="replace"),
            "stderr": run.stderr.decode("utf-8", errors="replace"),
        })
    if run.returncode not in allowed:
        _fail("NATIVE_GIT_ERROR", root, f"Explicit local Git {args[0]} failed with exit {run.returncode}")
    return run.stdout


def _module_values(root, path):
    if not path.exists():
        return {}
    raw = _native(root, "config", "--no-includes", "--null", "--file", str(path),
                  "--get-regexp", r"^submodule\.", allowed=(0, 1))
    values = {}
    for item in raw.split(b"\0"):
        if item:
            key, _, value = item.decode("utf-8").partition("\n")
            values.setdefault(key, []).append(value)
    return values


def _index(root):
    entries = {}
    for entry in _git(root, "ls-files", "--stage", "-z").split(b"\0"):
        if entry:
            header, name = entry.split(b"\t", 1)
            mode, sha, stage = header.decode("ascii").split()
            entries.setdefault(name.decode("utf-8"), []).append((mode, sha, stage))
    return entries


def _target_state(path):
    _checked_location(path, missing_ok=True)
    if not path.exists():
        return "absent"
    if not path.is_dir():
        return "non-directory"
    return "nonempty" if any(path.iterdir()) else "empty"


def _quote(value):
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def _append(raw, text):
    before = raw or b""
    newline = b"\r\n" if b"\r\n" in before else b"\n"
    return before + (newline if before and not before.endswith(b"\n") else b"") \
        + text.replace("\n", newline.decode("ascii")).encode("utf-8")


def _submodule(root, source_root, source, context, result):
    if source["kind"] != "git":
        _fail("INVALID_SOURCE_CONFIG", "domainSource.kind", "Local submodules require kind: git and an exact commit")
    target_value = _relative(context["target_value"], root)
    target = _checked_location(root / target_value, missing_ok=True)
    _local_root(target.parent)  # Do not manufacture undeclared parent directories.
    result["target"] = {"path": str(target), "state": _target_state(target)}
    suggested = dict(source, root=target_value)
    result["suggested_registration"] = suggested
    project, origin = context["project_repo"], context["source_repo"]
    if project is None or origin is None:
        _fail("BASE_UNAVAILABLE", root, "Local submodule setup needs explicit source and target checkout roots")
    if project["object_format"] != origin["object_format"]:
        _fail("GIT_FORMAT_MISMATCH", root, "Source and parent Git object formats must match before materialization")
    for repo in (project, origin):
        if repo["git_dir"] != repo["common_dir"] or Path(repo["git_dir"]) != Path(repo["root"]) / ".git":
            _fail("SHARED_METADATA", repo["root"], "Submodule setup refuses linked/shared or separately located metadata")
    directory = Path(project["git_dir"])
    if len(_git(root, "worktree", "list", "--porcelain", "-z").split(b"worktree ")) != 2:
        _fail("SHARED_METADATA", root, "Submodule setup must not affect sibling worktrees")
    origin_directory = Path(origin["git_dir"])
    for item in (origin_directory / "objects/info/alternates", origin_directory / "shallow"):
        if item.exists():
            _fail("BASE_UNAVAILABLE", item, "Local clone requires self-contained, non-shallow source objects")
    if any((origin_directory / "objects/pack").glob("*.promisor")):
        _fail("BASE_UNAVAILABLE", source_root, "Partial/promisor sources are not local setup inputs")
    modules = _checked_location(directory / "modules" / source["id"], missing_ok=True)
    for protected in (target, modules, directory):
        if _overlap(source_root, protected):
            _fail("SOURCE_OUTPUT_OVERLAP", protected, "Materialization cannot write into the source checkout/metadata")
    for name in ("index.lock", "config.lock"):
        if (directory / name).exists():
            _fail("INDEX_CONFLICT", directory / name, "An existing owner lock stops native metadata changes")
    gitmodules = root / ".gitmodules"
    raw_modules = _read_file(gitmodules, optional=True)
    local_config = directory / "config"
    raw_local = _read_file(local_config)
    module_values, local_values = _module_values(root, gitmodules), _module_values(root, local_config)
    prefix = "submodule." + source["id"] + "."
    selected = {key[len(prefix):]: value for key, value in module_values.items() if key.startswith(prefix)}
    local_selected = {key[len(prefix):]: value for key, value in local_values.items() if key.startswith(prefix)}
    for values in (module_values, local_values):
        for key, items in values.items():
            if key.casefold().startswith(prefix.casefold()) and not key.startswith(prefix):
                _fail("SUBMODULE_CONFLICT", gitmodules, "A case-aliased submodule ID already exists")
            if key.endswith(".path"):
                for value in items:
                    _relative(value, root)
                    if key != prefix + "path" and _overlap(root / value, target):
                        _fail("SUBMODULE_CONFLICT", gitmodules, "Another native module owns this target path")
    entries = _index(root)
    current_modules = entries.get(".gitmodules", [])
    if current_modules and (len(current_modules) != 1 or current_modules[0][0] != "100644"
                            or current_modules[0][2] != "0" or raw_modules is None
                            or _git(root, "cat-file", "blob", current_modules[0][1]) != raw_modules):
        _fail("INDEX_CONFLICT", gitmodules, "Staged and working .gitmodules differ; preserve the owner index")
    context.update(target=target, modules=modules, gitmodules=gitmodules, raw_modules=raw_modules,
                   local_config=local_config, raw_local=raw_local, target_value=target_value)
    source_url = source_root.as_posix()
    expected_modules = {"path": [target_value], "url": [source_url]}
    expected_local = {"url": [source_url], "active": ["true"]}
    if result["target"]["state"] not in ("absent", "empty"):
        if (result["target"]["state"] == "nonempty" and selected == expected_modules
                and local_selected == expected_local and entries.get(target_value) == [("160000", source["baseline"], "0")]
                and (target / ".git").is_file() and modules.is_dir()):
            if not current_modules:
                _fail("INDEX_CONFLICT", gitmodules, "The native .gitmodules entry is not staged; setup is incomplete")
            actual = _repo(target)
            if actual["git_dir"] != str(modules) or _git(target, "rev-parse", "HEAD").decode("ascii").strip() != source["baseline"]:
                _fail("SUBMODULE_CONFLICT", target, "Existing native metadata is not the exact selected setup")
            commit = Commit(target, source["baseline"])
            expected_index = {name: [(mode, blob, "0")] for name, (mode, kind, blob) in commit.files.items()}
            if _index(target) != expected_index:
                _fail("INDEX_CONFLICT", target, "The module index contains owner changes; it is not identical setup")
            files, _ = domain_files(target, ".", source["baseline"], lambda p, r: _read_file(p))
            context["target_files"] = {str(path): _sha(raw) for path, raw in files.items()}
            context["target_repo"] = actual
            result.update(outcome="no-change")
            return
        _fail("TARGET_CONFLICT", target, "A nonempty owner/materialization target is not replaced or skipped")
    if selected or local_selected or modules.exists():
        _fail("SUBMODULE_CONFLICT", target, "Partial/existing native setup requires explicit manual ownership recovery")
    if any(_overlap(root / name, target) for name in entries):
        _fail("INDEX_CONFLICT", target, "Tracked owner paths overlap the proposed gitlink")
    commit = Commit(source_root, source["baseline"])
    files, names = {}, set()
    for name, (mode, kind, blob) in sorted(commit.files.items()):
        _relative(name, source_root)
        folded = name.casefold()
        if folded in names or any(folded.startswith(other + "/") or other.startswith(folded + "/") for other in names):
            _fail("INVALID_PATH", source_root, "Commit paths alias or have file/directory collisions")
        names.add(folded)
        files[name] = (mode, blob, commit.read(name))  # Refuses links/gitlinks; never recursive checkout.
    context["materialized_files"] = files
    context["new_modules"] = _append(raw_modules,
        f'[submodule "{source["id"]}"]\n\tpath = {_quote(target_value)}\n\turl = {_quote(source_url)}\n')
    context["new_local"] = _append(raw_local,
        f'[submodule "{source["id"]}"]\n\turl = {_quote(source_url)}\n\tactive = true\n')
    # hash-object without -w only computes the raw identity; inspect creates no object.
    blob = _native(root, "hash-object", "--stdin", input=context["new_modules"]).decode("ascii").strip()
    context["modules_blob"] = blob
    context["object_path"] = _checked_location(directory / "objects" / blob[:2] / blob[2:], missing_ok=True)
    result["actions"] = [
        {"operation": "clone-local-no-checkout", "path": str(target), "module_metadata": str(modules),
         "source": str(source_root), "baseline": source["baseline"]},
        {"operation": "materialize-blobs", "path": str(target), "file_count": len(files),
         "filters_hooks": False},
        {"operation": "gitmodules", "path": str(gitmodules)},
        {"operation": "local-config", "path": str(local_config)},
        {"operation": "git-object", "path": str(context["object_path"]), "object": blob},
        {"operation": "git-index", "path": str(directory / "index"),
         "entries": [".gitmodules", target_value], "separate_consent_required": True},
    ]


def _prepare(root, source_config, operation, config_path, target, result):
    source = _source(source_config)  # Deny network before config, Git, or any credential/tool probing.
    result["source"] = source
    result["ownership"]["readOnly"] = source["readOnly"]
    if operation not in ("register", "submodule") or operation == "register" and target is not None:
        _fail("INVALID_OPERATION", "operation", "Choose registration OR an explicit submodule target, not both")
    actual = _local_root(_checked_location(root))
    _relative(source["path"], actual, directory=True)
    if any(part.casefold() in _TOOL_DIRS for part in source["root"].split("/")):
        _fail("EXCLUDED_TARGET", actual, "The declared source root cannot alias Git/environment data")
    source_root, path = _domain_location(actual, source["root"], source["path"])
    result["location"] = {"root": str(source_root), "path": source["path"],
                          "selected": str(path), "baseline": source["baseline"]}
    _checked_location(actual / source["root"])  # Check raw canceled traversal before dereferencing bytes.
    source_root = _local_root(source_root)
    config, raw_config, data, locations, registration = _config(actual, config_path)
    result["config"] = {"path": str(config), "sha256": _sha(raw_config), "state": "new"}
    existing = [entry for entry in data["domainSources"] if entry["id"] == source["id"]]
    wanted = dict(source, root=target) if operation == "submodule" and target is not None else source
    if existing:
        if existing[0] not in (source, wanted):
            _fail("SOURCE_ID_CONFLICT", config, "The selected source ID has a different owner declaration")
        result["config"]["state"] = "registered"
    for entry in data["domainSources"]:
        _, other = _domain_location(actual, entry["root"], entry["path"])
        if entry["id"] != source["id"] and _overlap(path, other):
            _fail("SOURCE_ALIAS", config, "A different source ID already owns this source location")
    files, directory = domain_files(source_root, source["path"], source["baseline"],
                                    lambda p, r: _read_file(p))
    context = {
        "root": actual, "source_root": source_root, "source": source, "config": config,
        "raw_config": raw_config, "data": data, "locations": locations, "target_value": target,
        "project_repo": _repo(actual), "source_repo": _repo(source_root),
    }
    if operation == "register":
        if _overlap(path, config):
            _fail("SOURCE_OUTPUT_OVERLAP", config, "Registration cannot alter any selected source bytes")
        if existing:
            result["outcome"] = "no-change"
        else:
            context["new_config"] = _config_add(config, raw_config, data, locations, source)
            result["actions"] = [{"operation": "register", "path": str(config),
                                  "source_id": source["id"], "git_index": False}]
    else:
        _submodule(actual, source_root, source, context, result)
    identities = {
        "root": str(actual), "source": source, "operation": operation,
        "config": _file_identity(config), "registration": registration,
        "project_repo": context["project_repo"], "source_repo": context["source_repo"],
        "source_files": {str(name): _sha(raw) for name, raw in files.items()},
        "target": result["target"], "actions": result["actions"],
        "target_repo": context.get("target_repo"), "target_files": context.get("target_files"),
        "gitmodules": None if "gitmodules" not in context else _file_identity(context["gitmodules"]),
        "local_config": None if "local_config" not in context else _file_identity(context["local_config"]),
    }
    result["preflight"] = _sha(json.dumps(identities, sort_keys=True, separators=(",", ":")).encode("utf-8"))
    result.update(status="ready", exit_code=0,
                  outcome="no-change" if result["outcome"] == "no-change" else "proposed")
    return context


def inspect_domain_source(root, source_config, *, operation="register",
                          config_path="bc-config.yaml", target=None):
    """Read-only ready/conflict/unavailable inspection of one original v1 source."""
    result = _report(operation)
    try:
        _prepare(root, source_config, operation, config_path, target, result)
    except (ArtifactInputError, OSError, ValueError, UnicodeError) as error:
        _problem(result, error)
    return result


def _tree_identity(path):
    """Read exact retained regular files without following a recovery-time alias."""
    files = []

    def visit(directory):
        _checked_location(directory)
        for child in sorted(directory.iterdir()):
            _checked_location(child)
            if child.is_dir():
                visit(child)
            else:
                raw = _read_file(child)
                files.append({"path": child.relative_to(path).as_posix(), "sha256": _sha(raw),
                              "size": len(raw), "mode": stat.S_IMODE(child.stat().st_mode)})

    visit(path)
    return files


def _record(changes, path, before=None, *, directory=False, prior_state=None):
    if any(entry["path"] == str(path) for entry in changes):
        return
    _checked_location(path, missing_ok=True)
    if prior_state is None:
        if not path.exists():
            prior_state = "absent"
        elif directory and path.is_dir():
            prior_state = "nonempty-directory" if any(path.iterdir()) else "empty-directory"
        else:
            prior_state = "file"
            if before is None:
                before = _read_file(path)
    item = {"path": str(path), "before_sha256": None if before is None else _sha(before),
            "directory": directory, "prior_state": prior_state}
    if directory and prior_state != "absent":
        item["before_files"] = _tree_identity(path)
    changes.append(item)


def _atomic_write(path, raw, before, changes, *, guard=None):
    """Stage exclusively; replace only the exact owner bytes, never truncate them."""
    if _read_file(path, optional=True) != before:
        _fail("INPUT_CHANGED", path, "Owner bytes changed before the exact file operation")
    mode = 0o644 if before is None else stat.S_IMODE(path.stat().st_mode)
    descriptor, name = tempfile.mkstemp(prefix="." + path.name + ".domain-source-", suffix=".tmp", dir=path.parent)
    staged = Path(name)
    _record(changes, staged, prior_state="absent")  # mkstemp exclusively created it above.
    with os.fdopen(descriptor, "wb") as stream:
        if stream.write(raw) != len(raw):
            raise OSError("Short write preparing the explicit config operation")
        stream.flush()
        os.fsync(stream.fileno())
    staged.chmod(mode)
    if guard:
        guard()
    if _read_file(path, optional=True) != before:
        _fail("INPUT_CHANGED", path, "Owner bytes changed before replacement; staged file retained")
    _record(changes, path, before)
    os.replace(staged, path)


def _recovery(changes):
    paths = []
    for change in changes:
        path = Path(change["path"])
        item = dict(change)
        try:
            _checked_location(path, missing_ok=True)
            if path.is_dir():
                item.update(state="retained-directory", files=_tree_identity(path))
            else:
                raw = _read_file(path, optional=True)
                item.update(state="absent" if raw is None else "retained-file",
                            sha256=None if raw is None else _sha(raw), size=None if raw is None else len(raw))
        except (ArtifactInputError, OSError):
            item["state"] = "owner-conflict-or-unreadable"
        paths.append(item)
    return {
        "state": "manual-required", "automatic_cleanup": False, "paths": paths,
        "message": "Inspect these exact retained paths and prior hashes. Reconcile later owner edits before "
                   "restoring individual metadata/files. No recursive cleanup, reset, source overwrite or commit occurred.",
    }


def _changed_paths(changes):
    retained = _recovery(changes)["paths"]
    return [item["path"] for item in retained
            if (item["state"] == "retained-file" and item["sha256"] != item["before_sha256"])
            or (item["state"] == "retained-directory" and
                (item["prior_state"] == "absent" or item["files"] != item.get("before_files", [])))]


def _materialize(context, result, changes):
    root, source, target = context["root"], context["source"], context["target"]
    modules = context["modules"]
    if not modules.parent.exists():
        _record(changes, modules.parent, directory=True)
        modules.parent.mkdir()
    for path in (target, modules):
        _record(changes, path, directory=True)  # Account even for native partial creation/failure.
    _native(root, "clone", "--local", "--no-hardlinks", "--no-checkout", "--template=",
            "--separate-git-dir=" + str(modules), "--", str(context["source_root"]), str(target),
            payload=result, local_clone=True)
    _native(target, "update-ref", "--no-deref", "HEAD", source["baseline"], payload=result)
    _native(target, "config", "--local", "core.worktree", os.path.relpath(target, modules), payload=result)
    index = bytearray()
    for name, (mode, blob, raw) in context["materialized_files"].items():
        path = _checked_location(target / name, missing_ok=True)
        path.parent.mkdir(parents=True, exist_ok=True)
        _record(changes, path)
        with path.open("xb") as output:
            if output.write(raw) != len(raw):
                raise OSError("Short write materializing an owned blob")
        path.chmod(0o755 if mode == "100755" else 0o644)
        index.extend(f"{mode} {blob}\t{name}\0".encode("utf-8"))
    _native(target, "update-index", "-z", "--index-info", input=bytes(index), payload=result)
    # Recheck original source/config/index/refs before intended superproject edits.
    if (_repo(root) != context["project_repo"] or _repo(context["source_root"]) != context["source_repo"]
            or _read_file(context["config"]) != context["raw_config"]):
        _fail("INPUT_CHANGED", root, "Preflight source or owner metadata changed after local clone")
    domain_files(context["source_root"], source["path"], source["baseline"], lambda p, r: _read_file(p))
    _atomic_write(context["gitmodules"], context["new_modules"], context["raw_modules"], changes)
    _atomic_write(context["local_config"], context["new_local"], context["raw_local"], changes)
    _record(changes, context["object_path"].parent, directory=True)
    _record(changes, context["object_path"])
    blob = _native(root, "hash-object", "-w", "--stdin", input=context["new_modules"], payload=result).decode("ascii").strip()
    if blob != context["modules_blob"]:
        _fail("INPUT_CHANGED", context["gitmodules"], "The intended metadata object identity changed")
    main_index = Path(context["project_repo"]["git_dir"]) / "index"
    old_identity = next(item for item in context["project_repo"]["files"] if item["path"] == str(main_index))
    if _file_identity(main_index) != old_identity:
        _fail("INPUT_CHANGED", main_index, "Owner index changed before the explicitly consented update")
    _record(changes, main_index, _read_file(main_index, optional=True))
    _record(changes, main_index.with_name("index.lock"))
    update = f"100644 {blob}\t.gitmodules\0" + f"160000 {source['baseline']}\t{context['target_value']}\0"
    _native(root, "update-index", "-z", "--index-info", input=update.encode("utf-8"), payload=result)
    result["outcome"] = "materialized"


def apply_domain_source(root, source_config, *, operation, config_path, expected,
                        owned=False, target=None, index_consent=False):
    """Apply one explicit local operation after exact inspect identity and consent.

    Ownership is a caller declaration, not OS access enforcement. The API never
    commits, pushes, restores speculatively, or registers a materialized source.
    """
    result, changes = _report(operation), []
    try:
        context = _prepare(root, source_config, operation, config_path, target, result)
        if not owned:
            _fail("OWNERSHIP_CONSENT_REQUIRED", context["root"], "Explicit target-owner consent is required for apply")
        if not isinstance(expected, str) or not re.fullmatch(r"sha256:[0-9a-f]{64}", expected):
            _fail("PREFLIGHT_REQUIRED", context["root"], "Apply requires the exact preceding inspection preflight")
        if result["preflight"] != expected:
            _fail("INPUT_CHANGED", context["root"], "Source/target/config/index/refs differ from the selected preflight")
        if operation == "submodule" and not index_consent:
            _fail("INDEX_CONSENT_REQUIRED", context["root"], "Native submodule metadata and gitlink staging need separate consent")
        if result["outcome"] == "no-change":
            return result
        if operation == "register":
            def guard():
                check = inspect_domain_source(root, source_config, config_path=config_path)
                if check["status"] != "ready" or check["preflight"] != expected:
                    _fail("INPUT_CHANGED", context["root"], "Inputs changed before the selected config replacement")
            _atomic_write(context["config"], context["new_config"], context["raw_config"], changes, guard=guard)
            result["outcome"] = "registered"
        else:
            _materialize(context, result, changes)
        result["written"] = _changed_paths(changes)
        result.update(status="ready", exit_code=0)
    except (ArtifactInputError, OSError, ValueError, UnicodeError) as error:
        _problem(result, error)
        if changes:
            result.update(outcome="partial", recovery=_recovery(changes))
            result["written"] = _changed_paths(changes)
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True)
    parser.add_argument("--config", required=True, help="Exact existing root-relative BC configuration")
    parser.add_argument("--source-id", required=True)
    parser.add_argument("--kind", choices=("local", "git"))
    parser.add_argument("--source-root")
    parser.add_argument("--source-path")
    parser.add_argument("--baseline")
    nature = parser.add_mutually_exclusive_group()
    nature.add_argument("--read-only", dest="read_only", action="store_true")
    nature.add_argument("--owned-source", dest="read_only", action="store_false",
                        help="Declare readOnly: false; still does not authorize source writes")
    parser.set_defaults(read_only=None)
    parser.add_argument("--operation", choices=("register", "submodule"))
    parser.add_argument("--target", help="Exact root-relative local submodule checkout; not BC registration")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--owned-target", action="store_true")
    parser.add_argument("--index-consent", action="store_true")
    parser.add_argument("--expect", help="Exact inspect preflight required by apply")
    args = parser.parse_args(argv)
    operation = args.operation or "register"  # Default applies only to inspection.
    source = {"id": args.source_id, "kind": args.kind, "root": args.source_root,
              "path": args.source_path, "baseline": args.baseline, "readOnly": args.read_only}
    try:
        if args.apply and args.operation is None:
            _fail("INVALID_OPERATION", "operation", "Apply requires an explicit register or submodule operation")
        if all(value is None for key, value in source.items() if key != "id"):
            root = _local_root(_checked_location(args.root))
            _, _, data, _, _ = _config(root, args.config)
            selected = [entry for entry in data["domainSources"] if entry["id"] == args.source_id]
            if not selected:
                _fail("INVALID_SOURCE_CONFIG", "domainSource", "The explicit source ID is not registered")
            source = selected[0]
        if args.apply:
            result = apply_domain_source(
                args.root, source, operation=operation, config_path=args.config, target=args.target,
                expected=args.expect, owned=args.owned_target, index_consent=args.index_consent,
            )
        else:
            result = inspect_domain_source(
                args.root, source, operation=operation, config_path=args.config, target=args.target,
            )
    except (ArtifactInputError, OSError, ValueError, UnicodeError) as error:
        result = _report(operation)
        _problem(result, error)
    print(json.dumps(result, ensure_ascii=True, indent=2))
    return result["exit_code"]


if __name__ == "__main__":
    raise SystemExit(main())
