"""Read-only, source-bound summaries of explicitly supplied local usage values."""

from __future__ import annotations

import argparse
import hashlib
import json
import os

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


def _summary(raw: bytes, records: list[InteractionRecord]) -> dict:
    known: dict[tuple[str, str, str, str | None], list[InteractionRecord]] = {}
    unknown: dict[tuple[str, str], list[InteractionRecord]] = {}
    for record in records:
        if record.usage_value is None:
            unknown.setdefault((record.tool_name, record.tool_version), []).append(record)
        else:
            key = (record.tool_name, record.tool_version,
                   record.usage_unit or "", record.usage_currency)
            known.setdefault(key, []).append(record)
    known_groups = []
    for (tool_name, tool_version, unit, currency), items in sorted(
        known.items(),
        key=lambda group: (group[0][0], group[0][1], group[0][2], group[0][3] or ""),
    ):
        known_groups.append({
            "tool_name": tool_name, "tool_version": tool_version,
            "unit": unit, "currency": currency, "record_count": len(items),
            "total_value": _scaled_sum([item.usage_value for item in items
                                        if item.usage_value is not None]),
            "record_ids": sorted(item.record_id for item in items),
        })
    unknown_groups = [
        {
            "tool_name": tool_name, "tool_version": tool_version,
            "record_count": len(items), "record_ids": sorted(item.record_id for item in items),
        }
        for (tool_name, tool_version), items in sorted(unknown.items())
    ]
    return {
        "schema_version": 1,
        "source_sha256": hashlib.sha256(raw).hexdigest(),
        "record_count": len(records),
        "unknown_decision_reference_count": sum(not item.decision_ref for item in records),
        "unknown_evidence_reference_count": sum(not item.evidence_ref for item in records),
        "usage": {
            "known_record_count": sum(len(items) for items in known.values()),
            "unknown_record_count": sum(len(items) for items in unknown.values()),
            "known_groups": known_groups,
            "unknown_groups": unknown_groups,
        },
    }


def summarize_usage(log_path: str | os.PathLike[str]) -> dict:
    """Return a deterministic summary without creating or changing any file."""
    raw, records = ledger.read_ledger(log_path)
    return _summary(raw, records)


def write_summary(
    log_path: str | os.PathLike[str],
    output_path: str | os.PathLike[str],
    *,
    attest_local_storage: bool = False,
    lock_timeout: float = 10.0,
) -> dict:
    """Exclusively create a caller-selected file; preserve it on any later failure."""
    ledger.require_write_attestation(attest_local_storage)
    source = ledger.validate_existing_log(log_path)
    output = ledger.validate_new_output(output_path, source=source, suffix=".json")
    with ledger.file_lock(source, timeout=lock_timeout):
        result = _summary(*ledger.read_ledger(source))
        encoded = (json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2)
                   + "\n").encode("utf-8")
        try:
            descriptor = os.open(output, os.O_WRONLY | os.O_CREAT | os.O_EXCL
                                 | getattr(os, "O_BINARY", 0), 0o600)
        except FileExistsError as exc:
            raise LedgerError("OUTPUT_EXISTS", "summary output must be a new, absent file") from exc
        except OSError as exc:
            raise LedgerError("LOCAL_IO_ERROR", "cannot create the summary output") from exc
        written = 0
        try:
            try:
                while written < len(encoded):
                    count = os.write(descriptor, encoded[written:])
                    if count <= 0:
                        raise OSError("zero-byte summary write")
                    written += count
            finally:
                os.close(descriptor)
        except OSError as exc:
            raise LedgerError(
                "SUMMARY_OUTPUT_RECOVERY_REQUIRED",
                "summary output exists after a failure; preserve it and inspect before retrying",
                recovery_required=True,
                recovery={"expected_bytes": len(encoded), "observed_bytes": written},
            ) from exc
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--log", required=True, help="existing absolute local CSV ledger path")
    parser.add_argument("--output", help="optional explicit, new absolute JSON path")
    parser.add_argument(
        "--attest-local-storage", action="store_true",
        help="caller assertion for writes that the selected path is single-host local, not network/cloud-sync storage",
    )
    parser.add_argument("--lock-timeout", type=float, default=10.0,
                        help="wait limit when writing --output; ignored for read-only stdout summaries")
    args = parser.parse_args(argv)
    try:
        if args.output is None:
            result = summarize_usage(args.log)
        else:
            result = write_summary(args.log, args.output,
                                   attest_local_storage=args.attest_local_storage,
                                   lock_timeout=args.lock_timeout)
    except LedgerError as exc:
        ledger.emit_error(exc)
        return exc.exit_code
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
