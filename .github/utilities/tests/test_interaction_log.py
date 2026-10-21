"""Task18 / ENH-18: explicit local records and read-only usage summaries."""

from __future__ import annotations

import csv
from contextlib import redirect_stderr
import errno
import hashlib
import importlib
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch


WORKTREE = Path(__file__).resolve().parents[3]
UTILITIES = WORKTREE / ".github" / "utilities"
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


def directory_inventory(
    root: Path, *, excluded_paths: frozenset[str] = frozenset(),
) -> tuple[tuple[str, str], ...]:
    entries = []
    for path in sorted(root.rglob("*"), key=lambda item: item.relative_to(root).as_posix()):
        relative = path.relative_to(root).as_posix()
        if relative in excluded_paths:
            continue
        if path.is_file():
            entries.append((relative, "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()))
        elif path.is_dir():
            entries.append((relative, "directory"))
    return tuple(entries)


class InteractionLogTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="task18-")
        self.addCleanup(temporary.cleanup)
        self.caller_workspace = Path(temporary.name)
        self.workspace = Path(temporary.name).resolve()
        self.root = self.workspace / "путь € with spaces"
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

    def append(self, record=None, *, log=None, attest_local_storage=True):
        return self.module("log_interaction").append_record(
            self.log if log is None else log,
            self.record() if record is None else record,
            attest_local_storage=attest_local_storage,
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

    def append_cli(self, record_id: str, *, attest_local_storage=True,
                   lock_timeout=10.0, **changes):
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
            "--lock-timeout", str(lock_timeout),
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
        if attest_local_storage:
            args.append("--attest-local-storage")
        return self.cli("log_interaction", *args)

    def test_FIX1_01_default_summary_api_and_cli_do_not_create_or_change_files(self):
        cli_log = self.root / "cli-only.csv"
        cli_log.write_bytes(HEADER)
        before = directory_inventory(self.root)
        self.assertEqual(
            (("cli-only.csv", "sha256:" + hashlib.sha256(HEADER).hexdigest()),
             ("interaction log.csv", "sha256:" + hashlib.sha256(HEADER).hexdigest())),
            before,
        )

        api_result = self.module("summarize_usage").summarize_usage(self.log)
        after_api = directory_inventory(self.root)
        cli_result = self.cli("summarize_usage", "--log", str(cli_log))
        after_cli = directory_inventory(self.root)

        self.assertEqual(0, cli_result.returncode, cli_result.stderr)
        self.assertEqual(api_result, json.loads(cli_result.stdout))
        self.assertEqual(before, after_api)
        self.assertEqual(before, after_cli)

    def test_FIX1_03_default_summary_reports_partial_owner_row_without_lock(self):
        ledger = self.module("log_interaction")
        with self.log.open("ab") as owner:
            owner.write(b"1,partia")

        with self.assertRaises(ledger.LedgerError) as caught:
            self.module("summarize_usage").summarize_usage(self.log)

        self.assertEqual("INVALID_LOG_ROW", caught.exception.code)
        self.assertEqual(HEADER + b"1,partia", self.log.read_bytes())
        self.assertEqual((("interaction log.csv", "sha256:" + hashlib.sha256(
            HEADER + b"1,partia").hexdigest()),), directory_inventory(self.root))
        self.assertFalse(self.log.with_name(self.log.name + ".lock").exists())

    def test_FIX1_04_append_api_requires_attestation_before_mutation(self):
        ledger = self.module("log_interaction")
        before = directory_inventory(self.root)

        with self.assertRaises(ledger.LedgerError) as caught:
            ledger.append_record(self.log, self.record(record_id="missing-api-attestation"))

        self.assertEqual("WRITE_ATTESTATION_REQUIRED", caught.exception.code)
        self.assertEqual(before, directory_inventory(self.root))
        self.assertEqual(HEADER, self.log.read_bytes())

    def test_FIX1_05_append_cli_requires_attestation_before_mutation(self):
        before = directory_inventory(self.root)

        result = self.append_cli("missing-cli-attestation", attest_local_storage=False)

        self.assertEqual(2, result.returncode)
        self.assertEqual("WRITE_ATTESTATION_REQUIRED", json.loads(result.stderr)["code"])
        self.assertEqual(before, directory_inventory(self.root))
        self.assertEqual(HEADER, self.log.read_bytes())

    def test_FIX1_06_summary_output_cli_requires_attestation_before_mutation(self):
        output = self.root / "unattested summary.json"
        before = directory_inventory(self.root)

        with self.assertRaises(self.module("summarize_usage").LedgerError) as api_error:
            self.module("summarize_usage").write_summary(self.log, output)
        self.assertEqual("WRITE_ATTESTATION_REQUIRED", api_error.exception.code)
        self.assertEqual(before, directory_inventory(self.root))

        result = self.cli("summarize_usage", "--log", str(self.log),
                          "--output", str(output))

        self.assertEqual(2, result.returncode)
        self.assertEqual("WRITE_ATTESTATION_REQUIRED", json.loads(result.stderr)["code"])
        self.assertEqual(before, directory_inventory(self.root))
        self.assertFalse(output.exists())
        self.assertFalse(self.log.with_name(self.log.name + ".lock").exists())

    def test_FIX1_07_explicit_attestation_flag_enables_append_and_summary_output(self):
        output = self.root / "attested summary.json"
        append_args = [
            "--log", str(self.log),
            "--record-id", "attested-cli",
            "--time", "2026-10-18T12:34:56Z",
            "--tool", "caller-tool",
            "--tool-version", "1",
            "--task-ref", "TASK18",
            "--object-ref", "README.md",
            "--object-baseline", "sha256:attested",
            "--summary", "explicit attestation fixture",
            "--attest-local-storage",
        ]
        appended = self.cli("log_interaction", *append_args)
        self.assertEqual(0, appended.returncode, appended.stderr)
        self.assertEqual(
            ["record_id", "attested-cli"],
            [row[1] for row in independent_row_bytes(self.log.read_bytes())],
        )

        summary = self.cli("summarize_usage", "--log", str(self.log),
                           "--output", str(output), "--attest-local-storage")
        self.assertEqual(0, summary.returncode, summary.stderr)
        self.assertEqual(json.loads(summary.stdout),
                         json.loads(output.read_text(encoding="utf-8")))
        self.assertEqual(hashlib.sha256(self.log.read_bytes()).hexdigest(),
                         json.loads(summary.stdout)["source_sha256"])

    def test_FIX1_08_output_created_by_owner_at_create_boundary_is_not_overwritten(self):
        output = self.root / "owner-wins.json"
        ledger = self.module("log_interaction")
        original_open = os.open
        collided = False

        def owner_creates_before_exclusive_open(path, flags, *args, **kwargs):
            nonlocal collided
            if Path(path) == output and flags & os.O_EXCL:
                output.write_bytes(b"owner file")
                collided = True
            return original_open(path, flags, *args, **kwargs)

        with patch.object(os, "open", side_effect=owner_creates_before_exclusive_open):
            with self.assertRaises(ledger.LedgerError) as caught:
                self.module("summarize_usage").write_summary(
                    self.log, output, attest_local_storage=True)

        self.assertTrue(collided)
        self.assertEqual("OUTPUT_EXISTS", caught.exception.code)
        self.assertFalse(caught.exception.recovery_required)
        self.assertEqual(b"owner file", output.read_bytes())
        self.assertEqual(HEADER, self.log.read_bytes())

    def test_FIX1_11_append_and_summary_accept_normalized_parent_paths(self):
        parent = self.root / "already-existing"
        parent.mkdir()
        # No platform-specific root spelling or fixed drive is required.
        aliased_log = parent / ".." / self.log.name
        result = self.append(self.record(record_id="normalized-parent"), log=aliased_log)
        self.assertEqual("appended", result.status)
        output = parent / ".." / "summary.json"
        summary = self.module("summarize_usage").write_summary(
            aliased_log, output, attest_local_storage=True)
        self.assertEqual(1, summary["record_count"])
        self.assertEqual(summary, json.loads(output.read_text(encoding="utf-8")))
        self.assertEqual(["record_id", "normalized-parent"],
                         [row[1] for row in independent_row_bytes(self.log.read_bytes())])

    def test_PORTABLE_01_caller_system_temp_alias_is_usable_without_drive_detection(self):
        log = self.caller_workspace / self.root.name / self.log.name
        self.assertEqual("appended", self.append(log=log).status)
        output = self.caller_workspace / self.root.name / "temporary summary.json"
        result = self.cli("summarize_usage", "--log", str(log),
                          "--output", str(output), "--attest-local-storage")
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual(1, json.loads(output.read_text(encoding="utf-8"))["record_count"])
        self.assertEqual(hashlib.sha256(self.log.read_bytes()).hexdigest(),
                         json.loads(result.stdout)["source_sha256"])

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
        summary_text = 'строка один €, "quoted"\nстрока два; =HYPERLINK("https://invalid","data")'
        record = self.record(
            record_id="unicode-1",
            tool_name="инструмент €, α",
            operation_summary=summary_text,
            decision_ref='решение "оригинал", строка 1 €\nстрока 2',
            evidence_ref="данные €, 'цитата'\nдополнение",
        )

        self.append(record)
        rows = independent_row_bytes(self.log.read_bytes())

        self.assertEqual(2, len(rows))
        self.assertEqual("инструмент €, α", rows[1][3])
        self.assertEqual(summary_text, rows[1][8])
        self.assertEqual('решение "оригинал", строка 1 €\nстрока 2', rows[1][9])
        self.assertEqual("данные €, 'цитата'\nдополнение", rows[1][13])
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
        with module.file_lock(self.log, timeout=5):
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
                        "--attest-local-storage",
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

    def test_PORTABLE_02_real_process_timeout_and_unlocked_summary(self):
        module = self.module("log_interaction")
        with module.file_lock(self.log, timeout=1):
            result = self.append_cli("blocked-process", lock_timeout=0.1)
            self.assertEqual(2, result.returncode, result.stdout)
            self.assertEqual("LOCK_TIMEOUT", json.loads(result.stderr)["code"])
            lock_path = self.log.with_name(self.log.name + ".lock")
            lock_relative = lock_path.relative_to(self.root).as_posix()
            self.assertTrue(lock_path.is_file())
            before = directory_inventory(self.root, excluded_paths=frozenset({lock_relative}))
            readonly = self.cli("summarize_usage", "--log", str(self.log),
                                "--lock-timeout", "0")
            self.assertEqual(0, readonly.returncode, readonly.stderr)
            self.assertEqual(0, json.loads(readonly.stdout)["record_count"])
            self.assertEqual(HEADER, self.log.read_bytes())
            self.assertEqual(
                before,
                directory_inventory(self.root, excluded_paths=frozenset({lock_relative})),
            )
        self.assertEqual(HEADER, self.log.read_bytes())
        self.assertEqual(b"", lock_path.read_bytes())
        self.assertEqual(0, self.append_cli("after-timeout", lock_timeout=1).returncode)

    def test_PORTABLE_03_invalid_timeout_and_nonempty_lock_preserve_owner_bytes(self):
        module = self.module("log_interaction")
        before = directory_inventory(self.root)
        for timeout in (-1, float("nan"), float("inf"), "1"):
            with self.subTest(timeout=timeout):
                with self.assertRaises(module.LedgerError) as caught:
                    module.append_record(self.log, self.record(),
                                         attest_local_storage=True, lock_timeout=timeout)
                self.assertEqual("INVALID_LOCK_TIMEOUT", caught.exception.code)
                self.assertEqual(before, directory_inventory(self.root))
        lock = self.log.with_name(self.log.name + ".lock")
        lock.write_bytes(b"owner data")
        result = self.append_cli("nonempty-lock")
        self.assertEqual(2, result.returncode)
        self.assertEqual("INVALID_LOCK_FILE", json.loads(result.stderr)["code"])
        self.assertEqual(b"owner data", lock.read_bytes())
        self.assertEqual(HEADER, self.log.read_bytes())

    def test_PORTABLE_04_lock_primitive_failure_is_explicit_and_can_be_retried(self):
        module = self.module("log_interaction")
        with patch.object(module, "_lock_descriptor",
                          side_effect=OSError(errno.ENOSYS, "controlled locking failure")):
            with self.assertRaises(module.LedgerError) as caught:
                self.append()
        self.assertEqual("LOCK_UNAVAILABLE", caught.exception.code)
        self.assertEqual(HEADER, self.log.read_bytes())
        self.assertEqual("appended", self.append().status)

    def test_LEDGER_10_owner_byte_change_after_locked_read_is_detected_before_write(self):
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
                           "--output", str(output), "--attest-local-storage")

        self.assertEqual(0, created.returncode, created.stderr)
        self.assertEqual("7", json.loads(output.read_text(encoding="utf-8"))
                         ["usage"]["known_groups"][0]["total_value"])
        self.assertEqual(before, self.log.read_bytes())
        output_before = output.read_bytes()
        existing = self.cli("summarize_usage", "--log", str(self.log),
                            "--output", str(output), "--attest-local-storage")
        self.assertEqual(2, existing.returncode)
        self.assertEqual(output_before, output.read_bytes())

        same_source = self.cli("summarize_usage", "--log", str(self.log),
                               "--output", str(self.log), "--attest-local-storage")
        self.assertEqual(2, same_source.returncode)
        self.assertEqual(before, self.log.read_bytes())
        missing_parent = self.root / "missing-parent" / "never.json"
        missing = self.cli("summarize_usage", "--log", str(self.log),
                           "--output", str(missing_parent), "--attest-local-storage")
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
                summary_module.write_summary(
                    self.log, output, attest_local_storage=True)

        self.assertEqual("SUMMARY_OUTPUT_RECOVERY_REQUIRED", caught.exception.code)
        self.assertTrue(caught.exception.recovery_required)
        self.assertEqual(12, caught.exception.recovery["observed_bytes"])
        partial = output.read_bytes()
        self.assertEqual(12, len(partial))
        self.assertGreater(caught.exception.recovery["expected_bytes"], 12)
        self.assertEqual(before, self.log.read_bytes())
        retry = self.cli("summarize_usage", "--log", str(self.log),
                         "--output", str(output), "--attest-local-storage")
        self.assertEqual(2, retry.returncode)
        self.assertEqual(partial, output.read_bytes())

    def test_PORTABLE_06_relative_or_missing_input_paths_never_create_parents(self):
        module = self.module("log_interaction")
        before = directory_inventory(self.root)
        for log, code in (
            (Path("relative.csv"), "EXPLICIT_ABSOLUTE_PATH_REQUIRED"),
            (self.root / "absent.csv", "LOCAL_PATH_MISSING"),
            (self.root / "absent" / "log.csv", "LOCAL_PATH_MISSING"),
        ):
            with self.subTest(log=log):
                with self.assertRaises(module.LedgerError) as caught:
                    self.append(log=log)
                self.assertEqual(code, caught.exception.code)
                result = self.cli("summarize_usage", "--log", str(log))
                self.assertEqual(2, result.returncode)
                self.assertEqual(code, json.loads(result.stderr)["code"])
        self.assertEqual(before, directory_inventory(self.root))

    def test_PORTABLE_07_exact_totals_exceed_default_decimal_context_precision(self):
        self.append(self.record(record_id="very-large",
                                usage_value="999999999999999999999999999999.00000000000000000001"))
        self.append(self.record(record_id="small",
                                usage_value="0.99999999999999999999"))
        summary = self.module("summarize_usage").summarize_usage(self.log)
        self.assertEqual("1000000000000000000000000000000.00000000000000000000",
                         summary["usage"]["known_groups"][0]["total_value"])
        self.assertEqual(["small", "very-large"],
                         summary["usage"]["known_groups"][0]["record_ids"])

    def test_FIX2_01_first_output_write_failure_reports_retained_empty_file(self):
        output = self.root / "created-before-write.json"
        source_before = self.log.read_bytes()
        summary_module = self.module("summarize_usage")
        calls = 0
        stderr = io.StringIO()

        def fail_after_create(descriptor, content):
            nonlocal calls
            calls += 1
            self.assertTrue(output.is_file(),
                            "exclusive open must already have created the real output")
            raise OSError("controlled first write failure after exclusive create")

        with patch.object(summary_module.os, "write",
                          side_effect=fail_after_create), redirect_stderr(stderr):
            exit_code = summary_module.main([
                "--log", str(self.log),
                "--output", str(output),
                "--attest-local-storage",
            ])

        payload = json.loads(stderr.getvalue())
        self.assertEqual(2, exit_code)
        self.assertEqual(1, calls)
        self.assertEqual("SUMMARY_OUTPUT_RECOVERY_REQUIRED", payload["code"])
        self.assertTrue(payload["recovery_required"])
        self.assertEqual(0, payload["recovery"]["observed_bytes"])
        self.assertEqual(b"", output.read_bytes())
        self.assertEqual(source_before, self.log.read_bytes())

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

    def test_LEDGER_12_hard_link_log_and_existing_output_are_refused(self):
        link = self.root / "hard-linked.csv"
        os.link(self.log, link)
        for path in (self.log, link):
            result = self.cli("summarize_usage", "--log", str(path))
            self.assertEqual(2, result.returncode, result.stdout)
            self.assertEqual("UNSAFE_PATH", json.loads(result.stderr)["code"])
        self.assertEqual(HEADER, self.log.read_bytes())
        self.assertEqual(HEADER, link.read_bytes())
        link.unlink()
        output = self.root / "hard-linked.json"
        os.link(self.log, output)
        result = self.cli("summarize_usage", "--log", str(self.log),
                          "--output", str(output), "--attest-local-storage")
        self.assertEqual(2, result.returncode)
        self.assertEqual(HEADER, output.read_bytes())
        self.assertEqual(HEADER, self.log.read_bytes())

    def test_LEDGER_12_symbolic_link_log_and_output_are_refused(self):
        link = self.root / "symbolic.csv"
        try:
            link.symlink_to(self.log)
        except OSError as exc:
            if os.name == "nt" and getattr(exc, "winerror", None) == 1314:
                self.skipTest("Windows host has no symlink privilege or Developer Mode")
            raise
        self.addCleanup(link.unlink)
        result = self.cli("summarize_usage", "--log", str(link))
        self.assertEqual(2, result.returncode)
        self.assertEqual("UNSAFE_PATH", json.loads(result.stderr)["code"])
        with self.assertRaises(self.module("log_interaction").LedgerError) as caught:
            self.append(log=link)
        self.assertEqual("UNSAFE_PATH", caught.exception.code)
        output = self.root / "symbolic.json"
        output.symlink_to(self.log)
        self.addCleanup(output.unlink)
        result = self.cli("summarize_usage", "--log", str(self.log),
                          "--output", str(output), "--attest-local-storage")
        self.assertEqual(2, result.returncode)
        self.assertEqual("OUTPUT_EXISTS", json.loads(result.stderr)["code"])
        self.assertEqual(HEADER, self.log.read_bytes())


if __name__ == "__main__":
    unittest.main()
