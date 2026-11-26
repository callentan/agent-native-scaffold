"""Install, update, and verify scaffold files from the distribution manifest.

Locked files belong to the scaffold: only ``update`` writes them. Files marked
``projectOwned`` in the manifest are seeded once and never overwritten.
"""
from __future__ import annotations

import contextlib
import difflib
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath
from typing import Iterator

DEFAULT_SOURCE = "https://github.com/callentan/agent-native-scaffold.git"
MANIFEST_PATH = "docs/distribution-manifest.json"
STATE_DIR = ".scaffold"
RECEIPT_PATH = f"{STATE_DIR}/receipt.json"
LOCKED_LIST_PATH = f"{STATE_DIR}/locked.txt"
REPORT_PATH = f"{STATE_DIR}/update-report.md"
BASE_DIR = f"{STATE_DIR}/base"
OVERWRITTEN_DIR = f"{STATE_DIR}/overwritten"
PROJECT_FILE = "PROJECT.md"
RESERVED_NAMES = {"update", "verify", "install"} | {"con", "prn", "aux", "nul"} \
    | {f"com{i}" for i in range(1, 10)} | {f"lpt{i}" for i in range(1, 10)}
NAME_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,99}$")
MD_MARKER = b"<!-- scaffold: locked -->\n"
HASH_MARKER = b"# scaffold: locked\n"
HASH_SUFFIXES = {".py", ".yml", ".yaml", ".txt", ".lock"}


class ScaffoldError(Exception):
    """An expected failure; the message is safe to show to the user."""


def validate_name(name: str) -> str:
    name = name.strip()
    if not NAME_PATTERN.fullmatch(name) or name.endswith(".") or name.casefold() in RESERVED_NAMES:
        raise ScaffoldError(
            "Invalid project name: use letters, digits, '.', '_' or '-', start with a letter or digit, "
            "at most 100 characters, and avoid reserved names (install, update, verify, CON, NUL, ...)."
        )
    return name


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def safe_relative(value: object) -> str:
    if not isinstance(value, str) or not value or "\\" in value or "\0" in value:
        raise ScaffoldError(f"Unsafe manifest path: {value!r}")
    parts = value.split("/")
    if value.startswith("/") or any(part in ("", ".", "..") for part in parts) or ":" in parts[0]:
        raise ScaffoldError(f"Unsafe manifest path: {value!r}")
    return value


def inject_marker(relative: str, raw: bytes) -> bytes:
    """Add the visible locked marker where the file type has a safe comment form."""
    if relative.startswith("_templates/") or b"scaffold: locked" in raw[:300]:
        return raw
    suffix = PurePosixPath(relative).suffix.lower()
    if suffix == ".md":
        if raw.startswith(b"---\n"):
            end = raw.find(b"\n---\n", 3)
            if end != -1:
                cut = end + len(b"\n---\n")
                return raw[:cut] + MD_MARKER + raw[cut:]
        return MD_MARKER + raw
    if suffix in HASH_SUFFIXES or (not suffix and raw.startswith(b"#!")):
        if raw.startswith(b"#!"):
            newline = raw.find(b"\n")
            if newline == -1:
                return raw
            return raw[:newline + 1] + HASH_MARKER + raw[newline + 1:]
        return HASH_MARKER + raw
    return raw


@dataclass
class Entry:
    path: str
    project_owned: bool

    @property
    def locked(self) -> bool:
        return not self.project_owned


@dataclass
class Source:
    root: Path
    location: str
    ref: str | None
    commit: str | None
    entries: list[Entry] = field(default_factory=list)

    def raw(self, entry: Entry) -> bytes:
        path = self.root / entry.path
        if path.is_symlink() or not path.is_file():
            raise ScaffoldError(f"Source file is missing or not a regular file: {entry.path}")
        return path.read_bytes()

    def mode(self, entry: Entry) -> int:
        return 0o755 if (self.root / entry.path).stat().st_mode & 0o111 else 0o644


def load_entries(root: Path) -> list[Entry]:
    manifest = root / MANIFEST_PATH
    try:
        data = json.loads(manifest.read_text(encoding="utf-8"))
        files = data["files"]
    except (OSError, ValueError, KeyError, TypeError) as error:
        raise ScaffoldError(f"Cannot read the scaffold manifest {MANIFEST_PATH}") from error
    entries: list[Entry] = []
    seen: set[str] = set()
    for item in files:
        if not isinstance(item, dict) or "path" not in item:
            raise ScaffoldError("Manifest has a malformed file entry")
        relative = safe_relative(item["path"])
        if relative.casefold() in seen:
            raise ScaffoldError(f"Manifest has a duplicate path: {relative}")
        seen.add(relative.casefold())
        entries.append(Entry(relative, item.get("projectOwned") is True))
    if not entries:
        raise ScaffoldError("Manifest lists no files")
    return entries


def _git(*arguments: str, cwd: Path | None = None) -> str:
    try:
        result = subprocess.run(["git", *arguments], cwd=cwd, capture_output=True, text=True,
                                encoding="utf-8", check=False, shell=False)
    except OSError as error:
        raise ScaffoldError("git is required to fetch the scaffold source") from error
    if result.returncode:
        raise ScaffoldError(f"git {arguments[0]} failed: {result.stderr.strip()[:300]}")
    return result.stdout.strip()


