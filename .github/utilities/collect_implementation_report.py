"""Collect source-owned VT results against an exact local object; never run them."""

from __future__ import annotations

import argparse
from collections.abc import Iterable, Mapping
from datetime import date
import json
import os
from pathlib import Path, PurePosixPath
import re

import yaml

from artifact_io import (
    _sha, Artifact, ArtifactInputError, PathInput, _parse_artifact_bytes, _resolve_file,
    load_yaml_mapping,
)
from check_artifacts import (
    _anchors, _decode, _document_findings, _domain_location, _exclusion, _fixed_file,
    _formal, _INLINE_LINK, _local_root, _network_path, _output_path, _read, _write_new,
)
from check_traceability import _criterion, _layer, _meaningful, _OWNER_LAYERS, _table_values, section_lines
from vt_records import owned_runs, plan_bytes, result_rows
from source_baseline import (
    Commit as _Commit, domain_files, relative_path as _relative, validate_mapping as _validate,
)


_KEY = r"(?:[A-Za-z0-9][A-Za-z0-9._-]*/){2}[A-Za-z0-9][A-Za-z0-9._-]*"
_BASE = r"(?:[0-9a-f]{40}|[0-9a-f]{64}|sha256:[0-9a-f]{64})"
_MARKER = re.compile(r"^\s*(?:#|//) (implements|verifies): (" + _KEY
                     + r"#[A-Za-z][A-Za-z0-9._:-]*) (symbol|testId)=([A-Za-z_][A-Za-z0-9_]*)\s*$")
_MARKER_START = re.compile(r"^\s*(?:#|//) (?:implements|verifies):")
_DATE = r"([0-9]{4}-[0-9]{2}-[0-9]{2}); recorder=([^;]+)"


def _field(source: Artifact, anchor: str, label: str) -> str:
    values = _table_values(section_lines(source, anchor), label)
    if len(values) != 1 or not values[0][1].strip():
        raise ArtifactInputError("INVALID_RUN", source.path, values[0][0] if values else source.body_start_line,
                                 f"{anchor}: missing or ambiguous {label}")
    return values[0][1].strip()


def _detail(value: str) -> bool:
    plain = re.sub(r"[*_`]", "", value).strip()
    return (_meaningful(plain) and not re.fullmatch(
        r"(?:approved|success(?:ful)?|pass(?:ed)?|failed|failure|done)[.!\s]*", plain, re.I)
        and not re.match(r"^(?:not provided|not configured|not run|TBD|unknown|unverified)(?:$|[:,; ])", plain, re.I))


def _record_date(value: str, source: Artifact, *, mode: bool) -> str | None:
    match = re.fullmatch(_DATE + (r"; mode=(command|manual)" if mode else ""), value)
    try:
        if (not match or not match[2].strip()
                or re.fullmatch(r"unknown|unverified|none|n/?a|not provided|not run|TBD", match[2].strip(), re.I)):
            raise ValueError
        date.fromisoformat(match[1])
    except ValueError as error:
        raise ArtifactInputError("INVALID_RUN", source.path, 1, "Expected a concrete date, recorder and supported execution mode") from error
    return match[3] if mode else None


