"""ENH-12 / BRIDGE-01..16: real local objects; synthetic runs are INPUTS only."""

from __future__ import annotations

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
import yaml

from artifact_io import ArtifactInputError
from tests.helpers import (
    CONTRACTS, WORKTREE, git, metadata, seed_git_repo, seed_implementation_fixture,
    source_bytes, temporary_workspace, write_metadata,
)


DELIVERY = (
    "sample/CTX-001/REQ-001#req-001-ac-01",
    "sample/CTX-001/REQ-001#req-001-ac-02",
    "sample/CTX-001/SR-001#sr-001-ac-01",
    "sample/CTX-001/SR-001#sr-001-ac-02",
)


def digest(raw):
    return "sha256:" + hashlib.sha256(raw).hexdigest()


class ImplementationFixture(unittest.TestCase):
    def setUp(self):
        temporary = temporary_workspace()
        self.addCleanup(temporary.cleanup)
        self.workspace = Path(temporary.name)
        self.root = self.workspace / "实施 object with spaces"
        self.object = seed_implementation_fixture(self.root)
        self.scope = "sample/CTX-001"

    def tool(self):
        self.assertIsNotNone(importlib.util.find_spec("collect_implementation_report"),
                             "Task8 read-only implementation collector is not implemented")
        return importlib.import_module("collect_implementation_report")

    def collect(self, evidence=(), **kwargs):
        return self.tool().build_report(self.root, self.object, evidence, **kwargs)

    def entries(self, report):
        return {entry["target"]: entry for entry in report["entries"]}

    def error(self, code, evidence=(), **kwargs):
        with self.assertRaises(ArtifactInputError) as caught:
            self.collect(evidence, **kwargs)
        self.assertEqual(code, caught.exception.code, str(caught.exception))
        return caught.exception

    def commit(self):
        git(self.root, "add", "--", ".")
        git(self.root, "commit", "--quiet", "-m", "Change controlled collector inputs")
        self.object = git(self.root, "rev-parse", "HEAD")
        return self.object

    def config(self, update):
        path = self.root / "bc-config.yaml"
        data = yaml.safe_load(path.read_bytes())
        update(data)
        path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")
        return path

    def run_record(self, *, vt="VT-002", number=1, statuses=None, mode="command",
                   object_basis=None, requirement_basis=None, plan_basis=None,
                   counts="exit=0; discovered=1; executed=1; skipped=0",
                   steps=None, report=True):
        """Append synthetic source-owned data, NOT a receipt of business execution."""
        path = self.root / f"verification/{vt}.md"
        criteria = ("record", "no-write") if vt == "VT-002" else ("allow", "reject")
        owner = "SR-001" if vt == "VT-002" else "REQ-001"
        statuses = statuses or {criteria[0]: "pass", criteria[1]: "not-run"}
        raw_path = self.root / f"reports/原始 {vt}-{number}.txt"
        raw_path.parent.mkdir(exist_ok=True)
        raw_path.write_text(
            "SYNTHETIC TEST INPUT ONLY, not an actual application execution receipt.\n"
            "test_record: observed one new record; test_no_write: observed no mutation.\n"
            "Manual steps: inspect the prepared state, compare the independent criterion.\n",
            encoding="utf-8", newline="\n",
        )
        relative = f"../reports/{raw_path.name}"
        link = f"[原始输入](<{relative}>)"
        basis = requirement_basis or f"{self.scope}/{owner}@{self.object}"
        report_field = f"{link} @ {digest(raw_path.read_bytes())}" if report else "not-run"
        rows = []
        for criterion in criteria:
            status = statuses.get(criterion, "not-run")
            observation = (f"Observed the prepared state against {criterion}; {link}"
                           if status in ("pass", "fail") else "未执行")
            reason = ("Prepared observation differs from the independent criterion." if status == "fail"
                      else "No execution input was supplied for this criterion." if status == "not-run"
                      else "Fixture environment was explicitly unavailable." if status == "skipped" else "")
            rows.append(f"| [{criterion}](#{criterion}) | {observation} | {status} | {reason} |")
        anchor = f"{vt.lower()}-run-{number:02d}"
        block = (
            f'\n<a id="{anchor}"></a>\n### {vt}-RUN-{number:02d}: synthetic input\n\n'
            "| 实际执行信息 | 内容 |\n|---|---|\n"
            f"| 日期、执行者与方式 | 2026-10-16; recorder=synthetic fixture; mode={mode} |\n"
            f"| 实际对象基线 | {object_basis or self.object} |\n"
            f"| 当时的需求/设计/任务依据基线 | {basis} |\n"
            f"| 当时的 VT 基线 | {plan_basis or self.object} |\n"
            "| 实际环境与工具版本 | Synthetic collector input on a controlled local fixture |\n"
            "| 实际工作目录 | . |\n"
            f"| 实际命令或人工步骤/测试标识 | {steps or ('Inspect prepared membership, then compare the business register.' if mode == 'manual' else 'fixture-input-only-runner test_record test_no_write')} |\n"
            + (f"| 退出码、发现/执行/跳过数量（适用时） | {counts} |\n" if counts is not None else "")
            + f"| 原始报告与具体位置 | {report_field} |\n"
            "| 报告可访问性与限制 | Local synthetic fixture input only; no external event is asserted. |\n\n"
            "| 判据链接（目标由 frontmatter 定位） | 实际观察及原始报告定位 | 实际结果 | 未执行/跳过原因或失败差异 |\n"
            "|---|---|---|---|\n" + "\n".join(rows) + "\n"
        )
        with path.open("a", encoding="utf-8", newline="\n") as output:
            output.write(block)
        return path.relative_to(self.root).as_posix() + "#" + anchor, raw_path

    def replace_in_vt(self, old, new, vt="VT-002"):
        path = self.root / f"verification/{vt}.md"
        text = path.read_text(encoding="utf-8")
        self.assertIn(old, text, "Test mutation must touch the intended real record")
        path.write_text(text.replace(old, new), encoding="utf-8", newline="\n")

    def cli(self, *args, object_sha=None):
        script = WORKTREE / ".github/utilities/collect_implementation_report.py"
        self.assertTrue(script.is_file(), "Task8 collector CLI is not implemented")
        return subprocess.run(
            [sys.executable, "-B", "-X", "utf8", str(script),
             "--root", str(self.root), "--object", self.object if object_sha is None else object_sha, *args],
            cwd=self.workspace, shell=False, capture_output=True, text=True, encoding="utf-8",
        )