def _is_remote(source: str) -> bool:
    return "://" in source or source.startswith("git@")


@contextlib.contextmanager
def open_source(source: str | None, ref: str | None) -> Iterator[Source]:
    source = source or DEFAULT_SOURCE
    if not _is_remote(source):
        root = Path(source).resolve()
        if not root.is_dir():
            raise ScaffoldError(f"Source directory not found: {source}")
        try:
            commit = _git("rev-parse", "HEAD", cwd=root)
        except ScaffoldError:
            commit = None
        yield Source(root, str(root), None, commit, load_entries(root))
        return
    if ref is None:
        tags = _git("ls-remote", "--tags", "--refs", "--sort=-v:refname", source).splitlines()
        ref = tags[0].split("refs/tags/", 1)[1] if tags else None
    with tempfile.TemporaryDirectory(prefix="ddd-scaffold-src-") as temp:
        clone = Path(temp) / "src"
        command = ["clone", "--quiet", "--depth", "1"]
        if ref:
            command += ["--branch", ref]
        _git(*command, "--", source, str(clone))
        yield Source(clone, source, ref, _git("rev-parse", "HEAD", cwd=clone), load_entries(clone))


def customize(relative: str, raw: bytes, name: str) -> bytes:
    if relative != PROJECT_FILE:
        return raw
    text = raw.decode("utf-8")
    for old, new in (("# TBD: Project name", f"# {name}"), ("| Project name | TBD |", f"| Project name | {name} |")):
        if text.count(old) != 1:
            raise ScaffoldError(f"{PROJECT_FILE} is missing the expected project-name placeholder: {old}")
        text = text.replace(old, new)
    return text.encode("utf-8")


