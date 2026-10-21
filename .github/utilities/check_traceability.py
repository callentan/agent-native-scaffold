"""Read-only owner coverage and exact-base dependency impact candidates."""

from __future__ import annotations

import argparse
from collections import defaultdict, deque
from collections.abc import Iterable
from dataclasses import asdict, replace
import hashlib
import json
from pathlib import Path
import re

from artifact_io import (
    Artifact, ArtifactInputError, PathInput, _ANCHOR, _parse_artifact_bytes,
    iter_markdown_lines,
)
from check_artifacts import (
    CheckReport, Finding, _HEADING, _PLACEHOLDER, _error, _write_report, read_inventory,
)


_KEY = r"(?:[A-Za-z0-9][A-Za-z0-9._-]*/){2}[A-Za-z0-9][A-Za-z0-9._-]*"
_ACCEPTANCE = re.compile(_KEY + r"#[A-Za-z][A-Za-z0-9._:-]*")
_TASK = re.compile(_KEY)
_LAYERS = {
    "Business acceptance": "business", "Software behavior": "software",
    "Applicable design verification": "design", "Standalone maintenance or document check": "maintenance",
}
_OWNER_LAYERS = {
    **dict.fromkeys(("stakeholder-requirement", "use-case", "invariant",
                     "quality-attribute-scenario", "domain-model"), "business"),
    "software-requirement": "software",
    **dict.fromkeys(("architecture-building-block", "architecture-decision",
                     "architecture-specification", "sequence-diagram",
                     "published-interface"), "design"),
    **dict.fromkeys(("development-log", "backlog-item", "user-story",
                     "tool-qualification", "review-record"), "maintenance"),
}
_VT_FIELDS = ("Expected outcome and independent pass criterion for this target",
              "Corresponding method/steps or actual test identifier",
              "Preconditions, forbidden side effects, and open items")
_TS_FIELDS = ("Preconditions and inputs for this target",
              "Actions, observations, and independent pass criterion for this target",
              "Corresponding steps or actual test identifier",
              "Source navigation, open conditions, and forbidden side effects")
_GENERIC = re.compile(
    r"(?:all\s+(?:tests?\s+)?pass(?:ed)?|verify\s+all|(?:meets?|conforms?\s+to)\s+(?:the\s+)?requirements?|"
    r"as\s+required|see\s+(?:the\s+)?requirements?|same\s+as\s+above|pass|not[-\s]run|"
    r"to\s+be\s+confirmed|not\s+configured|n/?a|none|not\s+applicable)[.!\s]*", re.I,
)


def section_lines(artifact: Artifact, anchor: str) -> tuple[tuple[int, str], ...]:
    """A source-owned explicit-anchor section, ignoring literal code/comments."""
    entry = next((item for item in artifact.anchors if item.name == anchor), None)
    if entry is None:
        return ()
    result = []
    heading_level = None
    for number, line in iter_markdown_lines(artifact.body, artifact.body_start_line):
        if number <= entry.location.line or line is None:
            continue
        if _ANCHOR.fullmatch(line):
            break
        heading = _HEADING.fullmatch(line)
        if heading:
            if heading_level is not None and len(heading[1]) <= heading_level:
                break
            if heading_level is None:
                heading_level = len(heading[1])
        result.append((number, line))
    return tuple(result)


def _table_values(lines: Iterable[tuple[int, str]], field: str) -> list[tuple[int, str]]:
    values = []
    for number, line in lines:
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if line.lstrip().startswith("|") and len(cells) == 2 and cells[0] == field:
            values.append((number, cells[1]))
    return values


