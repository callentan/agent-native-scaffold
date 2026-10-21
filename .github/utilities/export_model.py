"""Deterministic read-only model derivation, optional local sources and drift checks."""

from __future__ import annotations

import argparse
from dataclasses import asdict, replace
import json
from pathlib import Path
import re
from typing import Any

import yaml

from artifact_io import (
    _sha, Artifact, ArtifactInputError, PathInput, _artifact_validator, _resolve_file,
    _schema_validator, load_yaml_mapping, section_fences,
)
from check_artifacts import (
    CheckReport, Finding, Inventory, _anchors, _baseline, _decode, _domain_location, _error, _exclusion,
    _fixed_file, _local_root, _network_path, _output_path, _read, _write_new, read_inventory,
)
from check_traceability import _meaningful, _table_values, section_lines
from vt_records import owned_runs as _owned_runs, result_rows


_SCOPE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*/[A-Za-z0-9][A-Za-z0-9._-]*")
_REFERENCE = re.compile(r"(?:[A-Za-z0-9][A-Za-z0-9._-]*/){2}[A-Za-z0-9][A-Za-z0-9._-]*#[A-Za-z][A-Za-z0-9._:-]*")
_FIXED = re.compile(r"(?:[0-9a-f]{40}|[0-9a-f]{64}|sha256:[0-9a-f]{64})")
_SUMMARY = {
    "requirements": "srSummary", "stories": "storySummary", "architecture": "abbSummary",
    "sequences": "sequenceSummary", "verification": "verificationSummary", "quality": "quality",
    "governance": "governanceSummary", "risk": "riskSummary", "release": "releaseStatus",
}
_KINDS = {
    "requirements": {"stakeholder-requirement", "software-requirement", "use-case"},
    "stories": {"software-requirement", "user-story"},
    "architecture": {"architecture-building-block", "architecture-decision", "integration-partner"},
    "sequences": {"sequence-diagram", "use-case", "architecture-building-block", "integration-partner"},
    "verification": {"verification-test", "validation-scenario", "user-story",
                     "stakeholder-requirement", "software-requirement"},
    "quality": {"quality-attribute-scenario", "stakeholder-requirement", "validation-scenario", "verification-test"},
    "governance": {"review-record", "tool-qualification", "stakeholder-requirement"},
    "risk": {"domain-model", "intended-use", "risk-control", "stakeholder-requirement", "verification-test"},
    "release": {"development-log", "bounded-context"},
}
_DIRECT_REQUIRED = {
    "requirements": {"stakeholder-requirement", "software-requirement", "use-case"},
    "stories": {"user-story", "software-requirement"},
    "architecture": {"architecture-building-block", "architecture-decision"},
    "sequences": {"sequence-diagram", "use-case", "architecture-building-block"},
    "verification": {"verification-test", "software-requirement", "stakeholder-requirement"},
    "quality": {"quality-attribute-scenario", "stakeholder-requirement"},
    "governance": {"review-record"}, "risk": {"risk-control", "stakeholder-requirement", "verification-test"},
    "release": {"development-log"},
}
_SECTIONS = {
    "user-story": ("task", "checklist"), "architecture-building-block": ("structure", "interfaces", "runtime"),
    "architecture-decision": ("decision",), "sequence-diagram": ("basis", "participants", "paths", "diagram"),
    "verification-test": ("plan", "targets", "runs"),
    "quality-attribute-scenario": ("scenario", "measurement"),
    "review-record": ("decision",), "risk-control": ("analysis", "control", "residual"),
    "development-log": ("release", "change-control"),
}
# Closed adapters for source-owned summaries, NOT extensible plugins or result models.
_ENTRY_FIELDS = {
    "requirements": {"reqId": "ref", "srIds": "refs+", "ucId": "ref", "status": "text", "notes": "text"},
    "stories": {"srId": "ref", "usIds": "refs+", "status": "text"},
    "architecture": {"abbId": "ref", "adrRef": "ref"},
    "sequences": {"seqId": "ref", "ucId": "ref", "title": "text", "hasAsync": "bool",
                  "externalPartners": "refs", "status": "text"},
    "verification": {"usId": "ref", "vtIds": "refs+", "result": "text", "automatedCount": "count",
                     "manualCount": "count", "notes": "text"},
    "governance": {"govId": "ref", "status": "text", "ref": "evidence", "notes": "text"},
    "risk": {"riskId": "ref", "title": "text", "preMitigationLevel": "text", "rcIds": "refs",
             "residualRiskLevel": "text", "reqIds": "refs", "vtCoverage": "refs", "status": "text"},
}
_ROOT_FIELDS = {
    "requirements": {"srVersion": "text"}, "stories": {"storyVersion": "text"},
    "architecture": {"abbVersion": "text", "language": "text", "framework": "text", "integrations": "refs"},
    "sequences": {"seqVersion": "text"},
    "verification": {"vtVersion": "text", "lastRunDate": "text"},
    "quality": {"qasRefs": "refs+", "utilityTree": "evidence", "testScenarios": "mixed+"},
    "governance": {"govVersion": "text"}, "risk": {"riskVersion": "text"},
    "release": {"lifecycle": "text", "safetyClass": "text", "currentVersion": "text",
                "lastReleaseDate": "text", "nextPlannedRelease": "text", "changeControlRef": "evidence"},
}
_ROLE_KINDS = {
    "reqId": {"stakeholder-requirement"}, "reqIds": {"stakeholder-requirement"},
    "srId": {"software-requirement"}, "srIds": {"software-requirement"},
    "ucId": {"use-case"}, "usId": {"user-story"}, "usIds": {"user-story"},
    "abbId": {"architecture-building-block"}, "adrRef": {"architecture-decision"},
    "seqId": {"sequence-diagram"}, "externalPartners": {"integration-partner"},
    "integrations": {"integration-partner"}, "vtIds": {"verification-test"},
    "vtCoverage": {"verification-test", "validation-scenario"},
    "qasRefs": {"quality-attribute-scenario"}, "testScenarios": {"validation-scenario", "verification-test"},
    "govId": {"review-record", "tool-qualification"}, "waiverRefs": {"review-record"},
    "riskId": {"domain-model", "intended-use", "risk-control"}, "rcIds": {"risk-control"},
    "releaseRef": {"development-log"}, "bcRefs": {"bounded-context"},
}
_DIRECT_VALUES = {
    ("stories", "user-story"): (
        ("task", "status", ("Task progress", "status"), "text"),
    ),
    ("architecture", "architecture-building-block"): (
        ("runtime", "language", ("language", "Implementation language"), "text"),
        ("runtime", "framework", ("framework", "Framework"), "text"),
    ),
    ("sequences", "sequence-diagram"): (
        ("paths", "hasAsync", ("hasAsync", "Asynchronous interaction"), "bool"),
        ("participants", "externalPartners", ("externalPartners", "External partners"), "text"),
    ),
    ("verification", "verification-test"): (
        ("runs", "lastRunDate", ("lastRunDate", "Date, executor, and mode"), "text"),
        ("runs", "result", ("result", "Actual result"), "text"),
        ("runs", "automatedCount", ("automatedCount", "Automated check count"), "count"),
        ("runs", "manualCount", ("manualCount", "Manual check count"), "count"),
        ("runs", "notes", ("notes", "Report accessibility and limitations"), "text"),
    ),
    ("quality", "quality-attribute-scenario"): (
        ("scenario", "stimulusSource", ("stimulusSource", "Source of stimulus: who or what initiates it"), "text"),
        ("scenario", "stimulus", ("stimulus", "Stimulus: what happens"), "text"),
        ("scenario", "environment", ("environment", "Environment: under which operational or business conditions"), "text"),
        ("scenario", "object", ("object", "Object: which business process or affected object"), "text"),
        ("scenario", "response", ("response", "Response: what should be observed"), "text"),
        ("scenario", "responseMeasure", ("responseMeasure", "Response measure: measurable criterion, unit, and scope"), "text"),
    ),
    ("governance", "review-record"): (
        ("decision", "status", ("status", "Review conclusion"), "text"),
        ("decision", "notes", ("notes", "Limitations and notes"), "text"),
    ),
    ("risk", "risk-control"): (
        ("analysis", "preMitigationLevel", ("preMitigationLevel", "Pre-mitigation risk"), "text"),
        ("residual", "residualRiskLevel", ("residualRiskLevel", "Residual risk"), "text"),
    ),
    ("release", "development-log"): tuple(
        ("release", name, (name,), "text")
        for name in ("lifecycle", "safetyClass", "currentVersion", "lastReleaseDate", "nextPlannedRelease")
    ),
}


