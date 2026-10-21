"""ENH-06 / Task7: independent source-selection and nine-view expectations."""

from __future__ import annotations

import copy
import hashlib
import importlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

from jsonschema import Draft202012Validator
from referencing import Registry
import yaml

from artifact_io import ArtifactInputError, parse_artifact
from tests.helpers import (
    CONTRACTS, VIEW_NAMES, WORKTREE, git, metadata, seed_git_repo, seed_implementation_fixture, source_bytes,
    temporary_workspace, write_artifact, write_delivery_fixture, write_metadata,
)


def no_remote_schema(uri):
    raise AssertionError(f"Unexpected nonlocal schema: {uri}")


class SourceManifestContractTests(unittest.TestCase):
    """Breaks caught: implicit scopes, mutable baselines or executable data fields."""

    def validator(self):
        path = CONTRACTS / "model-sources.schema.json"
        self.assertTrue(path.is_file(), "Task7 source-selection schema is not implemented")
        schema = json.loads(path.read_bytes())
        Draft202012Validator.check_schema(schema)
        return Draft202012Validator(schema, registry=Registry(retrieve=no_remote_schema))

    def data(self):
        # A real byte identity, independent of any exporter implementation.
        baseline = "sha256:" + hashlib.sha256(b"known local source\n").hexdigest()
        return {"schemaVersion": 1, "scopes": {
            "sample/CTX-001": {"sequences": [{"path": "sources/sequence.yaml", "baseline": baseline}]},
            "sample/CTX-002": {"quality": [{"path": "качество €/QAS-001.md", "baseline": baseline}]},
        }}

    def test_accepts_explicit_multiple_scopes_and_reference_only_entries(self):
        self.assertEqual([], list(self.validator().iter_errors(self.data())))

    def test_empty_scopes_is_a_blank_form_not_an_invented_project(self):
        self.assertEqual([], list(self.validator().iter_errors({"schemaVersion": 1, "scopes": {}})))

    def test_rejects_missing_version_or_scope_container(self):
        for field in ("schemaVersion", "scopes"):
            data = self.data()
            del data[field]
            with self.subTest(field=field):
                self.assertTrue(list(self.validator().iter_errors(data)))

    def test_rejects_unknown_version_and_non_numeric_version(self):
        for value in (0, 2, True, "1", None):
            with self.subTest(value=value):
                self.assertTrue(list(self.validator().iter_errors(dict(self.data(), schemaVersion=value))))

    def test_rejects_implicit_or_malformed_scopes(self):
        for scope in ("CTX-001", "sample/CTX-001/extra", "../CTX", "", "sample/CTX 001"):
            with self.subTest(scope=scope):
                data = {"schemaVersion": 1, "scopes": {scope: {}}}
                self.assertTrue(list(self.validator().iter_errors(data)))

    def test_rejects_unknown_view_and_empty_source_list(self):
        for views in ({"metrics": []}, {"risk": []}, {"release": {}}):
            with self.subTest(views=views):
                self.assertTrue(list(self.validator().iter_errors(
                    {"schemaVersion": 1, "scopes": {"sample/CTX-001": views}})))

    def test_rejects_network_traversal_anchors_and_non_file_paths(self):
        for value in ("https://example.invalid/data", "//server/share", r"\\server\share",
                      "../source.yaml", "source/../file.yaml", "./source.yaml", ".",
                      "/tmp/file.yaml", "C:/file.yaml", r"sources\file.yaml",
                      "source.yaml#view", " sources.yaml", "sources.yaml ", "source/\0file"):
            with self.subTest(path=value):
                data = self.data()
                data["scopes"]["sample/CTX-001"]["sequences"][0]["path"] = value
                self.assertTrue(list(self.validator().iter_errors(data)))

    def test_rejects_mutable_or_abbreviated_baselines(self):
        for value in ("HEAD", "main", "abc1234", "sha256:123", "", "A" * 40):
            with self.subTest(baseline=value):
                data = self.data()
                data["scopes"]["sample/CTX-001"]["sequences"][0]["baseline"] = value
                self.assertTrue(list(self.validator().iter_errors(data)))

    def test_rejects_duplicate_references_and_missing_reference_fields(self):
        for field in ("path", "baseline", "duplicate"):
            data = self.data()
            refs = data["scopes"]["sample/CTX-001"]["sequences"]
            if field == "duplicate":
                refs.append(copy.deepcopy(refs[0]))
            else:
                del refs[0][field]
            with self.subTest(field=field):
                self.assertTrue(list(self.validator().iter_errors(data)))

    def test_rejects_business_results_credentials_commands_and_write_switches(self):
        for field, value in (("command", "do-not-execute"), ("token", "not-a-secret"),
                             ("readOnly", False), ("status", "approved"),
                             ("body", "not a source copy"), ("result", "pass")):
            for level in ("root", "source"):
                with self.subTest(field=field, level=level):
                    data = self.data()
                    target = data if level == "root" else data["scopes"]["sample/CTX-001"]["sequences"][0]
                    target[field] = value
                    self.assertTrue(list(self.validator().iter_errors(data)))