def _layer(artifact: Artifact) -> tuple[str | None, int]:
    if artifact.kind == "verification-test":
        values = _table_values(section_lines(artifact, "plan"), "Verification layer")
        layer = _LAYERS.get(values[0][1]) if len(values) == 1 else None
    elif artifact.kind == "validation-scenario":
        values = _table_values(section_lines(artifact, "basis"), "Business scope and scenario type")
        valid = len(values) == 1 and re.match(
            r"^(?:Within context|Cross-context|REQ business acceptance|QAS)(?:$|[:,; ])", values[0][1],
        )
        layer = "business" if valid and not _PLACEHOLDER.search(values[0][1]) else None
    else:
        values, layer = [], None
    return layer, values[0][0] if values else artifact.body_start_line


def _meaningful(value: str) -> bool:
    plain = re.sub(r"[*_`]", "", value).strip()
    return (len(re.sub(r"\W", "", plain)) >= 4 and not _GENERIC.fullmatch(plain)
            and not _PLACEHOLDER.search(plain))


def _criterion(artifact: Artifact, anchor: str) -> tuple[bool, tuple[str, ...]]:
    lines = section_lines(artifact, anchor)
    values = []
    if artifact.kind == "validation-scenario":
        for field in _TS_FIELDS:
            matches = [re.match(r"^\s*[-*] " + re.escape(field) + r":\s*(.+)$", line)
                       for _, line in lines]
            entries = [match[1] for match in matches if match]
            if len(entries) != 1 or not _meaningful(entries[0]):
                return False, ()
            values.append(entries[0])
    else:
        for field in _VT_FIELDS:
            entries = _table_values(lines, field)
            if len(entries) != 1 or not _meaningful(entries[0][1]):
                return False, ()
            values.append(entries[0][1])
    return True, tuple(" ".join(value.split()) for value in values)


def _merge(report: CheckReport, findings: list[Finding], *, input_error: bool = False) -> CheckReport:
    combined = tuple(sorted((*report.findings, *findings),
                            key=lambda f: (f.path, f.line, f.code, f.target or "")))
    status = ("input-error" if input_error or report.status == "input-error"
              else "invalid" if combined else report.status)
    return replace(report, status=status, findings=combined)


def _selection(values, root: PathInput, pattern: re.Pattern, known: set[str],
               prefix: str, *, allow_empty: bool = False) -> tuple[tuple[str, ...], list[Finding]]:
    def finding(code, target, message):
        return Finding(code, str(root), 1, None, target, message)
    if isinstance(values, (str, bytes)) or not isinstance(values, Iterable):
        return (), [finding(f"INVALID_{prefix}", None, "Supply an explicit collection, not a string/scalar")]
    selected, errors, seen = [], [], set()
    for value in values:
        if not isinstance(value, str) or not pattern.fullmatch(value):
            errors.append(finding(f"INVALID_{prefix}_ID", str(value), "Use a complete canonical identity"))
        elif value in seen:
            errors.append(finding(f"DUPLICATE_{prefix}_ID", value, "Requested identity is repeated"))
        else:
            seen.add(value)
            if value not in known:
                errors.append(finding(f"UNKNOWN_{prefix}_ID", value, "Requested identity is not in the complete actual inventory"))
            else:
                selected.append(value)
    if not selected and not errors and not allow_empty:
        errors.append(finding(f"EMPTY_{prefix}", None, "An explicit complete nonempty selection is required"))
    return tuple(sorted(selected)), errors


def trace_report(root: PathInput, delivery_ids) -> CheckReport:
    """Check the explicitly complete delivery against ALL actual plan targets."""
    return _trace_inventory(read_inventory(root), delivery_ids)