def _ordered(data: dict) -> dict:
    return json.loads(json.dumps(data, ensure_ascii=False, sort_keys=True))


def _required_inventory(inventory: Inventory, scope: str) -> None:
    report = inventory.report
    if report.status in ("input-error", "invalid"):
        item = report.findings[0]
        raise ArtifactInputError(item.code, item.path, item.line, item.message)
    if not isinstance(scope, str) or not _SCOPE.fullmatch(scope):
        raise ArtifactInputError("INVALID_SCOPE", report.baseline.root, 1, "Select an explicit project/context")
    if scope not in {artifact.scope for artifact in inventory.artifacts}:
        raise ArtifactInputError("UNKNOWN_SCOPE", report.baseline.root, 1, f"No formal artifacts for {scope}")
    owners = {a.key: a for a in inventory.artifacts}
    for artifact in inventory.artifacts:
        locations = dict(artifact.metadata_locations)
        refs = [(value, locations[("upstream", index)].line) for index, value in enumerate(artifact.upstream)]
        refs.extend((target.target, target.location.line) for target in artifact.targets)
        for reference, line in refs:
            owner, _, anchor = reference.partition("#")
            source = owners.get(owner)
            if source is None or anchor and anchor not in {a.name for a in source.anchors}:
                raise ArtifactInputError("DANGLING_REFERENCE", artifact.path, line, f"Unresolved formal reference: {reference}")