class _Collection:
    def __init__(self, root: PathInput, object_sha: str, scope: str | None) -> None:
        self.root = _local_root(root)
        self.object = _Commit(self.root, object_sha)
        self.commits = {self.object.sha: self.object}
        self.raw: dict[Path, bytes] = {}
        self.records = {}
        self.protected = {self.root / name for name in self.object.files}
        self.directories: set[Path] = set()
        self.config, _ = load_yaml_mapping(_decode(self.object.read("bc-config.yaml"), self.root / "bc-config.yaml"),
                                           self.root / "bc-config.yaml")
        _validate(self.config, "bc-config", self.root / "bc-config.yaml")
        choices = {self.config["projectId"] + "/" + context["id"] for context in self.config["boundedContexts"]}
        if scope is None and len(choices) != 1:
            raise ArtifactInputError("AMBIGUOUS_SCOPE", self.root / "bc-config.yaml", 1, "Select one explicit configured scope")
        self.scope = next(iter(choices)) if scope is None else scope
        if not isinstance(self.scope, str) or self.scope not in choices:
            raise ArtifactInputError("INVALID_SCOPE", self.root / "bc-config.yaml", 1, "Scope is not a configured BC")
        self.owners: dict[str, Artifact] = {}
        self.paths: dict[str, Artifact] = {}
        for relative in sorted(self.object.files):
            if _exclusion(relative) or PurePosixPath(relative).suffix.lower() != ".md":
                continue
            raw = self.object.read(relative)
            if not _formal(relative, _decode(raw, self.root / relative)):
                continue
            artifact = _parse_artifact_bytes(raw, self.root / relative, self.root)
            if artifact.key in self.owners:
                raise ArtifactInputError("DUPLICATE_ARTIFACT_ID", artifact.path, 1, "Duplicate exact-object owner")
            findings = _document_findings(artifact)
            if findings:
                found = findings[0]
                raise ArtifactInputError(found.code, found.path, found.line, found.message)
            self.owners[artifact.key] = artifact
            self.paths[relative] = artifact
        if self.scope not in {a.scope for a in self.owners.values()}:
            raise ArtifactInputError("UNKNOWN_SCOPE", self.root, 1, "Configured BC has no actual formal owners")
        self.acceptances = {ac.reference: ac for a in self.owners.values() for ac in a.acceptances}
        self.targets = sorted(ref for ref, ac in self.acceptances.items() if self.owners[ac.owner].scope == self.scope)
        if not self.targets:
            raise ArtifactInputError("EMPTY_ACCEPTANCE", self.root, 1, "Selected BC has no source-owned acceptance inventory")
        for owner in self.owners.values():
            for ref in (*owner.upstream, *(target.target for target in owner.targets)):
                self.canonical(ref)
            for target in owner.targets:
                if target.target not in self.acceptances:
                    raise ArtifactInputError("TARGET_NOT_ACCEPTANCE", owner.path, target.location.line, target.target)
        registration, fragment = self.config["developmentRegistration"].split("#")
        if fragment not in _anchors(_decode(self.object.read(registration), self.root / registration)):
            raise ArtifactInputError("BROKEN_ANCHOR", self.root / registration, 1, "Development registration anchor is absent")
        self.domain_sources = self.domains()
        self.code, self.tests = self.locators()

    def canonical(self, ref: str) -> Artifact:
        key, _, anchor = ref.partition("#")
        owner = self.owners.get(key)
        if owner is None or anchor and anchor not in {a.name for a in owner.anchors}:
            raise ArtifactInputError("DANGLING_REFERENCE", self.root, 1, f"No exact owner/anchor for {ref}")
        return owner

    def live(self, path: Path, root: Path | None = None) -> bytes:
        local_root = self.root if root is None else root
        actual = _resolve_file(path, local_root)
        self.protected.add(actual)
        return _read(actual, local_root, self.raw, self.records, "reference")

    def domains(self) -> list[dict]:
        result, ids = [], set()
        for source in self.config["domainSources"]:
            if source["id"] in ids:
                raise ArtifactInputError("DUPLICATE_DOMAIN_SOURCE", self.root / "bc-config.yaml", 1, "Duplicate source id")
            ids.add(source["id"])
            root_value = source["root"]
            source_root, path = _domain_location(self.root, root_value, source["path"])
            self.protected.add(path)  # Reserve before read, including failures.
            source_root = _local_root(source_root)
            relative = source["path"]
            baseline = source["baseline"]
            files, directory = domain_files(source_root, relative, baseline, self.live)
            if directory:
                self.directories.add(path)
            for file, raw in files.items():
                if file.is_relative_to(self.root):
                    name = file.relative_to(self.root).as_posix()
                    if name in self.object.files and self.object.read(name) != raw:
                        raise ArtifactInputError("BASE_MISMATCH", file, 1, "Overlapping domain input differs from the selected object")
            result.append({"root": root_value, "path": relative, "baseline": baseline})
        return sorted(result, key=lambda item: (item["root"], item["path"], item["baseline"]))

    def locators(self) -> tuple[dict, dict]:
        code, tests = {ref: [] for ref in self.targets}, {ref: [] for ref in self.targets}
        located = set()
        for relative, (mode, kind, _) in sorted(self.object.files.items()):
            if (mode not in ("100644", "100755") or kind != "blob"
                    or _exclusion(relative) in ("TOOL_DATA", "TEMPLATE", "NATIVE_METADATA", "MAKER_DATA")
                    or PurePosixPath(relative).suffix.lower() in (".md", ".json", ".yaml", ".yml")):
                continue
            raw = self.object.read(relative)
            if not re.search(rb"(?m)^\s*(?:#|//) (?:implements|verifies):", raw):
                continue
            lines = _decode(raw, self.root / relative).splitlines()
            for index, line in enumerate(lines):
                if not _MARKER_START.match(line):
                    continue
                match = _MARKER.fullmatch(line)
                following = next((text.strip() for text in lines[index + 1:]
                                  if text.strip() and not text.lstrip().startswith(("#", "//"))), "")
                if (not match or (match[1] == "implements") != (match[3] == "symbol")
                        or not re.search(r"(?<![\w.])" + re.escape(match[4]) + r"\s*\(", following)):
                    raise ArtifactInputError("INVALID_MARKER", self.root / relative, index + 1,
                                             "Marker needs a complete target and an immediately located named declaration")
                operation, target, field, identifier = match.groups()
                if target not in self.acceptances:
                    raise ArtifactInputError("INVALID_MARKER", self.root / relative, index + 1, "Marker target is not an actual owner acceptance")
                if operation == "verifies":
                    located.add((target, identifier))
                if target in code:
                    values = code if operation == "implements" else tests
                    item = {"path": relative, "baseline": self.object.sha, field: identifier}
                    if item not in values[target]:
                        values[target].append(item)
        for source in self.owners.values():
            if source.scope == self.scope:
                for target in source.targets:
                    if target.test_id is not None and (target.target, target.test_id) not in located:
                        raise ArtifactInputError("MISSING_TEST_REFERENCE", source.path, target.location.line,
                                                 "Declared testId has no exact target/identifier source location at the object")
        return code, tests

    def at_basis(self, source: Artifact, baseline: str, *, plan: bool = False) -> None:
        if not isinstance(baseline, str) or not re.fullmatch(_BASE, baseline):
            raise ArtifactInputError("INVALID_BASE", source.path, 1, "Use a full exact commit or raw sha256")
        selected = self.object.read(source.relative_path)
        if baseline.startswith("sha256:"):
            if baseline != _sha(selected):
                raise ArtifactInputError("BASE_MISMATCH", source.path, 1, "Basis does not match the exact object's source bytes")
            return
        if baseline not in self.commits:
            self.commits[baseline] = _Commit(self.root, baseline)
        other = self.commits[baseline].read(source.relative_path)
        if plan:
            older = _parse_artifact_bytes(other, source.path, self.root)
            equal = plan_bytes(older, other) == plan_bytes(source, selected)
        else:
            equal = other == selected
        if not equal:
            raise ArtifactInputError("PLAN_MISMATCH" if plan else "BASE_MISMATCH", source.path, 1,
                                     "Referenced basis differs from the selected object's intended source")

    def requirements(self, value: str, source: Artifact) -> dict[str, str]:
        bases = {}
        for part in value.split(";"):
            match = re.fullmatch("(" + _KEY + ")@(" + _BASE + ")", part.strip())
            if not match or match[1] in bases:
                raise ArtifactInputError("REQUIREMENT_MISMATCH", source.path, 1, "Use one explicit owner@baseline per target owner")
            bases[match[1]] = match[2]
        if set(bases) != {target.target.split("#")[0] for target in source.targets}:
            raise ArtifactInputError("REQUIREMENT_MISMATCH", source.path, 1, "Requirement bases must match the exact target owners")
        for key, baseline in bases.items():
            self.at_basis(self.owners[key], baseline)
        return bases

    def link(self, value: str, source: Artifact) -> str:
        match = _INLINE_LINK.fullmatch(value)
        if not match:
            raise ArtifactInputError("INVALID_EVIDENCE", source.path, 1, "Expected one original local Markdown report link")
        destination = match[1].strip("<>")
        relative, separator, fragment = destination.partition("#")
        if (not relative or _network_path(relative) or re.search(r"[\\:\x00-\x1f]", relative)
                or Path(relative).is_absolute() or separator and not re.fullmatch(r"[A-Za-z][A-Za-z0-9._:-]*", fragment)):
            raise ArtifactInputError("INVALID_EVIDENCE", source.path, 1, "Report links must stay local with a supported fragment")
        path = (source.path.parent / relative).resolve()
        if not path.is_relative_to(self.root):
            raise ArtifactInputError("OUTSIDE_ROOT", source.path, 1, "Report reference leaves the selected root")
        name = _relative(path.relative_to(self.root).as_posix(), source.path)
        self.protected.add(path)
        return name + ("#" + fragment if separator else "")

    def reports(self, source: Artifact, anchor: str, executed: bool) -> list[dict]:
        value = _field(source, anchor, "Raw report and exact location")
        if not executed and value == "not-run":
            return []
        refs = []
        for part in value.split(";"):
            link, separator, baseline = part.strip().rpartition(" @ ")
            if not separator or not re.fullmatch(_BASE, baseline):
                raise ArtifactInputError("INVALID_EVIDENCE", source.path, 1, "Original report link needs its fixed baseline")
            reference = self.link(link, source)
            if reference in {item["reference"] for item in refs}:
                raise ArtifactInputError("INVALID_EVIDENCE", source.path, 1, "Duplicate raw report reference")
            relative, _, fragment = reference.partition("#")
            path = self.root / relative
            raw = self.live(path)
            _fixed_file(self.root, path, raw, baseline)
            if not raw.strip():
                raise ArtifactInputError("INVALID_EVIDENCE", path, 1, "Original report is empty")
            if fragment:
                if path.suffix.lower() == ".md":
                    known = _anchors(_decode(raw, path))
                elif path.suffix.lower() in (".json", ".yaml", ".yml"):
                    known, _ = load_yaml_mapping(_decode(raw, path), path)
                else:
                    known = ()
                if fragment not in known:
                    raise ArtifactInputError("BROKEN_ANCHOR", path, 1, "Original report fragment is absent or unsupported")
            refs.append({"reference": reference, "baseline": baseline})
        return refs

    def applicability(self, source: Artifact, anchor: str, target) -> dict:
        default = {"state": "unverified", "reason": "No independent applicability record matches this target, run and bases."}
        labels = ("Review date and recorder", "Original run/result and target link",
                  "Current object, requirement, and VT baselines", "Applicability", "Rationale, impact, and items to recheck")
        header, matches, previous = None, [], 0
        for number, line in section_lines(source, "applicability"):
            if number != previous + 1:
                header = None
            previous = number
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            if tuple(cells) == labels:
                header = True
                continue
            if not line.lstrip().startswith("|"):
                header = None
            if not header or len(cells) != 5 or re.fullmatch(r"[|:\-\s]+", line):
                continue
            refs = [link[1].strip("<>") for link in _INLINE_LINK.finditer(cells[1])]
            if refs != ["#" + anchor, "#" + target.criterion_anchor]:
                continue
            basis = re.fullmatch(r"object=([0-9a-f]{40}|[0-9a-f]{64}); requirement=(" + _KEY
                                 + r")@(" + _BASE + r"); vt=(" + _BASE + r")", cells[2])
            if not basis:
                raise ArtifactInputError("INVALID_APPLICABILITY", source.path, number, "Matching applicability row needs exact bases")
            if basis[1] != self.object.sha or basis[2] != target.target.split("#")[0]:
                continue
            self.at_basis(self.owners[basis[2]], basis[3])
            self.at_basis(self.paths[source.relative_path], basis[4], plan=True)
            _record_date(cells[0], source, mode=False)
            state = cells[3].strip("`")
            if state not in ("unverified", "applicable", "not-applicable") or not _detail(cells[4]):
                raise ArtifactInputError("INVALID_APPLICABILITY", source.path, number, "State and independent reason are required")
            matches.append({"state": state, "reason": cells[4]})
        if len(matches) > 1:
            raise ArtifactInputError("AMBIGUOUS_APPLICABILITY", source.path, 1, "Multiple matching applicability rows; no last-wins rule")
        return matches[0] if matches else default

    def run(self, source: Artifact, anchor: str, raw: bytes) -> dict:
        original = self.paths[source.relative_path]
        if plan_bytes(source, raw) != plan_bytes(original, self.object.read(source.relative_path)):
            raise ArtifactInputError("PLAN_MISMATCH", source.path, 1, "Supplied evidence changes the exact object's plan")
        if _field(source, anchor, "Actual object baseline") != self.object.sha:
            raise ArtifactInputError("OBJECT_MISMATCH", source.path, 1, "Run belongs to another tested object")
        bases = self.requirements(_field(source, anchor, "Requirement/design/task basis baseline at the time"), source)
        plan = _field(source, anchor, "VT baseline at the time")
        self.at_basis(original, plan, plan=True)
        rows, gaps = result_rows(source, anchor)
        if gaps:
            raise ArtifactInputError("INVALID_RUN", source.path, 1, "; ".join(gaps))
        mode = _record_date(_field(source, anchor, "Date, executor, and mode"), source, mode=True)
        executed = any(row["status"] in ("pass", "fail") for row in rows.values())
        steps = _field(source, anchor, "Actual command or manual steps/test identifier")
        if executed:
            for label in ("Actual environment and tool versions", "Report accessibility and limitations", "Actual command or manual steps/test identifier"):
                if not _detail(_field(source, anchor, label)):
                    raise ArtifactInputError("INVALID_RUN", source.path, 1, f"{anchor}: missing actual {label}")
        if mode == "command" and executed:
            cwd = _relative(_field(source, anchor, "Actual working directory"), source.path, directory=True)
            if not self.object.directory(cwd):
                raise ArtifactInputError("INVALID_EXECUTION", source.path, 1, "Execution cwd is not in the tested object")
            counts = re.fullmatch(r"exit=(-?[0-9]+); discovered=([0-9]+); executed=([0-9]+); skipped=([0-9]+)",
                                  _field(source, anchor, "Exit code and discovered/executed/skipped counts (when applicable)"))
            if not counts:
                raise ArtifactInputError("INVALID_EXECUTION", source.path, 1, "Explicit exit/discovered/executed/skipped counts required")
            exit_code, discovered, done, skipped = map(int, counts.groups())
            if (done == 0 or discovered != done + skipped
                    or exit_code != 0 and not any(row["status"] == "fail" for row in rows.values())):
                raise ArtifactInputError("INVALID_EXECUTION", source.path, 1, "Zero/all-skipped/inconsistent execution cannot supply a result")
        reports = self.reports(source, anchor, executed)
        result, criterion_owners, signatures = {}, {}, {}
        for target in source.targets:
            owner = self.owners[target.target.split("#")[0]]
            valid, signature = _criterion(source, target.criterion_anchor)
            layer, _ = _layer(source)
            if (not valid or layer != _OWNER_LAYERS.get(owner.kind)
                    or criterion_owners.get(target.criterion_anchor, target.target) != target.target
                    or signatures.get(signature, target.target) != target.target):
                raise ArtifactInputError("INVALID_CRITERION", source.path, target.location.line, "Criterion/layer does not independently match its owner")
            criterion_owners[target.criterion_anchor] = target.target
            signatures[signature] = target.target
            row = rows[target.criterion_anchor]
            if target.target in result:
                raise ArtifactInputError("AMBIGUOUS_RESULT", source.path, row["line"], "More than one result for a target")
            if row["status"] in ("pass", "fail"):
                links = [self.link(match[0], source) for match in _INLINE_LINK.finditer(row["observation"])]
                if (not _detail(_INLINE_LINK.sub("", row["observation"]))
                        or not links or not set(links).issubset({ref["reference"] for ref in reports})):
                    raise ArtifactInputError("INVALID_OBSERVATION", source.path, row["line"], "Concrete observation and matching original report location required")
                if mode == "command" and (target.test_id is None
                        or not re.search(r"(?<!\w)" + re.escape(target.test_id) + r"(?!\w)", steps)):
                    raise ArtifactInputError("INVALID_EXECUTION", source.path, row["line"], "Executed command must locate its declared testId")
                if row["status"] == "fail" and not _detail(row["reason"]):
                    raise ArtifactInputError("INVALID_OBSERVATION", source.path, row["line"], "Failure needs its source-owned difference")
            elif not _detail(row["reason"]):
                raise ArtifactInputError("INVALID_OBSERVATION", source.path, row["line"], "Not-run/skipped needs a concrete source reason")
            refs = [
                {"reference": source.relative_path + "#" + anchor, "baseline": _sha(raw)},
                {"reference": owner.relative_path + "#" + target.target.split("#")[1], "baseline": bases[owner.key]},
                {"reference": source.relative_path + "#" + target.criterion_anchor, "baseline": plan},
            ]
            if row["status"] in ("pass", "fail"):
                refs.extend(ref for ref in reports if ref["reference"] in links)
            execution = {"status": row["status"],
                         "evidenceRefs": sorted(refs, key=lambda item: (item["reference"], item["baseline"]))}
            if row["reason"]:
                execution["reason"] = row["reason"]
            result[target.target] = (execution, self.applicability(source, anchor, target))
        if mode == "command" and executed:
            # Count validated executed identities, not criteria or command words.
            # One test may cover multiple criteria; other actual tests may also
            # have run without being mapped to this selected VT's targets.
            executed_ids = {target.test_id for target in source.targets
                            if rows[target.criterion_anchor]["status"] in ("pass", "fail")}
            if len(executed_ids) > done:
                raise ArtifactInputError("INVALID_EXECUTION", source.path, 1,
                                         "Distinct executed testIds exceed the recorded executed count")
        return result

    def build(self, evidence_files) -> dict:
        if isinstance(evidence_files, (str, bytes, os.PathLike, Mapping)) or not isinstance(evidence_files, Iterable):
            raise ArtifactInputError("INVALID_EVIDENCE_SELECTION", self.root, 1, "Supply an explicit collection of VT file/run selectors")
        results, selected = {}, set()
        for value in evidence_files:
            if not isinstance(value, str):
                raise ArtifactInputError("INVALID_EVIDENCE_SELECTION", self.root, 1, "Each selector must be a VT path with optional owned run anchor")
            relative, separator, fragment = value.partition("#")
            _relative(relative, self.root)
            path = self.root / relative
            raw = self.live(path)
            source = _parse_artifact_bytes(raw, path, self.root)
            original = self.paths.get(relative)
            if original is None or original.key != source.key or source.kind != "verification-test":
                raise ArtifactInputError("INVALID_EVIDENCE_OWNER", path, 1, "Evidence must retain the exact object's VT path and owner")
            if source.scope != self.scope:
                raise ArtifactInputError("SCOPE_MISMATCH", path, 1, "Evidence VT is not in the selected BC")
            runs = owned_runs(source)
            if separator and fragment not in runs:
                raise ArtifactInputError("UNKNOWN_RUN", path, 1, "Selector is not an actual child run of this VT")
            if not separator and len(runs) > 1:
                raise ArtifactInputError("AMBIGUOUS_RUN", path, 1, "Multiple owned runs; select an explicit anchor")
            anchor = fragment if separator else runs[0] if runs else ""
            identity = (path.resolve(), anchor)
            if identity in selected:
                raise ArtifactInputError("DUPLICATE_EVIDENCE", path, 1, "Duplicate file/run selection")
            selected.add(identity)
            if not anchor:
                continue
            for target, outcome in self.run(source, anchor, raw).items():
                if target not in self.targets:
                    raise ArtifactInputError("SCOPE_MISMATCH", path, 1, "Selected run includes a target outside the selected delivery")
                if target in results:
                    raise ArtifactInputError("AMBIGUOUS_RESULT", path, 1, "Multiple selected runs supply this target; no merge or favorable selection")
                results[target] = outcome
        refs, visited = set(), set()
        pending = [a.key for a in self.owners.values() if a.scope == self.scope]
        while pending:
            key = pending.pop()
            if key in visited:
                continue
            visited.add(key)
            source = self.owners[key]
            refs.update(source.key + "#" + anchor.name for anchor in source.anchors)
            for ref in (*source.upstream, *(target.target for target in source.targets)):
                pending.append(self.canonical(ref).key)
        entries = []
        for target in self.targets:
            execution, applicability = results.get(target, (
                {"status": "not-run", "evidenceRefs": [], "reason": "No source-owned run was selected for this target at the exact object."},
                {"state": "unverified", "reason": "No independent applicability record matches this target, run and bases."},
            ))
            entries.append({"target": target, "codeRefs": self.code[target], "testRefs": self.tests[target],
                            "execution": execution, "applicability": applicability})
        report = {
            "schemaVersion": 1, "scope": self.scope, "object": {"root": ".", "baseline": self.object.sha},
            "bcConfig": {"reference": "bc-config.yaml", "baseline": self.object.sha},
            "domainSources": self.domain_sources, "artifactRefs": sorted(refs), "entries": entries,
        }
        _validate(report, "implementation-report", self.root)
        return report

    def output_path(self, value: str) -> Path:
        path = _output_path(value, self.root, (".json", ".yaml", ".yml"))
        # Reuse Task7's declaration-before-dereference protection. Current source
        # reservations affect ONLY a requested write, never the tested object.
        from check_artifacts import read_inventory
        from export_model import _Sources, _view
        reader = _Sources(read_inventory(self.root))
        manifests = []
        current = reader.manifest()
        if current is not None:
            manifests.append(current)
        if "model-sources.yaml" in self.object.files:
            data, _ = load_yaml_mapping(_decode(self.object.read("model-sources.yaml"), self.root / "model-sources.yaml"),
                                       self.root / "model-sources.yaml")
            _validate(data, "model-sources", self.root / "model-sources.yaml")
            manifests.append(data["scopes"])
        for manifest in manifests:
            for selected_scope, views in manifest.items():
                for view, sources in views.items():
                    for source in sources:
                        reader.reserve(source["path"])
                        # Even an unavailable current optional source must not
                        # erase nested declarations present at the tested object.
                        if source["path"] in self.object.files and Path(source["path"]).suffix.lower() in (".yaml", ".yml", ".json"):
                            data = reader.document(self.root / source["path"], self.object.read(source["path"]))
                            reader.reserve_declarations(data)
                    _view(reader, view, sources, scope=selected_scope)
        if (reader.reservation_errors or path in reader.reserved_paths
                or path in {item.resolve() for item in self.protected}
                or any(path.is_relative_to(directory) for directory in self.directories | reader.reserved_directories)):
            raise ArtifactInputError("REPORT_CONFLICT", path, 1, "Output overlaps an existing, referenced or declared source location")
        return path