def _write(path: Path, data: bytes, mode: int | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(f".{path.name}.scaffold-tmp")
    temp.write_bytes(data)
    if mode is not None:
        os.chmod(temp, mode)
    os.replace(temp, path)


def _write_state(root: Path, name: str, source: Source, files: dict[str, dict]) -> None:
    receipt = {
        "schemaVersion": 1,
        "project": name,
        "scaffold": {"source": source.location, "ref": source.ref, "commit": source.commit},
        "files": dict(sorted(files.items())),
    }
    _write(root / RECEIPT_PATH, (json.dumps(receipt, indent=2, ensure_ascii=False) + "\n").encode("utf-8"))
    locked = sorted(path for path, info in files.items() if info["locked"])
    _write(root / LOCKED_LIST_PATH, ("\n".join(locked) + "\n").encode("utf-8"))


def read_receipt(root: Path) -> dict:
    path = root / RECEIPT_PATH
    try:
        receipt = json.loads(path.read_text(encoding="utf-8"))
        if receipt["schemaVersion"] != 1 or not isinstance(receipt["files"], dict):
            raise ValueError
        for relative in receipt["files"]:
            safe_relative(relative)
        return receipt
    except (OSError, ValueError, KeyError, TypeError) as error:
        raise ScaffoldError(
            f"No valid {RECEIPT_PATH} in {root}; refusing to guess the installed baseline."
        ) from error


def install(name: str, parent: Path, source_arg: str | None, ref: str | None) -> Path:
    name = validate_name(name)
    target = parent / name
    if target.exists() and (not target.is_dir() or any(target.iterdir())):
        raise ScaffoldError(f"{target} already exists and is not empty; nothing was written.")
    with open_source(source_arg, ref) as source:
        staging = Path(tempfile.mkdtemp(prefix=f".{name}.tmp-", dir=parent))
        try:
            files: dict[str, dict] = {}
            for entry in source.entries:
                raw = source.raw(entry)
                data = inject_marker(entry.path, raw) if entry.locked else customize(entry.path, raw, name)
                _write(staging / entry.path, data, source.mode(entry))
                files[entry.path] = {"sha256": sha256(data), "locked": entry.locked}
                if entry.project_owned:
                    _write(staging / BASE_DIR / entry.path, raw)
            _write_state(staging, name, source, files)
            if target.exists():
                target.rmdir()
            os.rename(staging, target)
        except BaseException:
            shutil.rmtree(staging, ignore_errors=True)
            raise
    return target


@dataclass
class Action:
    kind: str
    path: str
    detail: str = ""


@dataclass
class UpdatePlan:
    actions: list[Action]
    diffs: dict[str, str]
    writes: dict[str, tuple[bytes, int]]
    backups: list[str]
    new_files: dict[str, dict]
    base_updates: dict[str, bytes]

    @property
    def conflicts(self) -> list[Action]:
        return [action for action in self.actions if action.kind == "conflict"]


def plan_update(root: Path, source: Source, force_locked: bool) -> UpdatePlan:
    receipt = read_receipt(root)
    name = receipt["project"]
    old_files: dict[str, dict] = receipt["files"]
    plan = UpdatePlan([], {}, {}, [], {}, {})
    current = {entry.path for entry in source.entries}
    for entry in source.entries:
        relative = entry.path
        local = root / relative
        raw = source.raw(entry)
        mode = source.mode(entry)
        if local.is_symlink() or (local.exists() and not local.is_file()):
            plan.actions.append(Action("conflict", relative, "local path is not a regular file"))
            if relative in old_files:
                plan.new_files[relative] = old_files[relative]
            continue
        if entry.project_owned:
            data = customize(relative, raw, name)
            base_path = root / BASE_DIR / relative
            if not local.exists():
                plan.actions.append(Action("seed", relative, "new project-owned file"))
                plan.writes[relative] = (data, mode)
                plan.base_updates[relative] = raw
                plan.new_files[relative] = {"sha256": sha256(data), "locked": False}
                continue
            plan.new_files[relative] = {
                "sha256": old_files.get(relative, {}).get("sha256", sha256(local.read_bytes())), "locked": False}
            if base_path.is_file():
                base = base_path.read_bytes()
                if base != raw:
                    plan.actions.append(Action("review", relative, "project-owned; see the diff in the report"))
                    plan.diffs[relative] = "".join(difflib.unified_diff(
                        base.decode("utf-8", "replace").splitlines(True),
                        raw.decode("utf-8", "replace").splitlines(True),
                        "installed baseline", "new scaffold version"))
                    plan.base_updates[relative] = raw
            else:
                plan.actions.append(Action("review", relative, "no stored baseline; compare manually"))
                plan.base_updates[relative] = raw
            continue
        data = inject_marker(relative, raw)
        new_sha = sha256(data)
        expected = old_files.get(relative, {}).get("sha256")
        info = {"sha256": new_sha, "locked": True}
        if not local.exists():
            plan.actions.append(Action("restore" if expected else "add", relative))
            plan.writes[relative] = (data, mode)
            plan.new_files[relative] = info
            continue
        local_sha = sha256(local.read_bytes())
        if expected is not None and local_sha == expected:
            if new_sha != expected:
                plan.actions.append(Action("update", relative))
                plan.writes[relative] = (data, mode)
            plan.new_files[relative] = info
        elif local_sha == new_sha:
            plan.new_files[relative] = info
        elif force_locked:
            plan.actions.append(Action("overwrite", relative, "locally modified; backed up first"))
            plan.writes[relative] = (data, mode)
            plan.backups.append(relative)
            plan.new_files[relative] = info
        else:
            plan.actions.append(Action(
                "conflict", relative, "locked file was modified locally; use --force-locked to overwrite"))
            if expected is not None:
                plan.new_files[relative] = old_files[relative]
    for relative in sorted(set(old_files) - current):
        plan.actions.append(Action("removed-upstream", relative, "no longer part of the scaffold; file kept"))
    return plan


def render_report(plan: UpdatePlan, applied: bool, source: Source) -> str:
    lines = [f"# Scaffold update report ({'applied' if applied else 'dry run'})", "",
             f"Source: {source.location}  ref: {source.ref or '-'}  commit: {source.commit or '-'}", ""]
    if not plan.actions:
        lines.append("Everything is up to date.")
    for action in plan.actions:
        lines.append(f"- {action.kind}: {action.path}" + (f" - {action.detail}" if action.detail else ""))
    for relative, diff in plan.diffs.items():
        lines += ["", f"## Changes to absorb manually: {relative}", "", "```diff", diff.rstrip("\n"), "```"]
    return "\n".join(lines) + "\n"


def _workspace_dirty(root: Path) -> bool:
    try:
        inside = _git("rev-parse", "--is-inside-work-tree", cwd=root)
    except ScaffoldError:
        return False
    return inside == "true" and bool(_git("status", "--porcelain", cwd=root))


def update(root: Path, source_arg: str | None, ref: str | None, apply: bool, force_locked: bool,
           allow_dirty: bool) -> tuple[UpdatePlan, str]:
    with open_source(source_arg, ref) as source:
        plan = plan_update(root, source, force_locked)
        report = render_report(plan, apply, source)
        if not apply:
            return plan, report
        if not allow_dirty and _workspace_dirty(root):
            raise ScaffoldError("The Git workspace has uncommitted changes; commit them first "
                                "(or pass --allow-dirty) so every change can be rolled back.")
        stamp = time.strftime("%Y%m%d-%H%M%S")
        for relative in plan.backups:
            backup = root / OVERWRITTEN_DIR / stamp / relative
            backup.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(root / relative, backup)
        for relative, (data, mode) in plan.writes.items():
            _write(root / relative, data, mode)
        for relative, raw in plan.base_updates.items():
            _write(root / BASE_DIR / relative, raw)
        _write_state(root, read_receipt(root)["project"], source, plan.new_files)
        _write(root / REPORT_PATH, report.encode("utf-8"))
        return plan, report


def verify(root: Path) -> list[Action]:
    receipt = read_receipt(root)
    problems: list[Action] = []
    for relative, info in sorted(receipt["files"].items()):
        if not info.get("locked"):
            continue
        path = root / relative
        if not path.is_file():
            problems.append(Action("missing", relative))
        elif sha256(path.read_bytes()) != info["sha256"]:
            problems.append(Action("modified", relative))
    return problems