class _Sources:
    """One derivation's local read set, concrete validators and reference checks."""

    def __init__(self, inventory: Inventory) -> None:
        self.inventory = inventory
        self.root = Path(inventory.report.baseline.root)
        self.raw = dict(inventory.raw_files)
        self.records = {self.root / item.path: item for item in inventory.report.baseline.files}
        self.owners = {a.key: a for a in inventory.artifacts}
        self.artifacts = {a.path: a for a in inventory.artifacts}
        self.contracts = {}
        self.validators = {}
        self.failures: set[tuple[str, str]] = set()
        self.reserved_paths = {self.root / "model-sources.yaml"}
        self.reserved_directories: set[Path] = set()
        self.implementation_reports: dict[tuple[str, str], dict] = {}
        self.reservation_errors: set[str] = set()
        self.selection = "absent"
        self.verified: set[tuple[Path, str, str]] = set()
        for name in ("artifact", "model", "model-sources"):
            path = Path(__file__).resolve().parents[1] / "contracts" / (name + ".schema.json")
            try:
                raw = path.read_bytes()
            except OSError as error:
                raise ArtifactInputError("CONTRACT_ERROR", path, 1, str(error)) from error
            self.validators[name] = _schema_validator(raw, path)
            self.contracts[path.name] = _sha(raw)
        if self.validators["artifact"].schema != _artifact_validator().schema:
            raise ArtifactInputError("CONTRACT_ERROR", self.root, 1, "Artifact schema changed after parser cache load; use a new process")

    def reserve(self, relative: str) -> Path:
        """Reserve a declared local path without requiring that it exists."""
        schema = self.validators["model-sources"].schema["$defs"]["source"]["properties"]["path"]
        if not isinstance(relative, str) or not self.validators["model-sources"].evolve(schema=schema).is_valid(relative):
            raise ArtifactInputError("INVALID_PATH", self.root, 1, "Source must name a local root-relative file")
        lexical = self.root / relative
        if _exclusion(relative) == "TOOL_DATA":
            raise ArtifactInputError("EXCLUDED_TARGET", lexical, 1, "Git, environment and dependencies are not sources")
        try:
            actual = lexical.resolve()
        except (OSError, ValueError, RuntimeError) as error:
            raise ArtifactInputError("INVALID_PATH", lexical, 1, str(error)) from error
        if not actual.is_relative_to(self.root):
            raise ArtifactInputError("OUTSIDE_ROOT", lexical, 1, "Declared source leaves the explicit root")
        if _exclusion(actual.relative_to(self.root).as_posix()) == "TOOL_DATA":
            raise ArtifactInputError("EXCLUDED_TARGET", actual, 1, "Resolved source is excluded tool data")
        self.reserved_paths.add(actual)
        return actual

    def path(self, relative: str) -> Path:
        # Registration precedes stat/read failure; path syntax and read permission
        # are still checked by the existing resolver, not granted by registration.
        return _resolve_file(self.reserve(relative), self.root)

    def reserve_declarations(self, data: dict) -> None:
        """Inspect the whole already-parsed document before the first dereference."""
        pending, visited = [(data, False)], set()
        while pending:
            node, domain_declaration = pending.pop()
            if domain_declaration and not isinstance(node, dict):
                self.reservation_errors.add("INVALID_PATH")
            identity = (id(node), domain_declaration)
            if not isinstance(node, (dict, list)) or identity in visited:
                continue
            visited.add(identity)
            if isinstance(node, list):
                pending.extend((item, False) for item in node)
                continue
            # Location protection is independent of evidence validity. A known
            # domainSources entry also keeps its context when root/path is absent
            # or when the same YAML node was already visited through another key.
            # Outside that context keep the established provenance shape:
            # ordinary business root/path keys alone do not declare a location.
            domain_location = domain_declaration or {"root", "path", "baseline"} <= node.keys()
            if domain_location:
                try:
                    _, path = _domain_location(self.root, node.get("root"), node.get("path"))
                    # The declaration may be a missing file or a directory.
                    # Reserve both the location and descendants before validation.
                    self.reserved_paths.add(path)
                    self.reserved_directories.add(path)
                except ArtifactInputError as error:
                    self.reservation_errors.add(error.code)
            # These are location declarations, not commands or a new data model.
            for field in ("reference", "path"):
                if field == "path" and domain_location:
                    continue
                value = node.get(field)
                if isinstance(value, str) and (field == "reference" or "baseline" in node):
                    try:
                        self.reserve(value.split("#", 1)[0] if field == "reference" else value)
                    except ArtifactInputError as error:
                        # Do not stop before later declarations. The source adapter
                        # still owns value validation; an unresolved location also
                        # prevents a writer from claiming output/source isolation.
                        self.reservation_errors.add(error.code)
            for field, value in node.items():
                if field == "domainSources":
                    if isinstance(value, list):
                        pending.extend((item, True) for item in value)
                    else:
                        self.reservation_errors.add("INVALID_PATH")
                        pending.append((value, True))  # Still preserve any resolvable location.
                else:
                    pending.append((value, False))

    def read(self, relative: str) -> tuple[Path, bytes]:
        path = self.path(relative)
        return path, _read(path, self.root, self.raw, self.records, "reference")

    def fixed(self, path: Path, raw: bytes, baseline: str) -> None:
        if not isinstance(baseline, str) or not _FIXED.fullmatch(baseline):
            raise ArtifactInputError("INVALID_BASE", path, 1, "A full local Git object or raw sha256 is required")
        identity = _sha(raw)
        if (path, baseline, identity) in self.verified:
            return
        _fixed_file(self.root, path, raw, baseline)
        self.verified.add((path, baseline, identity))

    def document(self, path: Path, raw: bytes) -> dict:
        data, _ = load_yaml_mapping(_decode(raw, path), path)
        self.reserve_declarations(data)
        if "views" in data and ("artifacts" in data or "source" in data):
            raise ArtifactInputError("DERIVED_SOURCE", path, 1, "A derived model is not an authoritative source")
        return data

    def manifest(self) -> dict | None:
        path = self.root / "model-sources.yaml"
        if not path.exists() and not path.is_symlink():
            return None
        try:
            path, raw = self.read("model-sources.yaml")
            data, _ = load_yaml_mapping(_decode(raw, path), path)
            if type(data.get("schemaVersion")) is not int or data["schemaVersion"] != 1:
                raise ArtifactInputError("UNSUPPORTED_SCHEMA_VERSION", path, 1, "Expected integer schemaVersion 1")
            violation = next(self.validators["model-sources"].iter_errors(data), None)
            if violation:
                raise ArtifactInputError("INVALID_METADATA", path, 1,
                                         f"Manifest schema violation at {list(violation.absolute_path)} ({violation.validator})")
            baselines = {}
            for views in data["scopes"].values():
                for refs in views.values():
                    paths = set()
                    for ref in refs:
                        # Strict resolution is deferred: a missing optional source is a gap.
                        actual = (self.root / ref["path"]).resolve()
                        if not actual.is_relative_to(self.root) or _exclusion(actual.relative_to(self.root).as_posix()) == "TOOL_DATA":
                            raise ArtifactInputError("OUTSIDE_ROOT", path, 1, "Source selection leaves allowed local data")
                        if actual == path or actual in paths:
                            raise ArtifactInputError("INVALID_METADATA", path, 1, "Self reference or duplicate path in view")
                        if actual in baselines and baselines[actual] != ref["baseline"]:
                            raise ArtifactInputError("INVALID_BASE", path, 1, "One source path has conflicting fixed baselines")
                        paths.add(actual)
                        baselines[actual] = ref["baseline"]
                        self.reserved_paths.add(actual)
            self.selection = "present"
            return data["scopes"]
        except ArtifactInputError as error:
            raise ArtifactInputError("INVALID_SOURCE_MANIFEST", path, error.line,
                                     f"{error.code}: {error.message}") from error
        except (OSError, ValueError, RuntimeError) as error:
            raise ArtifactInputError("INVALID_SOURCE_MANIFEST", path, 1, str(error)) from error

    def canonical(self, reference: str, field: str | None = None) -> Artifact:
        if not isinstance(reference, str) or not _REFERENCE.fullmatch(reference):
            raise ArtifactInputError("INVALID_REFERENCE", self.root, 1, "Use a complete scope/id#anchor")
        key, anchor = reference.split("#")
        artifact = self.owners.get(key)
        if artifact is None or anchor not in {a.name for a in artifact.anchors}:
            raise ArtifactInputError("DANGLING_REFERENCE", self.root, 1, "Source reference has no actual owner/anchor")
        if field in _ROLE_KINDS and artifact.kind not in _ROLE_KINDS[field]:
            raise ArtifactInputError("REFERENCE_KIND_MISMATCH", artifact.path, 1, f"{field} references an incompatible owner kind")
        return artifact

    def evidence(self, value: Any) -> dict:
        if not isinstance(value, dict) or set(value) != {"reference", "baseline"} or not isinstance(value["reference"], str):
            raise ArtifactInputError("INVALID_EVIDENCE", self.root, 1, "Evidence needs reference and fixed baseline only")
        relative, separator, fragment = value["reference"].partition("#")
        if separator and not re.fullmatch(r"[A-Za-z][A-Za-z0-9._:-]*", fragment):
            raise ArtifactInputError("INVALID_REFERENCE", self.root, 1, "Invalid evidence fragment")
        path, raw = self.read(relative)
        if path == (self.root / "model-sources.yaml").resolve():
            raise ArtifactInputError("DERIVED_SOURCE", path, 1, "The selection manifest is not view evidence")
        document = (self.document(path, raw) if path.suffix.lower() in (".json", ".yaml", ".yml") else None)
        self.fixed(path, raw, value["baseline"])
        if path.suffix.lower() in (".json", ".yaml", ".yml"):
            valid = not fragment or fragment in document
        elif path.suffix.lower() == ".md":
            valid = not fragment or fragment in _anchors(_decode(raw, path), self.artifacts.get(path))
        else:
            valid = not fragment
        if not valid:
            raise ArtifactInputError("BROKEN_ANCHOR", path, 1, "Evidence fragment is absent or unsupported")
        return dict(value)

    def expand(self, view: str, references: set[str]) -> tuple[set[str], set[str]]:
        """Follow actual declared relationships, keeping only this view's owner kinds."""
        pending = sorted({reference.split("#")[0] for reference in references})
        visited = set()
        while pending:
            key = pending.pop()
            if key in visited:
                continue
            visited.add(key)
            artifact = self.owners[key]
            dependencies = list(artifact.upstream) + [target.target for target in artifact.targets]
            if view == "quality" and artifact.kind == "quality-attribute-scenario":
                # testScenarios are owned by the actual TS/VT targets, not a duplicate QAS field.
                for candidate in self.owners.values():
                    if candidate.kind in ("validation-scenario", "verification-test"):
                        for target in candidate.targets:
                            if target.target.split("#")[0] == key:
                                dependencies.append(candidate.key + "#" + target.criterion_anchor)
            for dependency in dependencies:
                target_key, _, anchor = dependency.partition("#")
                target = self.owners.get(target_key)
                if target is None or target.kind not in _KINDS[view]:
                    continue
                selected = ([target.key + "#" + anchor] if anchor
                            else [a.reference for a in target.acceptances]
                            or [target.key + "#" + a.name for a in target.anchors])
                references.update(selected)
                if selected:
                    pending.append(target_key)
        return references, visited


