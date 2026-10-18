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
) -> dict:
    """Return a deterministic summary without creating or changing any file."""
    path = ledger._validate_existing_log(log_path)
    raw, records = ledger._read_validated(path)
    return _summary(path, raw, records)


def write_summary(
    log_path: str | os.PathLike[str],
    output_path: str | os.PathLike[str],
    *,
    attest_local_storage: bool = False,
    lock_timeout: float = 10.0,
) -> dict:
    """Create one new summary file after the caller explicitly attests its path."""
    ledger._require_write_attestation(attest_local_storage)
    source = ledger._validate_existing_log(log_path)
    output = ledger._validate_new_output(output_path, source=source, suffix=".json")
    created_identity = None
    output_bytes = 0
    expected_output_bytes = 0

    def remember_native_output(identity: dict, size: int) -> None:
        nonlocal created_identity, output_bytes
        created_identity = identity
        output_bytes = size

    try:
        with ledger._pinned_directory_chain(output.parent) as parent_binding:
            # The validated directory chain remains open without FILE_SHARE_DELETE
            # across source snapshot, exclusive create, write, and post-create checks.
            parent_binding.verify()
            output = ledger._validate_new_output(output, source=source, suffix=".json")
            with ledger._file_lock(source, timeout=lock_timeout):
                raw, records = ledger._read_validated(source)
                result = _summary(source, raw, records)
                content = json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
                encoded = content.encode("utf-8")
                expected_output_bytes = len(encoded)

                confirm_raw, _ = ledger._read_validated(source)
                if confirm_raw != raw:
                    raise ledger._error(
                        "OWNER_BYTES_CHANGED",
                        "ledger changed after summary calculation and before output creation",
                    )
                parent_binding.verify()
                descriptor = ledger._create_exclusive_output(
                    parent_binding,
                    output.name,
                    on_created=remember_native_output,
                )

                written_total = 0
                try:
                    details = os.fstat(descriptor)
                    if not stat.S_ISREG(details.st_mode):
                        raise ledger._error(
                            "SUMMARY_WRITE_ERROR",
                            "summary output is not a regular file",
                        )
                    output_bytes = details.st_size
                    identity = ledger._path_identity(details)
                    path_details = ledger._assert_single_regular_file(
                        output, code="UNSAFE_PATH")
                    if identity != ledger._path_identity(path_details):
                        raise ledger._error(
                            "UNSAFE_PATH",
                            "summary output identity changed during creation",
                        )

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
                        output_bytes = len(observed)
                        path_details = ledger._assert_single_regular_file(
                            output, code="UNSAFE_PATH")
                        if (observed != encoded
                                or ledger._path_identity(details) != identity
                                or ledger._path_identity(path_details) != identity
                                or details.st_ino != created_identity["file_id"]):
                            raise ledger.LedgerError(
                                "SUMMARY_OUTPUT_CHANGED",
                                "new summary output changed; preserve it and inspect before retrying",
                                exit_code=2,
                                recovery_required=True,
                                recovery={
                                    "expected_bytes": len(encoded),
                                    "observed_bytes": len(observed),
                                    "output_identity": created_identity,
                                },
                            )
                        parent_binding.verify()
                        final_raw, _ = ledger._read_validated(source)
                        if final_raw != raw:
                            raise ledger.LedgerError(
                                "OWNER_BYTES_CHANGED",
                                "ledger changed while its summary output was being written",
                                exit_code=2,
                                recovery_required=True,
                                recovery={
                                    "expected_source_sha256": result["source_sha256"],
                                    "observed_source_sha256": hashlib.sha256(final_raw).hexdigest(),
                                    "observed_output_bytes": len(observed),
                                    "output_identity": created_identity,
                                },
                            )
                    except OSError as exc:
                        try:
                            os.lseek(descriptor, 0, os.SEEK_SET)
                            observed_size = len(os.read(
                                descriptor, max(len(encoded) + 1, 65536)))
                            output_bytes = observed_size
                        except OSError:
                            observed_size = written_total
                            output_bytes = written_total
                        raise ledger.LedgerError(
                            "SUMMARY_OUTPUT_RECOVERY_REQUIRED",
                            "summary output I/O failed; preserve the new file and inspect it before retrying",
                            exit_code=2,
                            recovery_required=True,
                            recovery={
                                "expected_bytes": len(encoded),
                                "observed_bytes": observed_size,
                                "output_identity": created_identity,
                            },
                        ) from exc
                finally:
                    os.close(descriptor)
                return result
    except ledger.LedgerError as exc:
        if created_identity is not None:
            code = ("SUMMARY_OUTPUT_RECOVERY_REQUIRED"
                    if exc.code in ("LOCAL_IO_ERROR", "OUTPUT_CREATE_ERROR")
                    else exc.code)
            recovery = {
                **exc.recovery,
                "observed_output_bytes": output_bytes,
                "observed_bytes": output_bytes,
                "output_identity": created_identity,
            }
            if code != exc.code:
                recovery["cause_code"] = exc.code
            raise ledger.LedgerError(
                code,
                ("summary output exists after a post-create failure: " + str(exc)
                 if code == "SUMMARY_OUTPUT_RECOVERY_REQUIRED" else str(exc)),
                exit_code=2,
                recovery_required=True,
                recovery=recovery,
            ) from exc
        raise
    except OSError as exc:
        if created_identity is None:
            raise ledger._error("LOCAL_IO_ERROR", "summary output failed before file creation") from exc
        raise ledger.LedgerError(
            "SUMMARY_OUTPUT_RECOVERY_REQUIRED",
            "summary output exists after an OS handle failure; preserve it and inspect it before retrying",
            exit_code=2,
            recovery_required=True,
            recovery={
                "expected_bytes": expected_output_bytes,
                "observed_bytes": output_bytes,
                "output_identity": created_identity,
            },
        ) from exc


def _output_identity(details: os.stat_result) -> dict:
    return {
        "device": int(details.st_dev),
        "file_id": int(details.st_ino),
        "link_count": int(details.st_nlink),
    }


def _write_summary(
    log_path: str | os.PathLike[str],
    output_path: str | os.PathLike[str],
    *,
    attest_local_storage: bool = False,
    lock_timeout: float = 10.0,
) -> dict:
    """Compatibility wrapper for the original private test/helper entry point."""
    return write_summary(
        log_path,
        output_path,
        attest_local_storage=attest_local_storage,
        lock_timeout=lock_timeout,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--log", required=True, help="existing absolute local CSV ledger path")
    parser.add_argument("--output", help="optional explicit, new absolute JSON path")
    parser.add_argument(
        "--attest-local-storage",
        action="store_true",
        help="caller assertion for writes that the selected path is single-host local, not network/cloud-sync storage",
    )
    parser.add_argument(
        "--lock-timeout",
        type=float,
        default=10.0,
        help="wait limit for an explicit --output write; ignored by read-only stdout summaries",
    )
    args = parser.parse_args(argv)
    try:
        if args.output is None:
            result = summarize_usage(args.log)
        else:
            result = write_summary(
                args.log,
                args.output,
                attest_local_storage=args.attest_local_storage,
                lock_timeout=args.lock_timeout,
            )
    except LedgerError as exc:
        ledger._emit_error(exc)
        return exc.exit_code
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