def _trace_inventory(inventory, delivery_ids, *, allow_empty: bool = False) -> CheckReport:
    """Reuse one acquired snapshot; only the full-inventory hook allows no ACs."""
    report = inventory.report
    if report.status == "input-error":
        return report  # Missing primary input cannot manufacture coverage findings.
    root = report.baseline.root
    owners = {artifact.key: artifact for artifact in inventory.artifacts}
    acceptances = {entry.reference: entry for artifact in inventory.artifacts for entry in artifact.acceptances}
    selected, errors = _selection(delivery_ids, root, _ACCEPTANCE, set(acceptances), "DELIVERY",
                                  allow_empty=allow_empty)
    if errors:
        return _merge(report, errors, input_error=True)
    covered: set[str] = set()
    findings: list[Finding] = []
    for artifact in inventory.artifacts:
        layer, layer_line = _layer(artifact)
        anchor_targets: dict[str, set[str]] = defaultdict(set)
        signatures: dict[tuple[str, ...], set[str]] = defaultdict(set)
        criteria = {}
        for target in artifact.targets:
            anchor_targets[target.criterion_anchor].add(target.target)
            valid, signature = _criterion(artifact, target.criterion_anchor)
            criteria[target.criterion_anchor] = valid, signature
            if valid:
                signatures[signature].add(target.target)
        for target in artifact.targets:
            valid_target = True
            def add(code: str, message: str, line: int = target.location.line) -> None:
                nonlocal valid_target
                valid_target = False
                findings.append(Finding(code, str(artifact.path), line, artifact.key, target.target, message))
            owner_key, anchor = target.target.split("#")
            owner = owners.get(owner_key)
            if owner is None or anchor not in {a.name for a in owner.anchors}:
                add("DANGLING_TARGET", "Target owner or explicit anchor is absent")
            elif target.target not in acceptances:
                add("TARGET_NOT_ACCEPTANCE", "A normal anchor is not an owner AC/VC acceptance")
            if artifact.kind not in ("verification-test", "validation-scenario"):
                add("INVALID_TARGET_SOURCE", "Coverage requires an actual VT or TS plan")
            elif layer is None:
                add("UNKNOWN_VALIDATION_LAYER", "Missing, ambiguous or unsupported declaration in the plan/basis table", layer_line)
            elif owner is not None:
                expected = _OWNER_LAYERS.get(owner.kind)
                if expected is None:
                    add("UNKNOWN_TARGET_LAYER", f"No declared layer rule for owner kind {owner.kind}")
                elif expected != layer:
                    add("LAYER_MISMATCH", f"Plan declares {layer}; owner {owner.kind} requires {expected}", layer_line)
            meaningful, signature = criteria[target.criterion_anchor]
            if not meaningful:
                add("INSUFFICIENT_CRITERION", "Independent expected observation, method and constraints are required",
                    target.criterion_location.line)
            elif len(anchor_targets[target.criterion_anchor]) > 1 or len(signatures[signature]) > 1:
                add("SHARED_CRITERION", "Different targets need independent criterion content",
                    target.criterion_location.line)
            if valid_target:
                covered.add(target.target)
    for reference in selected:
        if reference not in covered:
            item = acceptances[reference]
            findings.append(Finding(
                "UNCOVERED_ACCEPTANCE", str(item.location.path), item.location.line,
                item.owner, reference, "Requested owner acceptance has no structurally sufficient compatible plan target",
            ))
    return _merge(report, findings)