def _summary_source(reader: _Sources, view: str, path: Path, raw: bytes, baseline: str,
                    data: dict | None = None) -> dict:
    container = _SUMMARY[view]
    data = reader.document(path, raw) if data is None else data
    if not isinstance(data.get(container), dict):
        raise ArtifactInputError("INVALID_OPTIONAL_SOURCE", path, 1, f"Expected {container} mapping")
    source = data[container]
    references: set[str] = set()
    evidence = [{"reference": path.relative_to(reader.root).as_posix() + "#" + container, "baseline": baseline}]
    gaps: list[str] = []

    def field(obj, key, kind, location):
        label = location + "." + key
        if key not in obj or obj[key] is None or obj[key] == "":
            gaps.append(f"{path.relative_to(reader.root).as_posix()}: missing {label}")
            return
        value = obj[key]
        if kind == "text":
            valid = isinstance(value, str)
            if valid and not value.strip():
                gaps.append(f"{path.relative_to(reader.root).as_posix()}: empty {label}")
        elif kind == "bool":
            valid = type(value) is bool
        elif kind == "count":
            valid = type(value) is int and value >= 0
        elif kind == "ref":
            reader.canonical(value, key)
            references.add(value)
            valid = True
        elif kind == "evidence":
            evidence.append(reader.evidence(value))
            valid = True
        else:
            valid = isinstance(value, list)
            if valid:
                if kind.endswith("+") and not value:
                    gaps.append(f"{path.relative_to(reader.root).as_posix()}: missing items in {label}")
                for item in value:
                    if kind.startswith("mixed") and isinstance(item, dict):
                        evidence.append(reader.evidence(item))
                    else:
                        reader.canonical(item, key)
                        references.add(item)
        if not valid:
            raise ArtifactInputError("INVALID_OPTIONAL_SOURCE", path, 1, f"Wrong source field type: {label}")

    def evidence_refs(obj):
        if "evidenceRefs" in obj:
            if not isinstance(obj["evidenceRefs"], list):
                raise ArtifactInputError("INVALID_OPTIONAL_SOURCE", path, 1, "evidenceRefs must be a list")
            evidence.extend(reader.evidence(item) for item in obj["evidenceRefs"])

    for key, kind in _ROOT_FIELDS[view].items():
        field(source, key, kind, container)
    evidence_refs(source)
    if view in _ENTRY_FIELDS:
        key = "blocks" if view == "architecture" else "entries"
        entries = source.get(key)
        if entries is None:
            gaps.append(f"{path.relative_to(reader.root).as_posix()}: missing {container}.{key}")
        elif not isinstance(entries, list) or any(not isinstance(item, dict) for item in entries):
            raise ArtifactInputError("INVALID_OPTIONAL_SOURCE", path, 1, f"{container}.{key} must contain objects")
        else:
            for index, entry in enumerate(entries):
                for name, kind in _ENTRY_FIELDS[view].items():
                    field(entry, name, kind, f"{container}.{key}[{index}]")
                if view == "governance":
                    for name in ("reqIds", "waiverRefs"):
                        if name in entry:
                            field(entry, name, "refs", f"{container}.{key}[{index}]")
                evidence_refs(entry)
    if view == "release":
        for key, kind in (("releaseRef", "ref"), ("bcRefs", "refs")):
            if key in source:
                field(source, key, kind, container)
    references, visited = reader.expand(view, references)
    for key in sorted(visited):
        artifact = reader.owners[key]
        evidence.append({"reference": artifact.relative_path, "baseline": _sha(reader.raw[artifact.path])})
    return {"artifactRefs": references, "evidenceRefs": evidence, "gaps": gaps,
            "utility_tree": view == "quality" and isinstance(source.get("utilityTree"), dict)}


