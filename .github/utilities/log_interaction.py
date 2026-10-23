"""Append explicit, caller-supplied interaction facts to a local CSV ledger."""

from __future__ import annotations

import argparse
from contextlib import contextmanager
import csv
from dataclasses import dataclass
from datetime import datetime
import decimal
import errno
import hashlib
import io
import json
import math
import os
from pathlib import Path
import re
import stat
import sys
import time
from typing import Iterator

if os.name == "nt":
    import msvcrt
else:
    import fcntl


SCHEMA_VERSION = "1"
CSV_HEADER = (
    "schema_version",
    "record_id",
    "recorded_at",
    "tool_name",
    "tool_version",
    "task_ref",
    "object_ref",
    "object_baseline",
    "operation_summary",
    "decision_ref",
    "usage_value",
    "usage_unit",
    "usage_currency",
    "evidence_ref",
)
_TIMESTAMP = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$"
)
_DECIMAL = re.compile(r"^\d+(?:\.\d+)?$")
_MAX_VALUE_LENGTH = 128
_MAX_SUMMARY_LENGTH = 512
_MAX_TEXT_LENGTH = 2048
_LOCK_CONTENTION_ERRNOS = {errno.EACCES, errno.EDEADLK, errno.EAGAIN}


@dataclass(frozen=True)
class InteractionRecord:
    """A narrow record of caller-supplied facts; no field asserts qualification."""

    record_id: str
    recorded_at: str
    tool_name: str
    tool_version: str
    task_ref: str
    object_ref: str
    object_baseline: str
    operation_summary: str
    decision_ref: str | None = None
    usage_value: str | None = None
    usage_unit: str | None = None
    usage_currency: str | None = None
    evidence_ref: str | None = None


@dataclass(frozen=True)
class AppendResult:
    status: str
    record_id: str
    record_count: int
    source_sha256: str


class LedgerError(Exception):
    """A stable, bounded error suitable for a CLI result without row contents."""

    def __init__(
        self,
        code: str,
        message: str,
        *,
        exit_code: int = 2,
        recovery_required: bool = False,
        recovery: dict | None = None,
    ):
        super().__init__(message)
        self.code = code
        self.exit_code = exit_code
        self.recovery_required = recovery_required
        self.recovery = recovery or {}


def _error(code: str, message: str, *, exit_code: int = 2) -> LedgerError:
    return LedgerError(code, message, exit_code=exit_code)


def require_write_attestation(attest_local_storage: bool) -> None:
    if attest_local_storage is not True:
        raise _error(
            "WRITE_ATTESTATION_REQUIRED",
            "caller must explicitly attest this write target is single-host local and not network/cloud-sync storage",
        )


def _text(name: str, value: object, *, limit: int = _MAX_TEXT_LENGTH) -> str:
    if not isinstance(value, str) or not value.strip():
        raise _error("INVALID_RECORD", f"{name} must be a non-empty string", exit_code=1)
    if len(value) > limit or "\x00" in value:
        raise _error("INVALID_RECORD", f"{name} exceeds its supported text boundary", exit_code=1)
    return value


def _optional_text(name: str, value: object, *, limit: int = _MAX_TEXT_LENGTH) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise _error("INVALID_RECORD", f"{name} must be text or unknown", exit_code=1)
    if "\x00" in value or len(value) > limit:
        raise _error("INVALID_RECORD", f"{name} exceeds its supported text boundary", exit_code=1)
    return value if value.strip() else None


