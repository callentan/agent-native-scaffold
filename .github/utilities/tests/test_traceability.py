"""ENH-08 / TRACE-01..09: full owner inventory, layered criteria and impact.

Each expectation uses independent source files/IDs and real Git or subprocesses.
No business VT is executed by these maintenance tests.
"""

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

from artifact_io import parse_artifact
from tests.helpers import (
    WORKTREE, criterion_block, git, metadata, seed_git_repo, source_bytes,
    temporary_workspace, write_artifact, write_delivery_fixture, write_metadata,
)


DELIVERY = (
    "sample/CTX-001/REQ-001#req-001-ac-01", "sample/CTX-001/REQ-001#req-001-ac-02",
    "sample/CTX-001/SR-001#sr-001-ac-01", "sample/CTX-001/SR-001#sr-001-ac-02",
)
SCRIPT = WORKTREE / ".github" / "utilities" / "check_traceability.py"


class TraceFixture(unittest.TestCase):
    def setUp(self):
        temporary = temporary_workspace()
        self.addCleanup(temporary.cleanup)
        self.workspace = Path(temporary.name)
        self.root = self.workspace / "交付 inputs with spaces"
        self.root.mkdir()
        self.delivery = write_delivery_fixture(self.root)

    def tool(self):
        self.assertIsNotNone(importlib.util.find_spec("check_traceability"),
                             "Task7 traceability module is not implemented")
        return importlib.import_module("check_traceability")

    def report(self, delivery=DELIVERY):
        return self.tool().trace_report(self.root, delivery)

    def replace(self, relative, before, after):
        path = self.root / relative
        original = path.read_text(encoding="utf-8")
        self.assertIn(before, original)
        path.write_text(original.replace(before, after), encoding="utf-8", newline="\n")

    def cli(self, *arguments, root=None):
        self.assertTrue(SCRIPT.is_file(), "Task7 traceability CLI is not implemented")
        return subprocess.run(
            [sys.executable, "-B", "-X", "utf8", str(SCRIPT),
             "--root", str(self.root if root is None else root), *arguments],
            cwd=self.workspace, shell=False, capture_output=True, text=True, encoding="utf-8",
        )

    def delivery_args(self):
        return [arg for target in DELIVERY for arg in ("--delivery", target)]

    def finding(self, report, code):
        found = [item for item in report.findings if item.code == code]
        self.assertTrue(found, (code, report))
        return found[0]