def _tree_source(reader: _Sources, path: Path, baseline: str, data: dict) -> dict:
    """An explicitly selected existing utility tree, not a new artifact kind/model."""
    tree = data.get("tree")
    if not isinstance(tree, (dict, list)):
        raise ArtifactInputError("INVALID_OPTIONAL_SOURCE", path, 1, "Utility-tree source needs a tree mapping or list")
    relative = path.relative_to(reader.root).as_posix()
    return {
        "artifactRefs": set(),
        "evidenceRefs": [{"reference": relative + "#tree", "baseline": baseline}],
        "gaps": [] if tree else [f"{relative}#tree: missing utility-tree items"],
        "utility_tree": True,
    }


def _section_has_content(source: Artifact, anchor: str) -> bool:
    if source.kind == "sequence-diagram" and anchor == "diagram":
        for block in section_fences(source, anchor):
            if not block.info.split() or block.info.split()[0] != "mermaid":
                continue
            lines = [line.strip() for line in block.body.splitlines()
                     if line.strip() and not line.lstrip().startswith("%%")]
            if (lines and lines[0] == "sequenceDiagram"
                    and any(re.match(r"^\w+[ \t]*--?>>[ \t]*\w+[ \t]*:[ \t]*\S", line) for line in lines[1:])):
                return True
        return False
    lines = [line.strip() for _, line in section_lines(source, anchor)
             if line.strip() and not line.lstrip().startswith("#")]
    for index, line in enumerate(lines):
        if re.fullmatch(r"[|:\-\s]+", line):
            continue
        if index + 1 < len(lines) and re.fullmatch(r"[|:\-\s]+", lines[index + 1]):
            continue  # Table column labels are not source-owned field values.
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if any(_meaningful(cell) for cell in (cells[1:] if line.startswith("|") else cells)):
            return True
    return False


def _run_results(source: Artifact, anchor: str, lines: tuple[tuple[int, str], ...]) -> tuple[dict, list[str]]:
    rows, gaps = result_rows(source, anchor, lines)
    return {criterion: row["status"] for criterion, row in rows.items()}, gaps