class ImplementationReportTests(ImplementationFixture):
    def test_absent_execution_evidence_keeps_all_four_targets_not_run(self):
        before = source_bytes(self.root)
        report = self.collect()
        self.assertEqual(list(DELIVERY), [item["target"] for item in report["entries"]])
        self.assertEqual({"schemaVersion", "scope", "object", "bcConfig", "domainSources", "artifactRefs", "entries"},
                         set(report))
        self.assertEqual({"root": ".", "baseline": self.object}, report["object"])
        self.assertEqual({"reference": "bc-config.yaml", "baseline": self.object}, report["bcConfig"])
        self.assertEqual("domain-model/DM-001.md", report["domainSources"][0]["path"])
        for entry in report["entries"]:
            self.assertEqual("not-run", entry["execution"]["status"])
            self.assertEqual([], entry["execution"]["evidenceRefs"])
            self.assertTrue(entry["execution"]["reason"])
            self.assertEqual("unverified", entry["applicability"]["state"])
        schema = json.loads((CONTRACTS / "implementation-report.schema.json").read_bytes())
        self.assertEqual([], list(Draft202012Validator(schema).iter_errors(report)))
        self.assertEqual(report, self.collect())
        self.assertEqual(before, source_bytes(self.root))
        self.assertNotIn(str(self.root), json.dumps(report))

    def test_commit_approved_filename_and_markers_are_not_runs(self):
        (self.root / "Approved-test_record-pass.txt").write_text("Approved; pass", encoding="utf-8")
        report = self.collect(["verification/VT-002.md"])
        entries = self.entries(report)
        self.assertEqual([{"path": "source code/借用.txt", "baseline": self.object, "symbol": "record"}],
                         entries[DELIVERY[2]]["codeRefs"])
        self.assertEqual([{"path": "native tests/验证.txt", "baseline": self.object, "testId": "test_record"}],
                         entries[DELIVERY[2]]["testRefs"])
        self.assertEqual([], entries[DELIVERY[0]]["testRefs"])
        self.assertEqual(["not-run"] * 4, [item["execution"]["status"] for item in report["entries"]])

    def test_one_synthetic_run_collects_only_its_actual_per_target_result(self):
        selector, raw = self.run_record()
        before = source_bytes(self.root)
        report = self.collect([selector])
        entries = self.entries(report)
        self.assertEqual(["not-run", "not-run", "pass", "not-run"],
                         [item["execution"]["status"] for item in report["entries"]])
        refs = entries[DELIVERY[2]]["execution"]["evidenceRefs"]
        vt = self.root / "verification/VT-002.md"
        self.assertIn({"reference": selector, "baseline": digest(vt.read_bytes())}, refs)
        self.assertIn({"reference": "software-requirements/SR-001.md#sr-001-ac-01", "baseline": self.object}, refs)
        self.assertIn({"reference": "verification/VT-002.md#record", "baseline": self.object}, refs)
        self.assertIn({"reference": raw.relative_to(self.root).as_posix(), "baseline": digest(raw.read_bytes())}, refs)
        self.assertEqual("unverified", entries[DELIVERY[2]]["applicability"]["state"])
        self.assertEqual(before, source_bytes(self.root))

    def test_failure_and_skipped_reasons_are_not_a_global_success(self):
        selector, _ = self.run_record(statuses={"record": "fail", "no-write": "skipped"},
                                     counts="exit=1; discovered=2; executed=1; skipped=1")
        entries = self.entries(self.collect([selector]))
        self.assertEqual("fail", entries[DELIVERY[2]]["execution"]["status"])
        self.assertIn("differs", entries[DELIVERY[2]]["execution"]["reason"])
        self.assertEqual("skipped", entries[DELIVERY[3]]["execution"]["status"])
        self.assertIn("unavailable", entries[DELIVERY[3]]["execution"]["reason"])
        self.assertEqual("unverified", entries[DELIVERY[2]]["applicability"]["state"])

    def test_manual_steps_need_no_invented_command_or_automatic_manual_split(self):
        selector, _ = self.run_record(vt="VT-001", mode="manual", counts=None)
        entries = self.entries(self.collect([selector]))
        self.assertEqual("pass", entries[DELIVERY[0]]["execution"]["status"])
        self.assertEqual([], entries[DELIVERY[0]]["testRefs"])
        self.assertEqual("not-run", entries[DELIVERY[2]]["execution"]["status"])

    def test_selected_not_run_is_preserved_without_a_raw_execution_report(self):
        selector, _ = self.run_record(statuses={"record": "not-run", "no-write": "not-run"},
                                     report=False, counts="exit=0; discovered=0; executed=0; skipped=0")
        report = self.collect([selector])
        self.assertEqual(["not-run"] * 4, [item["execution"]["status"] for item in report["entries"]])
        self.assertIn(selector, [ref["reference"] for ref in report["entries"][2]["execution"]["evidenceRefs"]])

    def test_missing_and_non_collection_evidence_selection_are_explicit_errors(self):
        error = self.error("FILE_NOT_FOUND", ["verification/missing.md"])
        self.assertIn("missing.md", str(error.path))
        for selection in (None, "verification/VT-002.md", 3, [None], ["../outside.md"]):
            with self.subTest(selection=selection):
                with self.assertRaises(ArtifactInputError):
                    self.collect(selection)

    def test_duplicate_selection_and_conflicting_runs_never_choose_last_pass(self):
        first, _ = self.run_record(statuses={"record": "fail"})
        second, _ = self.run_record(number=2)
        self.error("AMBIGUOUS_RUN", ["verification/VT-002.md"])
        self.error("DUPLICATE_EVIDENCE", [first, first])
        self.error("AMBIGUOUS_RESULT", [first, second])
        self.assertEqual("fail", self.entries(self.collect([first]))[DELIVERY[2]]["execution"]["status"])
        self.assertEqual("pass", self.entries(self.collect([second]))[DELIVERY[2]]["execution"]["status"])

    def test_unknown_anchor_and_duplicate_criterion_results_are_rejected(self):
        selector, _ = self.run_record()
        self.error("UNKNOWN_RUN", ["verification/VT-002.md#vt-002-run-99"])
        path = self.root / "verification/VT-002.md"
        row = next(line for line in path.read_text(encoding="utf-8").splitlines()
                   if line.startswith("| [record](#record)"))
        with path.open("a", encoding="utf-8") as output:
            output.write(row + "\n")
        self.error("INVALID_RUN", [selector])

    def test_each_record_keeps_its_own_fields_without_cross_run_stitching(self):
        first, _ = self.run_record()
        second, _ = self.run_record(number=2)
        self.replace_in_vt("| 实际环境与工具版本 | Synthetic collector input on a controlled local fixture |",
                           "| 实际环境与工具版本 | 未配置 |")
        self.error("INVALID_RUN", [first])
        self.error("INVALID_RUN", [second])

    def test_exact_object_requirement_and_vt_baselines_cannot_be_replaced_by_old_pass(self):
        selector, _ = self.run_record(object_basis="f" * 40)
        self.error("OBJECT_MISMATCH", [selector])
        self.replace_in_vt("f" * 40, self.object)
        self.replace_in_vt(f"{self.scope}/SR-001@{self.object}", f"{self.scope}/SR-001@sha256:" + "0" * 64)
        self.error("BASE_MISMATCH", [selector])
        self.replace_in_vt("sha256:" + "0" * 64, self.object)
        self.replace_in_vt(f"| 当时的 VT 基线 | {self.object} |", "| 当时的 VT 基线 | HEAD |")
        self.error("INVALID_BASE", [selector])

    def test_requirement_basis_is_exact_owner_not_another_same_short_id(self):
        selector, _ = self.run_record(requirement_basis=f"foreign/CTX-001/SR-001@{self.object}")
        self.error("REQUIREMENT_MISMATCH", [selector])

    def test_plan_drift_in_supplied_current_vt_is_not_just_an_appended_run(self):
        selector, _ = self.run_record()
        self.replace_in_vt("有效请求新增一条关联会员的记录。", "有效请求删除所有关联会员记录。")
        self.error("PLAN_MISMATCH", [selector])

    def test_other_commit_is_accepted_only_when_requirement_and_plan_content_match(self):
        tested = self.object
        (self.root / "other.txt").write_text("Unrelated later file", encoding="utf-8")
        later = self.commit()
        self.object = tested
        selector, _ = self.run_record(requirement_basis=f"{self.scope}/SR-001@{later}", plan_basis=later)
        self.assertEqual("pass", self.entries(self.collect([selector]))[DELIVERY[2]]["execution"]["status"])
        self.assertIn({"reference": "verification/VT-002.md#record", "baseline": later},
                      self.entries(self.collect([selector]))[DELIVERY[2]]["execution"]["evidenceRefs"])

    def test_missing_empty_or_drifted_raw_report_never_supplies_pass(self):
        selector, raw = self.run_record()
        original = raw.read_bytes()
        raw.unlink()
        self.error("FILE_NOT_FOUND", [selector])
        raw.write_bytes(b"")
        self.error("BASE_MISMATCH", [selector])
        raw.write_bytes(original + b"Changed after recording")
        self.error("BASE_MISMATCH", [selector])

    def test_zero_all_skipped_and_inconsistent_discovery_cannot_be_executed_pass(self):
        selector, _ = self.run_record()
        good = "exit=0; discovered=1; executed=1; skipped=0"
        for bad in ("exit=0; discovered=0; executed=0; skipped=0",
                    "exit=0; discovered=2; executed=0; skipped=2",
                    "exit=0; discovered=1; executed=2; skipped=0",
                    "exit=1; discovered=1; executed=1; skipped=0",
                    "exit=0; discovered=1; executed=True; skipped=0"):
            with self.subTest(counts=bad):
                self.replace_in_vt(good, bad)
                try:
                    self.error("INVALID_EXECUTION", [selector])
                finally:
                    self.replace_in_vt(bad, good)

    def test_status_word_or_report_file_alone_is_not_a_concrete_observation(self):
        selector, _ = self.run_record()
        self.replace_in_vt("Observed the prepared state against record; ", "")
        self.error("INVALID_OBSERVATION", [selector])

    def test_source_command_text_cannot_execute_a_side_effect(self):
        marker = self.root / "SHOULD-NOT-EXIST.txt"
        selector, _ = self.run_record(steps=
            f'python -c "open({str(marker)!r}, \'w\').write(\'wrong\')" test_record test_no_write')
        before = source_bytes(self.root)
        self.collect([selector])
        self.assertFalse(marker.exists())
        self.assertEqual(before, source_bytes(self.root))

    def test_exact_object_not_current_code_config_index_or_head(self):
        original = self.object
        code = self.root / "source code/借用.txt"
        code.write_text("Current file has no markers", encoding="utf-8")
        self.config(lambda data: data.update(projectId="not-selected"))
        git(self.root, "add", "--", ".")
        git(self.root, "commit", "--quiet", "-m", "Different current object")
        (self.root / "native tests/验证.txt").write_text("Uncommitted test drift", encoding="utf-8")
        git(self.root, "add", "--", "native tests/验证.txt")
        before = source_bytes(self.root)
        report = self.collect()
        self.assertEqual(original, report["object"]["baseline"])
        self.assertEqual("record", report["entries"][2]["codeRefs"][0]["symbol"])
        self.assertEqual("test_record", report["entries"][2]["testRefs"][0]["testId"])
        self.assertEqual(before, source_bytes(self.root))

    def test_invalid_symbolic_short_unavailable_and_noncommit_object_inputs(self):
        tool = self.tool()
        tree = git(self.root, "rev-parse", self.object + "^{tree}")
        blob = git(self.root, "rev-parse", self.object + ":bc-config.yaml")
        git(self.root, "tag", "-a", "local-tag", "-m", "tag fixture")
        tag = git(self.root, "rev-parse", "refs/tags/local-tag")
        for value in (None, True, 1, "", "HEAD", "main", self.object[:12], "0" * 40, tree, blob, tag):
            with self.subTest(object=value):
                with self.assertRaises(ArtifactInputError):
                    tool.build_report(self.root, value, [])

    def test_missing_vt_cannot_remove_its_owner_acceptances(self):
        (self.root / "verification/VT-002.md").unlink()
        self.commit()
        report = self.collect()
        self.assertEqual(list(DELIVERY), [entry["target"] for entry in report["entries"]])
        self.assertEqual("not-run", report["entries"][3]["execution"]["status"])

    def test_foreign_vt_with_same_short_ids_cannot_satisfy_selected_scope(self):
        for relative in ("software-requirements/SR-001.md", "verification/VT-002.md"):
            path = self.root / relative
            text = path.read_text(encoding="utf-8").replace("sample/CTX-001", "foreign/CTX-001")
            # Foreign source REQ dependencies are supplied, not aliased by suffix.
            dest = self.root / "foreign" / relative
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(text, encoding="utf-8")
        for relative in ("domain-model/DM-001.md", "stakeholder-requirements/REQ-001.md"):
            path = self.root / relative
            dest = self.root / "foreign" / relative
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(path.read_text(encoding="utf-8").replace("sample/CTX-001", "foreign/CTX-001"), encoding="utf-8")
        self.commit()
        self.error("SCOPE_MISMATCH", ["foreign/verification/VT-002.md"])

    def test_marker_requires_real_named_location_and_exact_test_id(self):
        code = self.root / "native tests/验证.txt"
        code.write_text(code.read_text(encoding="utf-8").replace("test_record():", "another_test():"), encoding="utf-8")
        self.commit()
        self.error("INVALID_MARKER")

    def test_declared_test_id_without_matching_source_location_is_input_error(self):
        (self.root / "native tests/验证.txt").unlink()
        self.commit()
        self.error("MISSING_TEST_REFERENCE")

    def test_multiple_bc_choices_require_explicit_scope_and_cannot_guess_cwd(self):
        write_metadata(self.root, metadata(id="REQ-010", scope="sample/CTX-002"),
                       '# REQ-010: another scope\n<a id="req-010-ac-01"></a>\n'
                       '### REQ-010-AC-01: another acceptance\nA separate owner criterion.\n',
                       "other/REQ-010.md")
        self.config(lambda data: data["boundedContexts"].append({"id": "CTX-002"}))
        self.commit()
        self.error("AMBIGUOUS_SCOPE")
        self.assertEqual(list(DELIVERY), [e["target"] for e in self.collect(scope=self.scope)["entries"]])
        self.assertEqual(["sample/CTX-002/REQ-010#req-010-ac-01"],
                         [e["target"] for e in self.collect(scope="sample/CTX-002")["entries"]])
        self.error("INVALID_SCOPE", scope="sample/CTX-999")

    def test_primary_missing_config_domain_or_empty_acceptance_corpus_is_not_optional_success(self):
        config = self.root / "bc-config.yaml"
        config.unlink()
        self.commit()
        self.error("OBJECT_PATH_MISSING")
        empty = self.workspace / "empty"
        sha = seed_git_repo(empty)
        with self.assertRaises(ArtifactInputError):
            self.tool().build_report(empty, sha, [])

    def test_separate_local_domain_git_bytes_index_and_config_unchanged_success_and_error(self):
        domain = self.workspace / "领域 readonly"
        seed_git_repo(domain)
        (domain / "model").mkdir()
        (domain / "model/rule.txt").write_bytes(b"Owned domain rule, fixed version.\n")
        git(domain, "add", "--", ".")
        git(domain, "commit", "--quiet", "-m", "Fixed local domain source")
        baseline = git(domain, "rev-parse", "HEAD")
        self.config(lambda data: data.update(domainSources=[{
            "id": "external-local-domain", "kind": "git", "root": "../领域 readonly",
            "path": "model", "baseline": baseline, "readOnly": True,
        }]))
        self.commit()
        before = source_bytes(self.workspace)
        report = self.collect()
        self.assertEqual([{"root": "../领域 readonly", "path": "model", "baseline": baseline}], report["domainSources"])
        self.assertEqual(before, source_bytes(self.workspace))
        (domain / "model/rule.txt").write_bytes(b"Changed local rule, must not repair.\n")
        before_error = source_bytes(self.workspace)
        self.error("BASE_MISMATCH")
        self.assertEqual(before_error, source_bytes(self.workspace))

    def test_domain_root_and_path_are_not_guessed_or_doubled(self):
        self.config(lambda data: data["domainSources"][0].update(root="domain-model", path="domain-model/DM-001.md"))
        self.commit()
        self.error("FILE_NOT_FOUND")

    def test_h2_h1_comments_and_literal_examples_do_not_become_owned_runs(self):
        selector, _ = self.run_record()
        path = self.root / "verification/VT-002.md"
        original = path.read_text(encoding="utf-8")
        start = original.index('<a id="vt-002-run-01">')
        prefix, block = original[:start], original[start:]
        for fake in (block.replace("### VT-002-RUN-", "## VT-002-RUN-"),
                     block.replace("### VT-002-RUN-", "# VT-002-RUN-"),
                     "<!--\n" + block + "\n-->\n", "````markdown\n" + block + "\n````\n"):
            with self.subTest(fake=fake[:50]):
                path.write_text(prefix + fake, encoding="utf-8")
                report = self.collect(["verification/VT-002.md"])
                self.assertEqual(["not-run"] * 4, [e["execution"]["status"] for e in report["entries"]])
                self.error("UNKNOWN_RUN", [selector])

    def test_applicability_requires_separate_matching_source_row(self):
        selector, _ = self.run_record()
        path = self.root / "verification/VT-002.md"
        row = (
            f"| 2026-10-16; recorder=synthetic reviewer | [运行](#{selector.split('#')[1]}) [判据](#record) "
            f"| object={self.object}; requirement={self.scope}/SR-001@{self.object}; vt={self.object} "
            "| 适用 | Independent synthetic applicability input for this exact criterion and bases. |\n"
        )
        with path.open("a", encoding="utf-8") as output:
            output.write('\n<a id="applicability"></a>\n## 当前适用性复核\n\n'
                         '| 复核日期与记录者 | 原运行/结果及目标链接 | 当前对象、需求与 VT 基线 | 适用性 | 理由、影响与待重查事项 |\n'
                         '|---|---|---|---|---|\n' + row)
        self.assertEqual("applicable", self.entries(self.collect([selector]))[DELIVERY[2]]["applicability"]["state"])
        self.assertEqual("unverified", self.entries(self.collect([selector]))[DELIVERY[3]]["applicability"]["state"])
        with path.open("a", encoding="utf-8") as output:
            output.write(row)
        self.error("AMBIGUOUS_APPLICABILITY", [selector])

    def test_cli_default_is_read_only_and_fail_input_and_output_have_real_exits(self):
        before = source_bytes(self.root)
        result = self.cli()
        self.assertEqual(0, result.returncode, result.stderr + result.stdout)
        self.assertEqual(4, len(json.loads(result.stdout)["entries"]))
        self.assertEqual(before, source_bytes(self.root))
        selector, _ = self.run_record(statuses={"record": "fail"}, counts="exit=1; discovered=1; executed=1; skipped=0")
        output = self.root / "报告 summary.json"
        before = source_bytes(self.root)
        result = self.cli("--evidence", selector, "--output", str(output))
        self.assertEqual(1, result.returncode, result.stderr + result.stdout)
        self.assertEqual(json.loads(result.stdout), json.loads(output.read_bytes()))
        after = source_bytes(self.root)
        del after[output.relative_to(self.root).as_posix()]
        self.assertEqual(before, after)
        second = self.cli("--output", str(output))
        self.assertEqual(2, second.returncode)
        self.assertIn("REPORT_CONFLICT", second.stdout)
        invalid = self.cli("--output", str(self.root / "never.json"), object_sha="HEAD")
        self.assertEqual(2, invalid.returncode)
        self.assertFalse((self.root / "never.json").exists())

    def test_cli_protects_object_files_missing_now_and_does_not_create_directories(self):
        current = self.root / "bc-config.yaml"
        current.unlink()
        result = self.cli("--output", str(current))
        self.assertEqual(2, result.returncode, result.stderr + result.stdout)
        self.assertIn("REPORT_CONFLICT", result.stdout)
        self.assertFalse(current.exists())
        result = self.cli("--output", str(self.root / "not-created/report.json"))
        self.assertEqual(2, result.returncode)
        self.assertFalse((self.root / "not-created").exists())

    def test_cli_protects_later_missing_nested_optional_declarations_after_first_failure(self):
        (self.root / "sources").mkdir()
        source = self.root / "sources/quality.yaml"
        source.write_text(yaml.safe_dump({"quality": {
            "qasRefs": [], "utilityTree": {"reference": "sources/first-missing.yaml", "baseline": "sha256:" + "0" * 64},
            "testScenarios": [{"reference": "sources/later-missing.yaml", "baseline": "sha256:" + "1" * 64}],
        }}), encoding="utf-8")
        (self.root / "model-sources.yaml").write_text(yaml.safe_dump({
            "schemaVersion": 1, "scopes": {self.scope: {"quality": [
                {"path": "sources/quality.yaml", "baseline": digest(source.read_bytes())}
            ]}}
        }), encoding="utf-8")
        before = source_bytes(self.root)
        result = self.cli("--output", "sources/later-missing.yaml")
        self.assertEqual(2, result.returncode, result.stderr + result.stdout)
        self.assertIn("REPORT_CONFLICT", result.stdout)
        self.assertEqual(before, source_bytes(self.root))


