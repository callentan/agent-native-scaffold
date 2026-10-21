"""Real, isolated filesystem/Git fixtures. No production parsing in expectations."""

from __future__ import annotations

import hashlib
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
    """Use the host's temporary directory, independent of the checkout and venv."""
    temporary = tempfile.TemporaryDirectory(prefix="ddd-fixture-")
    temporary.name = str(Path(temporary.name).resolve())
    return temporary


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
    body = f"# {id}: Local fixture\n\n"
    for acceptance_id in acceptance_ids:
        body += f'<a id="{acceptance_id.lower()}"></a>\n### {acceptance_id}: Criterion\n\n'
    return write_metadata(root, data, body, relative_path or f"{id}.md")


def criterion_block(anchor: str, expected: str, method: str, constraints: str) -> str:
    """An actual VT-form criterion, not an expected value derived from a tool."""
    return (
        f'<a id="{anchor}"></a>\n### {anchor}\n\n'
        "| Criterion information for this target | Content |\n|---|---|\n"
        f"| Expected outcome and independent pass criterion for this target | {expected} |\n"
        f"| Corresponding method/steps or actual test identifier | {method} |\n"
        f"| Preconditions, forbidden side effects, and open items | {constraints} |\n\n"
    )


def write_delivery_fixture(root: Path, omit_software_reject: bool = False) -> tuple[str, ...]:
    """Task7's four source-owned acceptances; omission changes ONLY software VT."""
    delivery = (
        "sample/CTX-001/REQ-001#req-001-ac-01",
        "sample/CTX-001/REQ-001#req-001-ac-02",
        "sample/CTX-001/SR-001#sr-001-ac-01",
        "sample/CTX-001/SR-001#sr-001-ac-02",
    )
    write_metadata(root, metadata(id="DM-001", kind="domain-model"),
                   '# DM-001: Borrowing rules\n\n<a id="rule-001"></a>\n## RULE-001: Allowance\n'
                   'Allowance limit: 2\n\nMembership is valid; eligibility expiry and the concurrency policy '
                   'are not yet determined.\n',
                   "domain-model/DM-001.md")
    write_metadata(
        root, metadata(upstream=["sample/CTX-001/DM-001#rule-001"]),
        '# REQ-001: Borrowing business\n\n<a id="req-001-ac-01"></a>\n'
        '### REQ-001-AC-01: Allow borrowing\n\n'
        'A valid member can complete a loan within the source rule allowance.\n\n'
        '<a id="req-001-ac-02"></a>\n### REQ-001-AC-02: Reject over-allowance\n\n'
        'Beyond the source rule allowance, no new business loan may be created.\n',
        "stakeholder-requirements/REQ-001.md",
    )
    write_metadata(
        root, metadata(id="SR-001", kind="software-requirement", upstream=list(delivery[:2])),
        '# SR-001: Software borrowing behavior\n\n<a id="sr-001-ac-01"></a>\n'
        '### SR-001-AC-01: Record an allowed request\n\n'
        'A submission within the source rule allowance adds one loan record.\n\n'
        '<a id="sr-001-ac-02"></a>\n### SR-001-AC-02: Rejected request has no side effects\n\n'
        'A submission over the allowance returns a rejection and leaves loan records unchanged.\n',
        "software-requirements/SR-001.md",
    )
    business = [
        {"target": delivery[0], "criterionAnchor": "allow"},
        {"target": delivery[1], "criterionAnchor": "reject"},
    ]
    software = [
        {"target": delivery[2], "criterionAnchor": "record"},
        {"target": delivery[3], "criterionAnchor": "no-write"},
    ]
    plans = (
        ("VT-001", "Business acceptance", business,
         criterion_block("allow", "A member within the allowance obtains one new loan.",
                         "Prepare a within-allowance state per the rule, borrow, "
                         "and observe the business register.",
                         "Eligibility is already valid; the still-unknown expiry "
                         "and concurrency policies are not decided.")
         + criterion_block("reject", "A member over the allowance does not obtain a new loan.",
                           "Prepare a member already at the allowance, apply again, "
                           "and observe the business register after the rejection.",
                           "Must not decrease or increase loans of other members; "
                           "the concurrency policy is undefined.")),
        ("VT-002", "Software behavior", software[:1] if omit_software_reject else software,
         criterion_block("record", "A valid request adds one record linked to the member.",
                         "Send a within-allowance submission and read the record set "
                         "before and after the operation.",
                         "Eligibility is fixed as valid; the unknown eligibility-expiry "
                         "branch is not asserted.")
         + ("" if omit_software_reject else
            criterion_block("no-write", "An over-allowance request returns a rejection "
                            "and the records before and after are identical.",
                            "Send a request over the allowance; compare the response "
                            "and the records before and after the submission.",
                            "Adding or modifying any loan is forbidden; the concurrency "
                            "policy still awaits clarification from the source."))),
    )
    for identifier, layer, targets, criteria in plans:
        write_metadata(
            root, metadata(id=identifier, kind="verification-test", targets=targets),
            f'# {identifier}: Independent verification plan\n\n<a id="plan"></a>\n## Plan and layer\n\n'
            f'| Field | Content |\n|---|---|\n| Verification layer | {layer} |\n\n'
            '<a id="targets"></a>\n## Per-target criteria\n\n' + criteria
            + '<a id="runs"></a>\n## Actual runs\n\n'
            'not-run: no business or software execution environment yet.\n',
            f"verification/{identifier}.md",
        )
    return delivery