def _run_source(source: Artifact, baseline: str) -> tuple[list[dict], list[str]]:
    """Keep every owned run separate; never merge dates, counts or observations."""
    runs = _owned_runs(source)
    fields = _DIRECT_VALUES[("verification", "verification-test")]
    if not runs:
        return [], [f"{source.relative_path}#runs: missing owned run block for verificationSummary.{field}"
                    for _, field, _, _ in fields]
    evidence, gaps, complete = [], [], []
    basis_labels = ("Actual object baseline", "Requirement/design/task basis baseline at the time",
                    "VT baseline at the time")
    for anchor in runs:
        lines = section_lines(source, anchor)  # Strict criterion/anchor isolation is unchanged.
        evidence.append({"reference": source.relative_path + "#" + anchor, "baseline": baseline})
        run_gaps, basis = [], []
        prefix = f"{source.relative_path}#{anchor}"
        for _, field, labels, kind in fields:
            if field == "result":
                continue
            values = [value for label in labels for _, value in _table_values(lines, label)]
            if kind == "count":
                # The form's compound count row may explicitly state auto/manual
                # counts. Overall found/executed totals never imply those splits.
                stem = "automated" if field == "automatedCount" else "manual"
                pattern = re.compile(r"(?<![\w])(?:" + field + "|(?i:" + stem
                                     + r")(?:[ \t]+(?i:checks?))?(?:[ \t]+(?i:count))?)[ \t]*[:=]?[ \t]*([0-9]+)(?![\w.])")
                for _, text in _table_values(lines, "Exit code and discovered/executed/skipped counts (when applicable)"):
                    values.extend(pattern.findall(text))
            valid = len(values) == 1 and bool(values[0].strip())
            if valid and kind == "count":
                valid = bool(re.fullmatch(r"[0-9]+", values[0].strip()))
            elif valid:
                valid = not re.match(r"^(?:not provided|not configured|not run|TBD|unknown)(?:$|[:,; ])",
                                     values[0].strip(), re.I)
            if not valid:
                run_gaps.append(f"{prefix}: missing or ambiguous verificationSummary.{field}")
        for label in basis_labels:
            values = _table_values(lines, label)
            value = values[0][1].strip() if len(values) == 1 else ""
            if not value or re.match(r"^(?:not provided|not run|TBD|unknown)(?:$|[:,; ])", value, re.I):
                run_gaps.append(f"{prefix}: missing or ambiguous run basis {label}")
            basis.append(value)
        results, result_gaps = _run_results(source, anchor, lines)
        run_gaps.extend(result_gaps)
        gaps.extend(run_gaps)
        if not run_gaps:
            complete.append((anchor, tuple(basis), results))
    for index, (anchor, basis, results) in enumerate(complete):
        for other, other_basis, other_results in complete[:index]:
            if basis == other_basis and results != other_results:
                gaps.append(f"{source.relative_path}: conflicting runs {other} and {anchor} at the same object/requirement/VT basis")
    return evidence, gaps


def _direct_source(reader: _Sources, view: str, artifact: Artifact, baseline: str) -> dict:
    if artifact.kind not in _KINDS[view]:
        raise ArtifactInputError("INVALID_OPTIONAL_SOURCE", artifact.path, 1, f"Owner kind cannot supply {view}")
    references = {a.reference for a in artifact.acceptances} or {artifact.key + "#" + a.name for a in artifact.anchors}
    references, visited = reader.expand(view, references)
    visited.add(artifact.key)
    # A source with no anchors is still locatable evidence but not complete content.
    gaps, evidence = [], []
    for key in sorted(visited):
        source = reader.owners[key]
        source_baseline = baseline if source.key == artifact.key else _sha(reader.raw[source.path])
        evidence.append({"reference": source.relative_path,
                         "baseline": source_baseline})
        if not source.anchors:
            gaps.append(f"{source.relative_path}: missing explicit source sections")
        if source.kind in ("stakeholder-requirement", "software-requirement") and not source.acceptances:
            gaps.append(f"{source.relative_path}: missing owner acceptances")
        for anchor in _SECTIONS.get(source.kind, ()):
            if source.kind == "verification-test" and anchor == "runs" and _owned_runs(source):
                continue
            if not _section_has_content(source, anchor):
                gaps.append(f"{source.relative_path}: missing content in {anchor}")
        if view == "verification" and source.kind == "verification-test":
            run_evidence, run_gaps = _run_source(source, source_baseline)
            evidence.extend(run_evidence)
            gaps.extend(run_gaps)
            continue
        for anchor, field, labels, kind in _DIRECT_VALUES.get((view, source.kind), ()):
            if field == "externalPartners" and any(reader.owners[key].kind == "integration-partner" for key in visited):
                continue  # Actual partners are declared by canonical upstream, not copied.
            rows = [row for label in labels for row in _table_values(section_lines(source, anchor), label)]
            value = rows[0][1].strip() if len(rows) == 1 else ""
            valid = (bool(value) and not re.match(
                r"^(?:not provided|not configured|not run|TBD|unknown|unverified)(?:$|[:,; ])", value, re.I))
            if kind == "bool":
                valid = value in ("true", "false")
            elif kind == "count":
                valid = bool(re.fullmatch(r"[0-9]+", value))
            if not valid:
                gaps.append(f"{source.relative_path}#{anchor}: missing or ambiguous {_SUMMARY[view]}.{field}")
    return {"artifactRefs": references, "evidenceRefs": evidence, "gaps": gaps,
            "kinds": {reader.owners[key].kind for key in visited}}