def byte_baseline(path):
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def write_yaml(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8", newline="\n")
    return path


class ModelFixture(unittest.TestCase):
    def setUp(self):
        temporary = temporary_workspace()
        self.addCleanup(temporary.cleanup)
        self.workspace = Path(temporary.name)
        self.root = self.workspace / "модель € sources with spaces"
        self.root.mkdir()
        write_delivery_fixture(self.root)
        self.scope = "sample/CTX-001"

    def tool(self):
        self.assertIsNotNone(importlib.util.find_spec("export_model"),
                             "Task7 model exporter is not implemented")
        return importlib.import_module("export_model")

    def export(self, scope=None):
        return self.tool().export_view(self.root, self.scope if scope is None else scope)

    def manifest(self, views=None, scopes=None):
        return write_yaml(self.root / "model-sources.yaml", {
            "schemaVersion": 1, "scopes": scopes if scopes is not None else {self.scope: views or {}},
        })

    def select(self, view, path, baseline=None):
        return {view: [{"path": path.relative_to(self.root).as_posix(),
                        "baseline": byte_baseline(path) if baseline is None else baseline}]}

    def cli(self, *arguments, scope=None, root=None):
        script = WORKTREE / ".github" / "utilities" / "export_model.py"
        self.assertTrue(script.is_file(), "Task7 model CLI is not implemented")
        return subprocess.run(
            [sys.executable, "-B", "-X", "utf8", str(script),
             "--root", str(self.root if root is None else root),
             "--scope", self.scope if scope is None else scope, *arguments],
            cwd=self.workspace, shell=False, capture_output=True, text=True, encoding="utf-8",
        )

    def summary_sources(self):
        # All identities really exist with their source-owned explicit anchors.
        for identifier, kind, anchor, upstream in (
            ("UC-001", "use-case", "main", []),
            ("US-001", "user-story", "task", [self.scope + "/SR-001"]),
            ("ABB-001", "architecture-building-block", "structure", []),
            ("ADR-001", "architecture-decision", "decision", []),
            ("IP-001", "integration-partner", "contract", []),
            ("SEQ-001", "sequence-diagram", "diagram",
             [self.scope + "/ABB-001#structure", self.scope + "/IP-001#contract"]),
            ("QAS-001", "quality-attribute-scenario", "qas-001-ac-01", [self.scope + "/REQ-001"]),
            ("GOV-001", "review-record", "decision", []),
            ("RISK-001", "domain-model", "analysis", []),
            ("RC-001", "risk-control", "control", []),
            ("REL-001", "development-log", "release", []),
            ("CTX-001", "bounded-context", "scope", []),
        ):
            body = f'# {identifier}: Source record\n\n<a id="{anchor}"></a>\n'
            body += ("### QAS-001-AC-01: Measurable scenario\n" if identifier == "QAS-001" else f"## {anchor}\n")
            body += "The original notes are kept only in the source; the export does not copy this paragraph.\n"
            write_metadata(self.root, metadata(id=identifier, kind=kind, upstream=upstream),
                           body, f"records/{identifier}.md")
        write_metadata(self.root, metadata(id="TS-001", kind="validation-scenario", targets=[
            {"target": self.scope + "/QAS-001#qas-001-ac-01", "criterionAnchor": "criterion"}]),
            '# TS-001: Quality scenario\n<a id="criterion"></a>\n## Observation\n'
            'Compare the response with the original QAS metric under the given load.\n', "records/TS-001.md")
        (self.root / "evidence").mkdir(exist_ok=True)
        for name, anchor in (("governance", "decision"), ("change-control", "change"), ("run", "run")):
            (self.root / f"evidence/{name}.md").write_text(
                f'# Source-owned evidence\n<a id="{anchor}"></a>\n## {anchor}\n'
                "SOURCE-OWNED-CONTENT: recorded statement, not a model verdict.\n", encoding="utf-8")
        write_yaml(self.root / "evidence/utility.yaml", {"tree": {"quality": "source-owned grouping"}})
        (self.root / "evidence/scenario.feature").write_text(
            "Feature: Source-owned quality observation\n  Scenario: Declared measurement\n", encoding="utf-8")
        def ref(identifier, anchor):
            return self.scope + "/" + identifier + "#" + anchor
        def evidence(name, anchor=""):
            path = self.root / name
            return {"reference": name + ("#" + anchor if anchor else ""), "baseline": byte_baseline(path)}
        sources = {
            "requirements": {"srSummary": {"srVersion": "source-v1", "entries": [
                {"reqId": ref("REQ-001", "req-001-ac-01"), "srIds": [ref("SR-001", "sr-001-ac-01")],
                 "ucId": ref("UC-001", "main"), "status": "draft", "notes": "source-owned requirement note"}]}},
            "stories": {"storySummary": {"storyVersion": "source-v1", "entries": [
                {"srId": ref("SR-001", "sr-001-ac-01"), "usIds": [ref("US-001", "task")], "status": "todo"}]}},
            "architecture": {"abbSummary": {"abbVersion": "source-v1", "language": "source-selected",
                "framework": "source-selected", "blocks": [
                    {"abbId": ref("ABB-001", "structure"), "adrRef": ref("ADR-001", "decision")}],
                "integrations": [ref("IP-001", "contract")]}},
            "sequences": {"sequenceSummary": {"seqVersion": "source-v1", "entries": [
                {"seqId": ref("SEQ-001", "diagram"), "ucId": ref("UC-001", "main"),
                 "title": "Source-owned borrowing path", "hasAsync": False,
                 "externalPartners": [ref("IP-001", "contract")], "status": "draft"}]}},
            "verification": {"verificationSummary": {"vtVersion": "source-v1", "lastRunDate": "source-date",
                "entries": [{"usId": ref("US-001", "task"), "vtIds": [ref("VT-002", "record")],
                             "result": "not-run", "automatedCount": 0, "manualCount": 0,
                             "notes": "source-owned unexecuted plan"}],
                "evidenceRefs": [evidence("evidence/run.md", "run")]}},
            "quality": {"quality": {"qasRefs": [ref("QAS-001", "qas-001-ac-01")],
                "utilityTree": evidence("evidence/utility.yaml", "tree"),
                "testScenarios": [ref("TS-001", "criterion"), evidence("evidence/scenario.feature")]}},
            "governance": {"governanceSummary": {"govVersion": "source-v1", "entries": [
                {"govId": ref("GOV-001", "decision"), "status": "review-needed",
                 "ref": evidence("evidence/governance.md", "decision"), "notes": "source-owned limitations",
                 "reqIds": [ref("REQ-001", "req-001-ac-01")], "waiverRefs": []}]}},
            "risk": {"riskSummary": {"riskVersion": "source-v1", "entries": [
                {"riskId": ref("RISK-001", "analysis"), "title": "Source-owned risk",
                 "preMitigationLevel": "source-declared-before", "rcIds": [ref("RC-001", "control")],
                 "residualRiskLevel": "source-declared-after", "reqIds": [ref("REQ-001", "req-001-ac-02")],
                 "vtCoverage": [ref("VT-001", "reject")], "status": "review-needed"}]}},
            "release": {"releaseStatus": {"lifecycle": "source-lifecycle", "safetyClass": "source-only-class",
                "currentVersion": "source-only-version", "lastReleaseDate": "source-date",
                "nextPlannedRelease": "source-next", "changeControlRef": evidence("evidence/change-control.md", "change"),
                "releaseRef": ref("REL-001", "release"), "bcRefs": [ref("CTX-001", "scope")]}},
        }
        paths, selection = {}, {}
        for view, value in sources.items():
            path = write_yaml(self.root / f"sources/{view}.yaml", value)
            paths[view] = path
            selection.update(self.select(view, path))
        self.manifest(selection)
        return sources, paths, selection


class ModelExportTests(ModelFixture):
    def test_absent_manifest_keeps_nine_explicit_views_and_deterministic_primary_index(self):
        before, cwd = source_bytes(self.root), Path.cwd()
        first = self.export()
        second = self.export()
        self.assertEqual(first, second)
        self.assertEqual(sorted(VIEW_NAMES), list(first["views"]))
        self.assertEqual(5, len(first["artifacts"]))
        self.assertEqual(".", first["source"]["root"])
        self.assertRegex(first["source"]["baseline"], r"^sha256:[0-9a-f]{64}$")
        for view in first["views"].values():
            self.assertEqual("unverified", view["state"])
            self.assertEqual([], view["artifactRefs"])
            self.assertEqual([], view["evidenceRefs"])
            self.assertIn("model-sources.yaml", " ".join(view["gaps"]))
        schema = json.loads((CONTRACTS / "model.schema.json").read_bytes())
        self.assertEqual([], list(Draft202012Validator(schema).iter_errors(first)))
        self.assertEqual(before, source_bytes(self.root))
        self.assertEqual(cwd, Path.cwd())
        self.assertNotIn(str(self.root), json.dumps(first))

    def test_actual_artifact_bytes_and_sorted_canonical_relations_are_preserved(self):
        path = self.root / "software-requirements/SR-001.md"
        raw = path.read_bytes()
        path.write_bytes(b"\xef\xbb\xbf" + raw.replace(b"\n", b"\r\n"))
        model = self.export()
        self.assertEqual(sorted(item["key"] for item in model["artifacts"]), [item["key"] for item in model["artifacts"]])
        sr = next(a for a in model["artifacts"] if a["key"] == self.scope + "/SR-001")
        self.assertEqual(byte_baseline(path), sr["baseline"])
        self.assertEqual([self.scope + "/REQ-001#req-001-ac-01", self.scope + "/REQ-001#req-001-ac-02"], sr["upstream"])
        self.assertEqual([], model["implementationReports"])
        self.assertNotIn("contentState", sr)
        self.assertNotIn("body", sr)

    def test_same_id_two_explicit_scopes_does_not_merge_or_infer_scope(self):
        write_artifact(self.root, id="SR-001", scope="sample/CTX-002", kind="software-requirement",
                       relative_path="other/SR-001.md", acceptance_ids=("SR-001-AC-01",))
        self.manifest(scopes={"sample/CTX-002": {}})
        first, second = self.export(), self.export("sample/CTX-002")
        self.assertEqual(5, len(first["artifacts"]))
        self.assertEqual(["sample/CTX-002/SR-001"], [a["key"] for a in second["artifacts"]])
        self.assertNotEqual(first["scope"], second["scope"])
        self.assertIn("scope", " ".join(first["views"]["risk"]["gaps"]).lower())

    def test_invalid_primary_root_scope_version_and_duplicate_id_raise_input_errors(self):
        tool = self.tool()
        for root, scope, code in (
            (self.root / "absent", self.scope, "INVALID_ROOT"),
            (self.root, "CTX-001", "INVALID_SCOPE"), (self.root, "sample/CTX-999", "UNKNOWN_SCOPE"),
            (self.root, True, "INVALID_SCOPE"), (self.root, "", "INVALID_SCOPE"),
        ):
            with self.subTest(root=root, scope=scope):
                with self.assertRaises(ArtifactInputError) as caught:
                    tool.export_view(root, scope)
                self.assertEqual(code, caught.exception.code)
        write_artifact(self.root, schema_version=2, id="REQ-999")
        with self.assertRaises(ArtifactInputError) as caught:
            self.export()
        self.assertEqual("UNSUPPORTED_SCHEMA_VERSION", caught.exception.code)
        (self.root / "REQ-999.md").unlink()
        write_artifact(self.root, relative_path="duplicate/REQ-001.md")
        with self.assertRaises(ArtifactInputError) as caught:
            self.export()
        self.assertEqual("DUPLICATE_ARTIFACT_ID", caught.exception.code)

    def test_empty_primary_inventory_cannot_become_nine_empty_success_views(self):
        empty = self.workspace / "empty"
        empty.mkdir()
        with self.assertRaises(ArtifactInputError) as caught:
            self.tool().export_view(empty, self.scope)
        self.assertEqual("UNKNOWN_SCOPE", caught.exception.code)

    def test_primary_malformed_artifact_cannot_hide_behind_optional_source_selection(self):
        path = self.root / "software-requirements/SR-001.md"
        path.write_bytes(path.read_bytes().replace(b"schemaVersion: 1", b"schemaVersion: 2"))
        self.manifest(self.select("requirements", path))
        with self.assertRaises(ArtifactInputError) as caught:
            self.export()
        self.assertEqual("UNSUPPORTED_SCHEMA_VERSION", caught.exception.code)

    def test_primary_dangling_canonical_reference_is_not_optional_failure(self):
        path = self.root / "software-requirements/SR-001.md"
        path.write_text(path.read_text(encoding="utf-8").replace(
            "REQ-001#req-001-ac-01", "REQ-999#req-999-ac-01"), encoding="utf-8")
        with self.assertRaises(ArtifactInputError) as caught:
            self.export()
        self.assertEqual("DANGLING_REFERENCE", caught.exception.code)

    def test_absent_scope_and_absent_view_entries_have_distinct_gaps(self):
        self.manifest(scopes={"sample/CTX-002": {}})
        absent_scope = self.export()["views"]["risk"]["gaps"]
        self.manifest()
        absent_view = self.export()["views"]["risk"]["gaps"]
        self.assertNotEqual(absent_scope, absent_view)
        self.assertIn("scope", " ".join(absent_scope).lower())
        self.assertIn("view", " ".join(absent_view).lower())

    def test_malformed_supplied_manifest_is_config_error_not_optional_gap(self):
        path = self.root / "model-sources.yaml"
        for text in (
            "schemaVersion: [", "schemaVersion: 1\nschemaVersion: 1\nscopes: {}",
            "schemaVersion: 1.0\nscopes: {}", "schemaVersion: true\nscopes: {}",
            "schemaVersion: 1\nscopes: []", "schemaVersion: 1\nscopes: {}\ncommand: ignored",
            "schemaVersion: 1\nscopes: &cycle {sample/CTX-001: *cycle}",
            "schemaVersion: 1\nscopes:\n  sample/CTX-001:\n    risk:\n"
            "      - {path: sources/risk.yaml, baseline: HEAD}",
        ):
            with self.subTest(text=text):
                path.write_text(text, encoding="utf-8")
                with self.assertRaises(ArtifactInputError) as caught:
                    self.export()
                self.assertEqual("INVALID_SOURCE_MANIFEST", caught.exception.code)

    def test_duplicate_path_or_conflicting_baseline_is_configuration_error(self):
        path = self.root / "software-requirements/SR-001.md"
        entry = self.select("requirements", path)["requirements"][0]
        for views in (
            {"requirements": [entry, dict(entry, baseline="sha256:" + "0" * 64)]},
            {"requirements": [entry], "stories": [dict(entry, baseline="sha256:" + "0" * 64)]},
        ):
            with self.subTest(views=views):
                self.manifest(views)
                with self.assertRaises(ArtifactInputError) as caught:
                    self.export()
                self.assertEqual("INVALID_SOURCE_MANIFEST", caught.exception.code)

    def test_all_nine_summary_sources_preserve_refs_without_copying_owned_values(self):
        _, paths, _ = self.summary_sources()
        before = source_bytes(self.root)
        model = self.export()
        self.assertEqual({view: "available" for view in VIEW_NAMES},
                         {view: data["state"] for view, data in model["views"].items()})
        seq = model["views"]["sequences"]
        self.assertEqual([self.scope + "/" + value for value in (
            "ABB-001#structure", "IP-001#contract", "SEQ-001#diagram", "UC-001#main")], seq["artifactRefs"])
        self.assertIn({"reference": "sources/sequences.yaml#sequenceSummary",
                       "baseline": byte_baseline(paths["sequences"])}, seq["evidenceRefs"])
        self.assertIn({"reference": "evidence/governance.md#decision",
                       "baseline": byte_baseline(self.root / "evidence/governance.md")},
                      model["views"]["governance"]["evidenceRefs"])
        self.assertIn(self.scope + "/REL-001#release", model["views"]["release"]["artifactRefs"])
        self.assertIn(self.scope + "/RC-001#control", model["views"]["risk"]["artifactRefs"])
        output = json.dumps(model, ensure_ascii=False)
        for value in ("source-only-class", "source-only-version", "source-declared-before",
                      "SOURCE-OWNED-CONTENT", "Source-owned borrowing path", "automatedCount"):
            self.assertNotIn(value, output)
        self.assertEqual(before, source_bytes(self.root))

    def test_removing_each_optional_source_preserves_other_views_and_empty_failed_refs(self):
        _, paths, _ = self.summary_sources()
        for view, path in paths.items():
            with self.subTest(view=view):
                raw = path.read_bytes()
                path.unlink()
                model = self.export()
                affected = model["views"][view]
                self.assertEqual("unverified", affected["state"])
                self.assertEqual([], affected["artifactRefs"])
                self.assertEqual([], affected["evidenceRefs"])
                self.assertIn(path.relative_to(self.root).as_posix(), " ".join(affected["gaps"]))
                self.assertEqual({"available"}, {data["state"] for name, data in model["views"].items() if name != view})
                path.write_bytes(raw)

    def test_malformed_optional_yaml_and_bad_types_are_unverified_not_partial(self):
        _, paths, selection = self.summary_sources()
        path = paths["sequences"]
        for raw in (b"sequenceSummary: [", b"sequenceSummary: 9",
                    b"sequenceSummary: {seqVersion: 1, entries: []}",
                    b"sequenceSummary: {seqVersion: one, entries: nope}",
                    b"sequenceSummary: {seqVersion: one, seqVersion: two}",
                    b"\xff\xfeinvalid"):
            with self.subTest(raw=raw):
                path.write_bytes(raw)
                selection["sequences"][0]["baseline"] = byte_baseline(path)
                self.manifest(selection)
                view = self.export()["views"]["sequences"]
                self.assertEqual("unverified", view["state"])
                self.assertEqual([], view["artifactRefs"])
                self.assertTrue(view["gaps"])

    def test_unreadable_optional_file_is_explicit_injected_io_gap(self):
        _, paths, _ = self.summary_sources()
        read = Path.read_bytes
        def deny_selected(path):
            if path == paths["risk"]:
                raise PermissionError("Injected optional source is unavailable")
            return read(path)
        self.tool()
        with patch.object(Path, "read_bytes", deny_selected):
            model = self.export()
        self.assertEqual("unverified", model["views"]["risk"]["state"])
        self.assertIn("FILE_READ_ERROR", " ".join(model["views"]["risk"]["gaps"]))
        self.assertEqual("available", model["views"]["release"]["state"])

    def test_unverifiable_optional_baseline_is_concrete_gap_not_primary_success_claim(self):
        _, _, selection = self.summary_sources()
        for baseline in ("sha256:" + "0" * 64, "0" * 40):
            with self.subTest(baseline=baseline):
                selection["risk"][0]["baseline"] = baseline
                self.manifest(selection)
                model = self.export()
                self.assertEqual("unverified", model["views"]["risk"]["state"])
                self.assertIn("BASE", " ".join(model["views"]["risk"]["gaps"]))
                self.assertEqual("available", model["views"]["quality"]["state"])

    def test_each_valid_incomplete_summary_keeps_known_refs_and_exact_field_gap(self):
        sources, paths, selection = self.summary_sources()
        fields = {
            "requirements": ("srSummary", "srVersion"), "stories": ("storySummary", "storyVersion"),
            "architecture": ("abbSummary", "framework"), "sequences": ("sequenceSummary", "seqVersion"),
            "verification": ("verificationSummary", "lastRunDate"), "quality": ("quality", "testScenarios"),
            "governance": ("governanceSummary", "govVersion"), "risk": ("riskSummary", "riskVersion"),
            "release": ("releaseStatus", "lifecycle"),
        }
        for view, (container, field) in fields.items():
            with self.subTest(view=view):
                data = copy.deepcopy(sources[view])
                del data[container][field]
                write_yaml(paths[view], data)
                selection[view][0]["baseline"] = byte_baseline(paths[view])
                self.manifest(selection)
                affected = self.export()["views"][view]
                self.assertEqual("partial", affected["state"])
                self.assertTrue(affected["artifactRefs"])
                self.assertIn(container + "." + field, " ".join(affected["gaps"]))
                write_yaml(paths[view], sources[view])
                selection[view][0]["baseline"] = byte_baseline(paths[view])

    def test_missing_entry_field_is_partial_but_wrong_boolean_or_count_type_is_malformed(self):
        sources, paths, selection = self.summary_sources()
        del sources["sequences"]["sequenceSummary"]["entries"][0]["externalPartners"]
        write_yaml(paths["sequences"], sources["sequences"])
        selection["sequences"][0]["baseline"] = byte_baseline(paths["sequences"])
        self.manifest(selection)
        view = self.export()["views"]["sequences"]
        self.assertEqual("partial", view["state"])
        self.assertIn("entries[0].externalPartners", " ".join(view["gaps"]))
        sources["sequences"]["sequenceSummary"]["entries"][0]["hasAsync"] = "false"
        sources["verification"]["verificationSummary"]["entries"][0]["manualCount"] = True
        for name in ("sequences", "verification"):
            write_yaml(paths[name], sources[name])
            selection[name][0]["baseline"] = byte_baseline(paths[name])
        self.manifest(selection)
        model = self.export()
        self.assertEqual("unverified", model["views"]["sequences"]["state"])
        self.assertEqual("unverified", model["views"]["verification"]["state"])

    def test_dangling_optional_canonical_or_evidence_anchor_is_unverified(self):
        sources, paths, selection = self.summary_sources()
        for reference in ("sample/CTX-001/SEQ-999#diagram", "sample/CTX-001/SEQ-001#absent"):
            sources["sequences"]["sequenceSummary"]["entries"][0]["seqId"] = reference
            write_yaml(paths["sequences"], sources["sequences"])
            selection["sequences"][0]["baseline"] = byte_baseline(paths["sequences"])
            self.manifest(selection)
            self.assertEqual("unverified", self.export()["views"]["sequences"]["state"])
        sources["governance"]["governanceSummary"]["entries"][0]["ref"]["reference"] = "evidence/governance.md#absent"
        write_yaml(paths["governance"], sources["governance"])
        selection["governance"][0]["baseline"] = byte_baseline(paths["governance"])
        self.manifest(selection)
        self.assertEqual("unverified", self.export()["views"]["governance"]["state"])

    def test_quality_retains_qas_req_ts_and_feature_evidence_relationships(self):
        _, _, _ = self.summary_sources()
        view = self.export()["views"]["quality"]
        for reference in ("QAS-001#qas-001-ac-01", "REQ-001#req-001-ac-01", "REQ-001#req-001-ac-02", "TS-001#criterion"):
            self.assertIn(self.scope + "/" + reference, view["artifactRefs"])
        self.assertIn({"reference": "evidence/scenario.feature",
                       "baseline": byte_baseline(self.root / "evidence/scenario.feature")}, view["evidenceRefs"])

    def test_direct_existing_markdown_needs_no_duplicate_summary(self):
        self.manifest(self.select("requirements", self.root / "software-requirements/SR-001.md"))
        model = self.export()
        view = model["views"]["requirements"]
        self.assertEqual("partial", view["state"])  # UC is not supplied by this delivery.
        self.assertIn(self.scope + "/SR-001#sr-001-ac-02", view["artifactRefs"])
        self.assertIn(self.scope + "/REQ-001#req-001-ac-02", view["artifactRefs"])
        self.assertTrue(any("use-case" in gap for gap in view["gaps"]))
        self.assertIn({"reference": "software-requirements/SR-001.md",
                       "baseline": byte_baseline(self.root / "software-requirements/SR-001.md")}, view["evidenceRefs"])

    def test_exact_local_git_commit_and_blob_sources_are_verified_without_filters(self):
        _, paths, selection = self.summary_sources()
        seed_git_repo(self.root)
        git(self.root, "add", "--", ".")
        git(self.root, "commit", "--quiet", "-m", "Local summary snapshot")
        commit = git(self.root, "rev-parse", "HEAD")
        blob = git(self.root, "rev-parse", f"{commit}:sources/sequences.yaml")
        marker = self.workspace / "filter-was-executed"
        git(self.root, "config", "diff.external", f"forbidden-command-{marker.name}")
        for baseline in (commit, blob):
            selection["sequences"][0]["baseline"] = baseline
            self.manifest(selection)
            before = source_bytes(self.root)
            view = self.export()["views"]["sequences"]
            self.assertEqual("available", view["state"])
            self.assertIn({"reference": "sources/sequences.yaml#sequenceSummary", "baseline": baseline}, view["evidenceRefs"])
            self.assertEqual(before, source_bytes(self.root))
            self.assertFalse(marker.exists())
        # A real tree and an unrelated real blob are not interchangeable file baselines.
        for baseline in (git(self.root, "rev-parse", f"{commit}^{{tree}}"),
                         git(self.root, "rev-parse", f"{commit}:README.md")):
            selection["sequences"][0]["baseline"] = baseline
            self.manifest(selection)
            self.assertEqual("unverified", self.export()["views"]["sequences"]["state"])

    def test_model_identity_tracks_yaml_selection_and_evidence_not_just_markdown(self):
        sources, paths, selection = self.summary_sources()
        original = self.export()
        sources["sequences"]["sequenceSummary"]["entries"][0]["title"] = "Changed only at its owner"
        write_yaml(paths["sequences"], sources["sequences"])
        selection["sequences"][0]["baseline"] = byte_baseline(paths["sequences"])
        self.manifest(selection)
        changed = self.export()
        self.assertNotEqual(original["source"]["baseline"], changed["source"]["baseline"])
        # Changing only source selection is also an input change, even if refs deduplicate.
        with (self.root / "model-sources.yaml").open("a", encoding="utf-8") as stream:
            stream.write("# source selection was reviewed locally\n")
        self.assertNotEqual(changed["source"]["baseline"], self.export()["source"]["baseline"])

    def test_persisted_model_check_detects_source_drift_without_repair(self):
        sources, paths, _ = self.summary_sources()
        model_path = write_yaml(self.workspace / "persisted.yaml", self.export())
        clean = self.tool().check_model(self.root, self.scope, model_path)
        self.assertEqual("clean", clean.status)
        saved = model_path.read_bytes()
        sources["risk"]["riskSummary"]["entries"][0]["title"] = "Source-only edited risk"
        write_yaml(paths["risk"], sources["risk"])  # Leave manifest at the old fixed SHA.
        changed = self.tool().check_model(self.root, self.scope, model_path)
        self.assertEqual("invalid", changed.status)
        self.assertIn("STALE_MODEL_SOURCE", [f.code for f in changed.findings])
        self.assertEqual(saved, model_path.read_bytes())

    def test_manually_edited_valid_view_detected_without_auto_repair(self):
        self.summary_sources()
        model = self.export()
        model["views"]["sequences"]["artifactRefs"].remove(self.scope + "/UC-001#main")
        path = write_yaml(self.workspace / "manually-edited.yaml", model)
        before = path.read_bytes()
        report = self.tool().check_model(self.root, self.scope, path)
        self.assertEqual("invalid", report.status)
        self.assertIn("MODEL_MISMATCH", [f.code for f in report.findings])
        self.assertEqual(before, path.read_bytes())

    def test_invalid_persisted_model_schema_is_input_error(self):
        model = self.export()
        model["schemaVersion"] = 2
        path = write_yaml(self.workspace / "bad.yaml", model)
        report = self.tool().check_model(self.root, self.scope, path)
        self.assertEqual("input-error", report.status)
        self.assertIn("UNSUPPORTED_SCHEMA_VERSION", [f.code for f in report.findings])
        model["schemaVersion"] = 1
        model["source"]["baseline"] = "HEAD"
        write_yaml(path, model)
        report = self.tool().check_model(self.root, self.scope, path)
        self.assertEqual("input-error", report.status)
        self.assertIn("INVALID_MODEL", [f.code for f in report.findings])
        self.assertEqual(2, self.cli("--check", str(path)).returncode)

    def test_derived_model_and_manifest_cannot_become_validated_sources(self):
        model_path = write_yaml(self.root / "derived.yaml", self.export())
        self.manifest(self.select("risk", model_path))
        view = self.export()["views"]["risk"]
        self.assertEqual("unverified", view["state"])
        self.assertIn("DERIVED_SOURCE", " ".join(view["gaps"]))
        self.manifest({"risk": [{"path": "model-sources.yaml", "baseline": "sha256:" + "0" * 64}]})
        with self.assertRaises(ArtifactInputError) as caught:
            self.export()
        self.assertEqual("INVALID_SOURCE_MANIFEST", caught.exception.code)

    def test_model_cli_default_output_and_checks_have_real_exits_and_protect_inputs(self):
        before = source_bytes(self.root)
        default = self.cli()
        self.assertEqual(0, default.returncode, default.stdout + default.stderr)
        self.assertEqual(self.scope, json.loads(default.stdout)["scope"])
        self.assertEqual(before, source_bytes(self.root))
        path = self.workspace / "model.json"
        written = self.cli("--output", str(path))
        self.assertEqual(0, written.returncode, written.stdout + written.stderr)
        check = self.cli("--check", str(path))
        self.assertEqual(0, check.returncode, check.stdout + check.stderr)
        saved = path.read_bytes()
        conflict = self.cli("--output", str(path))
        self.assertEqual(2, conflict.returncode)
        self.assertEqual(saved, path.read_bytes())
        data = json.loads(saved)
        data["views"]["risk"]["gaps"] = ["manually replaced gap"]
        path.write_text(json.dumps(data), encoding="utf-8")
        mismatch = self.cli("--check", str(path))
        self.assertEqual(1, mismatch.returncode, mismatch.stdout + mismatch.stderr)
        bad = self.cli(scope="CTX-001")
        self.assertEqual(2, bad.returncode)
        self.assertEqual(before, source_bytes(self.root))

    def test_output_errors_do_not_overwrite_sources_or_create_model_on_invalid_input(self):
        manifest = self.manifest()
        before = source_bytes(self.root)
        for output in (manifest, self.root / "software-requirements/SR-001.md",
                       self.workspace / "absent-parent/model.yaml"):
            with self.subTest(output=output):
                result = self.cli("--output", str(output))
                self.assertEqual(2, result.returncode, result.stdout + result.stderr)
                self.assertEqual(before, source_bytes(self.root))
        new = self.workspace / "must-not-exist.yaml"
        failed = self.cli("--output", str(new), scope="bad")
        self.assertEqual(2, failed.returncode)
        self.assertFalse(new.exists())


class ModelBoundaryTests(ModelFixture):
    def test_nested_evidence_gap_locates_the_failed_source_without_absolute_path(self):
        self.summary_sources()
        (self.root / "evidence/governance.md").unlink()
        view = self.export()["views"]["governance"]
        self.assertEqual("unverified", view["state"])
        self.assertIn("evidence/governance.md", " ".join(view["gaps"]))
        self.assertNotIn(str(self.root), json.dumps(view))

    def test_explicit_direct_sources_are_combined_before_kind_completeness_check(self):
        uc = write_metadata(self.root, metadata(id="UC-001", kind="use-case"),
                            '# UC-001: Business path\n<a id="main"></a>\n## Normal path\n'
                            'A member submits a loan request, handled per the original rule.\n',
                            "domain-model/UC-001.md")
        views = self.select("requirements", self.root / "software-requirements/SR-001.md")
        views["requirements"] += self.select("requirements", uc)["requirements"]
        self.manifest(views)
        view = self.export()["views"]["requirements"]
        self.assertEqual("available", view["state"])
        self.assertEqual([], view["gaps"])
        self.assertIn(self.scope + "/UC-001#main", view["artifactRefs"])

    def test_header_only_direct_source_is_partial_not_available(self):
        source = write_metadata(self.root, metadata(id="GOV-001", kind="review-record"),
                                '# GOV-001: Decision record\n<a id="decision"></a>\n## Record\n'
                                '| Item | Content |\n|---|---|\n', "records/GOV-001.md")
        self.manifest(self.select("governance", source))
        view = self.export()["views"]["governance"]
        self.assertEqual("partial", view["state"])
        self.assertIn("decision", " ".join(view["gaps"]))

    def test_sequence_code_elsewhere_cannot_fill_missing_diagram_section(self):
        uc = write_metadata(self.root, metadata(id="UC-001", kind="use-case"),
                            '# UC-001: Business path\n<a id="main"></a>\n## Path\nActual source.\n',
                            "domain-model/UC-001.md")
        abb = write_metadata(self.root, metadata(id="ABB-001", kind="architecture-building-block"),
                             '# ABB-001: Responsibility\n' + "".join(
                                 f'<a id="{anchor}"></a>\n## {anchor}\n'
                                 'The source states the responsibility and version boundary of this building block.\n'
                                 for anchor in ("structure", "interfaces", "runtime")), "records/ABB-001.md")
        seq = write_metadata(self.root, metadata(id="SEQ-001", kind="sequence-diagram",
                             upstream=[self.scope + "/UC-001#main", self.scope + "/ABB-001#structure"]),
                             '# SEQ-001: Path\n' + "".join(
                                 f'<a id="{anchor}"></a>\n## {anchor}\n'
                                 'This section states the existing participants, messages, and source limitations.\n'
                                 for anchor in ("basis", "participants", "paths"))
                             + '\n```mermaid\nsequenceDiagram\n  participant Member\n```\n',
                             "records/SEQ-001.md")
        seq.write_text(seq.read_text(encoding="utf-8")
                       .replace("## paths\n", "## paths\n| hasAsync | false |\n")
                       .replace("## participants\n", "## participants\n| externalPartners | No external partners |\n"),
                       encoding="utf-8")
        self.manifest(self.select("sequences", seq))
        view = self.export()["views"]["sequences"]
        self.assertEqual("partial", view["state"])
        self.assertIn("diagram", " ".join(view["gaps"]))
        with seq.open("a", encoding="utf-8") as stream:
            stream.write('<a id="diagram"></a>\n## Original diagram\n```mermaid\n'
                         'sequenceDiagram\n    participant Member\n    participant Clerk\n'
                         '    Member->>Clerk: Known borrowing request\n```\n')
        self.manifest(self.select("sequences", seq))
        self.assertEqual("available", self.export()["views"]["sequences"]["state"])

    def test_cross_scope_refs_keep_actual_source_path_and_byte_baseline(self):
        sources, paths, selection = self.summary_sources()
        other = write_metadata(self.root, metadata(id="UC-001", kind="use-case", scope="other/CTX-002"),
                               '# UC-001: External context path\n<a id="main"></a>\n## Path\n'
                               'This known source is in another explicit scope.\n', "other/UC-001.md")
        sources["sequences"]["sequenceSummary"]["entries"][0]["ucId"] = "other/CTX-002/UC-001#main"
        write_yaml(paths["sequences"], sources["sequences"])
        selection["sequences"][0]["baseline"] = byte_baseline(paths["sequences"])
        self.manifest(selection)
        model = self.export()
        view = model["views"]["sequences"]
        self.assertIn("other/CTX-002/UC-001#main", view["artifactRefs"])
        self.assertNotIn("other/CTX-002/UC-001", [a["key"] for a in model["artifacts"]])
        self.assertIn({"reference": "other/UC-001.md", "baseline": byte_baseline(other)}, view["evidenceRefs"])

    def test_check_uses_the_same_schema_snapshot_as_derivation(self):
        model_path = write_yaml(self.workspace / "checked.yaml", self.export())
        read = Path.read_bytes
        count = 0
        def fail_second_schema_read(path):
            nonlocal count
            if path == CONTRACTS / "model.schema.json":
                count += 1
                if count > 1:
                    raise PermissionError("Injected concurrent contract disappearance")
            return read(path)
        with patch.object(Path, "read_bytes", fail_second_schema_read):
            report = self.tool().check_model(self.root, self.scope, model_path)
        self.assertEqual("clean", report.status)
        self.assertEqual(1, count)

    def test_evidence_byte_drift_is_in_identity_even_if_selected_yaml_did_not_change(self):
        self.summary_sources()
        original = self.export()
        path = self.root / "evidence/scenario.feature"
        path.write_bytes(path.read_bytes() + b"  # changed only the source-owned feature\n")
        current = self.export()
        self.assertNotEqual(original["source"]["baseline"], current["source"]["baseline"])
        self.assertEqual("unverified", current["views"]["quality"]["state"])

    def test_nonlocal_selection_rejected_before_read_and_does_not_expand_environment(self):
        for path in ("https://example.invalid/source.yaml", "../outside.yaml", r"\\server\share\file",
                     ".git/config", ".venv/source.yaml"):
            with self.subTest(path=path):
                self.manifest({"risk": [{"path": path, "baseline": "sha256:" + "0" * 64}]})
                with self.assertRaises(ArtifactInputError) as caught:
                    self.export()
                self.assertEqual("INVALID_SOURCE_MANIFEST", caught.exception.code)

    def test_real_cli_missing_schema_is_input_error_and_no_output_file(self):
        tool_dir = self.workspace / "installed/.github/utilities"
        contract_dir = tool_dir.parent / "contracts"
        tool_dir.mkdir(parents=True)
        contract_dir.mkdir()
        for name in ("artifact_io.py", "check_artifacts.py", "check_traceability.py", "vt_records.py", "export_model.py"):
            source = WORKTREE / ".github" / "utilities" / name
            self.assertTrue(source.is_file(), "Task7 module is not implemented")
            (tool_dir / name).write_bytes(source.read_bytes())
        for name in ("artifact.schema.json", "model-sources.schema.json"):
            (contract_dir / name).write_bytes((CONTRACTS / name).read_bytes())
        output = self.workspace / "must-not-be-created.json"
        result = subprocess.run(
            [sys.executable, "-B", "-X", "utf8", str(tool_dir / "export_model.py"),
             "--root", str(self.root), "--scope", self.scope, "--output", str(output)],
            cwd=self.workspace, shell=False, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(2, result.returncode, result.stdout + result.stderr)
        self.assertEqual("CONTRACT_ERROR", json.loads(result.stdout)["findings"][0]["code"])
        self.assertFalse(output.exists())

    def test_explicit_new_output_cannot_replace_a_missing_registered_source(self):
        selected = self.root / "sources/release.yaml"
        selected.parent.mkdir()
        self.manifest({"release": [{"path": "sources/release.yaml", "baseline": "sha256:" + "0" * 64}]})
        before = source_bytes(self.root)
        result = self.cli("--output", str(selected))
        self.assertEqual(2, result.returncode, result.stdout + result.stderr)
        self.assertEqual("REPORT_CONFLICT", json.loads(result.stdout)["findings"][0]["code"])
        self.assertEqual(before, source_bytes(self.root))
        self.assertFalse(selected.exists())

    def test_invalid_local_contract_object_fails_as_input_not_empty_validation(self):
        self.tool()
        read = Path.read_bytes
        for name in ("model", "model-sources"):
            for raw in (b"true", b"{}"):
                with self.subTest(schema=name, raw=raw):
                    def invalid_contract(path):
                        if path == CONTRACTS / (name + ".schema.json"):
                            return raw
                        return read(path)
                    with patch.object(Path, "read_bytes", invalid_contract):
                        with self.assertRaises(ArtifactInputError) as caught:
                            self.export()
                    self.assertEqual("CONTRACT_ERROR", caught.exception.code)

    def test_direct_release_needs_source_owned_fields_not_just_nonempty_sections(self):
        source = write_metadata(self.root, metadata(id="REL-001", kind="development-log"),
                                '# REL-001: Release source\n<a id="release"></a>\n## Release record\n'
                                'There is a paragraph here, but it is not the lifecycle and version fields.\n'
                                '<a id="change-control"></a>\n## Change control\n'
                                'This section locates the basis for this change.\n',
                                "records/REL-001.md")
        self.manifest(self.select("release", source))
        view = self.export()["views"]["release"]
        self.assertEqual("partial", view["state"])
        for field in ("lifecycle", "safetyClass", "currentVersion", "lastReleaseDate", "nextPlannedRelease"):
            self.assertIn("releaseStatus." + field, " ".join(view["gaps"]))
        text = source.read_text(encoding="utf-8").replace(
            "## Release record\n", "## Release record\n"
            "| lifecycle | source-declared lifecycle |\n| safetyClass | source-declared class |\n"
            "| currentVersion | source-version |\n| lastReleaseDate | source-date |\n"
            "| nextPlannedRelease | source-next |\n")
        source.write_text(text, encoding="utf-8")
        self.manifest(self.select("release", source))
        self.assertEqual("available", self.export()["views"]["release"]["state"])

    def test_direct_quality_missing_measure_is_partial_even_when_other_fields_are_filled(self):
        qas = write_metadata(self.root, metadata(id="QAS-001", kind="quality-attribute-scenario",
                             upstream=[self.scope + "/REQ-001"]),
                             '# QAS-001: Response scenario\n<a id="scenario"></a>\n## Six elements\n'
                             '| Source of stimulus: who or what initiates it | A user named in the source |\n'
                             '| Stimulus: what happens | A submit request stated in the source |\n'
                             '| Environment: under which operational or business conditions '
                             '| The specified controlled environment |\n'
                             '| Object: which business process or affected object | The loan record process |\n'
                             '| Response: what should be observed | An observable result is returned |\n'
                             '<a id="measurement"></a>\n## Measurement basis\n'
                             'The original measurement method is described in this source.\n'
                             '<a id="qas-001-ac-01"></a>\n### QAS-001-AC-01: Response\n'
                             'The target is still owned by this QAS.\n', "records/QAS-001.md")
        write_metadata(self.root, metadata(id="TS-001", kind="validation-scenario", targets=[
            {"target": self.scope + "/QAS-001#qas-001-ac-01", "criterionAnchor": "criterion"}]),
            '# TS-001: Measurement plan\n<a id="criterion"></a>\n## Independent measurement\n'
            'Compare the actual value with the source measure.\n',
            "records/TS-001.md")
        # Fix1 isolates the missing field: QAS AND an actual utility-tree source
        # must exist before field incompleteness can legitimately be partial.
        # The original partial/responseMeasure assertions below are unchanged.
        tree = write_yaml(self.root / "evidence/utility.yaml",
                          {"tree": {"Responsiveness": [self.scope + "/QAS-001#qas-001-ac-01"]}})
        selected = self.select("quality", qas)
        selected["quality"] += self.select("quality", tree)["quality"]
        self.manifest(selected)
        view = self.export()["views"]["quality"]
        self.assertEqual("partial", view["state"])
        self.assertIn("responseMeasure", " ".join(view["gaps"]))

    def test_direct_views_do_not_infer_summary_fields_from_generic_prose(self):
        self.summary_sources()
        def replace_body(identifier, kind, anchors, upstream=()):
            return write_metadata(
                self.root, metadata(id=identifier, kind=kind, upstream=list(upstream)),
                f"# {identifier}: Original record\n" + "".join(
                    f'<a id="{anchor}"></a>\n## {anchor}\n'
                    'A source note already exists; it does not replace explicit fields.\n'
                    for anchor in anchors), f"records/{identifier}.md")
        us = replace_body("US-001", "user-story", ("task", "checklist"), (self.scope + "/SR-001",))
        abb = replace_body("ABB-001", "architecture-building-block", ("structure", "interfaces", "runtime"))
        seq = replace_body("SEQ-001", "sequence-diagram", ("basis", "participants", "paths", "diagram"),
                           (self.scope + "/UC-001#main", self.scope + "/ABB-001#structure",
                            self.scope + "/IP-001#contract"))
        rc = replace_body("RC-001", "risk-control", ("analysis", "control", "residual"),
                          (self.scope + "/REQ-001", self.scope + "/VT-001"))
        for name in ("VT-001", "VT-002"):
            path = self.root / f"verification/{name}.md"
            path.write_text(path.read_text(encoding="utf-8").replace(
                "## Per-target criteria\n",
                "## Per-target criteria\nEach target below has its own actual source criterion.\n"),
                encoding="utf-8")
        for view, selected, field in (
            ("stories", [us], "storySummary.status"),
            ("architecture", [abb, self.root / "records/ADR-001.md"], "abbSummary.language"),
            ("sequences", [seq], "sequenceSummary.hasAsync"),
            ("verification", [self.root / "verification/VT-002.md"], "verificationSummary.lastRunDate"),
            ("governance", [self.root / "records/GOV-001.md"], "governanceSummary.status"),
            ("risk", [rc], "riskSummary.preMitigationLevel"),
        ):
            with self.subTest(view=view):
                self.manifest({view: [{"path": path.relative_to(self.root).as_posix(),
                                      "baseline": byte_baseline(path)} for path in selected]})
                result = self.export()["views"][view]
                self.assertEqual("partial", result["state"])
                self.assertIn(field, " ".join(result["gaps"]))


class QualityViewTests(ModelFixture):
    """T7-I1: direct quality needs both original QAS and utility-tree sources."""

    def quality_sources(self, *, tree=True, measure=True):
        qas = write_metadata(
            self.root, metadata(id="QAS-001", kind="quality-attribute-scenario",
                                upstream=[self.scope + "/REQ-001"]),
            '# QAS-001: Response scenario\n<a id="scenario"></a>\n## Six elements\n'
            '| Source of stimulus: who or what initiates it | A valid member stated in the source |\n'
            '| Stimulus: what happens | Submit a within-allowance loan request |\n'
            '| Environment: under which operational or business conditions | Controlled input stated in the source |\n'
            '| Object: which business process or affected object | The loan record process |\n'
            '| Response: what should be observed | Return the record defined by the source |\n'
            + ('| Response measure: measurable criterion, unit, and scope '
               '| Check this record count against the original source |\n' if measure else '')
            + '<a id="measurement"></a>\n## Measurement basis\n'
            'Source-owned measurement method and limitations.\n'
            '<a id="qas-001-ac-01"></a>\n### QAS-001-AC-01: Record response\n'
            'The independent response criterion is owned by this QAS.\n', "records/QAS-001.md")
        write_metadata(
            self.root, metadata(id="TS-001", kind="validation-scenario", targets=[
                {"target": self.scope + "/QAS-001#qas-001-ac-01", "criterionAnchor": "criterion"}]),
            '# TS-001: Measurement plan\n<a id="criterion"></a>\n## Measurement\n'
            'Compare the response with the QAS source criterion without running the application.\n',
            "records/TS-001.md")
        selections = self.select("quality", qas)
        tree_path = self.root / "evidence/utility.yaml"
        if tree:
            write_yaml(tree_path, {"tree": {"Responsiveness": [self.scope + "/QAS-001#qas-001-ac-01"]}})
            selections["quality"] += self.select("quality", tree_path)["quality"]
        self.manifest(selections)
        return qas, tree_path, selections

    def test_fix1_i1_missing_tree_is_unverified_not_available(self):
        self.quality_sources(tree=False)
        before = source_bytes(self.root)
        view = self.export()["views"]["quality"]
        self.assertEqual("unverified", view["state"])
        self.assertEqual([], view["artifactRefs"])
        self.assertEqual([], view["evidenceRefs"])
        self.assertIn("utility", " ".join(view["gaps"]).lower())
        self.assertEqual(before, source_bytes(self.root))

    def test_fix1_i1_real_tree_is_referenced_and_in_source_identity(self):
        _, tree, selected = self.quality_sources()
        before = source_bytes(self.root)
        model = self.export()
        view = model["views"]["quality"]
        self.assertEqual("available", view["state"])
        self.assertEqual([], view["gaps"])
        self.assertIn({"reference": "evidence/utility.yaml#tree", "baseline": byte_baseline(tree)}, view["evidenceRefs"])
        self.assertEqual(before, source_bytes(self.root))
        write_yaml(tree, {"tree": {"Changed source grouping": [self.scope + "/QAS-001#qas-001-ac-01"]}})
        selected["quality"][1]["baseline"] = byte_baseline(tree)
        self.manifest(selected)
        changed = self.export()
        self.assertNotEqual(model["source"]["baseline"], changed["source"]["baseline"])
        self.assertNotIn("Changed source grouping", json.dumps(changed))

    def test_fix1_i1_missing_qas_is_unverified_with_no_refs(self):
        tree = write_yaml(self.root / "evidence/utility.yaml", {"tree": {"Responsiveness": []}})
        self.manifest(self.select("quality", tree))
        view = self.export()["views"]["quality"]
        self.assertEqual("unverified", view["state"])
        self.assertEqual([], view["artifactRefs"])
        self.assertEqual([], view["evidenceRefs"])
        self.assertIn("QAS", " ".join(view["gaps"]))

    def test_fix1_i1_known_sources_but_missing_measure_remains_partial(self):
        self.quality_sources(measure=False)
        view = self.export()["views"]["quality"]
        self.assertEqual("partial", view["state"])
        self.assertTrue(view["artifactRefs"] and view["evidenceRefs"])
        self.assertIn("responseMeasure", " ".join(view["gaps"]))

    def test_fix1_i1_declared_tree_missing_unreadable_shape_and_empty_items(self):
        _, tree, selected = self.quality_sources()
        tree.unlink()
        absent = self.export()["views"]["quality"]
        self.assertEqual("unverified", absent["state"])
        self.assertIn("evidence/utility.yaml", " ".join(absent["gaps"]))
        for data, expected in (({"tree": 4}, "unverified"), ({"tree": {}}, "partial")):
            with self.subTest(data=data):
                write_yaml(tree, data)
                selected["quality"][1]["baseline"] = byte_baseline(tree)
                self.manifest(selected)
                self.assertEqual(expected, self.export()["views"]["quality"]["state"])


class ModelOutputTests(ModelFixture):
    """T7-I2: reservation is based on declarations, not successful dereferences."""

    def test_fix1_i2_missing_utility_reference_cannot_be_output(self):
        self.summary_sources()
        missing = self.root / "evidence/utility.yaml"
        missing.unlink()
        before = source_bytes(self.root)
        result = self.cli("--output", str(missing))
        self.assertEqual(2, result.returncode, result.stdout + result.stderr)
        self.assertIn("REPORT_CONFLICT", [f["code"] for f in json.loads(result.stdout)["findings"]])
        self.assertEqual(before, source_bytes(self.root))
        self.assertFalse(missing.exists())

    def test_fix1_i2_later_nested_reference_reserved_after_an_earlier_failure(self):
        sources, paths, selected = self.summary_sources()
        later = write_yaml(self.root / "evidence/later.yaml", {"record": "Actual source-owned record"})
        sources["quality"]["quality"]["evidenceRefs"] = [
            {"reference": "evidence/later.yaml#record", "baseline": byte_baseline(later)}]
        write_yaml(paths["quality"], sources["quality"])
        selected["quality"][0]["baseline"] = byte_baseline(paths["quality"])
        self.manifest(selected)
        (self.root / "evidence/utility.yaml").unlink()
        later.unlink()
        old = self.workspace / "old-output.json"
        old.write_bytes(b'{"old":"must remain unchanged"}\n')
        before, old_bytes = source_bytes(self.root), old.read_bytes()
        result = self.cli("--output", str(later))
        self.assertEqual(2, result.returncode, result.stdout + result.stderr)
        self.assertIn("REPORT_CONFLICT", [f["code"] for f in json.loads(result.stdout)["findings"]])
        self.assertFalse(later.exists())
        self.assertEqual(before, source_bytes(self.root))
        self.assertEqual(old_bytes, old.read_bytes())

    def test_fix1_i2_legitimate_export_check_round_trip_with_optional_gap(self):
        self.summary_sources()
        (self.root / "evidence/utility.yaml").unlink()
        before = source_bytes(self.root)
        output = self.root / "new-model.yaml"
        created = self.cli("--output", str(output))
        self.assertEqual(0, created.returncode, created.stdout + created.stderr)
        saved = output.read_bytes()
        checked = self.cli("--check", str(output))
        self.assertEqual(0, checked.returncode, checked.stdout + checked.stderr)
        self.assertEqual("clean", json.loads(checked.stdout)["status"])
        self.assertEqual(saved, output.read_bytes())
        remaining = source_bytes(self.root)
        del remaining["new-model.yaml"]
        self.assertEqual(before, remaining)
        self.assertEqual(2, self.cli("--output", str(output)).returncode)
        self.assertEqual(saved, output.read_bytes())

    def test_fix1_i2_unreservable_later_location_cannot_authorize_output(self):
        sources, paths, selected = self.summary_sources()
        outside = write_yaml(self.workspace / "outside-source.yaml", {"record": "A supplied location"})
        sources["quality"]["quality"]["evidenceRefs"] = [
            {"reference": "../outside-source.yaml#record", "baseline": byte_baseline(outside)}]
        write_yaml(paths["quality"], sources["quality"])
        selected["quality"][0]["baseline"] = byte_baseline(paths["quality"])
        self.manifest(selected)
        outside.unlink()
        (self.root / "evidence/utility.yaml").unlink()
        before = source_bytes(self.root)
        # Read-only derivation may still report optional gaps; a writer cannot
        # infer that a malformed later declaration is safe to occupy.
        self.assertEqual("unverified", self.export()["views"]["quality"]["state"])
        result = self.cli("--output", str(outside))
        self.assertEqual(2, result.returncode, result.stdout + result.stderr)
        self.assertIn("REPORT_CONFLICT", [f["code"] for f in json.loads(result.stdout)["findings"]])
        self.assertFalse(outside.exists())
        self.assertEqual(before, source_bytes(self.root))


class DiagramViewTests(ModelFixture):
    """T7-I3: only a real, owned Mermaid fence can establish diagram content."""

    BLOCK = "```mermaid\nsequenceDiagram\n  Member->>Clerk: Known request\n```\n"

    def sequence_source(self, diagram):
        write_metadata(self.root, metadata(id="UC-001", kind="use-case"),
                       '# UC-001: Path\n<a id="main"></a>\n## Path\nA business path stated in the source.\n',
                       "records/UC-001.md")
        write_metadata(self.root, metadata(id="ABB-001", kind="architecture-building-block"),
                       '# ABB-001: Building block\n' + "".join(
                           f'<a id="{anchor}"></a>\n## {anchor}\n'
                           'The source states the responsibility and interface limitations.\n'
                           for anchor in ("structure", "interfaces", "runtime")), "records/ABB-001.md")
        path = write_metadata(
            self.root, metadata(id="SEQ-001", kind="sequence-diagram",
                                upstream=[self.scope + "/UC-001#main", self.scope + "/ABB-001#structure"]),
            '# SEQ-001: Scenario\n<a id="basis"></a>\n## Source\n'
            'Keeps the scope and conditions of the original scenario.\n'
            '<a id="participants"></a>\n## Participants\n| externalPartners | No external partners |\n'
            '<a id="paths"></a>\n## Paths\n| hasAsync | false |\n'
            'The source explains the meaning of these messages.\n'
            '<a id="diagram"></a>\n## Original diagram\n' + diagram
            + '<a id="verification-needs"></a>\n## Limitations\n'
            'This test runs neither the diagram nor the application.\n',
            "records/SEQ-001.md")
        self.manifest(self.select("sequences", path))
        return path

    def test_fix1_i3_commented_and_enclosing_literal_fences_do_not_count(self):
        for diagram in (
            "<!--\n" + self.BLOCK + "-->\n",
            "````text\n" + self.BLOCK + "````\n",
            "~~~text\n" + self.BLOCK + "~~~\n",
            "There is a paragraph here, but no diagram code.\n",
            "```mermaid\nsequenceDiagram\n  Member->>Clerk: Known request\n",
        ):
            with self.subTest(diagram=diagram):
                self.sequence_source(diagram)
                before = source_bytes(self.root)
                view = self.export()["views"]["sequences"]
                self.assertEqual("partial", view["state"])
                self.assertIn("diagram", " ".join(view["gaps"]))
                self.assertEqual(before, source_bytes(self.root))

    def test_fix1_i3_real_closed_mermaid_still_satisfies_diagram(self):
        self.sequence_source(self.BLOCK)
        self.assertEqual("available", self.export()["views"]["sequences"]["state"])
        self.sequence_source("<!-- closed context -->" + self.BLOCK)
        self.assertEqual("available", self.export()["views"]["sequences"]["state"])


class VerificationRunTests(ModelFixture):
    """T7-I4: source-owned child run records use the actual VT form's tables."""

    def run_block(self, number=1, *, result="pass", counts=True, date=True, object_baseline=None):
        object_baseline = object_baseline or byte_baseline(self.root / "software-requirements/SR-001.md")
        requirements = byte_baseline(self.root / "stakeholder-requirements/REQ-001.md")
        return (
            f'<a id="vt-002-run-{number:02d}"></a>\n### VT-002-RUN-{number:02d}: Synthetic source record\n\n'
            '| Actual run information | Content |\n|---|---|\n'
            + ('| Date, executor, and mode | 2026-10-15, Fixture, manual check in the raw record |\n'
               if date else '')
            + f'| Actual object baseline | {object_baseline} |\n'
            f'| Requirement/design/task basis baseline at the time | {requirements} |\n'
            '| VT baseline at the time | Named record of the original plan; see the raw report |\n'
            '| Actual environment and tool versions | Supplied synthetic source; not a real application run |\n'
            '| Actual working directory | Controlled directory of the original record |\n'
            '| Actual command or manual steps/test identifier '
            '| The original record compares records before and after item by item; read-only here |\n'
            '| Exit code and discovered/executed/skipped counts (when applicable) '
            '| Exit code 0; discovered 2; executed 2; skipped 0'
            + ('; automated check count 0; manual check count 2' if counts else '') + ' |\n'
            '| Raw report and exact location | [Raw record](../evidence/run.md#run) |\n'
            '| Report accessibility and limitations '
            '| Synthetic input only; keeps the original source limitations; not a tool run |\n\n'
            '| Criterion link (target located by frontmatter) | Actual observation and raw report location '
            '| Actual result | Not-run/skip reason or failure difference |\n'
            '|---|---|---|---|\n'
            f'| [Record criterion](#record) | Allowed observation in the raw record | {result} '
            '| Explained in the original record |\n'
            f'| [Reject criterion](#no-write) | Rejected observation in the raw record | {result} '
            '| Explained in the original record |\n\n'
        )

    def verification_source(self, blocks):
        evidence = self.root / "evidence/run.md"
        evidence.parent.mkdir(exist_ok=True)
        evidence.write_text('# Raw synthetic record\n<a id="run"></a>\n## Record\n'
                            'The source keeps the per-item observations.\n',
                            encoding="utf-8")
        path = self.root / "verification/VT-002.md"
        source = path.read_text(encoding="utf-8").split('<a id="runs">')[0]
        source = source.replace("## Per-target criteria\n",
                                "## Per-target criteria\nThe original independent criteria are kept separately below.\n")
        path.write_text(source + '<a id="runs"></a>\n## Actual run records\n\n' + blocks
                        + '<a id="applicability"></a>\n## Current applicability\n'
                        'Keeps the source limitations and the items pending re-review.\n',
                        encoding="utf-8")
        self.manifest(self.select("verification", path))
        return path

    def test_fix1_i4_actual_child_run_and_multicolumn_results_are_available(self):
        source = self.verification_source(self.run_block())
        before = source_bytes(self.root)
        model = self.export()
        view = model["views"]["verification"]
        self.assertEqual("available", view["state"])
        self.assertEqual([], view["gaps"])
        self.assertIn({"reference": "verification/VT-002.md#vt-002-run-01", "baseline": byte_baseline(source)},
                      view["evidenceRefs"])
        self.assertEqual(before, source_bytes(self.root))
        self.assertNotIn("automatedCount", json.dumps(model))
        self.assertNotIn("Allowed observation in the raw record", json.dumps(model, ensure_ascii=False))

    def test_fix1_i4_missing_split_counts_are_not_invented_from_totals_or_rows(self):
        self.verification_source(self.run_block(counts=False))
        view = self.export()["views"]["verification"]
        self.assertEqual("partial", view["state"])
        gaps = " ".join(view["gaps"])
        self.assertIn("vt-002-run-01", gaps)
        self.assertIn("automatedCount", gaps)
        self.assertIn("manualCount", gaps)

    def test_fix1_i4_missing_result_for_one_criterion_is_a_located_gap(self):
        block = self.run_block().replace(
            '| [Reject criterion](#no-write) | Rejected observation in the raw record | pass '
            '| Explained in the original record |\n', '')
        self.verification_source(block)
        view = self.export()["views"]["verification"]
        self.assertEqual("partial", view["state"])
        self.assertIn("no-write", " ".join(view["gaps"]))
        self.assertIn("vt-002-run-01", " ".join(view["gaps"]))

    def test_fix1_i4_complementary_incomplete_runs_cannot_fill_each_other(self):
        self.verification_source(self.run_block(1, counts=False) + self.run_block(2, date=False))
        view = self.export()["views"]["verification"]
        self.assertEqual("partial", view["state"])
        self.assertTrue(any("vt-002-run-01" in gap and "automatedCount" in gap for gap in view["gaps"]))
        self.assertTrue(any("vt-002-run-02" in gap and "lastRunDate" in gap for gap in view["gaps"]))

    def test_fix1_i4_conflicting_same_baseline_runs_are_explicit_not_merged(self):
        self.verification_source(self.run_block(1) + self.run_block(2, result="fail"))
        view = self.export()["views"]["verification"]
        self.assertEqual("partial", view["state"])
        self.assertIn("conflicting", " ".join(view["gaps"]).lower())
        for number in ("01", "02"):
            self.assertIn(self.scope + "/VT-002#vt-002-run-" + number, view["artifactRefs"])

    def test_fix1_i4_distinct_baseline_histories_retain_separate_run_refs(self):
        first = self.run_block(1)
        second = self.run_block(2, result="fail",
                                object_baseline=byte_baseline(self.root / "domain-model/DM-001.md"))
        path = self.verification_source(first + second)
        view = self.export()["views"]["verification"]
        self.assertEqual("available", view["state"])
        for number in ("01", "02"):
            self.assertIn({"reference": "verification/VT-002.md#vt-002-run-" + number,
                           "baseline": byte_baseline(path)}, view["evidenceRefs"])

    def test_fix1_i4_duplicate_criterion_results_remain_ambiguous(self):
        block = (self.run_block().rstrip() + '\n| [Reject criterion](#no-write) | Another conflicting observation '
                 '| fail | Needs confirmation from the source |\n')
        self.verification_source(block)
        view = self.export()["views"]["verification"]
        self.assertEqual("partial", view["state"])
        self.assertTrue(any("ambiguous" in gap and "no-write" in gap and "vt-002-run-01" in gap
                            for gap in view["gaps"]))


class RunOwnershipTests(ModelFixture):
    """F1-N1: an anchor belongs to its actual heading, not the preceding interval."""

    # Reuse the exact positive run fixture without rerunning its class by inheritance.
    run_block = VerificationRunTests.run_block
    verification_source = VerificationRunTests.verification_source

    def owned(self, path):
        before = source_bytes(self.root)
        result = self.tool()._owned_runs(parse_artifact(path, self.root))
        self.assertEqual(before, source_bytes(self.root))
        return result

    def readonly_view(self):
        before = source_bytes(self.root)
        try:
            return self.export()["views"]["verification"]
        finally:
            self.assertEqual(before, source_bytes(self.root))

    def test_fix2_peer_h2_heading_alone_cannot_supply_an_owned_run(self):
        path = self.verification_source(self.run_block())
        original = path.read_bytes()
        self.assertEqual(1, original.count(b"### VT-002-RUN-01"))
        changed = original.replace(b"### VT-002-RUN-01", b"## VT-002-RUN-01", 1)
        path.write_bytes(changed)
        self.manifest(self.select("verification", path))  # Refresh only the selected byte baseline.
        self.assertEqual(changed, path.read_bytes())  # Every table/criterion remains intact.
        view = self.readonly_view()
        self.assertEqual("partial", view["state"])
        self.assertIn("owned run block", " ".join(view["gaps"]))
        self.assertEqual((), self.owned(path))
        self.assertNotIn("verification/VT-002.md#vt-002-run-01",
                         [item["reference"] for item in view["evidenceRefs"]])

    def test_fix2_valid_h3_and_blank_comment_gap_still_belong_to_runs(self):
        for gap in ("", "\n<!-- source-owned note -->\n\n"):
            with self.subTest(gap=gap):
                block = self.run_block().replace(
                    '<a id="vt-002-run-01"></a>\n', '<a id="vt-002-run-01"></a>\n' + gap)
                path = self.verification_source(block)
                self.assertEqual(("vt-002-run-01",), self.owned(path))
                self.assertEqual("available", self.readonly_view()["state"])

    def test_fix2_ancestor_h1_is_not_owned_and_primary_title_error_is_preserved(self):
        path = self.verification_source(self.run_block().replace("### VT-002-RUN-01", "# VT-002-RUN-01", 1))
        # The raw parser legitimately returns this body; the document checker
        # independently rejects its second H1. Do not change either parser for this fix.
        self.assertEqual((), self.owned(path))
        with self.assertRaises(ArtifactInputError) as caught:
            self.readonly_view()
        self.assertEqual("MULTIPLE_TITLES", caught.exception.code)

    def test_fix2_valid_child_does_not_merge_a_following_peer_record(self):
        first = self.run_block(1)
        peer = self.run_block(2, result="fail").replace("### VT-002-RUN-02", "## VT-002-RUN-02", 1)
        path = self.verification_source(first + peer)
        self.assertEqual(("vt-002-run-01",), self.owned(path))
        view = self.readonly_view()
        self.assertEqual("available", view["state"])  # The peer is not a conflicting child run.
        refs = [item["reference"] for item in view["evidenceRefs"]]
        self.assertIn("verification/VT-002.md#vt-002-run-01", refs)
        self.assertNotIn("verification/VT-002.md#vt-002-run-02", refs)

    def test_fix2_record_after_a_following_section_cannot_fill_missing_run(self):
        block = '<a id="later-section"></a>\n## Later source\n\n' + self.run_block()
        path = self.verification_source(block)
        self.assertEqual((), self.owned(path))
        self.assertEqual("partial", self.readonly_view()["state"])

    def test_fix2_unpaired_anchor_does_not_borrow_a_later_heading(self):
        for interruption in ("This anchor is followed by prose, not a run heading.\n",
                             "```text\n### VT-002-RUN-01: literal example\n```\n",
                             '<a id="another-owner-section"></a>\n'):
            with self.subTest(interruption=interruption):
                block = self.run_block().replace(
                    '<a id="vt-002-run-01"></a>\n', '<a id="vt-002-run-01"></a>\n' + interruption)
                path = self.verification_source(block)
                self.assertEqual((), self.owned(path))
                self.assertEqual("partial", self.readonly_view()["state"])


class Task8BridgeTests(ModelFixture):
    """ENH-12 / BRIDGE-11,12: report references, never a second result catalog."""

    def implementation_source(self, *, executed=False):
        from collect_implementation_report import build_report
        from tests.test_implementation_report import ImplementationFixture
        seed_implementation_fixture(self.root)
        sources, paths, selection = self.summary_sources()
        git(self.root, "add", "--", ".")
        git(self.root, "commit", "--quiet", "-m", "All nine controlled model sources")
        self.object = git(self.root, "rev-parse", "HEAD")
        evidence = []
        if executed:
            selector, _ = ImplementationFixture.run_record(self)
            evidence.append(selector)
        # Real producer output is INPUT to the model adapter. Expectations below
        # are independently stated, never produced by the collector/exporter.
        report = build_report(self.root, self.object, evidence)
        path = write_yaml(self.root / "reports/implementation.yaml", report)
        selection["verification"].extend(self.select("verification", path)["verification"])
        self.manifest(selection)
        return report, path, sources, paths, selection

    def test_reference_only_report_round_trip_preserves_all_nine_source_views(self):
        report, path, _, _, selection = self.implementation_source(executed=True)
        before = source_bytes(self.root)
        model = self.export()
        pointer = {"reference": "reports/implementation.yaml", "baseline": byte_baseline(path)}
        self.assertEqual([pointer], model["implementationReports"])
        self.assertIn(pointer, model["views"]["verification"]["evidenceRefs"])
        self.assertEqual("available", model["views"]["verification"]["state"])
        self.assertEqual(sorted(VIEW_NAMES), sorted(model["views"]))
        self.assertEqual("pass", next(e for e in report["entries"]
                                     if e["target"] == self.scope + "/SR-001#sr-001-ac-01")["execution"]["status"])
        for forbidden in ('"entries"', '"execution"', '"applicability"', "SOURCE-OWNED-CONTENT", "source-declared-before"):
            self.assertNotIn(forbidden, json.dumps(model))
        without_report = copy.deepcopy(selection)
        without_report["verification"] = without_report["verification"][:1]
        self.manifest(without_report)
        previous = self.export()
        for name in ("requirements", "stories", "architecture", "sequences", "quality", "governance", "risk", "release"):
            self.assertEqual(previous["views"][name], model["views"][name], name)
        self.manifest(selection)
        self.assertEqual(before, source_bytes(self.root))
        persisted = write_yaml(self.workspace / "persisted model.yaml", model)
        self.assertEqual("clean", self.tool().check_model(self.root, self.scope, persisted).status)

    def test_report_requires_later_explicit_selection_and_build_does_not_mutate_manifest(self):
        _, path, _, _, selection = self.implementation_source()
        selection["verification"] = selection["verification"][:1]
        self.manifest(selection)
        before = source_bytes(self.root)
        self.assertEqual([], self.export()["implementationReports"])
        selection["verification"].extend(self.select("verification", path)["verification"])
        self.manifest(selection)
        self.assertEqual([{"reference": "reports/implementation.yaml", "baseline": byte_baseline(path)}],
                         self.export()["implementationReports"])
        # The only write above is the explicit test-owned selection.
        after = source_bytes(self.root)
        before.pop("model-sources.yaml")
        after.pop("model-sources.yaml")
        self.assertEqual(before, after)

    def test_report_alone_is_a_verification_reference_not_copied_entries(self):
        _, path, _, _, _ = self.implementation_source()
        self.manifest(self.select("verification", path))
        model = self.export()
        self.assertEqual("available", model["views"]["verification"]["state"])
        self.assertEqual([], model["views"]["verification"]["artifactRefs"])
        self.assertEqual([{"reference": "reports/implementation.yaml", "baseline": byte_baseline(path)}],
                         model["implementationReports"])
        for name in set(VIEW_NAMES) - {"verification"}:
            self.assertEqual("unverified", model["views"][name]["state"])
            self.assertTrue(model["views"][name]["gaps"])

    def test_missing_or_malformed_report_keeps_optional_gap_without_false_reference(self):
        _, path, _, _, selection = self.implementation_source()
        raw = path.read_bytes()
        for changed in (None, b"schemaVersion: 1\nentries: []\n"):
            with self.subTest(changed=changed):
                if changed is None:
                    path.unlink()
                else:
                    path.write_bytes(changed)
                    selection["verification"][-1]["baseline"] = byte_baseline(path)
                    self.manifest(selection)
                model = self.export()
                self.assertEqual("unverified", model["views"]["verification"]["state"])
                self.assertEqual([], model["implementationReports"])
                self.assertTrue(model["views"]["verification"]["gaps"])
                self.assertEqual("available", model["views"]["risk"]["state"])
                path.write_bytes(raw)

    def test_hand_edited_schema_valid_report_is_not_verified_by_its_file_hash_alone(self):
        report, path, _, _, selection = self.implementation_source()
        report["entries"][0]["applicability"] = {"state": "applicable", "reason": "Invented applicable result without independent record."}
        write_yaml(path, report)
        selection["verification"][-1]["baseline"] = byte_baseline(path)
        self.manifest(selection)
        model = self.export()
        self.assertEqual("unverified", model["views"]["verification"]["state"])
        self.assertIn("REPORT_MISMATCH", " ".join(model["views"]["verification"]["gaps"]))
        self.assertEqual([], model["implementationReports"])

    def test_unreadable_or_drifted_original_run_report_removes_only_optional_bridge(self):
        _, path, _, _, selection = self.implementation_source(executed=True)
        raw_report = self.root / "reports/сырые € VT-002-1.txt"
        raw_report.write_bytes(raw_report.read_bytes() + b"unrecorded drift")
        before = source_bytes(self.root)
        model = self.export()
        self.assertEqual("unverified", model["views"]["verification"]["state"])
        self.assertIn("BASE_MISMATCH", " ".join(model["views"]["verification"]["gaps"]))
        self.assertEqual([], model["implementationReports"])
        self.assertEqual(before, source_bytes(self.root))

    def test_optional_quality_risk_gaps_do_not_erase_valid_report_or_other_views(self):
        _, path, _, paths, _ = self.implementation_source()
        paths["quality"].unlink()
        paths["risk"].write_text("riskSummary: [invalid type]\n", encoding="utf-8")
        model = self.export()
        self.assertEqual("unverified", model["views"]["quality"]["state"])
        self.assertEqual("unverified", model["views"]["risk"]["state"])
        self.assertEqual("available", model["views"]["sequences"]["state"])
        self.assertEqual("available", model["views"]["verification"]["state"])
        self.assertEqual([{"reference": "reports/implementation.yaml", "baseline": byte_baseline(path)}],
                         model["implementationReports"])

    def test_primary_invalid_artifact_still_errors_even_with_valid_optional_report(self):
        self.implementation_source()
        path = self.root / "software-requirements/SR-001.md"
        path.write_text("id: SR-001\nNo valid frontmatter.\n", encoding="utf-8")
        with self.assertRaises(ArtifactInputError):
            self.export()

    def test_final_report_domain_declarations_protect_output_even_when_optional_validation_fails(self):
        from collect_implementation_report import build_report
        seed_implementation_fixture(self.root)
        domain = self.workspace / "домен € read-only"
        seed_git_repo(domain)
        (domain / "model").mkdir()
        (domain / "model/rule.txt").write_bytes(b"Explicit local domain input.\n")
        git(domain, "add", "--", ".")
        git(domain, "commit", "--quiet", "-m", "Fixed local domain")
        baseline = git(domain, "rev-parse", "HEAD")
        config = yaml.safe_load((self.root / "bc-config.yaml").read_bytes())
        config["domainSources"] = [{"id": "external-domain", "kind": "git", "root": "../домен € read-only",
                                    "path": "model", "baseline": baseline, "readOnly": True}]
        write_yaml(self.root / "bc-config.yaml", config)
        git(self.root, "add", "--", ".")
        git(self.root, "commit", "--quiet", "-m", "Select independent local domain")
        report = build_report(self.root, git(self.root, "rev-parse", "HEAD"), [])
        path = write_yaml(self.root / "reports/implementation.yaml", report)
        (domain / "model/rule.txt").write_bytes(b"Drift: optional report adapter must now produce a gap.\n")
        for value in (byte_baseline(path), "sha256:" + "0" * 64):
            with self.subTest(report_baseline=value):
                self.manifest(self.select("verification", path, value))
                output = domain / "model/never-occupy.yaml"
                before = source_bytes(self.workspace)
                result = self.cli("--output", str(output))
                try:
                    self.assertEqual(2, result.returncode, result.stdout + result.stderr)
                    self.assertIn("REPORT_CONFLICT", result.stdout)
                    self.assertEqual(before, source_bytes(self.workspace))
                finally:
                    if output.exists():
                        output.unlink()  # Test-owned cleanup after reproducing a bad write.


class DomainReservationTests(ModelFixture):
    """T8-I1: optional read gaps never grant writes to declared source locations."""

    def domain_report(self):
        from collect_implementation_report import build_report
        seed_implementation_fixture(self.root)
        domain = self.workspace / "fix1 домен €"
        seed_git_repo(domain)
        (domain / "model").mkdir()
        (domain / "model/rule.txt").write_bytes(b"Fixed source input, never an output location.\n")
        git(domain, "add", "--", ".")
        git(domain, "commit", "--quiet", "-m", "Fix1 fixed local domain input")
        config = yaml.safe_load((self.root / "bc-config.yaml").read_bytes())
        config["domainSources"] = [{"id": "fixed-domain", "kind": "git", "root": "../fix1 домен €",
                                    "path": "model", "baseline": git(domain, "rev-parse", "HEAD"), "readOnly": True}]
        write_yaml(self.root / "bc-config.yaml", config)
        git(self.root, "add", "--", ".")
        git(self.root, "commit", "--quiet", "-m", "Fix1 explicit read-only domain selection")
        report = build_report(self.root, git(self.root, "rev-parse", "HEAD"), [])
        path = write_yaml(self.root / "reports/implementation.yaml", report)
        return domain, report, path

    def select_changed_report(self, path, data):
        write_yaml(path, data)
        self.manifest(self.select("verification", path))

    def refused_output_preserves_sources(self, output):
        before = source_bytes(self.workspace)
        result = self.cli("--output", str(output))
        try:
            self.assertFalse(output.exists(), f"Unverified declaration allowed creation of {output.relative_to(self.workspace)}")
            self.assertEqual(2, result.returncode, result.stdout + result.stderr)
            self.assertIn("REPORT_CONFLICT", result.stdout)
            self.assertEqual(before, source_bytes(self.workspace))
        finally:
            if output.exists():
                output.unlink()  # Clean up only a test-owned wrongly created output.

    def test_i1_missing_baseline_still_protects_resolvable_domain_and_descendants(self):
        domain, report, path = self.domain_report()
        del report["domainSources"][0]["baseline"]
        self.select_changed_report(path, report)
        before = source_bytes(self.workspace)
        model = self.export()
        self.assertEqual("unverified", model["views"]["verification"]["state"])
        self.assertEqual([], model["implementationReports"])
        self.assertEqual(before, source_bytes(self.workspace))
        self.refused_output_preserves_sources(domain / "model/new-model.yaml")

    def test_i1_invalid_baseline_values_do_not_disable_location_reservation(self):
        domain, report, path = self.domain_report()
        for baseline in (None, False, "HEAD", {"not": "a baseline"}):
            with self.subTest(baseline=baseline):
                changed = copy.deepcopy(report)
                changed["domainSources"][0]["baseline"] = baseline
                self.select_changed_report(path, changed)
                self.refused_output_preserves_sources(domain / "model/new-model.yaml")

    def test_i1_incomplete_or_unresolvable_locations_block_even_unrelated_output(self):
        _, report, path = self.domain_report()
        declarations = (
            {"root": "../fix1 домен €"}, {"path": "model"}, {},
            {"root": None, "path": "model"}, {"root": "../fix1 домен €", "path": None},
            {"root": "https://example.invalid/domain", "path": "model"},
            {"root": "../fix1 домен €", "path": "../outside"},
        )
        for declaration in declarations:
            with self.subTest(declaration=declaration):
                changed = copy.deepcopy(report)
                changed["domainSources"] = [declaration]
                self.select_changed_report(path, changed)
                before = source_bytes(self.workspace)
                self.assertEqual("unverified", self.export()["views"]["verification"]["state"])
                self.assertEqual(before, source_bytes(self.workspace))
                self.refused_output_preserves_sources(self.root / "unrelated-output.yaml")

    def test_i1_malformed_domain_declaration_container_cannot_authorize_output(self):
        _, report, path = self.domain_report()
        for declarations in (None, "unresolved source", [None], {"root": "../fix1 домен €", "path": "model"}):
            with self.subTest(declarations=declarations):
                changed = copy.deepcopy(report)
                changed["domainSources"] = declarations
                self.select_changed_report(path, changed)
                self.refused_output_preserves_sources(self.root / "unrelated-output.yaml")

    def test_i1_resolvable_missing_baseline_does_not_block_safe_unrelated_output(self):
        domain, report, path = self.domain_report()
        del report["domainSources"][0]["baseline"]
        self.select_changed_report(path, report)
        before = source_bytes(self.workspace)
        output = self.root / "safe-new-model.yaml"
        result = self.cli("--output", str(output))
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertEqual("unverified", json.loads(result.stdout)["views"]["verification"]["state"])
        self.assertEqual([domain / "model/rule.txt"], list((domain / "model").iterdir()))
        after = source_bytes(self.workspace)
        del after[output.relative_to(self.workspace).as_posix()]
        self.assertEqual(before, after)

    def test_i1_shared_yaml_node_keeps_domain_declaration_context(self):
        _, report, path = self.domain_report()
        incomplete = {"path": "model"}  # Acyclic YAML alias, not another source ledger.
        report["domainSources"] = [incomplete]
        report["otherReference"] = incomplete  # Traversed first by the LIFO reader.
        self.select_changed_report(path, report)
        self.refused_output_preserves_sources(self.root / "unrelated-output.yaml")


class ImplementationTreeTests(ModelFixture):
    """T8-F1-N1: business tree keys are not baseline-free domain declarations."""

    quality_sources = QualityViewTests.quality_sources

    def assert_tree_round_trip(self, data, output):
        _, tree, selected = self.quality_sources()
        write_yaml(tree, {"tree": data})
        selected["quality"][1]["baseline"] = byte_baseline(tree)
        self.manifest(selected)  # Use the real refreshed bytes, never a stale selection.
        output.parent.mkdir(parents=True, exist_ok=True)
        before = source_bytes(self.workspace)
        try:
            model = self.export()
            self.assertEqual("available", model["views"]["quality"]["state"])
            self.assertEqual([], model["views"]["quality"]["gaps"])
            self.assertIn({"reference": "evidence/utility.yaml#tree", "baseline": byte_baseline(tree)},
                          model["views"]["quality"]["evidenceRefs"])
            self.assertNotIn("response-time", json.dumps(model))
            result = self.cli("--output", str(output))
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertTrue(output.is_file())
            self.assertEqual(model, json.loads(result.stdout))
            self.assertEqual(model, yaml.safe_load(output.read_bytes()))
            checked = self.cli("--check", str(output))
            self.assertEqual(0, checked.returncode, checked.stdout + checked.stderr)
            self.assertEqual("clean", json.loads(checked.stdout)["status"])
            self.assertEqual({"tree": data}, yaml.safe_load(tree.read_bytes()))
        finally:
            after = source_bytes(self.workspace)
            after.pop(output.relative_to(self.workspace).as_posix(), None)
            self.assertEqual(before, after)  # All source bytes/file sets are unchanged.

    def test_valid_tree_root_mapping_and_path_list_export_and_check_round_trip(self):
        self.assert_tree_round_trip(
            {"root": {"label": "quality"}, "path": ["response-time"]},
            self.workspace / "safe модель € export.yaml",
        )

    def test_business_root_path_labels_do_not_reserve_phantom_source_directories(self):
        self.assert_tree_round_trip(
            {"root": "quality", "path": "response-time"},
            self.root / "quality/response-time/safe модель € export.yaml",
        )


if __name__ == "__main__":
    unittest.main()
