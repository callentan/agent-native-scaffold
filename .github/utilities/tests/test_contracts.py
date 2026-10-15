"""Task 2 DATA contracts, separate from parser behavior and future view derivation."""

from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator
from referencing import Registry

from tests.helpers import (
    CONTRACTS, KINDS, VIEW_NAMES, git, metadata, seed_git_repo, temporary_workspace,
)


def _no_external_schema(uri: str):
    raise AssertionError(f"Schema attempted nonlocal resolution: {uri}")


def bc_data(baseline: str) -> dict:
    return {
        "schemaVersion": 1,
        "projectId": "sample",
        "boundedContexts": [{"id": "CTX-001"}, {"id": "CTX-002"}],
        "domainSources": [
            {"id": "local-domain", "kind": "local", "root": ".", "path": "domain-model",
             "baseline": baseline, "readOnly": False},
            {"id": "git-domain", "kind": "git",
             "root": "https://example.invalid/owner/domain.git", "path": "domain-model",
             "baseline": baseline, "readOnly": True},
        ],
        "developmentRegistration": "docs/development.md#project-registration",
    }


def model_data(baseline: str) -> dict:
    return {
        "schemaVersion": 1,
        "scope": "sample/CTX-001",
        "source": {"root": ".", "baseline": baseline},
        "artifacts": [{
            "key": "sample/CTX-001/SR-001", "path": "software-requirements/SR-001.md",
            "baseline": baseline, "upstream": ["sample/CTX-001/REQ-001#req-001-ac-01"],
            "targets": [],
        }],
        "implementationReports": [],
        "views": {
            name: {"state": "unverified", "artifactRefs": [], "evidenceRefs": [],
                   "gaps": [f"{name} optional source is absent"]}
            for name in VIEW_NAMES
        },
    }


def report_data(baseline: str) -> dict:
    return {
        "schemaVersion": 1,
        "scope": "sample/CTX-001",
        "object": {"root": ".", "baseline": baseline},
        "bcConfig": {"reference": "bc-config.yaml", "baseline": baseline},
        "domainSources": [{"root": "domain-source", "path": "domain-model", "baseline": baseline}],
        "artifactRefs": [
            "sample/CTX-001/SR-001#sr-001-ac-01", "sample/CTX-001/VT-001#criterion-01",
        ],
        "entries": [{
            "target": "sample/CTX-001/SR-001#sr-001-ac-01",
            "codeRefs": [{"path": "src/policy.py", "baseline": baseline, "symbol": "validate"}],
            "testRefs": [{"path": "native-checks/check_policy.py", "baseline": baseline,
                          "testId": "policy.reject_invalid"}],
            "execution": {"status": "not-run", "evidenceRefs": [],
                          "reason": "Application environment is not configured"},
            "applicability": {"state": "unverified", "reason": "No execution to reassess"},
        }],
    }


VIEW_SOURCES = {
    "requirements": ("SR-001#sr-001-ac-01", "sources/model.yaml#srSummary"),
    "stories": ("US-001#scope", "sources/model.yaml#storySummary"),
    "architecture": ("ABB-001#structure", "sources/model.yaml#abbSummary"),
    "sequences": ("SEQ-001#sequence", "sources/model.yaml#sequenceSummary"),
    "verification": ("VT-001#criterion-01", "sources/model.yaml#verificationSummary"),
    "quality": ("QAS-001#scenario", "domain-model/QAS-001.md#testScenarios"),
    "governance": ("GOV-001#decision", "sources/model.yaml#governanceSummary"),
    "risk": ("RISK-001#analysis", "sources/model.yaml#riskSummary"),
    "release": ("REL-001#release", "sources/model.yaml#releaseStatus"),
}


class ContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        temporary = temporary_workspace()
        cls.addClassCleanup(temporary.cleanup)
        cls.root = Path(temporary.name) / "git baseline with spaces"
        cls.baseline = seed_git_repo(cls.root)

    def validator(self, name: str) -> Draft202012Validator:
        schema = json.loads((CONTRACTS / f"{name}.schema.json").read_text(encoding="utf-8"))
        return Draft202012Validator(schema, registry=Registry(retrieve=_no_external_schema))

    def assert_valid(self, name: str, data: dict) -> None:
        errors = list(self.validator(name).iter_errors(data))
        self.assertEqual(errors, [], "\n".join(error.message for error in errors))

    def assert_invalid(self, name: str, data: dict) -> None:
        self.assertTrue(list(self.validator(name).iter_errors(data)),
                        f"{name} silently accepted invalid data: {data!r}")

    def test_git_fixture_baseline_is_a_real_exact_local_object(self) -> None:
        self.assertRegex(self.baseline, r"^[0-9a-f]{40}$")
        self.assertEqual(git(self.root, "show", f"{self.baseline}:README.md"), "# Local baseline fixture")
        self.assertEqual(git(self.root, "remote"), "")

    def test_all_four_contracts_reject_missing_or_wrong_schema_version(self) -> None:
        for name, factory in (
            ("artifact", lambda: metadata()),
            ("bc-config", lambda: bc_data(self.baseline)),
            ("model", lambda: model_data(self.baseline)),
            ("implementation-report", lambda: report_data(self.baseline)),
        ):
            for version in (0, 9, True, False, "1", None):
                with self.subTest(schema=name, version=repr(version)):
                    data = factory()
                    data["schemaVersion"] = version
                    self.assert_invalid(name, data)
            with self.subTest(schema=name, version="missing"):
                data = factory()
                del data["schemaVersion"]
                self.assert_invalid(name, data)

    def test_artifact_required_identity_fields_and_closed_metadata(self) -> None:
        for key in ("id", "scope", "kind", "contentState"):
            with self.subTest(missing=key):
                data = metadata()
                del data[key]
                self.assert_invalid("artifact", data)
        for changes in (
            {"kind": "unknown"}, {"contentState": "approved"}, {"scope": "CTX-001"},
            {"id": "../REQ-001"}, {"schemaVersion": 1, "command": "do not execute"},
        ):
            with self.subTest(changes=changes):
                self.assert_invalid("artifact", metadata(**changes))

    def test_artifact_states_and_confirmation_structure(self) -> None:
        for state in ("draft", "retired"):
            self.assert_valid("artifact", metadata(contentState=state))
        declaration = {"by": "Named person", "reference": "reviews/decision.md#record",
                       "baseline": "review-object-01"}
        self.assert_valid("artifact", metadata(contentState="confirmed", confirmation=declaration))
        self.assert_invalid("artifact", metadata(contentState="confirmed"))
        for key in declaration:
            for bad in ("", " \t\n", None, 7):
                with self.subTest(field=key, bad=repr(bad)):
                    invalid = dict(declaration, **{key: bad})
                    self.assert_invalid("artifact", metadata(contentState="confirmed", confirmation=invalid))
            invalid = dict(declaration)
            del invalid[key]
            self.assert_invalid("artifact", metadata(contentState="confirmed", confirmation=invalid))

    def test_artifact_upstream_targets_and_no_coercion(self) -> None:
        target = {"target": "sample/CTX-001/SR-001#sr-001-ac-01",
                  "criterionAnchor": "criterion-01", "testId": "native::test_id"}
        self.assert_valid("artifact", metadata(upstream=["sample/CTX-001/REQ-001"], targets=[target]))
        for field in ("upstream", "targets"):
            for value in (None, {}, "", 1, [None]):
                with self.subTest(field=field, value=value):
                    self.assert_invalid("artifact", metadata(**{field: value}))
        for changes in (
            {"target": "SR-001#sr-001-ac-01"}, {"target": "sample/CTX-001/SR-001"},
            {"criterionAnchor": "#criterion-01"}, {"criterionAnchor": "has space"},
            {"testId": ""}, {"testId": None}, {"extra": "not allowed"},
        ):
            self.assert_invalid("artifact", metadata(targets=[dict(target, **changes)]))
        self.assert_invalid("artifact", metadata(targets=[target, dict(target)]))
        self.assert_invalid("artifact", metadata(upstream=["sample/CTX-001/REQ-001"] * 2))

    def test_bc_local_and_explicit_git_sources_are_data_without_resolution(self) -> None:
        self.assert_valid("bc-config", bc_data(self.baseline))
        data = bc_data(self.baseline)
        data["domainSources"][0]["baseline"] = "sha256:" + "a" * 64
        self.assert_valid("bc-config", data)

    def test_bc_requires_project_context_source_and_registration_identities(self) -> None:
        for field in ("projectId", "boundedContexts", "domainSources", "developmentRegistration"):
            with self.subTest(field=field):
                data = bc_data(self.baseline)
                del data[field]
                self.assert_invalid("bc-config", data)
        for field in ("id", "kind", "root", "path", "baseline", "readOnly"):
            with self.subTest(source_field=field):
                data = bc_data(self.baseline)
                del data["domainSources"][0][field]
                self.assert_invalid("bc-config", data)
        data = bc_data(self.baseline)
        data["boundedContexts"] = [{}]
        self.assert_invalid("bc-config", data)

    def test_bc_rejects_commands_secrets_floating_baselines_and_bad_paths(self) -> None:
        for changes in (
            {"kind": "auto"}, {"root": " "}, {"path": "../domain"}, {"path": "/domain"},
            {"path": "C:\\domain"}, {"path": "domain/../private"}, {"readOnly": "true"},
            {"baseline": "HEAD"}, {"baseline": "main"}, {"baseline": self.baseline[:7]},
            {"command": "git clone"}, {"token": "not-a-real-secret"},
        ):
            with self.subTest(changes=changes):
                data = bc_data(self.baseline)
                data["domainSources"][1].update(changes)
                self.assert_invalid("bc-config", data)
        for registration in ("docs/development.md", "../docs/development.md#project-registration",
                             "https://example.invalid/development#commands"):
            data = bc_data(self.baseline)
            data["developmentRegistration"] = registration
            self.assert_invalid("bc-config", data)

    def test_model_all_nine_unverified_views_keep_specific_gaps(self) -> None:
        data = model_data(self.baseline)
        self.assert_valid("model", data)
        self.assertEqual(set(data["views"]), set(VIEW_NAMES))

    def test_model_requires_primary_source_scope_artifact_identity_and_baselines(self) -> None:
        for field in ("scope", "source", "artifacts", "implementationReports", "views"):
            data = model_data(self.baseline)
            del data[field]
            self.assert_invalid("model", data)
        for field in ("root", "baseline"):
            data = model_data(self.baseline)
            del data["source"][field]
            self.assert_invalid("model", data)
        for field in ("key", "path", "baseline", "upstream", "targets"):
            data = model_data(self.baseline)
            del data["artifacts"][0][field]
            self.assert_invalid("model", data)
        for baseline in ("", "HEAD", "latest", self.baseline[:7]):
            data = model_data(self.baseline)
            data["source"]["baseline"] = baseline
            self.assert_invalid("model", data)
        data = model_data(self.baseline)
        data["scope"] = "CTX-001"
        self.assert_invalid("model", data)

    def test_model_does_not_copy_body_or_invent_additional_views(self) -> None:
        data = model_data(self.baseline)
        data["artifacts"][0]["body"] = "Copied business fact"
        self.assert_invalid("model", data)
        data = model_data(self.baseline)
        data["views"]["custom"] = copy.deepcopy(data["views"]["requirements"])
        self.assert_invalid("model", data)
        for missing in VIEW_NAMES:
            with self.subTest(missing=missing):
                data = model_data(self.baseline)
                del data["views"][missing]
                self.assert_invalid("model", data)

    def test_model_view_evidence_and_artifact_refs_require_owner_and_baseline(self) -> None:
        for reference in ("SR-001#sr-001-ac-01", "sample/CTX-001/SR-001",
                          "sample/CTX-001/SR-001#sr-001-ac-01\n"):
            data = model_data(self.baseline)
            data["views"]["requirements"].update(
                state="partial", artifactRefs=[reference], gaps=["Missing a second entry"])
            self.assert_invalid("model", data)
        for evidence in (
            {"reference": "reports/check.json#run"},
            {"reference": "reports/check.json#run", "baseline": ""},
            {"reference": "../reports/check.json#run", "baseline": self.baseline},
        ):
            data = model_data(self.baseline)
            data["views"]["requirements"].update(
                state="partial", evidenceRefs=[evidence], gaps=["Missing a second entry"])
            self.assert_invalid("model", data)

    def test_implementation_report_not_run_does_not_imply_pass(self) -> None:
        self.assert_valid("implementation-report", report_data(self.baseline))
        data = report_data(self.baseline)
        data["entries"] = []
        self.assert_valid("implementation-report", data)
        for status in ("pass", "fail", "approved", "done"):
            data = report_data(self.baseline)
            data["entries"][0]["execution"]["status"] = status
            self.assert_invalid("implementation-report", data)

    def test_report_pass_requires_locatable_evidence_and_keeps_applicability_separate(self) -> None:
        data = report_data(self.baseline)
        entry = data["entries"][0]
        entry["execution"] = {
            "status": "pass",
            "evidenceRefs": [{"reference": "reports/run.json#case-01", "baseline": self.baseline}],
        }
        # A historical pass may be unverified for the current baseline.
        self.assert_valid("implementation-report", data)
        for evidence in ([], [{"reference": "reports/run.json#case-01"}],
                         [{"reference": "reports/run.json#case-01", "baseline": " "}]):
            invalid = copy.deepcopy(data)
            invalid["entries"][0]["execution"]["evidenceRefs"] = evidence
            self.assert_invalid("implementation-report", invalid)
        for field in ("state", "reason"):
            invalid = copy.deepcopy(data)
            del invalid["entries"][0]["applicability"][field]
            self.assert_invalid("implementation-report", invalid)

    def test_report_skips_and_not_run_require_concrete_reasons(self) -> None:
        for status in ("not-run", "skipped"):
            data = report_data(self.baseline)
            data["entries"][0]["execution"]["status"] = status
            self.assert_valid("implementation-report", data)
            for reason in ("", " ", None):
                data["entries"][0]["execution"]["reason"] = reason
                self.assert_invalid("implementation-report", data)
            del data["entries"][0]["execution"]["reason"]
            self.assert_invalid("implementation-report", data)

    def test_report_requires_object_source_code_test_and_target_identity(self) -> None:
        for field in ("object", "domainSources", "bcConfig", "artifactRefs", "entries"):
            data = report_data(self.baseline)
            del data[field]
            self.assert_invalid("implementation-report", data)
        for container, fields in (
            ("object", ("root", "baseline")),
            ("domainSources", ("root", "path", "baseline")),
            ("codeRefs", ("path", "baseline")),
            ("testRefs", ("path", "baseline", "testId")),
        ):
            for field in fields:
                data = report_data(self.baseline)
                node = (data["entries"][0][container][0] if container in ("codeRefs", "testRefs")
                        else data["domainSources"][0] if container == "domainSources"
                        else data["object"])
                del node[field]
                self.assert_invalid("implementation-report", data)
        data = report_data(self.baseline)
        data["entries"][0]["target"] = "AC-01"
        self.assert_invalid("implementation-report", data)
        data = report_data(self.baseline)
        data["entries"][0]["execution"]["evidenceRefs"] = [{"reference": "report.json", "baseline": None}]
        self.assert_invalid("implementation-report", data)