def _implementation_source(reader: _Sources, path: Path, baseline: str, data: dict, scope: str) -> dict:
    """The v1 report is an explicitly selected reference, not another result owner."""
    from collect_implementation_report import _validate_collected_report
    collection = _validate_collected_report(reader.root, data, path, scope)
    reader.reserved_paths.update(item.resolve() for item in collection.protected)
    reader.reserved_directories.update(collection.directories)
    for source_path in collection.raw:
        if source_path.is_relative_to(reader.root):
            # Registers the report's sources as protected model inputs.
            reader.read(source_path.relative_to(reader.root).as_posix())
    for name in ("bc-config", "implementation-report"):
        contract = Path(__file__).resolve().parents[1] / "contracts" / (name + ".schema.json")
        try:
            reader.contracts[contract.name] = _sha(contract.read_bytes())
        except OSError as error:
            raise ArtifactInputError("CONTRACT_ERROR", contract, 1, str(error)) from error
    pointer = {"reference": path.relative_to(reader.root).as_posix(), "baseline": baseline}
    return {"artifactRefs": set(), "evidenceRefs": [pointer], "gaps": [], "implementationReports": [pointer]}


def _view(reader: _Sources, view: str, selected: list[dict], *, scope: str | None = None) -> dict:
    references: set[str] = set()
    evidence: dict[tuple[str, str], dict] = {}
    gaps: set[str] = set()
    failed = False
    direct_kinds: set[str] = set()
    has_direct = False
    utility_tree = False
    implementation_reports = {}
    for entry in sorted(selected, key=lambda item: (item["path"], item["baseline"])):
        try:
            path, raw = reader.read(entry["path"])
            data = (reader.document(path, raw) if path.suffix.lower() in (".yaml", ".yml", ".json") else None)
            reader.fixed(path, raw, entry["baseline"])
            if path.suffix.lower() == ".md" and path in reader.artifacts:
                part = _direct_source(reader, view, reader.artifacts[path], entry["baseline"])
                direct_kinds.update(part["kinds"])
                has_direct = True
            elif path.suffix.lower() in (".yaml", ".yml", ".json"):
                if view == "quality" and "quality" not in data and "tree" in data:
                    part = _tree_source(reader, path, entry["baseline"], data)
                elif view == "verification" and ("bcConfig" in data or "object" in data and "entries" in data):
                    part = _implementation_source(reader, path, entry["baseline"], data, scope)
                else:
                    part = _summary_source(reader, view, path, raw, entry["baseline"], data)
            else:
                raise ArtifactInputError("INVALID_OPTIONAL_SOURCE", path, 1, "Use a formal Markdown artifact or YAML/JSON summary")
            references.update(part["artifactRefs"])
            for item in part["evidenceRefs"]:
                evidence[(item["reference"], item["baseline"])] = item
            gaps.update(part["gaps"])
            utility_tree = utility_tree or part.get("utility_tree", False)
            for item in part.get("implementationReports", []):
                implementation_reports[(item["reference"], item["baseline"])] = item
        except ArtifactInputError as error:
            if error.code in ("INPUT_CHANGED", "CONTRACT_ERROR"):
                raise
            failed = True
            # Do not leak OS errors containing personal absolute paths into a portable model.
            gap = f"{view}: {entry['path']}: {error.code}"
            failed_path = Path(error.path)
            if failed_path.is_absolute() and failed_path.is_relative_to(reader.root):
                gap += f" at {failed_path.relative_to(reader.root).as_posix()}:{error.line}"
            if error.code == "INVALID_OPTIONAL_SOURCE":
                gap += f": {error.message}"
            gaps.add(gap)
            reader.failures.add((entry["path"], error.code))
    kinds = direct_kinds | {reader.owners[ref.split("#")[0]].kind for ref in references}
    selection = ", ".join(sorted(entry["path"] for entry in selected))
    if view == "quality" and not failed:
        if "quality-attribute-scenario" not in kinds:
            gaps.add(f"quality: {selection}: QAS source is absent")
            failed = True
        if not utility_tree:
            gaps.add(f"quality: {selection}: utility-tree source is absent")
            failed = True
    if has_direct and not failed:
        for kind in sorted(_DIRECT_REQUIRED[view] - kinds):
            gaps.add(f"{view}: {selection}: missing {kind} source")
        if view == "quality" and not kinds.intersection({"validation-scenario", "verification-test"}):
            gaps.add(f"{view}: {selection}: missing quality testScenarios source")
    if not failed:
        reader.implementation_reports.update(implementation_reports)
    return {
        "state": "unverified" if failed else "partial" if gaps else "available",
        "artifactRefs": [] if failed else sorted(references),
        "evidenceRefs": [] if failed else [evidence[key] for key in sorted(evidence)],
        "gaps": sorted(gaps),
    }


def _derive(inventory: Inventory, scope: str) -> tuple[dict, CheckReport, _Sources]:
    _required_inventory(inventory, scope)
    reader = _Sources(inventory)
    manifest = reader.manifest()
    views = {}
    for name in sorted(_SUMMARY):
        absent = ("model-sources.yaml is absent" if manifest is None else
                  f"model-sources.yaml scope {scope} is absent" if scope not in manifest else
                  f"model-sources.yaml view {name} is absent for scope {scope}" if name not in manifest[scope] else None)
        views[name] = ({"state": "unverified", "artifactRefs": [], "evidenceRefs": [],
                        "gaps": [f"{name}: {absent}"]} if absent else _view(reader, name, manifest[scope][name], scope=scope))
    baseline = _baseline(reader.root, None, None, reader.records, (), True)
    identity = {
        "scope": scope, "files": [asdict(item) for item in baseline.files],
        "manifest": reader.selection, "optional_failures": sorted(reader.failures),
        "contracts": reader.contracts,
    }
    artifacts = []
    for artifact in sorted(inventory.artifacts, key=lambda item: item.key):
        if artifact.scope != scope:
            continue
        targets = [{"target": item.target, "criterionAnchor": item.criterion_anchor,
                    **({"testId": item.test_id} if item.test_id is not None else {})} for item in artifact.targets]
        artifacts.append({
            "key": artifact.key, "path": artifact.relative_path, "baseline": _sha(reader.raw[artifact.path]),
            "upstream": sorted(artifact.upstream),
            "targets": sorted(targets, key=lambda item: (item["target"], item["criterionAnchor"], item.get("testId", ""))),
        })
    result = _ordered({
        "schemaVersion": 1, "scope": scope,
        "source": {"root": ".", "baseline": _sha(json.dumps(identity, sort_keys=True, separators=(",", ":")).encode("utf-8"))},
        "artifacts": artifacts,
        "implementationReports": [reader.implementation_reports[key] for key in sorted(reader.implementation_reports)],
        "views": views,
    })
    violation = next(reader.validators["model"].iter_errors(result), None)
    if violation:
        raise ArtifactInputError("CONTRACT_ERROR", reader.root, 1,
                                 f"Derived model violates output contract at {list(violation.absolute_path)}")
    return result, replace(inventory.report, baseline=baseline), reader