class Task8BoundaryTests(ImplementationFixture):
    """Additional source-boundary controls, including self-review reproductions."""

    def test_status_only_observations_cannot_be_execution_evidence(self):
        selector, _ = self.run_record()
        actual = "Observed the prepared state against record; "
        for word in ("Approved", "success", "passed", "成功", "已通过"):
            with self.subTest(word=word):
                self.replace_in_vt(actual, word + " ")
                try:
                    self.error("INVALID_OBSERVATION", [selector])
                finally:
                    self.replace_in_vt(word + " [原始输入]", actual + "[原始输入]")

    def test_short_real_recorder_name_is_not_rejected_as_missing_prose(self):
        selector, _ = self.run_record()
        self.replace_in_vt("recorder=synthetic fixture", "recorder=Li")
        try:
            report = self.collect([selector])
        except ArtifactInputError as error:
            self.fail(f"A concrete short recorder is a name, not missing observation prose: {error.code}")
        self.assertEqual("pass", self.entries(report)[DELIVERY[2]]["execution"]["status"])

    def test_known_empty_raw_report_and_unknown_fragment_are_errors(self):
        selector, path = self.run_record()
        old = digest(path.read_bytes())
        path.write_bytes(b"")
        self.replace_in_vt(old, digest(b""))
        self.error("INVALID_EVIDENCE", [selector])
        path.write_bytes(b"An explicit synthetic record without supported fragments.\n")
        self.replace_in_vt(digest(b""), digest(path.read_bytes()))
        self.replace_in_vt(f"../reports/{path.name}>", f"../reports/{path.name}#missing>")
        self.error("BROKEN_ANCHOR", [selector])

    def test_unreadable_raw_report_is_explicit_narrow_io_failure_not_optional_gap(self):
        selector, raw = self.run_record()
        before = source_bytes(self.root)
        actual_read = Path.read_bytes
        def deny_only_raw(path):
            if path == raw:
                raise PermissionError("Injected I/O boundary at the original report")
            return actual_read(path)
        with patch.object(Path, "read_bytes", deny_only_raw):
            self.error("FILE_READ_ERROR", [selector])
        self.assertEqual(before, source_bytes(self.root))

    def test_different_requirement_content_at_readable_commit_is_not_same_basis(self):
        selected = self.object
        path = self.root / "software-requirements/SR-001.md"
        path.write_text(path.read_text(encoding="utf-8").replace("新增一条", "新增两条"), encoding="utf-8")
        other = self.commit()
        self.object = selected
        selector, _ = self.run_record(requirement_basis=f"{self.scope}/SR-001@{other}")
        self.error("BASE_MISMATCH", [selector])

    def test_different_plan_content_at_readable_commit_is_not_same_plan(self):
        selected = self.object
        self.replace_in_vt("有效请求新增一条关联会员的记录。", "有效请求新增两条关联会员的记录。")
        other = self.commit()
        # Restore the tested object's plan in the working tree before appending.
        raw = subprocess.run(
            ["git", "--no-pager", "show", selected + ":verification/VT-002.md"],
            cwd=self.root, shell=False, capture_output=True, check=True).stdout
        (self.root / "verification/VT-002.md").write_bytes(raw)
        self.object = selected
        selector, _ = self.run_record(plan_basis=other)
        self.error("PLAN_MISMATCH", [selector])

    def test_missing_actual_test_id_in_command_is_not_inferred_from_locator(self):
        selector, _ = self.run_record(steps="fixture-input-only-runner an_unrelated_test")
        self.error("INVALID_EXECUTION", [selector])

    def test_actual_manual_steps_cannot_be_replaced_by_unexecuted_placeholder(self):
        selector, _ = self.run_record(vt="VT-001", mode="manual", counts=None, steps="未执行")
        self.error("INVALID_RUN", [selector])

    def test_valid_bc_without_any_owner_acceptances_is_explicitly_empty_input(self):
        for relative in ("stakeholder-requirements/REQ-001.md", "software-requirements/SR-001.md",
                         "verification/VT-001.md", "verification/VT-002.md"):
            (self.root / relative).unlink()
        self.commit()
        self.error("EMPTY_ACCEPTANCE")

    def test_invalid_bc_readonly_type_is_not_silently_coerced(self):
        self.config(lambda data: data["domainSources"][0].update(readOnly="true"))
        self.commit()
        before = source_bytes(self.root)
        self.error("INVALID_METADATA")
        self.assertEqual(before, source_bytes(self.root))

    def test_raw_sha_bases_preserve_exact_requirement_and_plan_bytes(self):
        requirement = digest((self.root / "software-requirements/SR-001.md").read_bytes())
        plan = digest((self.root / "verification/VT-002.md").read_bytes())
        selector, _ = self.run_record(requirement_basis=f"{self.scope}/SR-001@{requirement}", plan_basis=plan)
        refs = self.entries(self.collect([selector]))[DELIVERY[2]]["execution"]["evidenceRefs"]
        self.assertIn({"reference": "software-requirements/SR-001.md#sr-001-ac-01", "baseline": requirement}, refs)
        self.assertIn({"reference": "verification/VT-002.md#record", "baseline": plan}, refs)

    def test_replace_refs_and_filter_settings_cannot_change_the_exact_object_or_run(self):
        selected = self.object
        (self.root / "source code/借用.txt").write_text("Other object's content", encoding="utf-8")
        replacement = self.commit()
        git(self.root, "replace", selected, replacement)
        marker = self.root / "filter-was-executed.txt"
        git(self.root, "config", "filter.unused.smudge",
            f'{sys.executable} -c "open({str(marker)!r}, \'w\').write(\'wrong\')"')
        self.object = selected
        before = source_bytes(self.root)
        report = self.collect()
        self.assertEqual("record", report["entries"][2]["codeRefs"][0]["symbol"])
        self.assertFalse(marker.exists())
        self.assertEqual(before, source_bytes(self.root))

    def test_unsafe_declared_optional_path_blocks_output_but_not_readonly_collection(self):
        (self.root / "sources").mkdir()
        source = self.root / "sources/quality.yaml"
        source.write_text(yaml.safe_dump({"quality": {
            "utilityTree": {"reference": "../escape.yaml", "baseline": "sha256:" + "0" * 64}
        }}), encoding="utf-8")
        (self.root / "model-sources.yaml").write_text(yaml.safe_dump({
            "schemaVersion": 1, "scopes": {self.scope: {"quality": [
                {"path": "sources/quality.yaml", "baseline": digest(source.read_bytes())}
            ]}}
        }), encoding="utf-8")
        self.assertEqual(4, len(self.collect()["entries"]))
        before = source_bytes(self.root)
        result = self.cli("--output", "otherwise-new.yaml")
        self.assertEqual(2, result.returncode, result.stderr + result.stdout)
        self.assertIn("REPORT_CONFLICT", result.stdout)
        self.assertEqual(before, source_bytes(self.root))

    def test_final_shared_criterion_cannot_supply_two_independent_targets(self):
        self.replace_in_vt("criterionAnchor: no-write", "criterionAnchor: record")
        self.commit()
        selector, _ = self.run_record()
        path = self.root / "verification/VT-002.md"
        path.write_text("\n".join(line for line in path.read_text(encoding="utf-8").splitlines()
                                  if not line.startswith("| [no-write](#no-write)")) + "\n",
                        encoding="utf-8", newline="\n")
        self.error("INVALID_CRITERION", [selector])

    def test_final_applicability_table_does_not_continue_across_a_literal_block(self):
        selector, _ = self.run_record()
        path = self.root / "verification/VT-002.md"
        with path.open("a", encoding="utf-8") as output:
            output.write('\n<a id="applicability"></a>\n## 当前适用性复核\n\n'
                         '| 复核日期与记录者 | 原运行/结果及目标链接 | 当前对象、需求与 VT 基线 | 适用性 | 理由、影响与待重查事项 |\n'
                         '|---|---|---|---|---|\n'
                         '```text\nA literal example interrupts the real table.\n```\n'
                         f'| 2026-10-16; recorder=synthetic reviewer | [运行](#{selector.split("#")[1]}) [判据](#record) '
                         f'| object={self.object}; requirement={self.scope}/SR-001@{self.object}; vt={self.object} '
                         '| 适用 | This isolated row is not part of the preceding table. |\n')
        self.assertEqual("unverified", self.entries(self.collect([selector]))[DELIVERY[2]]["applicability"]["state"])

    def test_final_plan_projection_uses_parser_line_boundaries_without_normalizing_bytes(self):
        path = self.root / "verification/VT-002.md"
        self.replace_in_vt('<a id="runs"></a>', 'Known plan notes:' + "\u2028" * 40 + '\n<a id="runs"></a>')
        self.commit()
        selector, _ = self.run_record()
        before = source_bytes(self.root)
        try:
            report = self.collect([selector])
        except ArtifactInputError as error:
            self.fail(f"Appending an owned run must retain the exact UTF-8 plan with Unicode line separators: {error.code}")
        self.assertEqual("pass", self.entries(report)[DELIVERY[2]]["execution"]["status"])
        self.assertEqual(before, source_bytes(self.root))

    def test_final_evidence_mapping_cannot_silently_drop_its_values(self):
        self.error("INVALID_EVIDENCE_SELECTION", {"verification/VT-002.md": "copied status is not an evidence selector"})