def _schema_case(name: str):
    def test(self: ContractTests) -> None:
        schema = self.validator(name).schema
        Draft202012Validator.check_schema(schema)
        self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
        self.assertIn("$defs", schema)

        def check_refs(node: object) -> None:
            if isinstance(node, dict):
                for key, value in node.items():
                    if key == "$ref":
                        self.assertTrue(value.startswith("#/"), value)
                        target = schema
                        for part in value[2:].split("/"):
                            target = target[part.replace("~1", "/").replace("~0", "~")]
                        self.assertIsInstance(target, (dict, bool))
                    check_refs(value)
            elif isinstance(node, list):
                for value in node:
                    check_refs(value)
        check_refs(schema)
    return test


def _kind_case(kind: str):
    def test(self: ContractTests) -> None:
        self.assert_valid("artifact", metadata(kind=kind))
    return test


def _view_positive_case(name: str):
    def test(self: ContractTests) -> None:
        artifact, reference = VIEW_SOURCES[name]
        for state, gaps in (("available", []), ("partial", ["One source entry is missing"])):
            with self.subTest(state=state):
                data = model_data(self.baseline)
                data["views"][name] = {
                    "state": state,
                    "artifactRefs": [f"sample/CTX-001/{artifact}"],
                    "evidenceRefs": [{"reference": reference, "baseline": self.baseline}],
                    "gaps": gaps,
                }
                self.assert_valid("model", data)
    return test