def export_view(root: PathInput, scope: str) -> dict:
    """Return the derived nine-view reference index. Never write a file."""
    model, _, _ = _derive(read_inventory(root), scope)
    return model


def _failure(report: CheckReport, error: ArtifactInputError) -> CheckReport:
    finding = _error(error)
    found = any((f.code, f.path, f.line) == (finding.code, finding.path, finding.line) for f in report.findings)
    return replace(report, status="input-error",
                   findings=report.findings if found else (*report.findings, finding))


def _model_path(root: PathInput, model_path: PathInput) -> Path:
    if not isinstance(model_path, (str, Path)) or not str(model_path).strip() or _network_path(str(model_path)) or "://" in str(model_path):
        raise ArtifactInputError("INVALID_PATH", str(model_path), 1, "Supply an explicit local model file")
    requested = Path(model_path)
    if requested.anchor and not requested.is_absolute():
        raise ArtifactInputError("INVALID_PATH", str(model_path), 1, "Ambiguous model path")
    if not requested.is_absolute():
        requested = _local_root(root) / requested
    if requested.suffix.lower() not in (".json", ".yaml", ".yml"):
        raise ArtifactInputError("INVALID_PATH", requested, 1, "Model input must be .json, .yaml or .yml")
    return _resolve_file(requested, _local_root(requested.parent))


def check_model(root: PathInput, scope: str, model_path: PathInput) -> CheckReport:
    """Validate and recompute a persisted model; report drift, never repair it."""
    inventory = read_inventory(root)
    report = inventory.report
    try:
        expected, report, reader = _derive(inventory, scope)
        path = _model_path(root, model_path)
        try:
            raw = path.read_bytes()
        except OSError as error:
            raise ArtifactInputError("FILE_READ_ERROR", path, 1, str(error)) from error
        data, _ = load_yaml_mapping(_decode(raw, path), path)
        if type(data.get("schemaVersion")) is not int or data["schemaVersion"] != 1:
            raise ArtifactInputError("UNSUPPORTED_SCHEMA_VERSION", path, 1, "Expected integer schemaVersion 1")
        violation = next(reader.validators["model"].iter_errors(data), None)
        if violation:
            raise ArtifactInputError("INVALID_MODEL", path, 1, f"Model schema violation at {list(violation.absolute_path)}")
        if data["scope"] != scope:
            raise ArtifactInputError("INVALID_SCOPE", path, 1, "Persisted model scope differs from explicit selection")
        if data != expected:
            stale = data["source"] != expected["source"]
            finding = Finding("STALE_MODEL_SOURCE" if stale else "MODEL_MISMATCH",
                              str(path), 1, None, scope,
                              "Source read identity changed" if stale else "Persisted view differs from deterministic derivation")
            report = replace(report, status="invalid", findings=(*report.findings, finding))
        return report
    except ArtifactInputError as error:
        return _failure(report, error)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True)
    parser.add_argument("--scope", required=True)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--output")
    mode.add_argument("--check")
    arguments = parser.parse_args()
    if arguments.check is not None:
        report = check_model(arguments.root, arguments.scope, arguments.check)
        print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
        return {"clean": 0, "empty": 0, "invalid": 1, "input-error": 2}[report.status]
    inventory = read_inventory(arguments.root)
    report = inventory.report
    try:
        model, report, reader = _derive(inventory, arguments.scope)
        if arguments.output is not None:
            path = _output_path(arguments.output, _local_root(arguments.root), (".json", ".yaml", ".yml"))
            if reader.reservation_errors:
                raise ArtifactInputError("REPORT_CONFLICT", path, 1, "Malformed declared source/evidence locations prevent safe output isolation")
            if path in reader.reserved_paths or any(path.is_relative_to(directory) for directory in reader.reserved_directories):
                raise ArtifactInputError("REPORT_CONFLICT", path, 1, "Output is a registered source/selection path, even if absent")
            content = (json.dumps(model, ensure_ascii=False, sort_keys=True, indent=2)
                       if path.suffix.lower() == ".json" else yaml.safe_dump(model, allow_unicode=True, sort_keys=True).rstrip())
            _write_new(path, content + "\n")
        print(json.dumps(model, ensure_ascii=False, sort_keys=True, indent=2))
        return 0
    except ArtifactInputError as error:
        report = _failure(report, error)
        payload = report.to_dict()
        if arguments.output is not None:
            payload["report_output"] = {"path": str(error.path), "written": False}
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