def source_bytes(root: Path, *, include_git: bool = True) -> dict[str, bytes]:
    result = {}
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(root).as_posix()
        if not include_git and (relative == ".git" or relative.startswith(".git/")):
            continue
        result[relative] = path.read_bytes()
    return result


def git(root: Path, *arguments: str) -> str:
    # No inherited repository/index, global hooks, signing or network operations.
    from check_artifacts import _git_environment
    result = subprocess.run(
        ["git", "--no-pager", "-c", "core.autocrlf=false",
         "-c", "commit.gpgSign=false", "-c", "user.name=Local fixture",
         "-c", "user.email=fixture@example.invalid", *arguments],
        cwd=root, env=_git_environment(), shell=False, capture_output=True, text=True, encoding="utf-8",
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


def seed_implementation_fixture(root: Path) -> str:
    """Task8: commit four acceptances, two plans and self-owned TEXT locators.

    No application/runner is created or run. Synthetic VT results are appended
    separately AFTER this object by individual collector behavior tests.
    """
    root.mkdir(parents=True, exist_ok=True)
    seed_git_repo(root)
    targets = write_delivery_fixture(root)
    vt = root / "verification/VT-002.md"
    _, frontmatter, body = vt.read_text(encoding="utf-8").split("---", 2)
    data = yaml.safe_load(frontmatter)
    for target, test_id in zip(data["targets"], ("test_record", "test_no_write")):
        target["testId"] = test_id
    write_metadata(root, data, body.lstrip("\n"), "verification/VT-002.md")
    (root / "docs").mkdir()
    (root / "docs/development.md").write_text(
        '# Fixture registration\n<a id="project-registration"></a>\n## Text only\n'
        'Collector locator fixture; there is no application or runnable business test.\n',
        encoding="utf-8", newline="\n",
    )
    domain = root / "domain-model/DM-001.md"
    config = {
        "schemaVersion": 1, "projectId": "sample", "boundedContexts": [{"id": "CTX-001"}],
        "domainSources": [{"id": "owned-domain", "kind": "local", "root": ".",
                           "path": "domain-model/DM-001.md",
                           "baseline": "sha256:" + hashlib.sha256(domain.read_bytes()).hexdigest(),
                           "readOnly": True}],
        "developmentRegistration": "docs/development.md#project-registration",
    }
    (root / "bc-config.yaml").write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")
    (root / "source code").mkdir()
    (root / "native tests").mkdir()
    (root / "source code/заем€.txt").write_text(
        "# TEXT LOCATORS ONLY; not an application.\n"
        f"# implements: {targets[2]} symbol=record\nrecord(): owned text location\n"
        f"// implements: {targets[3]} symbol=reject\nreject(): owned text location\n",
        encoding="utf-8", newline="\n",
    )
    (root / "native tests/проверка€.txt").write_text(
        "# TEXT LOCATORS ONLY; not discovered or executed by any runner.\n"
        f"# verifies: {targets[2]} testId=test_record\ntest_record(): owned text location\n"
        f"// verifies: {targets[3]} testId=test_no_write\ntest_no_write(): owned text location\n",
        encoding="utf-8", newline="\n",
    )
    git(root, "add", "--", ".")
    git(root, "commit", "--quiet", "-m", "Task8 self-owned text and plan fixture")
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
