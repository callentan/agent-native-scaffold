"""Task18 / ENH-18: explicit local records and read-only usage summaries."""

from __future__ import annotations

import csv
import hashlib
import importlib
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch


WORKTREE = Path(__file__).resolve().parents[3]
UTILITIES = WORKTREE / ".github" / "utilities"
FIXTURES = WORKTREE / ".venv" / "task18-fixtures"
HEADER = (
    "schema_version,record_id,recorded_at,tool_name,tool_version,task_ref,"
    "object_ref,object_baseline,operation_summary,decision_ref,usage_value,"
    "usage_unit,usage_currency,evidence_ref\r\n"
).encode("ascii")
OWNER_ROW = (
    "1,owner-row,2026-10-18T00:00:00Z,manual,1,task-owner,doc-owner,"
    "sha256:owner,independent owner append,,,,,\r\n"
).encode("ascii")


def independent_row_bytes(raw: bytes) -> list[list[str]]:
    """Parse fixture bytes independently of either production module."""
    return list(csv.reader(io.StringIO(raw.decode("utf-8"), newline=""), strict=True))


class InteractionLogTests(unittest.TestCase):
    def setUp(self):
        FIXTURES.mkdir(parents=True, exist_ok=True)
        temporary = tempfile.TemporaryDirectory(prefix="task18-", dir=FIXTURES)
        self.addCleanup(temporary.cleanup)
        self.workspace = Path(temporary.name)
        self.root = self.workspace / "路径 with spaces"
        self.root.mkdir()
        self.log = self.root / "interaction log.csv"
        self.log.write_bytes(HEADER)

    def module(self, name: str):
        self.assertIsNotNone(
            importlib.util.find_spec(name),
            f"Task18 {name} is not implemented",
        )
        return importlib.import_module(name)

    def record(self, record_id: str = "R-001", **changes):
        module = self.module("log_interaction")
        values = {
            "record_id": record_id,
            "recorded_at": "2026-10-18T12:34:56.123456+08:00",
            "tool_name": "copilot-app",
            "tool_version": "1.2.3",
            "task_ref": "TASK18",
            "object_ref": "docs/design/ddd-functional-alignment.md#enh-18",
            "object_baseline": "sha256:ab12",
            "operation_summary": "Added an explicit record",
            "decision_ref": "governance.md#decisions",
            "usage_value": "1.2300",
            "usage_unit": "input_tokens",
            "usage_currency": None,
            "evidence_ref": "reports/receipt.txt#record-1",
        }
        values.update(changes)
        return module.InteractionRecord(**values)

    def append(self, record=None, *, log=None):
        return self.module("log_interaction").append_record(
            self.log if log is None else log,
            self.record() if record is None else record,
        )

    def cli(self, script: str, *arguments: str, cwd: Path | None = None):
        path = UTILITIES / f"{script}.py"
        self.assertTrue(path.is_file(), f"Task18 {script} CLI is not implemented")
        return subprocess.run(
            [sys.executable, "-B", "-X", "utf8", str(path), *map(str, arguments)],
            cwd=self.workspace if cwd is None else cwd,
            shell=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=20,
        )

    def append_cli(self, record_id: str, **changes):
        values = {
            "recorded_at": "2026-10-18T12:34:56+08:00",
            "tool_name": "copilot-cli",
            "tool_version": "5.6",
            "task_ref": "TASK18",
            "object_ref": "README.md",
            "object_baseline": "sha256:cli",
            "operation_summary": "A CLI-supplied summary",
        }
        values.update(changes)
        args = [
            "--log", str(self.log),
            "--record-id", record_id,
            "--time", values["recorded_at"],
            "--tool", values["tool_name"],
            "--tool-version", values["tool_version"],
            "--task-ref", values["task_ref"],
            "--object-ref", values["object_ref"],
            "--object-baseline", values["object_baseline"],
            "--summary", values["operation_summary"],
        ]
        for key, option in (
            ("decision_ref", "--decision-ref"),
            ("usage_value", "--usage-value"),
            ("usage_unit", "--usage-unit"),
            ("usage_currency", "--usage-currency"),
            ("evidence_ref", "--evidence-ref"),
        ):
            if values.get(key) is not None:
                args.extend((option, values[key]))
        return self.cli("log_interaction", *args)

    def test_LEDGER_01_appends_explicit_record_without_rewriting_prior_bytes(self):
        previous = (
            HEADER
            + b"1,prior,2026-10-18T11:00:00Z,manual,1,task-0,doc-0,"
            b"sha256:prior,existing owner row,,,,,\r\n"
        )
        self.log.write_bytes(previous)
        supplied = self.record(
            operation_summary="literal ; not a command",
            usage_value="12.3400",
            usage_unit="output_tokens",
            evidence_ref="owned report.txt#case-1",
        )

        result = self.append(supplied)
        actual = self.log.read_bytes()
        rows = independent_row_bytes(actual)

        self.assertEqual("appended", result.status)
        self.assertTrue(actual.startswith(previous))
        self.assertEqual(
            [
                HEADER.decode("ascii").rstrip("\r\n").split(","),
                ["1", "prior", "2026-10-18T11:00:00Z", "manual", "1",
                 "task-0", "doc-0", "sha256:prior", "existing owner row",
                 "", "", "", "", ""],
                ["1", "R-001", "2026-10-18T12:34:56.123456+08:00",
                 "copilot-app", "1.2.3", "TASK18",
                 "docs/design/ddd-functional-alignment.md#enh-18", "sha256:ab12",
                 "literal ; not a command", "governance.md#decisions", "12.3400",
                 "output_tokens", "", "owned report.txt#case-1"],
            ],
            rows,
        )
        self.assertFalse((self.root / "not-a-command").exists())

    def test_LEDGER_02_identical_record_replay_is_idempotent(self):
        supplied = self.record()
        first = self.append(supplied)
        before_replay = self.log.read_bytes()

        replay = self.append(supplied)

        self.assertEqual("appended", first.status)
        self.assertEqual("duplicate", replay.status)
        self.assertEqual(before_replay, self.log.read_bytes())
        self.assertEqual(2, len(independent_row_bytes(self.log.read_bytes())))

    def test_LEDGER_03_conflicting_record_id_fails_and_preserves_original_bytes(self):
        self.append(self.record())
        previous = self.log.read_bytes()

        error_type = self.module("log_interaction").LedgerError
        with self.assertRaises(error_type) as caught:
            self.append(self.record(operation_summary="different owner value"))

        self.assertEqual("RECORD_ID_CONFLICT", caught.exception.code)
        self.assertEqual(previous, self.log.read_bytes())

    def test_LEDGER_04_invalid_time_quantity_or_unit_shape_never_appends(self):
        module = self.module("log_interaction")
        error_type = module.LedgerError
        invalid = (
            ({"recorded_at": "2026-02-30T12:00:00Z"}, "INVALID_TIMESTAMP"),
            ({"usage_value": "-0.1"}, "INVALID_USAGE"),
            ({"usage_value": "NaN"}, "INVALID_USAGE"),
            ({"usage_value": "3", "usage_unit": None}, "INVALID_USAGE"),
            ({"usage_value": None, "usage_unit": "tokens"}, "INVALID_USAGE"),
        )
        for changes, code in invalid:
            with self.subTest(changes=changes):
                before = self.log.read_bytes()
                with self.assertRaises(error_type) as caught:
                    self.append(self.record(record_id=f"bad-{len(changes)}-{code}",
                                            **changes))
                self.assertEqual(code, caught.exception.code)
                self.assertEqual(before, self.log.read_bytes())

        valid_zero = self.record(record_id="known-zero", usage_value="0")
        self.assertEqual("appended", self.append(valid_zero).status)

    def test_LEDGER_05_unsupplied_usage_stays_unknown_not_zero_or_model_estimate(self):
        record = self.record(
            record_id="unknown-usage",
            tool_name="named-model-DO-NOT-PRICE",
            usage_value=None,
            usage_unit=None,
            usage_currency=None,
        )
        self.append(record)

        summary = self.module("summarize_usage").summarize_usage(self.log)

        self.assertEqual(1, summary["usage"]["unknown_record_count"])
        self.assertEqual(0, summary["usage"]["known_record_count"])
        self.assertEqual([], summary["usage"]["known_groups"])
        self.assertEqual(
            [{"tool_name": "named-model-DO-NOT-PRICE", "tool_version": "1.2.3",
              "record_count": 1, "record_ids": ["unknown-usage"]}],
            summary["usage"]["unknown_groups"],
        )
        self.assertNotIn("cost", json.dumps(summary).lower())

    def test_LEDGER_06_totals_keep_units_currencies_tools_versions_separate(self):
        entries = (
            self.record(record_id="a", tool_name="tool-A", tool_version="v1",
                        usage_value="0.10", usage_unit="credits",
                        usage_currency=None),
            self.record(record_id="b", tool_name="tool-A", tool_version="v1",
                        usage_value="0.20", usage_unit="credits",
                        usage_currency=None),
            self.record(record_id="c", tool_name="tool-A", tool_version="v2",
                        usage_value="1.00", usage_unit="currency",
                        usage_currency="USD"),
            self.record(record_id="d", tool_name="tool-B", tool_version="v1",
                        usage_value="2.00", usage_unit="currency",
                        usage_currency="EUR"),
            self.record(record_id="e", tool_name="tool-B", tool_version="v1",
                        usage_value="500", usage_unit="output_tokens",
                        usage_currency=None),
        )
        for entry in entries:
            self.append(entry)

        summary = self.module("summarize_usage").summarize_usage(self.log)

        self.assertEqual(5, summary["record_count"])
        self.assertEqual(5, summary["usage"]["known_record_count"])
        self.assertEqual(0, summary["usage"]["unknown_record_count"])
        self.assertEqual(
            [
                {"tool_name": "tool-A", "tool_version": "v1",
                 "unit": "credits", "currency": None, "record_count": 2,
                 "total_value": "0.30", "record_ids": ["a", "b"]},
                {"tool_name": "tool-A", "tool_version": "v2",
                 "unit": "currency", "currency": "USD", "record_count": 1,
                 "total_value": "1.00", "record_ids": ["c"]},
                {"tool_name": "tool-B", "tool_version": "v1",
                 "unit": "currency", "currency": "EUR", "record_count": 1,
                 "total_value": "2.00", "record_ids": ["d"]},
                {"tool_name": "tool-B", "tool_version": "v1",
                 "unit": "output_tokens", "currency": None, "record_count": 1,
                 "total_value": "500", "record_ids": ["e"]},
            ],
            summary["usage"]["known_groups"],
        )
        self.assertEqual(
            summary,
            self.module("summarize_usage").summarize_usage(self.log),
        )

    def test_LEDGER_07_missing_decision_and_evidence_remain_unknown_not_approval(self):
        record = self.record(
            record_id="no-evidence",
            decision_ref=None,
            evidence_ref=None,
            usage_value=None,
            usage_unit=None,
        )
        self.append(record)
        unverified_claim = self.record(
            record_id="unverified-approval-claim",
            decision_ref="Approved",
            evidence_ref=None,
            usage_value=None,
            usage_unit=None,
        )
        self.append(unverified_claim)
        row = independent_row_bytes(self.log.read_bytes())[1]
        summary = self.module("summarize_usage").summarize_usage(self.log)

        self.assertEqual("", row[9])
        self.assertEqual("", row[13])
        self.assertEqual("Approved",
                         independent_row_bytes(self.log.read_bytes())[2][9])
        self.assertEqual(1, summary["unknown_decision_reference_count"])
        self.assertEqual(2, summary["unknown_evidence_reference_count"])
        self.assertNotIn("approved", json.dumps(summary).lower())
        self.assertNotIn("qualified", json.dumps(summary).lower())

    def test_LEDGER_08_csv_escapes_unicode_quotes_commas_and_newlines_as_data(self):
        summary_text = '行一, "quoted"\n行二; =HYPERLINK("https://invalid","data")'
        record = self.record(
            record_id="unicode-1",
            tool_name="工具, α",
            operation_summary=summary_text,
            decision_ref='决策 "原文", 第1行\n第二行',
            evidence_ref="证据, '引用'\n补充",
        )

        self.append(record)
        rows = independent_row_bytes(self.log.read_bytes())

        self.assertEqual(2, len(rows))
        self.assertEqual("工具, α", rows[1][3])
        self.assertEqual(summary_text, rows[1][8])
        self.assertEqual('决策 "原文", 第1行\n第二行', rows[1][9])
        self.assertEqual("证据, '引用'\n补充", rows[1][13])
        self.assertFalse((self.root / "data").exists())

    def test_LEDGER_09_malformed_duplicate_or_incompatible_history_is_never_rebuilt(self):
        module = self.module("log_interaction")
        error_type = module.LedgerError
        malformed_sources = (
            HEADER + b'"unfinished,quoted field\r\n',
            HEADER + OWNER_ROW + OWNER_ROW,
            HEADER.replace(b"schema_version", b"schema_version")
            + b"2,wrong-version,2026-10-18T00:00:00Z,tool,1,task,doc,base,summary,,,,,\r\n",
        )
        codes = ("INVALID_LOG", "DUPLICATE_LOG_ID", "INCOMPATIBLE_LOG_VERSION")
        for source, expected_code in zip(malformed_sources, codes):
            with self.subTest(expected_code=expected_code):
                self.log.write_bytes(source)
                before = self.log.read_bytes()
                with self.assertRaises(error_type) as caught:
                    self.append(self.record(record_id="new"))
                self.assertEqual(expected_code, caught.exception.code)
                self.assertEqual(before, self.log.read_bytes())

        wrong_header = b"schema_version,record_id\r\n"
        self.log.write_bytes(wrong_header)
        with self.assertRaises(error_type) as caught:
            self.append(self.record(record_id="new-header"))
        self.assertEqual("INCOMPATIBLE_LOG_HEADER", caught.exception.code)
        self.assertEqual(wrong_header, self.log.read_bytes())

    def test_LEDGER_10_native_process_lock_serializes_two_writers_without_lost_rows(self):
        module = self.module("log_interaction")
        processes = []
        with module._file_lock(self.log, timeout=5):
            processes = [
                subprocess.Popen(
                    [
                        sys.executable, "-B", "-X", "utf8",
                        str(UTILITIES / "log_interaction.py"),
                        "--log", str(self.log),
                        "--record-id", record_id,
                        "--time", "2026-10-18T12:00:00Z",
                        "--tool", "process-test",
                        "--tool-version", "1",
                        "--task-ref", "TASK18",
                        "--object-ref", "native-lock-test",
                        "--object-baseline", "sha256:lock",
                        "--summary", "concurrent append",
                        "--lock-timeout", "5",
                    ],
                    cwd=self.workspace,
                    shell=False,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    encoding="utf-8",
                )
                for record_id in ("proc-A", "proc-B")
            ]
            time.sleep(0.25)
            self.assertTrue(all(process.poll() is None for process in processes),
                            "Subprocesses must wait while the parent owns the native lock")
        outputs = [process.communicate(timeout=10) for process in processes]
        self.assertEqual([0, 0], [process.returncode for process in processes], outputs)
        rows = independent_row_bytes(self.log.read_bytes())
        self.assertEqual(["proc-A", "proc-B"], sorted(row[1] for row in rows[1:]))
        self.assertEqual(3, len(rows))

    def test_LEDGER_10_owner_byte_change_between_snapshot_and_write_is_detected(self):
        module = self.module("log_interaction")
        original_reader = module._read_log_bytes
        calls = 0

        def changed_owner_after_snapshot(path):
            nonlocal calls
            result = original_reader(path)
            calls += 1
            if calls == 1:
                with path.open("ab") as owner:
                    owner.write(OWNER_ROW)
            return result

        before = self.log.read_bytes()
        with patch.object(module, "_read_log_bytes", side_effect=changed_owner_after_snapshot):
            with self.assertRaises(module.LedgerError) as caught:
                self.append(self.record(record_id="must-not-append"))

        self.assertEqual("OWNER_BYTES_CHANGED", caught.exception.code)
        self.assertEqual(before + OWNER_ROW, self.log.read_bytes())
        self.assertEqual(["record_id", "owner-row"],
                         [row[1] for row in independent_row_bytes(self.log.read_bytes())])

    def test_LEDGER_10_partial_append_failure_is_reported_and_never_auto_repaired(self):
        module = self.module("log_interaction")
        before = self.log.read_bytes()
        actual_write = module.os.write
        calls = 0

        def fail_after_owned_prefix(descriptor, content):
            nonlocal calls
            calls += 1
            if calls == 1:
                return actual_write(descriptor, content[:8])
            raise OSError("controlled partial-write boundary")

        with patch.object(module.os, "write", side_effect=fail_after_owned_prefix):
            with self.assertRaises(module.LedgerError) as caught:
                self.append(self.record(record_id="partial-row"))

        self.assertEqual("APPEND_IO_RECOVERY_REQUIRED", caught.exception.code)
        self.assertTrue(caught.exception.recovery_required)
        self.assertEqual(8, caught.exception.recovery["observed_delta_bytes"])
        self.assertEqual(before + b"1,partia", self.log.read_bytes())
        damaged = self.log.read_bytes()
        with self.assertRaises(module.LedgerError) as retry:
            self.append(self.record(record_id="later-row"))
        self.assertEqual("INVALID_LOG_ROW", retry.exception.code)
        self.assertEqual(damaged, self.log.read_bytes())

    def test_LEDGER_11_summary_cli_is_read_only_stable_and_has_documented_exit_codes(self):
        initial = self.append_cli(
            "cli-known", usage_value="2.500", usage_unit="requests")
        self.assertEqual(0, initial.returncode, initial.stderr)
        before = self.log.read_bytes()
        source_hash = hashlib.sha256(before).hexdigest()

        first = self.cli("summarize_usage", "--log", str(self.log))
        second = self.cli("summarize_usage", "--log", str(self.log))
        self.assertEqual((0, 0), (first.returncode, second.returncode),
                         (first.stderr, second.stderr))
        self.assertEqual(first.stdout, second.stdout)
        parsed = json.loads(first.stdout)
        self.assertEqual(source_hash, parsed["source_sha256"])
        self.assertEqual(1, parsed["usage"]["known_record_count"])
        self.assertEqual(before, self.log.read_bytes())

        duplicate = self.append_cli(
            "cli-known", usage_value="2.500", usage_unit="requests")
        self.assertEqual(0, duplicate.returncode, duplicate.stderr)
        conflict = self.append_cli(
            "cli-known", usage_value="9", usage_unit="requests")
        self.assertEqual(1, conflict.returncode, conflict.stdout)
        self.assertEqual(before, self.log.read_bytes())
        invalid = self.append_cli(
            "cli-invalid", usage_value="-1", usage_unit="tokens")
        self.assertEqual(1, invalid.returncode, invalid.stdout)
        self.assertEqual(before, self.log.read_bytes())

    def test_LEDGER_12_explicit_new_output_paths_and_spaces_preserve_owner_files(self):
        self.append(self.record(record_id="path-test", usage_value="7",
                                usage_unit="requests"))
        before = self.log.read_bytes()
        output = self.root / "new summary with spaces.json"

        created = self.cli("summarize_usage", "--log", str(self.log),
                           "--output", str(output))

        self.assertEqual(0, created.returncode, created.stderr)
        self.assertEqual("7", json.loads(output.read_text(encoding="utf-8"))
                         ["usage"]["known_groups"][0]["total_value"])
        self.assertEqual(before, self.log.read_bytes())
        output_before = output.read_bytes()
        existing = self.cli("summarize_usage", "--log", str(self.log),
                            "--output", str(output))
        self.assertEqual(2, existing.returncode)
        self.assertEqual(output_before, output.read_bytes())

        same_source = self.cli("summarize_usage", "--log", str(self.log),
                               "--output", str(self.log))
        self.assertEqual(2, same_source.returncode)
        self.assertEqual(before, self.log.read_bytes())
        missing_parent = self.root / "missing-parent" / "never.json"
        missing = self.cli("summarize_usage", "--log", str(self.log),
                           "--output", str(missing_parent))
        self.assertEqual(2, missing.returncode)
        self.assertFalse(missing_parent.parent.exists())

    def test_LEDGER_12_partial_summary_output_is_retained_and_requires_manual_recovery(self):
        self.append(self.record(record_id="partial-summary", usage_value="1",
                                usage_unit="requests"))
        before = self.log.read_bytes()
        output = self.root / "partial summary.json"
        summary_module = self.module("summarize_usage")
        actual_write = summary_module.os.write
        calls = 0

        def fail_after_output_prefix(descriptor, content):
            nonlocal calls
            calls += 1
            if calls == 1:
                return actual_write(descriptor, content[:12])
            raise OSError("controlled summary-write boundary")

        with patch.object(summary_module.os, "write", side_effect=fail_after_output_prefix):
            with self.assertRaises(summary_module.LedgerError) as caught:
                summary_module._write_summary(self.log, output)

        self.assertEqual("SUMMARY_OUTPUT_RECOVERY_REQUIRED", caught.exception.code)
        self.assertTrue(caught.exception.recovery_required)
        self.assertEqual(12, caught.exception.recovery["observed_bytes"])
        partial = output.read_bytes()
        self.assertEqual(12, len(partial))
        self.assertEqual(before, self.log.read_bytes())
        retry = self.cli("summarize_usage", "--log", str(self.log),
                         "--output", str(output))
        self.assertEqual(2, retry.returncode)
        self.assertEqual(partial, output.read_bytes())

    def test_LEDGER_12_blank_template_is_never_treated_as_a_live_ledger(self):
        template = WORKTREE / "_templates" / "reports" / "ai-interaction-log.csv"
        before = template.read_bytes()
        self.assertEqual(
            ["schema_version", "record_id", "recorded_at", "tool_name",
             "tool_version", "task_ref", "object_ref", "object_baseline",
             "operation_summary", "decision_ref", "usage_value", "usage_unit",
             "usage_currency", "evidence_ref"],
            independent_row_bytes(before)[0],
        )

        with self.assertRaises(self.module("log_interaction").LedgerError) as caught:
            self.append(self.record(record_id="must-use-copy"), log=template)

        self.assertEqual("TEMPLATE_NOT_LEDGER", caught.exception.code)
        self.assertEqual(before, template.read_bytes())

    def test_LEDGER_12_native_directory_symlink_escape_is_rejected(self):
        outside = self.workspace / "outside-owner"
        outside.mkdir()
        output_target = outside / "escaped-summary.json"
        junction = self.root / "escape-to-owner"
        if os.name == "nt":
            executable = shutil.which("powershell.exe")
            self.assertIsNotNone(executable, "Windows PowerShell is needed for a local junction fixture")
            environment = os.environ.copy()
            environment["TASK18_JUNCTION"] = str(junction)
            environment["TASK18_TARGET"] = str(outside)
            made = subprocess.run(
                [
                    executable, "-NoLogo", "-NoProfile", "-NonInteractive",
                    "-Command",
                    "$ErrorActionPreference='Stop'; "
                    "New-Item -ItemType Junction -Path $env:TASK18_JUNCTION "
                    "-Target $env:TASK18_TARGET | Out-Null",
                ],
                cwd=self.workspace,
                env=environment,
                shell=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=10,
            )
            self.assertEqual(0, made.returncode, made.stderr)
        else:
            junction.symlink_to(outside, target_is_directory=True)
        self.addCleanup(lambda: junction.rmdir() if junction.exists() else None)

        result = self.cli(
            "summarize_usage", "--log", str(self.log),
            "--output", str(junction / "escaped-summary.json"),
        )

        self.assertEqual(2, result.returncode, result.stdout)
        self.assertFalse(output_target.exists())
        self.assertEqual(HEADER, self.log.read_bytes())


if __name__ == "__main__":
    unittest.main()