def _validated_record(record: InteractionRecord) -> InteractionRecord:
    if not isinstance(record, InteractionRecord):
        raise _error("INVALID_RECORD", "record must be an InteractionRecord", exit_code=1)
    record_id = _text("record_id", record.record_id, limit=128)
    if record_id != record_id.strip():
        raise _error("INVALID_RECORD", "record_id cannot have boundary whitespace", exit_code=1)
    recorded_at = _text("recorded_at", record.recorded_at, limit=128)
    if not _TIMESTAMP.fullmatch(recorded_at):
        raise _error("INVALID_TIMESTAMP",
                     "recorded_at must be a timezone-aware ISO 8601 timestamp", exit_code=1)
    parsed_time = recorded_at[:-1] + "+00:00" if recorded_at.endswith("Z") else recorded_at
    try:
        parsed = datetime.fromisoformat(parsed_time)
    except ValueError as exc:
        raise _error("INVALID_TIMESTAMP", "recorded_at is not a valid calendar time",
                     exit_code=1) from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise _error("INVALID_TIMESTAMP", "recorded_at must include an explicit UTC offset",
                     exit_code=1)

    tool_name = _text("tool_name", record.tool_name)
    tool_version = _text("tool_version", record.tool_version)
    task_ref = _text("task_ref", record.task_ref)
    object_ref = _text("object_ref", record.object_ref)
    object_baseline = _text("object_baseline", record.object_baseline)
    operation_summary = _text(
        "operation_summary", record.operation_summary, limit=_MAX_SUMMARY_LENGTH)
    decision_ref = _optional_text("decision_ref", record.decision_ref)
    evidence_ref = _optional_text("evidence_ref", record.evidence_ref)
    usage_value = record.usage_value
    usage_unit = _optional_text("usage_unit", record.usage_unit, limit=128)
    usage_currency = _optional_text("usage_currency", record.usage_currency, limit=32)
    if usage_value is None:
        if usage_unit is not None or usage_currency is not None:
            raise _error("INVALID_USAGE",
                         "usage value, unit, and currency must be supplied together or left unknown",
                         exit_code=1)
    else:
        if (not isinstance(usage_value, str) or len(usage_value) > _MAX_VALUE_LENGTH
                or not _DECIMAL.fullmatch(usage_value)):
            raise _error("INVALID_USAGE",
                         "usage_value must be a finite, non-negative decimal without exponent notation",
                         exit_code=1)
        try:
            parsed_value = decimal.Decimal(usage_value)
        except decimal.InvalidOperation as exc:
            raise _error("INVALID_USAGE", "usage_value is not a decimal", exit_code=1) from exc
        if not parsed_value.is_finite() or parsed_value < 0:
            raise _error("INVALID_USAGE", "usage_value must be finite and non-negative",
                         exit_code=1)
        if usage_unit is None:
            raise _error("INVALID_USAGE", "known usage requires a non-empty usage_unit",
                         exit_code=1)
    return InteractionRecord(
        record_id=record_id, recorded_at=recorded_at, tool_name=tool_name,
        tool_version=tool_version, task_ref=task_ref, object_ref=object_ref,
        object_baseline=object_baseline, operation_summary=operation_summary,
        decision_ref=decision_ref, usage_value=usage_value, usage_unit=usage_unit,
        usage_currency=usage_currency, evidence_ref=evidence_ref,
    )


def _normalized_path(path: Path) -> str:
    return os.path.normcase(os.path.normpath(str(path)))


def _explicit_path(value: str | os.PathLike[str], *, label: str) -> Path:
    path = Path(value)
    if not path.is_absolute():
        raise _error("EXPLICIT_ABSOLUTE_PATH_REQUIRED",
                     f"{label} path must be explicitly absolute")
    try:
        # Resolve parent aliases, including macOS /var and /tmp, but not the leaf:
        # a caller-selected file symlink must still be rejected by lstat.
        parent = path.parent.resolve(strict=True)
        if not parent.is_dir():
            raise _error("LOCAL_PATH_MISSING", f"{label} parent must already exist")
    except FileNotFoundError as exc:
        raise _error("LOCAL_PATH_MISSING", f"{label} parent must already exist") from exc
    except (OSError, RuntimeError) as exc:
        raise _error("LOCAL_IO_ERROR", f"cannot inspect the explicit {label} parent") from exc
    return parent / path.name


def _assert_single_regular_file(path: Path, *, code: str) -> os.stat_result:
    try:
        details = path.lstat()
    except FileNotFoundError as exc:
        raise _error("LOCAL_PATH_MISSING", "the requested local file must already exist") from exc
    except OSError as exc:
        raise _error("LOCAL_IO_ERROR", "cannot inspect the requested local file") from exc
    if not stat.S_ISREG(details.st_mode):
        raise _error(code, "the requested path must be a regular file, not a symbolic link")
    if details.st_nlink != 1:
        raise _error(code, "hard-linked files are unsupported to protect other owner paths")
    return details