class Task8Fix1EvidenceTests(ImplementationFixture):
    """T8-I2/I3: source-owned accounting and protected committed criteria."""

    def assert_input_error_preserves_sources(self, code, selector):
        before = source_bytes(self.root)
        try:
            return self.error(code, [selector])
        finally:
            self.assertEqual(before, source_bytes(self.root))

    def test_i2_distinct_executed_ids_cannot_fit_one_recorded_execution(self):
        for number, second in enumerate(("pass", "fail"), 1):
            with self.subTest(second=second):
                selector, _ = self.run_record(
                    number=number, statuses={"record": "pass", "no-write": second},
                    counts=f"exit={0 if second == 'pass' else 1}; discovered=1; executed=1; skipped=0",
                )
                self.assert_input_error_preserves_sources("INVALID_EXECUTION", selector)

    def test_i2_one_test_covering_independent_criteria_is_counted_once(self):
        self.replace_in_vt("testId: test_no_write", "testId: test_record")
        (self.root / "native tests/验证.txt").write_text(
            "# Self-owned TEXT locator; no native test is executed.\n"
            f"# verifies: {DELIVERY[2]} testId=test_record\n"
            f"# verifies: {DELIVERY[3]} testId=test_record\n"
            "test_record(): one test text location covering two independent criteria\n",
            encoding="utf-8", newline="\n",
        )
        self.commit()
        selector, raw = self.run_record(statuses={"record": "pass", "no-write": "pass"},
                                        steps="fixture-input-only-runner test_record")
        previous = digest(raw.read_bytes())
        raw.write_bytes(b"SYNTHETIC INPUT ONLY: test_record observed record and no-write criteria.\n")
        self.replace_in_vt(previous, digest(raw.read_bytes()))
        before = source_bytes(self.root)
        entries = self.entries(self.collect([selector]))
        for target in DELIVERY[2:]:
            self.assertEqual("pass", entries[target]["execution"]["status"])
            self.assertEqual("test_record", entries[target]["testRefs"][0]["testId"])
        self.assertEqual(before, source_bytes(self.root))

    def test_i2_additional_actual_tests_outside_mapped_criteria_are_allowed(self):
        selector, _ = self.run_record(statuses={"record": "pass", "no-write": "pass"},
                                     counts="exit=0; discovered=4; executed=3; skipped=1")
        before = source_bytes(self.root)
        entries = self.entries(self.collect([selector]))
        self.assertEqual(["pass", "pass"], [entries[target]["execution"]["status"] for target in DELIVERY[2:]])
        self.assertEqual(before, source_bytes(self.root))

    def test_i2_skip_not_run_and_names_in_command_text_do_not_inflate_executed_ids(self):
        for number, second in enumerate(("not-run", "skipped"), 1):
            with self.subTest(second=second):
                skipped = int(second == "skipped")
                selector, _ = self.run_record(
                    number=number, statuses={"record": "pass", "no-write": second},
                    steps="fixture-input-only-runner test_record test_no_write extra_unmapped_name",
                    counts=f"exit=0; discovered={1 + skipped}; executed=1; skipped={skipped}",
                )
                before = source_bytes(self.root)
                entries = self.entries(self.collect([selector]))
                self.assertEqual("pass", entries[DELIVERY[2]]["execution"]["status"])
                self.assertEqual(second, entries[DELIVERY[3]]["execution"]["status"])
                self.assertEqual(before, source_bytes(self.root))

    def test_i2_manual_observations_need_no_command_execution_counts(self):
        selector, _ = self.run_record(vt="VT-001", mode="manual", counts=None,
                                     statuses={"allow": "pass", "reject": "pass"})
        before = source_bytes(self.root)
        entries = self.entries(self.collect([selector]))
        self.assertEqual(["pass", "pass"], [entries[target]["execution"]["status"] for target in DELIVERY[:2]])
        self.assertEqual(before, source_bytes(self.root))

    def test_i2_no_executed_rows_remain_skip_or_not_run_with_zero_executions(self):
        for number, status in enumerate(("skipped", "not-run"), 1):
            with self.subTest(status=status):
                skipped = 2 if status == "skipped" else 0
                selector, _ = self.run_record(
                    number=number, statuses={"record": status, "no-write": status},
                    steps="未执行", report=False,
                    counts=f"exit=0; discovered={skipped}; executed=0; skipped={skipped}",
                )
                before = source_bytes(self.root)
                entries = self.entries(self.collect([selector]))
                self.assertEqual([status, status], [entries[target]["execution"]["status"] for target in DELIVERY[2:]])
                self.assertEqual(before, source_bytes(self.root))

    def misplaced_criterion(self, section, *, criterion="record", changed=True):
        """Commit the misplaced plan FIRST; append a genuinely owned run later."""
        path = self.root / "verification/VT-002.md"
        text = path.read_text(encoding="utf-8")
        start = text.index(f'<a id="{criterion}"></a>')
        end = text.index('<a id="', start + 1)
        block = text[start:end]
        text = text[:start] + text[end:]
        if section == "runs":
            heading = '<a id="runs"></a>\n## 实际执行\n\n'
            self.assertIn(heading, text)
            text = text.replace(heading, heading + block)
        else:
            text += '\n<a id="applicability"></a>\n## 当前适用性复核\n\n' + block
        path.write_text(text, encoding="utf-8", newline="\n")
        self.commit()
        old = ("有效请求新增一条关联会员的记录。" if criterion == "record"
               else "超额请求返回拒绝且前后记录完全相同。")
        new = ("有效请求删除所有关联会员记录。" if criterion == "record"
               else "超额请求返回许可并重写既有记录。")
        committed = git(self.root, "show", self.object + ":verification/VT-002.md")
        self.assertIn(old, committed)
        self.assertLess(committed.index(f'<a id="{section}"></a>'),
                        committed.index(f'<a id="{criterion}"></a>'))
        if changed:
            self.replace_in_vt(old, new)
        selector, _ = self.run_record()  # One pass ID / one execution: not masked by I2.
        if section == "applicability":
            text = path.read_text(encoding="utf-8")
            split = text.index('<a id="vt-002-run-01"></a>')
            prefix, run = text[:split], text[split:]
            # Keep the new child under runs, BEFORE the closing applicability H2.
            prefix = prefix.replace('<a id="applicability"></a>', run + '\n<a id="applicability"></a>')
            path.write_text(prefix, encoding="utf-8", newline="\n")
        if changed:
            self.assertIn(new, path.read_text(encoding="utf-8"))
            self.assertNotIn(new, committed)
        return selector

    def test_i3_changed_criterion_committed_under_runs_is_not_an_old_plan_pass(self):
        selector = self.misplaced_criterion("runs")
        self.assert_input_error_preserves_sources("INVALID_CRITERION", selector)

    def test_i3_changed_criterion_committed_under_applicability_is_protected(self):
        selector = self.misplaced_criterion("applicability")
        self.assert_input_error_preserves_sources("INVALID_CRITERION", selector)

    def test_i3_unexecuted_declared_criterion_cannot_be_omitted_from_plan_comparison(self):
        selector = self.misplaced_criterion("applicability", criterion="no-write")
        self.assert_input_error_preserves_sources("INVALID_CRITERION", selector)

    def test_i3_misplaced_unchanged_criterion_is_explicitly_unsupported(self):
        selector = self.misplaced_criterion("runs", changed=False)
        self.assert_input_error_preserves_sources("INVALID_CRITERION", selector)

    def test_i3_genuine_appends_keep_criteria_unicode_and_crlf_bytes_protected(self):
        path = self.root / "verification/VT-002.md"
        raw = path.read_bytes().replace(
            b'<a id="runs"></a>',
            ("Known plan note：" + "\u2028" * 3 + '\n<a id="runs"></a>').encode("utf-8"),
        )
        path.write_bytes(b"\xef\xbb\xbf" + raw.replace(b"\n", b"\r\n"))
        self.commit()
        committed_prefix = path.read_bytes()
        selector, _ = self.run_record()
        self.assertTrue(path.read_bytes().startswith(committed_prefix))
        with path.open("a", encoding="utf-8", newline="\r\n") as output:
            output.write('\n<a id="applicability"></a>\n## 当前适用性复核\n\n'
                         '| 复核日期与记录者 | 原运行/结果及目标链接 | 当前对象、需求与 VT 基线 | 适用性 | 理由、影响与待重查事项 |\n'
                         '|---|---|---|---|---|\n'
                         f'| 2026-10-16; recorder=fixture reviewer | [运行](#{selector.split("#")[1]}) [判据](#record) '
                         f'| object={self.object}; requirement={self.scope}/SR-001@{self.object}; vt={self.object} '
                         '| 适用 | Independently supplied synthetic applicability for these exact bases. |\n')
        before = source_bytes(self.root)
        entry = self.entries(self.collect([selector]))[DELIVERY[2]]
        self.assertEqual("pass", entry["execution"]["status"])
        self.assertEqual("applicable", entry["applicability"]["state"])
        self.assertEqual(before, source_bytes(self.root))


if __name__ == "__main__":
    unittest.main()