class TraceabilityTests(TraceFixture):
    def test_fixture_omission_keeps_all_four_owner_acceptances_and_other_files(self):
        original = source_bytes(self.root)
        self.assertEqual(DELIVERY, self.delivery)
        self.assertEqual(DELIVERY, write_delivery_fixture(self.root, True))
        after = source_bytes(self.root)
        self.assertEqual(["verification/VT-002.md"],
                         [name for name in original if original[name] != after[name]])
        self.assertEqual(DELIVERY[2:], parse_artifact(
            "software-requirements/SR-001.md", self.root).acceptance_ids)
        self.assertEqual(1, len(parse_artifact("verification/VT-002.md", self.root).targets))

    def test_all_four_have_independent_layered_coverage_without_us_or_execution(self):
        before, cwd = source_bytes(self.root), Path.cwd()
        report = self.report()
        self.assertEqual("clean", report.status)
        self.assertEqual((5, 5), (report.checked_count, report.attempted_count))
        self.assertEqual((), report.findings)
        self.assertEqual("working-tree", report.baseline.target)
        self.assertEqual(report, self.report())
        self.assertEqual(before, source_bytes(self.root))
        self.assertEqual(cwd, Path.cwd())
        self.assertNotIn("execution", report.to_dict())

    def test_omitted_software_reject_has_exact_owner_path_line_and_baseline(self):
        write_delivery_fixture(self.root, True)
        before = source_bytes(self.root)
        report = self.report()
        self.assertEqual("invalid", report.status)
        self.assertEqual([("UNCOVERED_ACCEPTANCE", DELIVERY[3])],
                         [(f.code, f.target) for f in report.findings])
        item = report.findings[0]
        self.assertEqual("sample/CTX-001/SR-001", item.owner)
        self.assertEqual(str(self.root / "software-requirements/SR-001.md"), item.path)
        lines = before["software-requirements/SR-001.md"].decode().splitlines()
        self.assertEqual(lines.index("### SR-001-AC-02：拒绝请求无副作用") + 1, item.line)
        source = next(f for f in report.baseline.files if f.path == "software-requirements/SR-001.md")
        self.assertEqual(hashlib.sha256(before[source.path]).hexdigest(), source.sha256)
        self.assertEqual(before, source_bytes(self.root))

    def test_dangling_target_outside_delivery_still_has_origin_location(self):
        write_metadata(self.root, metadata(id="VT-003", kind="verification-test", targets=[
            {"target": "other/CTX-002/REQ-999#req-999-ac-01", "criterionAnchor": "extra"}]),
            '# VT-003：范围外\n<a id="plan"></a>\n## 计划\n'
            '| 验证层次 | 业务验收 |\n' +
            criterion_block("extra", "在已知前提下没有新增借用。",
                            "提交再比较业务记录。", "已有有效资格但并发未知。"),
            "verification/VT-003.md")
        report = self.report()
        self.assertEqual("invalid", report.status)
        finding = self.finding(report, "DANGLING_TARGET")
        self.assertEqual("other/CTX-002/REQ-999#req-999-ac-01", finding.target)
        self.assertEqual("sample/CTX-001/VT-003", finding.owner)
        self.assertEqual(str(self.root / "verification/VT-003.md"), finding.path)
        self.assertEqual(8, finding.line)
        self.assertNotIn("UNCOVERED_ACCEPTANCE", [f.code for f in report.findings])

    def test_target_ordinary_anchor_is_not_owner_acceptance(self):
        self.replace("verification/VT-001.md", DELIVERY[0], "sample/CTX-001/DM-001#rule-001")
        report = self.report()
        self.finding(report, "TARGET_NOT_ACCEPTANCE")
        self.assertEqual([DELIVERY[0]], [f.target for f in report.findings if f.code == "UNCOVERED_ACCEPTANCE"])

    def test_same_short_id_other_scope_cannot_fill_omitted_owner(self):
        write_delivery_fixture(self.root, True)
        write_artifact(self.root, id="SR-001", scope="sample/CTX-002", kind="software-requirement",
                       acceptance_ids=("SR-001-AC-02",), relative_path="other/SR-001.md")
        self.replace("verification/VT-002.md", DELIVERY[2], "sample/CTX-002/SR-001#sr-001-ac-02")
        report = self.report()
        self.assertEqual(set(DELIVERY[2:]), {f.target for f in report.findings if f.code == "UNCOVERED_ACCEPTANCE"})
        self.assertNotIn("DUPLICATE_ARTIFACT_ID", [f.code for f in report.findings])

    def test_missing_criterion_anchor_keeps_parser_input_failure(self):
        self.replace("verification/VT-002.md", '<a id="no-write"></a>', "")
        report = self.report()
        self.assertEqual("input-error", report.status)
        self.finding(report, "MISSING_CRITERION_ANCHOR")
        self.assertNotIn("UNCOVERED_ACCEPTANCE", [f.code for f in report.findings])

    def test_anchor_heading_placeholders_and_generic_summary_are_not_criteria(self):
        path = self.root / "verification/VT-002.md"
        original = path.read_text(encoding="utf-8")
        start = original.index('<a id="no-write">')
        stop = original.index('<a id="runs">')
        for content in ("", "全部通过。", "all pass", "<!-- meaningful-looking ignored text -->",
                        "```text\n预期：拒绝；方法：观察；前提：有效。\n```",
                        "| 本目标预期与独立判定标准 | 待填写 |\n"):
            with self.subTest(content=content):
                path.write_text(original[:start] + '<a id="no-write"></a>\n### 独立判据\n'
                                + content + "\n" + original[stop:], encoding="utf-8")
                report = self.report()
                self.finding(report, "INSUFFICIENT_CRITERION")
                self.assertIn(DELIVERY[3], [f.target for f in report.findings if f.code == "UNCOVERED_ACCEPTANCE"])

    def test_declared_wrong_layer_is_not_inferred_from_vt_filename(self):
        self.replace("verification/VT-002.md", "| 验证层次 | 软件行为 |", "| 验证层次 | 业务验收 |")
        report = self.report()
        self.assertEqual(set(DELIVERY[2:]), {f.target for f in report.findings if f.code == "LAYER_MISMATCH"})

    def test_missing_unknown_or_ambiguous_plan_layer_is_explicit(self):
        path = self.root / "verification/VT-002.md"
        original = path.read_text(encoding="utf-8")
        for row in ("", "| 验证层次 | unknown |", "| 验证层次 | 软件行为／业务验收 |",
                    "| 验证层次 | 软件行为 |\n| 验证层次 | 业务验收 |",
                    "```text\n| 验证层次 | 软件行为 |\n```"):
            with self.subTest(row=row):
                path.write_text(original.replace("| 验证层次 | 软件行为 |", row), encoding="utf-8")
                report = self.report()
                self.finding(report, "UNKNOWN_VALIDATION_LAYER")
                self.assertEqual(set(DELIVERY[2:]), {f.target for f in report.findings if f.code == "UNCOVERED_ACCEPTANCE"})

    def test_layer_declaration_in_runs_cannot_replace_missing_plan(self):
        self.replace("verification/VT-002.md", "| 验证层次 | 软件行为 |", "")
        self.replace("verification/VT-002.md", "## 实际执行", "## 实际执行\n| 验证层次 | 软件行为 |")
        self.finding(self.report(), "UNKNOWN_VALIDATION_LAYER")

    def test_two_targets_cannot_share_one_criterion(self):
        self.replace("verification/VT-002.md", "criterionAnchor: no-write", "criterionAnchor: record")
        report = self.report()
        self.finding(report, "SHARED_CRITERION")
        self.assertEqual(set(DELIVERY[2:]), {f.target for f in report.findings if f.code == "UNCOVERED_ACCEPTANCE"})

    def test_business_ts_uses_real_basis_declaration_and_cannot_cover_software(self):
        (self.root / "verification/VT-001.md").unlink()
        write_metadata(self.root, metadata(id="TS-001", kind="validation-scenario", targets=[
            {"target": DELIVERY[0], "criterionAnchor": "allow"},
            {"target": DELIVERY[1], "criterionAnchor": "reject"}]),
            '# TS-001：业务场景\n<a id="basis"></a>\n## 依据\n'
            '| 业务范围与场景类型 | REQ 业务验收：借用额度 |\n'
            '<a id="targets"></a>\n## 逐项目标\n'
            '<a id="allow"></a>\n### 允许\n'
            '- 本目标前提与输入：会员资格有效且在额度内。\n'
            '- 本目标动作、观察与独立判定标准：办理一次借用后业务登记增加。\n'
            '- 对应步骤或实际测试标识：人工比较前后业务登记。\n'
            '- 来源导航、未决条件与禁止副作用：不得改变其他会员登记；并发未知。\n'
            '<a id="reject"></a>\n### 拒绝\n'
            '- 本目标前提与输入：会员资格有效但已达额度。\n'
            '- 本目标动作、观察与独立判定标准：再次申请后业务登记不变。\n'
            '- 对应步骤或实际测试标识：人工核对拒绝响应及业务登记。\n'
            '- 来源导航、未决条件与禁止副作用：不能形成新借用；失效策略未知。\n',
            "verification/TS-001.md")
        self.assertEqual("clean", self.report().status)
        self.replace("verification/TS-001.md", DELIVERY[0], DELIVERY[2])
        self.finding(self.report(), "LAYER_MISMATCH")

    def test_mentions_code_and_comments_do_not_become_acceptance_inventory(self):
        path = self.root / "stakeholder-requirements/REQ-001.md"
        with path.open("a", encoding="utf-8") as stream:
            stream.write('\nMention REQ-001-AC-99 and SR-001-AC-03.\n'
                         '<!-- <a id="req-001-ac-03"></a>\n### REQ-001-AC-03：comment -->\n'
                         '```md\n<a id="req-001-ac-04"></a>\n### REQ-001-AC-04：code\n```\n')
        self.assertEqual("clean", self.report().status)

    def test_bad_formal_inventory_cannot_be_reclassified_as_coverage(self):
        write_artifact(self.root, relative_path="duplicate/REQ-001.md")
        report = self.report()
        self.assertEqual("input-error", report.status)
        self.finding(report, "DUPLICATE_ARTIFACT_ID")
        self.assertNotIn("UNCOVERED_ACCEPTANCE", [f.code for f in report.findings])

    def test_unreadable_primary_injected_io_error_is_not_empty_success(self):
        # Explicit I/O failure injection only; all source parsing remains real.
        read = Path.read_bytes
        denied = self.root / "software-requirements/SR-001.md"
        def read_or_deny(path):
            if path == denied:
                raise PermissionError("Injected unavailable primary input")
            return read(path)
        self.tool()
        with patch.object(Path, "read_bytes", read_or_deny):
            report = self.report()
        self.assertEqual("input-error", report.status)
        self.finding(report, "FILE_READ_ERROR")

    def test_bad_root_preserves_input_error(self):
        report = self.tool().trace_report(self.root / "absent", DELIVERY)
        self.assertEqual("input-error", report.status)
        self.finding(report, "INVALID_ROOT")

    def test_malformed_duplicate_unknown_and_empty_delivery_are_input_errors(self):
        for delivery, code in (
            ("not-a-list", "INVALID_DELIVERY"), ([], "EMPTY_DELIVERY"),
            ([DELIVERY[0], DELIVERY[0]], "DUPLICATE_DELIVERY_ID"),
            (["SR-001-AC-01"], "INVALID_DELIVERY_ID"), ([None], "INVALID_DELIVERY_ID"),
            (["sample/CTX-001/SR-999#sr-999-ac-01"], "UNKNOWN_DELIVERY_ID"),
            (["sample/CTX-001/DM-001#rule-001"], "UNKNOWN_DELIVERY_ID"),
        ):
            with self.subTest(delivery=delivery):
                report = self.report(delivery)
                self.assertEqual("input-error", report.status)
                self.finding(report, code)
                self.assertNotIn("UNCOVERED_ACCEPTANCE", [f.code for f in report.findings])

    def test_duplicate_unknown_selection_is_not_silently_shrunk(self):
        unknown = "sample/CTX-001/SR-999#sr-999-ac-01"
        report = self.report([DELIVERY[0], unknown, unknown])
        self.assertEqual("input-error", report.status)
        self.finding(report, "UNKNOWN_DELIVERY_ID")
        self.finding(report, "DUPLICATE_DELIVERY_ID")

    def test_explicit_design_and_maintenance_layers_use_actual_owner_kinds(self):
        for owner, kind, layer in (("ABB-001", "architecture-building-block", "适用的设计验证"),
                                   ("TASK-001", "development-log", "独立维护或文档检查")):
            with self.subTest(owner=owner):
                write_artifact(self.root, id=owner, kind=kind, acceptance_ids=(owner + "-VC-01",))
                target = "sample/CTX-001/" + owner + "#" + owner.lower() + "-vc-01"
                write_metadata(self.root, metadata(id="VT-003", kind="verification-test",
                               targets=[{"target": target, "criterionAnchor": "inspect"}]),
                               f'# VT-003：约束检查\n<a id="plan"></a>\n## 计划\n'
                               f'| 验证层次 | {layer} |\n'
                               + criterion_block("inspect", "实际变化符合来源中明确的边界。",
                                                 "直接逐项比较来源与维护范围。",
                                                 "不执行应用，也不改变无关的所有者文件。"),
                               "verification/VT-003.md")
                self.assertEqual("clean", self.report([*DELIVERY, target]).status)

    def test_cli_real_exits_and_explicit_report_never_overwrite_inputs(self):
        before = source_bytes(self.root)
        clean = self.cli(*self.delivery_args())
        self.assertEqual(0, clean.returncode, clean.stdout + clean.stderr)
        self.assertEqual("clean", json.loads(clean.stdout)["status"])
        self.assertEqual(before, source_bytes(self.root))
        write_delivery_fixture(self.root, True)
        invalid = self.cli(*self.delivery_args())
        self.assertEqual(1, invalid.returncode, invalid.stdout + invalid.stderr)
        bad = self.cli("--delivery", "SR-001")
        self.assertEqual(2, bad.returncode, bad.stdout + bad.stderr)
        usage = self.cli()
        self.assertEqual(2, usage.returncode)
        output = self.workspace / "trace-report.json"
        written = self.cli(*self.delivery_args(), "--report", str(output))
        self.assertEqual(1, written.returncode)
        saved = output.read_bytes()
        conflict = self.cli(*self.delivery_args(), "--report", str(output))
        self.assertEqual(2, conflict.returncode)
        self.assertEqual(saved, output.read_bytes())
        before = source_bytes(self.root)
        source_conflict = self.cli(*self.delivery_args(), "--report",
                                   str(self.root / "software-requirements/SR-001.md"))
        self.assertEqual(2, source_conflict.returncode)
        self.assertEqual(before, source_bytes(self.root))


