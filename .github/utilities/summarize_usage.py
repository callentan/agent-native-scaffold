"""Read-only, source-bound summaries of explicitly supplied local usage values."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import stat
import sys

import log_interaction as ledger
from log_interaction import InteractionRecord, LedgerError


def _scaled_sum(values: list[str]) -> str:
    parts: list[tuple[int, int]] = []
    for value in values:
        whole, separator, fraction = value.partition(".")
        coefficient = int(whole + fraction) if separator else int(whole)
        parts.append((coefficient, len(fraction) if separator else 0))
    scale = max((item[1] for item in parts), default=0)
    total = sum(coefficient * (10 ** (scale - item_scale))
                for coefficient, item_scale in parts)
    digits = str(total)
    if scale == 0:
        return digits
    digits = digits.zfill(scale + 1)
    return digits[:-scale] + "." + digits[-scale:]


def _summary(path: Path, raw: bytes, records: list[InteractionRecord]) -> dict:
    known: dict[tuple[str, str, str, str | None], list[InteractionRecord]] = {}
    unknown: dict[tuple[str, str], list[InteractionRecord]] = {}
    for record in records:
        if record.usage_value is None:
            unknown.setdefault((record.tool_name, record.tool_version), []).append(record)
        else:
            key = (
                record.tool_name,
                record.tool_version,
                record.usage_unit or "",
                record.usage_currency,
            )
            known.setdefault(key, []).append(record)

    known_groups = []
    for (tool_name, tool_version, unit, currency), items in sorted(
        known.items(),
        key=lambda group: (group[0][0], group[0][1], group[0][2], group[0][3] or ""),
    ):
        known_groups.append(
            {
                "tool_name": tool_name,
                "tool_version": tool_version,
                "unit": unit,
                "currency": currency,
                "record_count": len(items),
                "total_value": _scaled_sum([item.usage_value for item in items
                                            if item.usage_value is not None]),
                "record_ids": sorted(item.record_id for item in items),
            }
        )

    unknown_groups = [
        {
            "tool_name": tool_name,
            "tool_version": tool_version,
            "record_count": len(items),
            "record_ids": sorted(item.record_id for item in items),
        }
        for (tool_name, tool_version), items in sorted(unknown.items())
    ]
    return {
        "schema_version": 1,
        "source_sha256": hashlib.sha256(raw).hexdigest(),
        "record_count": len(records),
        "unknown_decision_reference_count": sum(
            not item.decision_ref for item in records
        ),
        "unknown_evidence_reference_count": sum(
            not item.evidence_ref for item in records
        ),
        "usage": {
            "known_record_count": sum(len(items) for items in known.values()),
            "unknown_record_count": sum(len(items) for items in unknown.values()),
            "known_groups": known_groups,
            "unknown_groups": unknown_groups,
        },
    }


def summarize_usage(
    log_path: str | os.PathLike[str],
    *,
    lock_timeout: float = 10.0,
) -> dict:
    """Return a deterministic summary; source CSV bytes are never modified."""
    path = ledger._validate_existing_log(log_path)
    raw, records = ledger._read_validated(path, lock_timeout=lock_timeout)
    return _summary(path, raw, records)


def _write_summary(
    log_path: str | os.PathLike[str],
    output_path: str | os.PathLike[str],
    *,
    lock_timeout: float = 10.0,
) -> dict:
    source = ledger._validate_existing_log(log_path)
    output = ledger._validate_new_output(output_path, source=source, suffix=".json")
    result = summarize_usage(source, lock_timeout=lock_timeout)
    content = (json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + "\n")
    encoded = content.encode("utf-8")
    flags = os.O_RDWR | os.O_CREAT | os.O_EXCL | getattr(os, "O_BINARY", 0)
    try:
        descriptor = os.open(output, flags, 0o600)
    except FileExistsError as exc:
        raise ledger._error("OUTPUT_EXISTS", "summary output must remain absent until exclusive creation") from exc
    except OSError as exc:
        raise ledger._error("SUMMARY_WRITE_ERROR", "cannot create the new summary output") from exc

    written_total = 0
    try:
        details = os.fstat(descriptor)
        if not stat.S_ISREG(details.st_mode):
            raise ledger._error("SUMMARY_WRITE_ERROR", "summary output is not a regular file")
        identity = ledger._path_identity(details)
        path_details = ledger._assert_single_regular_file(output, code="UNSAFE_PATH")
        if identity != ledger._path_identity(path_details):
            raise ledger._error("UNSAFE_PATH", "summary output identity changed during creation")
        try:
            while written_total < len(encoded):
                count = os.write(descriptor, encoded[written_total:])
                if count <= 0:
                    raise OSError("zero-byte summary write")
                written_total += count
            os.fsync(descriptor)
            os.lseek(descriptor, 0, os.SEEK_SET)
            chunks = []
            while True:
                part = os.read(descriptor, 65536)
                if not part:
                    break
                chunks.append(part)
            observed = b"".join(chunks)
            details = os.fstat(descriptor)
            path_details = ledger._assert_single_regular_file(output, code="UNSAFE_PATH")
            if (observed != encoded
                    or ledger._path_identity(details) != identity
                    or ledger._path_identity(path_details) != identity):
                raise ledger.LedgerError(
                    "SUMMARY_OUTPUT_CHANGED",
                    "new summary output changed; preserve it and inspect before retrying",
                    exit_code=2,
                    recovery_required=True,
                    recovery={
                        "expected_bytes": len(encoded),
                        "observed_bytes": len(observed),
                    },
                )
        except OSError as exc:
            try:
                os.lseek(descriptor, 0, os.SEEK_SET)
                observed_size = len(os.read(descriptor, max(len(encoded) + 1, 65536)))
            except OSError:
                observed_size = written_total
            raise ledger.LedgerError(
                "SUMMARY_OUTPUT_RECOVERY_REQUIRED",
                "summary output I/O failed; preserve the new file and inspect it before retrying",
                exit_code=2,
                recovery_required=observed_size > 0,
                recovery={
                    "expected_bytes": len(encoded),
                    "observed_bytes": observed_size,
                },
            ) from exc
    finally:
        os.close(descriptor)
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--log", required=True, help="existing absolute local CSV ledger path")
    parser.add_argument("--output", help="optional explicit, new absolute JSON path")
    parser.add_argument("--lock-timeout", type=float, default=10.0)
    args = parser.parse_args(argv)
    try:
        if args.output is None:
            result = summarize_usage(args.log, lock_timeout=args.lock_timeout)
        else:
            result = _write_summary(args.log, args.output, lock_timeout=args.lock_timeout)
    except LedgerError as exc:
        ledger._emit_error(exc)
        return exc.exit_code
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
