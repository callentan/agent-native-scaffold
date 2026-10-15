"""Real, isolated filesystem/Git fixtures. No production parsing in expectations."""

from __future__ import annotations

import os
import subprocess
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, Sequence

import yaml


WORKTREE = Path(__file__).resolve().parents[3]
CONTRACTS = WORKTREE / ".github" / "contracts"

# Independent inventory from the approved specification, not the implementation.
KINDS = (
    "domain-model", "subdomain", "bounded-context", "capability", "use-case",
    "invariant", "validation-scenario", "backlog-item", "stakeholder-requirement",
    "software-requirement", "user-story", "architecture-building-block",
    "architecture-decision", "verification-test", "review-record",
    "tool-qualification", "development-log", "quality-attribute-scenario",
    "context-map", "published-interface", "aggregate", "entity", "value-object",
    "factory", "domain-service", "policy", "domain-event", "integration-partner",
    "intended-use", "risk-control", "architecture-specification", "sequence-diagram",
)
VIEW_NAMES = (
    "requirements", "stories", "architecture", "sequences", "verification",
    "quality", "governance", "risk", "release",
)


def temporary_workspace() -> tempfile.TemporaryDirectory:
    """Keep test writes inside this checkout's ignored, authorized tool environment."""
    return tempfile.TemporaryDirectory(prefix="task2-fixture-", dir=WORKTREE / ".venv")


def metadata(**changes: object) -> dict:
    result = {
        "schemaVersion": 1,
        "id": "REQ-001",
        "kind": "stakeholder-requirement",
        "scope": "sample/CTX-001",
        "contentState": "draft",
    }
    result.update(changes)
    return result


def write_metadata(
    root: Path,
    data: dict,
    body: str = "# Requirement\n",
    relative_path: str = "REQ-001.md",
    *,
    newline: str = "\n",
    bom: bool = False,
) -> Path:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    text = "---\n" + yaml.safe_dump(data, sort_keys=False, allow_unicode=True) + "---\n" + body
    path.write_bytes(text.replace("\n", newline).encode("utf-8-sig" if bom else "utf-8"))
    return path


def write_artifact(
    root: Path,
    schema_version: int = 1,
    id: str = "REQ-001",
    scope: str = "sample/CTX-001",
    kind: str = "stakeholder-requirement",
    upstream: Sequence[str] | None = None,
    targets: Sequence[dict] | None = None,
    acceptance_ids: Sequence[str] = (),
    *,
    relative_path: str | None = None,
) -> Path:
    data = metadata(schemaVersion=schema_version, id=id, scope=scope, kind=kind)
    if upstream is not None:
        data["upstream"] = list(upstream)
    if targets is not None:
        data["targets"] = list(targets)
    body = f"# {id}：本地夹具\n\n"
    for acceptance_id in acceptance_ids:
        body += f'<a id="{acceptance_id.lower()}"></a>\n### {acceptance_id}：判据\n\n'
    return write_metadata(root, data, body, relative_path or f"{id}.md")


def git(root: Path, *arguments: str) -> str:
    # No inherited repository/index, global hooks, signing or network operations.
    env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    env.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")
    result = subprocess.run(
        ["git", "--no-pager", "-c", "core.autocrlf=false",
         "-c", "commit.gpgSign=false", "-c", "user.name=Local fixture",
         "-c", "user.email=fixture@example.invalid", *arguments],
        cwd=root, env=env, shell=False, capture_output=True, text=True, encoding="utf-8",
    )
    if result.returncode:
        raise AssertionError(
            f"Git fixture failed ({result.returncode}): {arguments!r}\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
    return result.stdout.strip()


def seed_git_repo(root: Path) -> str:
    root.mkdir(parents=True, exist_ok=True)
    git(root, "init", "--quiet", "--template=")
    (root / "README.md").write_text("# Local baseline fixture\n", encoding="utf-8")
    git(root, "add", "--", "README.md")
    git(root, "commit", "--quiet", "-m", "Seed local fixture")
    return git(root, "rev-parse", "HEAD")


@contextmanager
def directory_link(link: Path, target: Path) -> Iterator[Path]:
    """Windows junctions need no symlink privilege; failure is a test ERROR, not skip."""
    if os.name == "nt":
        env = dict(os.environ, TASK2_LINK=str(link), TASK2_TARGET=str(target))
        result = subprocess.run(
            ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command",
             "$ErrorActionPreference='Stop'; "
             "$item = New-Item -ItemType Junction -Path $env:TASK2_LINK "
             "-Target $env:TASK2_TARGET; $item.FullName"],
            cwd=link.parent, env=env, shell=False, capture_output=True,
        )
        if result.returncode:
            raise RuntimeError(
                f"JUNCTION_UNAVAILABLE ({result.returncode}): "
                f"{result.stdout!r} {result.stderr!r}"
            )
    else:
        link.symlink_to(target, target_is_directory=True)
    try:
        if link.resolve() != target.resolve():
            raise AssertionError("Filesystem link did not resolve to the fixture target")
        yield link
    finally:
        if os.name == "nt":
            link.rmdir()  # Remove the junction, never the target tree.
        else:
            link.unlink()