def _view_negative_case(name: str):
    def test(self: ContractTests) -> None:
        for field in ("state", "artifactRefs", "evidenceRefs", "gaps"):
            with self.subTest(missing=field):
                data = model_data(self.baseline)
                del data["views"][name][field]
                self.assert_invalid("model", data)
        for changes in (
            {"state": "passed"}, {"state": "approved"}, {"gaps": []}, {"gaps": [" \t"]},
            {"artifactRefs": ["sample/CTX-001/SR-001#sr-001-ac-01"]},
            {"evidenceRefs": [{"reference": "reports/check.json", "baseline": self.baseline}]},
            {"state": "partial"},  # partial must retain at least one known reference
            {"state": "partial", "gaps": [], "artifactRefs": ["sample/CTX-001/SR-001#sr-001-ac-01"]},
            {"state": "available", "artifactRefs": ["sample/CTX-001/SR-001#sr-001-ac-01"]},
        ):
            with self.subTest(changes=changes):
                data = model_data(self.baseline)
                data["views"][name].update(changes)
                self.assert_invalid("model", data)
    return test


for _schema in ("artifact", "bc-config", "model", "implementation-report"):
    setattr(ContractTests, "test_schema_is_valid_and_local_" + _schema.replace("-", "_"),
            _schema_case(_schema))
for _kind in KINDS:
    setattr(ContractTests, "test_artifact_schema_accepts_" + _kind.replace("-", "_"), _kind_case(_kind))
for _view in VIEW_NAMES:
    setattr(ContractTests, "test_view_accepts_refs_" + _view, _view_positive_case(_view))
    setattr(ContractTests, "test_view_rejects_incomplete_or_false_state_" + _view,
            _view_negative_case(_view))