def _template_path() -> Path:
    return Path(__file__).resolve().parents[2] / "_templates" / "reports" / "ai-interaction-log.csv"


def _is_template(path: Path) -> bool:
    return _normalized_path(path) == _normalized_path(_template_path())


def validate_existing_log(value: str | os.PathLike[str]) -> Path:
    """Return the explicit, existing, singly linked regular ledger path."""
    path = _explicit_path(value, label="log")
    _assert_single_regular_file(path, code="UNSAFE_PATH")
    if _is_template(path):
        raise _error("TEMPLATE_NOT_LEDGER",
                     "copy the blank reusable template to a new explicit local ledger path")
    return path


def validate_new_output(
    value: str | os.PathLike[str], *, source: Path, suffix: str,
) -> Path:
    """Return an explicit, absent output path in an existing parent directory."""
    path = _explicit_path(value, label="output")
    if path.suffix.lower() != suffix:
        raise _error("INVALID_OUTPUT_PATH", f"output must use the {suffix} suffix")
    if _normalized_path(path) == _normalized_path(source):
        raise _error("OUTPUT_IS_SOURCE", "summary output cannot be the source ledger")
    if os.path.lexists(path):
        raise _error("OUTPUT_EXISTS", "summary output must be a new, absent file")
    if _is_template(path):
        raise _error("UNSAFE_PATH", "the reusable CSV template is not a summary output")
    return path


def _open_lock_file(path: Path) -> int:
    """Open (or create) the empty sibling lock file; never reuse an owner file."""
    lock_path = path.with_name(path.name + ".lock")
    if os.path.lexists(lock_path):
        _assert_single_regular_file(lock_path, code="INVALID_LOCK_FILE")
    descriptor = None
    try:
        descriptor = os.open(lock_path, os.O_RDWR | os.O_CREAT | getattr(os, "O_BINARY", 0), 0o600)
        if os.fstat(descriptor).st_size != 0:
            raise _error("INVALID_LOCK_FILE", "the persistent lock file must be an empty regular file")
        return descriptor
    except (LedgerError, OSError) as exc:
        if descriptor is not None:
            os.close(descriptor)
        if isinstance(exc, LedgerError):
            raise
        raise _error("LOCK_FILE_ERROR", "cannot open the persistent sibling lock file") from exc


def _lock_descriptor(descriptor: int, *, release: bool = False) -> None:
    """Small stdlib adapter; lock ownership is the same on all supported hosts."""
    if os.name == "nt":
        os.lseek(descriptor, 0, os.SEEK_SET)
        msvcrt.locking(descriptor, msvcrt.LK_UNLCK if release else msvcrt.LK_NBLCK, 1)
    else:
        fcntl.flock(descriptor, fcntl.LOCK_UN if release else fcntl.LOCK_EX | fcntl.LOCK_NB)


@contextmanager
def file_lock(
    log_path: str | os.PathLike[str], *, timeout: float = 10.0,
) -> Iterator[None]:
    """Serialize cooperating local processes; keep the empty lock sidecar."""
    path = validate_existing_log(log_path)
    if (not isinstance(timeout, (int, float)) or not math.isfinite(timeout) or timeout < 0):
        raise _error("INVALID_LOCK_TIMEOUT", "lock timeout must be a non-negative number")
    descriptor = _open_lock_file(path)
    locked = False
    deadline = time.monotonic() + float(timeout)
    try:
        while True:
            try:
                _lock_descriptor(descriptor)
                locked = True
                break
            except OSError as exc:
                if exc.errno not in _LOCK_CONTENTION_ERRNOS:
                    raise _error("LOCK_UNAVAILABLE", "local process locking failed") from exc
                if time.monotonic() >= deadline:
                    raise _error("LOCK_TIMEOUT", "timed out waiting for another local writer")
                time.sleep(min(0.05, max(0.0, deadline - time.monotonic())))
        yield
    except OSError as exc:
        raise _error("LOCAL_IO_ERROR", "local file locking or I/O failed") from exc
    finally:
        try:
            if locked:
                try:
                    _lock_descriptor(descriptor, release=True)
                except OSError as exc:
                    raise _error("LOCK_RELEASE_FAILED", "local process lock release failed") from exc
        finally:
            os.close(descriptor)