def build_report(root: PathInput, object_sha: str, evidence_files, *, scope: str | None = None) -> dict:
    """Return the existing v1 report, reading exact object inputs and supplied VT runs."""
    return _Collection(root, object_sha, scope).build(evidence_files)


def _validate_collected_report(root: Path, data: dict, path: Path, scope: str) -> _Collection:
    """The model's explicit report adapter: verify references and reconstruct, not run.

    Selection is recovered only from actual owned run pointers already in this
    report. Reconstruction rejects omitted targets, fabricated results/locators,
    stale current record bytes and additions unsupported by the original owner.
    """
    _validate(data, "implementation-report", path)
    if data["scope"] != scope or data["object"]["root"] != ".":
        raise ArtifactInputError("SCOPE_MISMATCH", path, 1, "Report must name the explicitly selected local scope/root")
    collection = _Collection(root, data["object"]["baseline"], scope)
    selectors = set()
    for entry in data["entries"]:
        for ref in entry["execution"]["evidenceRefs"]:
            relative, _, anchor = ref["reference"].partition("#")
            source = collection.paths.get(relative)
            if (source is not None and source.kind == "verification-test"
                    and re.fullmatch(re.escape(source.id.lower()) + r"-run-[0-9]+", anchor)):
                raw = collection.live(root / relative)
                _fixed_file(root, root / relative, raw, ref["baseline"])
                selectors.add(ref["reference"])
    if collection.build(sorted(selectors)) != data:
        raise ArtifactInputError("REPORT_MISMATCH", path, 1, "Report differs from reconstruction of its original object and owned run references")
    return collection


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True)
    parser.add_argument("--object", required=True, dest="object_sha")
    parser.add_argument("--scope")
    parser.add_argument("--evidence", action="append", default=[])
    parser.add_argument("--output")
    arguments = parser.parse_args()
    try:
        collection = _Collection(arguments.root, arguments.object_sha, arguments.scope)
        report = collection.build(arguments.evidence)
        if arguments.output is not None:
            path = collection.output_path(arguments.output)
            content = (json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2)
                       if path.suffix.lower() == ".json" else yaml.safe_dump(report, allow_unicode=True, sort_keys=True).rstrip())
            _write_new(path, content + "\n")
        print(json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2))
        return 1 if any(entry["execution"]["status"] == "fail" for entry in report["entries"]) else 0
    except ArtifactInputError as error:
        print(json.dumps({"status": "input-error", "findings": [{
            "code": error.code, "path": str(error.path), "line": error.line, "message": error.message,
        }]}, ensure_ascii=False, indent=2))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
