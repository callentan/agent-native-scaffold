"""Inspect, explicitly install, or restore selected optional hooks. No Git config writes."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shlex
import stat
import subprocess
import sys

from hook_checks import HOOKS, HookInputError, git_environment, git_read, git_scope


OWNER = "artifact-maintenance-hooks-v1"


def _sha(raw):
    return hashlib.sha256(raw).hexdigest()


def _regular(path):
    return (not path.is_symlink() and path.resolve() == path
            and stat.S_ISREG(path.stat().st_mode))


def _interpreter(value, root):
    path = Path(value)
    if not path.is_absolute():
        raise HookInputError("INTERPRETER_UNAVAILABLE", value, "Supply the absolute selected project Python path")
    path = path.absolute()
    if any(ord(c) < 32 for c in str(path)) or not path.is_file():
        raise HookInputError("INTERPRETER_UNAVAILABLE", path, "Selected interpreter is missing or invalid; no fallback")
    probe = (
        "import sys,json,importlib.metadata,yaml,jsonschema;"
        "print(json.dumps({'executable':sys.executable,'prefix':sys.prefix,"
        "'base_prefix':sys.base_prefix,'version':list(sys.version_info[:3]),"
        "'dependencies':{n:importlib.metadata.version(n) for n in ('PyYAML','jsonschema')}}))"
    )
    try:
        result = subprocess.run([str(path), "-B", "-X", "utf8", "-c", probe],
                                cwd=root, env=git_environment(), shell=False,
                                capture_output=True, timeout=30)
    except (OSError, subprocess.TimeoutExpired) as error:
        raise HookInputError("INTERPRETER_UNAVAILABLE", path, str(error)) from error
    if result.returncode:
        raise HookInputError("DEPENDENCY_UNAVAILABLE", path,
                             "Restore the selected project environment from requirements.lock: "
                             + result.stderr.decode("utf-8", errors="replace").strip())
    facts = json.loads(result.stdout)
    if (facts["version"][:2] < [3, 11] or facts["prefix"] == facts["base_prefix"]
            or Path(facts["executable"]).resolve() != path.resolve()
            or facts["dependencies"] != {"PyYAML": "6.0.2", "jsonschema": "4.23.0"}):
        raise HookInputError("INTERPRETER_UNAVAILABLE", path,
                             "Use the selected Python 3.11+ project venv with the pinned tool dependencies")
    return path, facts


def _launcher(root, hook, python):
    entry = root / ".github" / "hooks" / hook
    # Git for Windows' Python shebang dispatch was observed using a different
    # interpreter even with an absolute path. Git's bundled sh preserves the
    # selected interpreter. POSIX gets a direct Python shebang when representable.
    if os.name == "nt" or any(c.isspace() for c in str(python)) or len(os.fsencode(python)) > 120:
        args = [python.as_posix(), "-B", "-X", "utf8", entry.as_posix(), "--root", root.as_posix()]
        quoted = " ".join(shlex.quote(arg) for arg in args)
        text = ("#!/bin/sh\n# artifact-maintenance: startup only; no validation policy here.\n"
                f"if [ ! -x {shlex.quote(python.as_posix())} ]; then\n"
                "  printf '%s\\n' 'Selected project interpreter is unavailable; restore it or reinstall explicitly.' >&2\n"
                "  exit 2\nfi\n"
                f"exec {quoted} \"$@\"\n")
        return text.encode("utf-8"), "Git sh (startup only)"
    text = (f"#!{python}\n# artifact-maintenance: startup only.\n"
            "import os, sys\n"
            f"os.execv({str(python)!r}, [{str(python)!r}, '-B', '-X', 'utf8', "
            f"{str(entry)!r}, '--root', {str(root)!r}, *sys.argv[1:]])\n")
    return text.encode("utf-8"), "selected Python shebang"


def install(root, hooks, python=None, *, apply=False, restore=False):
    payload = {"status": "restore-proposed" if restore else "proposed", "exit_code": 0,
               "actions": [], "findings": [], "config_changes": [], "written": []}
    created = []
    try:
        scope = git_scope(root)
        payload["scope"] = scope
        actual = Path(scope["root"])
        git_dir, common = Path(scope["git_dir"]), Path(scope["common_dir"])
        worktrees = git_read(actual, "worktree", "list", "--porcelain", "-z").stdout
        paths = [entry.decode("utf-8")[9:] for entry in worktrees.split(b"\0")
                 if entry.startswith(b"worktree ")]
        payload["scope"].update(worktrees=paths, shared=git_dir != common or len(paths) != 1)
        if not hooks or len(hooks) != len(set(hooks)) or any(hook not in HOOKS for hook in hooks):
            raise HookInputError("INVALID_HOOK", actual, "Explicitly select unique supported hooks")
        directory = common / "hooks"
        payload["scope"]["hooks_dir"] = str(directory)
        for hook in hooks:
            payload["actions"].append({"hook": hook, "path": str(directory / hook),
                                       "receipt": str(directory / (hook + ".artifact-maintenance.json")),
                                       "operation": "restore" if restore else "create"})
        existing = git_read(actual, "config", "--null", "--show-origin", "--show-scope",
                            "--get-all", "core.hooksPath", allowed=(0, 1))
        payload["scope"]["hooks_path_config"] = existing.stdout.decode("utf-8").split("\0")[:-1]
        if existing.returncode == 0:
            raise HookInputError("HOOKS_PATH_CONFLICT", directory,
                                 "An owner hooksPath is configured; preserve it and integrate separately")
        if scope["shared"]:
            raise HookInputError("SHARED_HOOKS_SCOPE", directory,
                                 "Default hooks affect linked/sibling worktrees; this installer refuses shared metadata")
        if directory.is_symlink() or directory.resolve() != directory or (directory.exists() and not directory.is_dir()):
            raise HookInputError("HOOK_CONFLICT", directory, "Hooks directory is an owner link or non-directory")
        prepared = []
        if restore:
            for action in payload["actions"]:
                path, receipt = Path(action["path"]), Path(action["receipt"])
                if not path.exists() or not receipt.exists() or not _regular(path) or not _regular(receipt):
                    raise HookInputError("OWNERSHIP_CONFLICT", path, "Owned regular hook and receipt are both required")
                raw_receipt = receipt.read_bytes()
                try:
                    record = json.loads(raw_receipt)
                except (ValueError, UnicodeError) as error:
                    raise HookInputError("OWNERSHIP_CONFLICT", receipt, "Owner-edited receipt is not valid JSON") from error
                if (not isinstance(record, dict) or record.get("owner") != OWNER or record.get("root") != str(actual)
                        or record.get("git_dir") != str(git_dir) or record.get("path") != str(path)
                        or record.get("prior_state") != "absent" or record.get("config_changes") != []
                        or record.get("sha256") != _sha(path.read_bytes())
                        or record.get("mode") != stat.S_IMODE(path.stat().st_mode)):
                    raise HookInputError("OWNERSHIP_CONFLICT", path,
                                         "Owner-edited hook/receipt: do not overwrite or delete; reconcile manually")
                prepared.append((path, path.read_bytes(), receipt, raw_receipt))
        else:
            runtime_files = [
                ".github/utilities/hook_checks.py", ".github/utilities/artifact_io.py",
                ".github/utilities/check_artifacts.py", ".github/utilities/check_traceability.py",
                ".github/utilities/requirements.lock", ".github/contracts/artifact.schema.json",
            ]
            for relative in runtime_files:
                source = actual / relative
                if not source.exists() or not _regular(source):
                    raise HookInputError("SOURCE_UNAVAILABLE", source, "Distribute the regular local hook dependencies first")
            for action in payload["actions"]:
                for value in (action["path"], action["receipt"]):
                    path = Path(value)
                    if path.exists() or path.is_symlink():
                        raise HookInputError("HOOK_CONFLICT", path, "An existing owner file/link is a conflict, even if empty")
                entry = actual / ".github" / "hooks" / action["hook"]
                if not entry.exists() or not _regular(entry):
                    raise HookInputError("SOURCE_UNAVAILABLE", entry, "Distributed regular Python entry is required")
            selected, facts = _interpreter(python or "", actual)
            payload["interpreter"] = facts
            for action in payload["actions"]:
                raw, runtime = _launcher(actual, action["hook"], selected)
                path, receipt = Path(action["path"]), Path(action["receipt"])
                action.update(launcher=runtime, sha256=_sha(raw), prior_state="absent")
                prepared.append((path, raw, receipt, None))
        if apply:
            if restore:
                # Preflight ALL selected paths before any removal; recheck each
                # owned byte sequence immediately before its narrowly scoped delete.
                for path, raw, receipt, raw_receipt in prepared:
                    if not _regular(path) or path.read_bytes() != raw or receipt.read_bytes() != raw_receipt:
                        raise HookInputError("OWNERSHIP_CONFLICT", path, "Owned files changed during restoration")
                    path.unlink()
                    receipt.unlink()
                    payload["written"].extend([str(path), str(receipt)])
                payload["status"] = "restored"
            else:
                directory.mkdir(exist_ok=True)
                for path, raw, receipt, _ in prepared:
                    with path.open("xb") as out:
                        out.write(raw)
                    created.append((path, raw))
                    path.chmod(0o755)
                    record = {"owner": OWNER, "root": str(actual), "git_dir": str(git_dir),
                              "path": str(path), "sha256": _sha(raw),
                              "mode": stat.S_IMODE(path.stat().st_mode),
                              "interpreter": str(selected), "prior_state": "absent", "config_changes": []}
                    receipt_bytes = (json.dumps(record, ensure_ascii=True, indent=2) + "\n").encode("utf-8")
                    with receipt.open("xb") as out:
                        out.write(receipt_bytes)
                    created.append((receipt, receipt_bytes))
                    payload["written"].extend([str(path), str(receipt)])
                payload["status"] = "installed"
    except (HookInputError, OSError, ValueError) as error:
        # Only files exclusively created by this call, still byte-identical, may
        # be rolled back. No recursive cleanup, config reset or owner overwrite.
        for path, raw in reversed(created):
            if path.exists() and _regular(path) and path.read_bytes() == raw:
                path.unlink()
        code = getattr(error, "code", "INSTALLATION_ERROR")
        payload.update(status="conflict" if "CONFLICT" in code or code == "SHARED_HOOKS_SCOPE" else "input-error",
                       exit_code=2)
        payload["findings"].append(
            error.finding() if isinstance(error, HookInputError)
            else HookInputError(code, root, str(error)).finding())
    return payload


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True)
    parser.add_argument("--hook", action="append", choices=HOOKS, required=True)
    parser.add_argument("--python")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--restore", action="store_true")
    args = parser.parse_args()
    if not args.restore and not args.python:
        parser.error("Installation/inspection requires --python with the selected absolute project interpreter")
    payload = install(args.root, args.hook, args.python, apply=args.apply, restore=args.restore)
    print(json.dumps(payload, ensure_ascii=True, indent=2))
    return payload["exit_code"]


if __name__ == "__main__":
    raise SystemExit(main())