def _read_log_bytes(path: Path) -> bytes:
    try:
        return path.read_bytes()
    except OSError as exc:
        raise _error("LOCAL_IO_ERROR", "cannot read the requested local ledger") from exc


def _parse_record(row: list[str], line_number: int) -> InteractionRecord:
    if len(row) != len(CSV_HEADER):
        raise _error("INVALID_LOG_ROW",
                     f"existing CSV row at line {line_number} has an unexpected field count")
    if row[0] != SCHEMA_VERSION:
        raise _error("INCOMPATIBLE_LOG_VERSION",
                     f"existing CSV row at line {line_number} uses an unsupported schema version")
    try:
        return _validated_record(InteractionRecord(
            record_id=row[1], recorded_at=row[2], tool_name=row[3],
            tool_version=row[4], task_ref=row[5], object_ref=row[6],
            object_baseline=row[7], operation_summary=row[8],
            decision_ref=row[9] or None, usage_value=row[10] or None,
            usage_unit=row[11] or None, usage_currency=row[12] or None,
            evidence_ref=row[13] or None,
        ))
    except LedgerError as exc:
        raise _error("INVALID_LOG_ROW",
                     f"existing CSV row at line {line_number} violates the v1 record contract") from exc


def _parse_log(raw: bytes) -> list[InteractionRecord]:
    try:
        text = raw.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise _error("INVALID_LOG", "existing CSV is not valid UTF-8") from exc
    try:
        reader = csv.reader(io.StringIO(text, newline=""), strict=True)
        if next(reader, None) != list(CSV_HEADER):
            raise _error("INCOMPATIBLE_LOG_HEADER",
                         "existing CSV header does not exactly match schema version 1")
        records: list[InteractionRecord] = []
        seen: set[str] = set()
        for row in reader:
            line_number = reader.line_num
            if not row:
                raise _error("INVALID_LOG", f"existing CSV contains a blank row at line {line_number}")
            record = _parse_record(row, line_number)
            if record.record_id in seen:
                raise _error("DUPLICATE_LOG_ID", "existing CSV contains a duplicate record ID")
            seen.add(record.record_id)
            records.append(record)
    except csv.Error as exc:
        raise _error("INVALID_LOG", "existing CSV quoting or row syntax is malformed") from exc
    return records


def _csv_row_bytes(record: InteractionRecord) -> bytes:
    row = (
        SCHEMA_VERSION, record.record_id, record.recorded_at, record.tool_name,
        record.tool_version, record.task_ref, record.object_ref, record.object_baseline,
        record.operation_summary, record.decision_ref or "", record.usage_value or "",
        record.usage_unit or "", record.usage_currency or "", record.evidence_ref or "",
    )
    output = io.StringIO(newline="")
    csv.writer(output, lineterminator="\r\n", quoting=csv.QUOTE_MINIMAL).writerow(row)
    return output.getvalue().encode("utf-8")


def _read_descriptor(descriptor: int) -> bytes:
    os.lseek(descriptor, 0, os.SEEK_SET)
    chunks: list[bytes] = []
    while True:
        part = os.read(descriptor, 65536)
        if not part:
            return b"".join(chunks)
        chunks.append(part)


def _append_bytes(path: Path, original: bytes, suffix: bytes) -> None:
    """Append under the lock; refuse if a non-cooperating writer changed the ledger."""
    try:
        descriptor = os.open(path, os.O_RDWR | os.O_APPEND | getattr(os, "O_BINARY", 0))
    except OSError as exc:
        raise _error("LOCAL_IO_ERROR", "cannot open the validated ledger for append") from exc
    written = 0
    try:
        try:
            unchanged = _read_descriptor(descriptor) == original
        except OSError as exc:
            raise _error("LOCAL_IO_ERROR", "cannot re-read the ledger before append") from exc
        if not unchanged:
            raise _error("OWNER_BYTES_CHANGED",
                         "ledger bytes changed after the locked read; no bytes were written")
        try:
            while written < len(suffix):
                count = os.write(descriptor, suffix[written:])
                if count <= 0:
                    raise OSError("zero-byte append")
                written += count
            os.fsync(descriptor)
        except OSError as exc:
            try:
                observed = os.fstat(descriptor).st_size
            except OSError:
                observed = len(original) + written
            raise LedgerError(
                "APPEND_IO_RECOVERY_REQUIRED",
                "append failed; preserve the ledger and inspect its final CSV row before retrying",
                exit_code=2, recovery_required=True,
                recovery={
                    "original_bytes": len(original), "observed_bytes": observed,
                    "observed_delta_bytes": max(0, observed - len(original)),
                    "expected_append_bytes": len(suffix),
                },
            ) from exc
    finally:
        os.close(descriptor)