class ImpactTests(TraceFixture):

    def setUp(self):
        super().setUp()
        seed_git_repo(self.root)
        write_metadata(self.root, metadata(id="TASK-001", kind="development-log",
                       upstream=["sample/CTX-001/SR-001"]),
                       "# TASK-001：维护交付\n\n任务依赖软件要求，未执行应用。\n", "tasks/TASK-001.md")
        git(self.root, "add", "--", ".")
        git(self.root, "commit", "--quiet", "-m", "Independent rule and delivery baseline")
        self.base = git(self.root, "rev-parse", "HEAD")

    def impact(self, base=None, tasks=("sample/CTX-001/TASK-001",)):
        return self.tool().impact_report(self.root, self.base if base is None else base, tasks)

    def change_rule(self):
        self.replace("domain-model/DM-001.md", "Allowance limit: 2", "Allowance limit: 3")

    def test_rule_only_change_reaches_requirements_tests_and_supplied_task(self):
        before = (self.root / "domain-model/DM-001.md").read_bytes()
        self.change_rule()
        sources = source_bytes(self.root)
        report = self.impact()
        self.assertEqual("clean", report["status"])
        self.assertEqual(["sample/CTX-001/" + key for key in ("REQ-001", "SR-001", "TASK-001", "VT-001", "VT-002")],
                         [item["key"] for item in report["candidates"]])
        change = report["changed_sources"][0]
        self.assertEqual("domain-model/DM-001.md", change["path"])
        self.assertEqual(hashlib.sha256(before).hexdigest(), change["before_sha256"])
        self.assertNotEqual(change["before_sha256"], change["after_sha256"])
        req = report["candidates"][0]
        self.assertEqual("sample/CTX-001/DM-001#rule-001", req["reasons"][0]["reference"])
        self.assertEqual("upstream", req["reasons"][0]["relation"])
        self.assertEqual("stakeholder-requirements/REQ-001.md", req["after"]["path"])
        self.assertTrue(all(item["before"] and item["after"] and item["reasons"] for item in report["candidates"]))
        self.assertEqual(report, self.impact())
        self.assertEqual(sources, source_bytes(self.root))

    def test_deleted_source_and_removed_dependency_do_not_erase_old_chain(self):
        (self.root / "domain-model/DM-001.md").unlink()
        self.replace("stakeholder-requirements/REQ-001.md",
                     "upstream:\n- sample/CTX-001/DM-001#rule-001", "upstream: []")
        report = self.impact()
        self.assertIn("sample/CTX-001/TASK-001", [item["key"] for item in report["candidates"]])
        self.assertTrue(any(item["status"] == "deleted" for item in report["changed_sources"]))
        sr = next(item for item in report["candidates"] if item["key"].endswith("/SR-001"))
        self.assertTrue(sr["reasons"])

    def test_cycle_terminates_with_unique_candidates_and_real_reasons(self):
        self.replace("stakeholder-requirements/REQ-001.md",
                     "upstream:\n", "upstream:\n- sample/CTX-001/SR-001\n")
        self.change_rule()
        report = self.impact()
        keys = [item["key"] for item in report["candidates"]]
        self.assertEqual(len(keys), len(set(keys)))
        self.assertIn("sample/CTX-001/VT-002", keys)

    def test_no_changes_is_empty_candidates_not_semantic_approval(self):
        report = self.impact()
        self.assertEqual([], report["candidates"])
        self.assertEqual([], report["changed_sources"])
        self.assertNotIn("approved", report)
        self.assertEqual(self.base, report["baseline"]["base_sha"])

    def test_invalid_exact_base_and_task_selection_fail_explicitly(self):
        for base in ("HEAD", self.base[:8], "0" * 40, git(self.root, "rev-parse", f"{self.base}:README.md")):
            with self.subTest(base=base):
                report = self.impact(base)
                self.assertEqual("input-error", report["status"])
                self.assertIn(report["findings"][0]["code"], ("INVALID_BASE", "BASE_UNAVAILABLE"))
        for tasks in (["TASK-001"], ["sample/CTX-001/TASK-999"], ["sample/CTX-001/TASK-001"] * 2):
            with self.subTest(tasks=tasks):
                self.assertEqual("input-error", self.impact(tasks=tasks)["status"])

    def test_impact_cli_reads_exact_git_and_does_not_write_sources(self):
        self.change_rule()
        before = source_bytes(self.root)
        result = self.cli("--base", self.base, "--task", "sample/CTX-001/TASK-001")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertEqual(5, len(json.loads(result.stdout)["candidates"]))
        self.assertEqual(before, source_bytes(self.root))
        bad = self.cli("--base", "HEAD")
        self.assertEqual(2, bad.returncode)

    def test_fix1_i5_public_api_rejects_none_without_fixture_base_fallback(self):
        self.change_rule()
        before = source_bytes(self.root)
        # Call the production boundary directly: self.impact(None) substitutes self.base.
        report = self.tool().impact_report(self.root, None, ["sample/CTX-001/TASK-001"])
        self.assertEqual("input-error", report["status"])
        self.assertIn("INVALID_BASE", [finding["code"] for finding in report["findings"]])
        self.assertIsNone(report["baseline"])
        self.assertEqual([], report["candidates"])
        self.assertEqual(before, source_bytes(self.root))


class CriterionIsolationTests(TraceFixture):
    def test_fix1_i4_next_criterion_cannot_fill_an_empty_previous_criterion(self):
        path = self.root / "verification/VT-002.md"
        text = path.read_text(encoding="utf-8")
        start, end = text.index('<a id="record">'), text.index('<a id="no-write">')
        path.write_text(text[:start] + '<a id="record"></a>\n### 独立判据\n\n' + text[end:], encoding="utf-8")
        report = self.report()
        self.assertEqual("invalid", report.status)
        self.assertEqual([DELIVERY[2]], [f.target for f in report.findings if f.code == "UNCOVERED_ACCEPTANCE"])
        self.finding(report, "INSUFFICIENT_CRITERION")


if __name__ == "__main__":
    unittest.main()