def impact_report(root: PathInput, base_sha: str, task_ids=()) -> dict:
    """Conservative canonical dependency candidates; no semantic/execution verdict."""
    if base_sha is None:
        error = ArtifactInputError("INVALID_BASE", str(root), 1, "Impact requires an explicit exact Git commit base")
        result = CheckReport("input-error", (_error(error),), 0, None, (), 0).to_dict()
        result.update(changed_sources=[], candidates=[], task_ids=[])
        return result
    inventory = read_inventory(root, base_sha)
    report = inventory.report
    result = report.to_dict()
    result.update(changed_sources=[], candidates=[], task_ids=[])
    if report.baseline is None:
        return result
    actual_root = Path(report.baseline.root)
    current = {a.key: a for a in inventory.artifacts}
    historical: dict[str, Artifact] = {}
    errors: list[Finding] = []
    old_bytes = dict(inventory.base_raw_files)
    for record in report.baseline.base_files:
        if not record.formal:
            continue
        try:
            artifact = _parse_artifact_bytes(old_bytes[record.path], actual_root / record.path, actual_root)
            if artifact.key in historical:
                raise ArtifactInputError("DUPLICATE_ARTIFACT_ID", artifact.path,
                                         artifact.id_location.line, f"Duplicate historical {artifact.key}")
            historical[artifact.key] = artifact
        except ArtifactInputError as error:
            errors.append(Finding("HISTORICAL_INPUT_ERROR", str(error.path), error.line,
                                  None, None, f"{error.code}: {error.message}"))
    tasks, invalid_tasks = _selection(task_ids, root, _TASK, set(current) | set(historical), "TASK", allow_empty=True)
    errors.extend(invalid_tasks)
    report = _merge(report, errors, input_error=bool(errors))
    new_bytes = dict(inventory.raw_files)

    def identity(artifact, snapshot):
        if artifact is None:
            return None
        raw = old_bytes[artifact.relative_path] if snapshot == "base" else new_bytes[artifact.path]
        return {"key": artifact.key, "path": artifact.relative_path, "sha256": hashlib.sha256(raw).hexdigest()}

    old_paths = {a.relative_path: a for a in historical.values()}
    new_paths = {a.relative_path: a for a in current.values()}
    seeds = set()
    changes = []
    for change in report.baseline.changes:
        before, after = old_paths.get(change.path), new_paths.get(change.path)
        seeds.update(a.key for a in (before, after) if a is not None)
        changes.append(dict(asdict(change), before=identity(before, "base"), after=identity(after, "current")))
    edges: dict[str, list[dict]] = defaultdict(list)
    for snapshot, artifacts in (("base", historical), ("current", current)):
        for artifact in artifacts.values():
            locations = dict(artifact.metadata_locations)
            dependencies = [(ref, "upstream", locations[("upstream", index)].line)
                            for index, ref in enumerate(artifact.upstream)]
            dependencies.extend((t.target, "target", t.location.line) for t in artifact.targets)
            for reference, relation, line in dependencies:
                source = reference.split("#")[0]
                edges[source].append({"consumer": artifact.key, "source": source, "reference": reference,
                                      "relation": relation, "path": artifact.relative_path, "line": line,
                                      "snapshot": snapshot})
    reachable = set(seeds)
    pending = deque(sorted(seeds))
    while pending:
        source = pending.popleft()
        for edge in edges[source]:
            if edge["consumer"] not in reachable:
                reachable.add(edge["consumer"])
                pending.append(edge["consumer"])
    candidates = []
    for key in sorted(reachable - seeds):
        reasons = [edge for source in sorted(reachable) for edge in edges[source] if edge["consumer"] == key]
        candidates.append({
            "key": key, "before": identity(historical.get(key), "base"),
            "after": identity(current.get(key), "current"), "requested_task": key in tasks,
            "reasons": sorted(reasons, key=lambda r: (r["source"], r["path"], r["line"], r["snapshot"], r["reference"])),
        })
    result = report.to_dict()
    result.update(changed_sources=changes, candidates=candidates, task_ids=list(tasks))
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--delivery", action="append")
    mode.add_argument("--base")
    parser.add_argument("--task", action="append", default=[])
    parser.add_argument("--report")
    arguments = parser.parse_args()
    if arguments.task and arguments.base is None:
        parser.error("--task requires --base impact mode")
    if arguments.base is not None:
        payload = impact_report(arguments.root, arguments.base, arguments.task)
    else:
        payload = trace_report(arguments.root, arguments.delivery).to_dict()
        payload["delivery_ids"] = arguments.delivery
    if arguments.report is not None:
        try:
            _write_report(payload, arguments.report, arguments.root)
        except ArtifactInputError as error:
            payload["status"] = "input-error"
            payload["findings"] = [*payload["findings"], asdict(_error(error))]
            payload["report_output"] = {"path": str(error.path), "written": False}
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return {"clean": 0, "empty": 0, "invalid": 1, "input-error": 2}[payload["status"]]


if __name__ == "__main__":
    raise SystemExit(main())