def read_ledger(log_path: str | os.PathLike[str]) -> tuple[bytes, list[InteractionRecord]]:
    """Read and parse the ledger once; create no lock or other sidecar."""
    raw = _read_log_bytes(validate_existing_log(log_path))
    return raw, _parse_log(raw)


def append_record(
    log_path: str | os.PathLike[str],
    record: InteractionRecord,
    *,
    attest_local_storage: bool = False,
    lock_timeout: float = 10.0,
) -> AppendResult:
    """Append one exact record, or return a no-change result for an identical replay."""
    require_write_attestation(attest_local_storage)
    path = validate_existing_log(log_path)
    supplied = _validated_record(record)
    with file_lock(path, timeout=lock_timeout):
        original, records = read_ledger(path)
        for existing in records:
            if existing.record_id == supplied.record_id:
                if existing == supplied:
                    return AppendResult("duplicate", supplied.record_id, len(records),
                                        hashlib.sha256(original).hexdigest())
                raise _error("RECORD_ID_CONFLICT",
                             "record ID already exists with different caller-supplied values",
                             exit_code=1)
        separator = b"" if original.endswith((b"\n", b"\r")) else b"\r\n"
        suffix = separator + _csv_row_bytes(supplied)
        _append_bytes(path, original, suffix)
        return AppendResult("appended", supplied.record_id, len(records) + 1,
                            hashlib.sha256(original + suffix).hexdigest())


def emit_error(error: LedgerError) -> None:
    """Print one bounded JSON error object to stderr for CLI callers."""
    payload = {
        "status": "error", "code": error.code, "message": str(error),
        "recovery_required": error.recovery_required,
    }
    if error.recovery:
        payload["recovery"] = error.recovery
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True), file=sys.stderr)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--log", required=True, help="existing absolute local CSV ledger path")
    parser.add_argument("--record-id", required=True)
    parser.add_argument("--time", dest="recorded_at", required=True)
    parser.add_argument("--tool", dest="tool_name", required=True)
    parser.add_argument("--tool-version", required=True)
    parser.add_argument("--task-ref", required=True)
    parser.add_argument("--object-ref", required=True)
    parser.add_argument("--object-baseline", required=True)
    parser.add_argument("--summary", dest="operation_summary", required=True)
    parser.add_argument("--decision-ref")
    parser.add_argument("--usage-value")
    parser.add_argument("--usage-unit")
    parser.add_argument("--usage-currency")
    parser.add_argument("--evidence-ref")
    parser.add_argument(
        "--attest-local-storage", action="store_true",
        help="caller assertion that the selected ledger is single-host local, not network or cloud-sync storage",
    )
    parser.add_argument("--lock-timeout", type=float, default=10.0)
    args = parser.parse_args(argv)
    record = InteractionRecord(
        record_id=args.record_id, recorded_at=args.recorded_at, tool_name=args.tool_name,
        tool_version=args.tool_version, task_ref=args.task_ref, object_ref=args.object_ref,
        object_baseline=args.object_baseline, operation_summary=args.operation_summary,
        decision_ref=args.decision_ref, usage_value=args.usage_value,
        usage_unit=args.usage_unit, usage_currency=args.usage_currency, evidence_ref=args.evidence_ref,
    )
    try:
        result = append_record(args.log, record, attest_local_storage=args.attest_local_storage,
                               lock_timeout=args.lock_timeout)
    except LedgerError as exc:
        emit_error(exc)
        return exc.exit_code
    print(json.dumps({
        "status": result.status, "record_id": result.record_id,
        "record_count": result.record_count, "source_sha256": result.source_sha256,
    }, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
