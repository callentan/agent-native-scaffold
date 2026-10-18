"""Append explicit, caller-supplied interaction facts to a local CSV ledger."""

from __future__ import annotations

import argparse
from contextlib import contextmanager
import csv
import ctypes
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

try:
    import msvcrt
except ImportError:  # The public API returns an explicit unsupported-storage error.
    msvcrt = None


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
_FILE_ATTRIBUTE_REPARSE_POINT = 0x400
_DRIVE_FIXED = 3
_LOCK_CONTENTION_ERRNOS = {errno.EACCES, errno.EDEADLK, errno.EAGAIN}
_FILE_READ_ATTRIBUTES = 0x0080
_FILE_TRAVERSE = 0x0020
_FILE_SHARE_READ = 0x00000001
_FILE_SHARE_WRITE = 0x00000002
_OPEN_EXISTING = 3
_FILE_FLAG_OPEN_REPARSE_POINT = 0x00200000
_FILE_FLAG_BACKUP_SEMANTICS = 0x02000000
_FILE_ATTRIBUTE_DIRECTORY = 0x0010


class _WindowsFileTime(ctypes.Structure):
    _fields_ = [("low", ctypes.c_uint32), ("high", ctypes.c_uint32)]


class _WindowsFileInformation(ctypes.Structure):
    _fields_ = [
        ("attributes", ctypes.c_uint32),
        ("creation_time", _WindowsFileTime),
        ("last_access_time", _WindowsFileTime),
        ("last_write_time", _WindowsFileTime),
        ("volume_serial", ctypes.c_uint32),
        ("file_size_high", ctypes.c_uint32),
        ("file_size_low", ctypes.c_uint32),
        ("link_count", ctypes.c_uint32),
        ("file_index_high", ctypes.c_uint32),
        ("file_index_low", ctypes.c_uint32),
    ]


class _WindowsUnicodeString(ctypes.Structure):
    _fields_ = [
        ("length", ctypes.c_uint16),
        ("maximum_length", ctypes.c_uint16),
        ("buffer", ctypes.c_void_p),
    ]


class _WindowsObjectAttributes(ctypes.Structure):
    _fields_ = [
        ("length", ctypes.c_uint32),
        ("root_directory", ctypes.c_void_p),
        ("object_name", ctypes.POINTER(_WindowsUnicodeString)),
        ("attributes", ctypes.c_uint32),
        ("security_descriptor", ctypes.c_void_p),
        ("security_quality_of_service", ctypes.c_void_p),
    ]


class _WindowsIoStatusBlock(ctypes.Structure):
    _fields_ = [
        ("status", ctypes.c_void_p),
        ("information", ctypes.c_size_t),
    ]

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


def _require_write_attestation(attest_local_storage: bool) -> None:
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
        raise _error(
            "INVALID_TIMESTAMP",
            "recorded_at must be a timezone-aware ISO 8601 timestamp",
            exit_code=1,
        )
    parsed_time = recorded_at[:-1] + "+00:00" if recorded_at.endswith("Z") else recorded_at
    try:
        parsed = datetime.fromisoformat(parsed_time)
    except ValueError as exc:
        raise _error("INVALID_TIMESTAMP", "recorded_at is not a valid calendar time", exit_code=1) from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise _error(
            "INVALID_TIMESTAMP",
            "recorded_at must include an explicit UTC offset",
            exit_code=1,
        )

    tool_name = _text("tool_name", record.tool_name)
    tool_version = _text("tool_version", record.tool_version)
    task_ref = _text("task_ref", record.task_ref)
    object_ref = _text("object_ref", record.object_ref)
    object_baseline = _text("object_baseline", record.object_baseline)
    operation_summary = _text(
        "operation_summary", record.operation_summary, limit=_MAX_SUMMARY_LENGTH
    )
    decision_ref = _optional_text("decision_ref", record.decision_ref)
    evidence_ref = _optional_text("evidence_ref", record.evidence_ref)

    usage_value = record.usage_value
    usage_unit = _optional_text("usage_unit", record.usage_unit, limit=128)
    usage_currency = _optional_text("usage_currency", record.usage_currency, limit=32)
    if usage_value is None:
        if usage_unit is not None or usage_currency is not None:
            raise _error(
                "INVALID_USAGE",
                "usage value, unit, and currency must be supplied together or left unknown",
                exit_code=1,
            )
    else:
        if (not isinstance(usage_value, str) or len(usage_value) > _MAX_VALUE_LENGTH
                or not _DECIMAL.fullmatch(usage_value)):
            raise _error(
                "INVALID_USAGE",
                "usage_value must be a finite, non-negative decimal without exponent notation",
                exit_code=1,
            )
        try:
            parsed_value = decimal.Decimal(usage_value)
        except decimal.InvalidOperation as exc:
            raise _error("INVALID_USAGE", "usage_value is not a decimal", exit_code=1) from exc
        if not parsed_value.is_finite() or parsed_value < 0:
            raise _error("INVALID_USAGE", "usage_value must be finite and non-negative", exit_code=1)
        if usage_unit is None:
            raise _error("INVALID_USAGE", "known usage requires a non-empty usage_unit", exit_code=1)

    return InteractionRecord(
        record_id=record_id,
        recorded_at=recorded_at,
        tool_name=tool_name,
        tool_version=tool_version,
        task_ref=task_ref,
        object_ref=object_ref,
        object_baseline=object_baseline,
        operation_summary=operation_summary,
        decision_ref=decision_ref,
        usage_value=usage_value,
        usage_unit=usage_unit,
        usage_currency=usage_currency,
        evidence_ref=evidence_ref,
    )


def _normalized_path(path: Path) -> str:
    return os.path.normcase(os.path.normpath(str(path)))


def _is_reparse_point(details: os.stat_result) -> bool:
    return bool(getattr(details, "st_file_attributes", 0) & _FILE_ATTRIBUTE_REPARSE_POINT)


def _require_local_drive(path: Path) -> None:
    if os.name != "nt" or not path.drive or path.drive.startswith("\\\\"):
        raise _error(
            "UNSUPPORTED_STORAGE",
            "only an absolute path on a Windows fixed local drive is supported",
        )
    try:
        get_drive_type = ctypes.WinDLL("kernel32", use_last_error=True).GetDriveTypeW
        get_drive_type.argtypes = [ctypes.c_wchar_p]
        get_drive_type.restype = ctypes.c_uint
        drive_type = get_drive_type(path.anchor)
    except (AttributeError, OSError) as exc:
        raise _error("UNSUPPORTED_STORAGE", "cannot determine local drive semantics") from exc
    if drive_type != _DRIVE_FIXED:
        raise _error(
            "UNSUPPORTED_STORAGE",
            "network, removable, and unknown drive semantics are unsupported",
        )


def _assert_no_reparse_components(path: Path, *, allow_missing_leaf: bool = False) -> None:
    current = Path(path.anchor)
    parts = path.parts[1:]
    for index, part in enumerate(parts):
        current = current / part
        try:
            details = current.lstat()
        except FileNotFoundError:
            if allow_missing_leaf and index == len(parts) - 1:
                return
            raise _error("LOCAL_PATH_MISSING", "a required local path component is missing")
        except OSError as exc:
            raise _error("LOCAL_IO_ERROR", "cannot inspect a local path component") from exc
        if _is_reparse_point(details):
            raise _error("UNSAFE_PATH", "reparse-point and symbolic-link paths are unsupported")


def _path_identity(details: os.stat_result) -> tuple[int, int, int, int]:
    return (
        details.st_dev,
        details.st_ino,
        stat.S_IFMT(details.st_mode),
        details.st_nlink,
    )


def _directory_handle_information(handle: int) -> tuple[tuple[int, int], int]:
    if os.name != "nt":
        raise _error("OUTPUT_PARENT_BINDING_UNAVAILABLE",
                     "native Windows directory-handle binding is unavailable")
    try:
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        get_information = kernel32.GetFileInformationByHandle
        get_information.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(_WindowsFileInformation),
        ]
        get_information.restype = ctypes.c_int
        close_handle = kernel32.CloseHandle
        close_handle.argtypes = [ctypes.c_void_p]
        close_handle.restype = ctypes.c_int
        details = _WindowsFileInformation()
        if not get_information(ctypes.c_void_p(handle), ctypes.byref(details)):
            raise OSError(ctypes.get_last_error(), "GetFileInformationByHandle failed")
        file_id = (details.file_index_high << 32) | details.file_index_low
        return (details.volume_serial, file_id), details.attributes
    except (AttributeError, OSError) as exc:
        raise _error("OUTPUT_PARENT_BINDING_UNAVAILABLE",
                     "cannot verify native output-directory handle identity") from exc


def _close_directory_handle(handle: int) -> None:
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    close_handle = kernel32.CloseHandle
    close_handle.argtypes = [ctypes.c_void_p]
    close_handle.restype = ctypes.c_int
    if not close_handle(ctypes.c_void_p(handle)):
        raise _error("OUTPUT_PARENT_BINDING_RELEASE_FAILED",
                     "cannot release a native output-directory handle")


def _open_pinned_directory_handle(path: Path) -> tuple[int, tuple[int, int]]:
    if os.name != "nt":
        raise _error(
            "OUTPUT_PARENT_BINDING_UNAVAILABLE",
            "summary output requires native Windows directory-handle binding",
        )
    try:
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        create_file = kernel32.CreateFileW
        create_file.argtypes = [
            ctypes.c_wchar_p,
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.c_void_p,
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.c_void_p,
        ]
        create_file.restype = ctypes.c_void_p
        handle = create_file(
            str(path),
            _FILE_READ_ATTRIBUTES | _FILE_TRAVERSE,
            _FILE_SHARE_READ | _FILE_SHARE_WRITE,  # deliberately omit FILE_SHARE_DELETE
            None,
            _OPEN_EXISTING,
            _FILE_FLAG_BACKUP_SEMANTICS | _FILE_FLAG_OPEN_REPARSE_POINT,
            None,
        )
    except (AttributeError, OSError) as exc:
        raise _error(
            "OUTPUT_PARENT_BINDING_UNAVAILABLE",
            "cannot open the output directory without allowing rename/reparse replacement",
        ) from exc
    invalid_handle = ctypes.c_void_p(-1).value
    if handle is None or handle == invalid_handle:
        raise _error(
            "OUTPUT_PARENT_BINDING_UNAVAILABLE",
            "cannot pin the explicit output directory against replacement",
        )
    value = int(handle)
    try:
        identity, attributes = _directory_handle_information(value)
        if attributes & _FILE_ATTRIBUTE_REPARSE_POINT:
            raise _error("UNSAFE_PATH", "output parent is a reparse point")
        if not attributes & _FILE_ATTRIBUTE_DIRECTORY:
            raise _error("UNSAFE_PATH", "output parent is not an ordinary directory")
        return value, identity
    except BaseException:
        _close_directory_handle(value)
        raise


@dataclass
class _PinnedDirectoryChain:
    paths: tuple[Path, ...]
    handles: tuple[int, ...]
    identities: tuple[tuple[int, int], ...]

    def verify(self) -> None:
        for path, handle, expected in zip(self.paths, self.handles, self.identities):
            identity, attributes = _directory_handle_information(handle)
            if (identity != expected
                    or attributes & _FILE_ATTRIBUTE_REPARSE_POINT
                    or not attributes & _FILE_ATTRIBUTE_DIRECTORY):
                raise _error(
                    "OUTPUT_PARENT_CHANGED",
                    "a pinned output-directory handle changed identity or type",
                )
            probe, probe_identity = _open_pinned_directory_handle(path)
            try:
                if probe_identity != expected:
                    raise _error(
                        "OUTPUT_PARENT_CHANGED",
                        "explicit output path no longer resolves to the pinned directory",
                    )
            finally:
                _close_directory_handle(probe)


def _create_exclusive_output(
    parent: _PinnedDirectoryChain,
    file_name: str,
) -> int:
    """Create relative to the pinned directory handle; never re-resolve a parent path."""
    if os.name != "nt" or msvcrt is None:
        raise _error(
            "OUTPUT_PARENT_BINDING_UNAVAILABLE",
            "handle-relative exclusive output creation is unsupported on this host",
        )
    if (not file_name or file_name in (".", "..")
            or Path(file_name).name != file_name
            or "/" in file_name or "\\" in file_name):
        raise _error("INVALID_OUTPUT_PATH", "summary output must be one file name")

    filename_buffer = ctypes.create_unicode_buffer(file_name)
    filename_bytes = len(file_name.encode("utf-16-le"))
    unicode_name = _WindowsUnicodeString(
        filename_bytes,
        filename_bytes + ctypes.sizeof(ctypes.c_wchar),
        ctypes.cast(filename_buffer, ctypes.c_void_p),
    )
    attributes = _WindowsObjectAttributes(
        ctypes.sizeof(_WindowsObjectAttributes),
        ctypes.c_void_p(parent.handles[-1]),
        ctypes.pointer(unicode_name),
        0x0040 | 0x1000,  # OBJ_CASE_INSENSITIVE | OBJ_DONT_REPARSE
        None,
        None,
    )
    io_status = _WindowsIoStatusBlock()
    file_handle = ctypes.c_void_p()
    try:
        ntdll = ctypes.WinDLL("ntdll", use_last_error=True)
        create_file = ntdll.NtCreateFile
        create_file.argtypes = [
            ctypes.POINTER(ctypes.c_void_p),
            ctypes.c_uint32,
            ctypes.POINTER(_WindowsObjectAttributes),
            ctypes.POINTER(_WindowsIoStatusBlock),
            ctypes.c_void_p,
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.c_void_p,
            ctypes.c_uint32,
        ]
        create_file.restype = ctypes.c_long
        status = create_file(
            ctypes.byref(file_handle),
            0x0012019F,  # FILE_GENERIC_READ | FILE_GENERIC_WRITE
            ctypes.byref(attributes),
            ctypes.byref(io_status),
            None,
            0x0080,  # FILE_ATTRIBUTE_NORMAL
            _FILE_SHARE_READ | _FILE_SHARE_WRITE,
            2,  # FILE_CREATE: fail if the selected directory already has the name
            0x00000040 | 0x00000020,  # FILE_NON_DIRECTORY_FILE | FILE_SYNCHRONOUS_IO_NONALERT
            None,
            0,
        )
    except (AttributeError, OSError) as exc:
        raise _error(
            "OUTPUT_PARENT_BINDING_UNAVAILABLE",
            "native handle-relative summary creation is unavailable",
        ) from exc

    unsigned_status = int(status) & 0xFFFFFFFF
    if status < 0:
        if unsigned_status == 0xC0000035:  # STATUS_OBJECT_NAME_COLLISION
            raise _error("OUTPUT_EXISTS", "summary output must be a new, absent file")
        raise _error(
            "OUTPUT_CREATE_ERROR",
            f"native handle-relative summary creation failed with NTSTATUS 0x{unsigned_status:08X}",
        )
    if not file_handle.value:
        raise _error("OUTPUT_CREATE_ERROR", "native output creation returned no file handle")
    try:
        return msvcrt.open_osfhandle(
            int(file_handle.value),
            os.O_RDWR | getattr(os, "O_BINARY", 0),
        )
    except OSError as exc:
        ntdll.NtClose.argtypes = [ctypes.c_void_p]
        ntdll.NtClose.restype = ctypes.c_long
        ntdll.NtClose(file_handle)
        raise _error("OUTPUT_CREATE_ERROR", "cannot wrap the new native output handle") from exc


@contextmanager
def _pinned_directory_chain(path: str | os.PathLike[str]) -> Iterator[_PinnedDirectoryChain]:
    directory = Path(path)
    if not directory.is_absolute():
        raise _error("EXPLICIT_ABSOLUTE_PATH_REQUIRED",
                     "summary output parent must be explicitly absolute")
    _require_local_drive(directory)
    if not directory.is_dir():
        raise _error("LOCAL_PATH_MISSING", "summary output parent must already exist")
    _assert_no_reparse_components(directory)
    resolved = directory.resolve(strict=True)
    if _normalized_path(resolved) != _normalized_path(directory):
        raise _error("UNSAFE_PATH", "resolved output parent differs from the explicit path")

    paths = [Path(directory.anchor)]
    current = Path(directory.anchor)
    for part in directory.parts[1:]:
        current = current / part
        paths.append(current)

    handles: list[int] = []
    identities: list[tuple[int, int]] = []
    try:
        for component in paths:
            handle, identity = _open_pinned_directory_handle(component)
            handles.append(handle)
            identities.append(identity)
        binding = _PinnedDirectoryChain(tuple(paths), tuple(handles), tuple(identities))
        binding.verify()
        yield binding
    finally:
        for handle in reversed(handles):
            _close_directory_handle(handle)


def _assert_single_regular_file(path: Path, *, code: str) -> os.stat_result:
    try:
        details = path.lstat()
    except OSError as exc:
        raise _error("LOCAL_IO_ERROR", "cannot inspect the requested local file") from exc
    if _is_reparse_point(details) or not stat.S_ISREG(details.st_mode):
        raise _error(code, "the requested path must be a regular, non-reparse file")
    if details.st_nlink != 1:
        raise _error(code, "hard-linked files are unsupported to protect other owner paths")
    return details


def _template_path() -> Path:
    return Path(__file__).resolve().parents[2] / "_templates" / "reports" / "ai-interaction-log.csv"


def _is_template(path: Path) -> bool:
    return _normalized_path(path) == _normalized_path(_template_path())


def _validate_existing_log(value: str | os.PathLike[str]) -> Path:
    path = Path(value)
    if not path.is_absolute():
        raise _error("EXPLICIT_ABSOLUTE_PATH_REQUIRED", "log path must be explicitly absolute")
    _require_local_drive(path)
    try:
        if not path.parent.is_dir():
            raise _error("LOCAL_PATH_MISSING", "log parent must already exist")
        _assert_no_reparse_components(path)
        details = _assert_single_regular_file(path, code="UNSAFE_PATH")
        resolved = path.resolve(strict=True)
        if _normalized_path(resolved) != _normalized_path(path):
            raise _error("UNSAFE_PATH", "resolved log path differs from the explicit path")
    except LedgerError:
        raise
    except OSError as exc:
        raise _error("LOCAL_IO_ERROR", "cannot inspect the explicit log path") from exc
    if _is_template(path):
        raise _error(
            "TEMPLATE_NOT_LEDGER",
            "copy the blank reusable template to a new explicit local ledger path",
        )
    return path


def _validate_new_output(
    value: str | os.PathLike[str],
    *,
    source: Path,
    suffix: str,
) -> Path:
    path = Path(value)
    if not path.is_absolute():
        raise _error("EXPLICIT_ABSOLUTE_PATH_REQUIRED", "output path must be explicitly absolute")
    _require_local_drive(path)
    if path.suffix.lower() != suffix:
        raise _error("INVALID_OUTPUT_PATH", f"output must use the {suffix} suffix")
    if _normalized_path(path) == _normalized_path(source):
        raise _error("OUTPUT_IS_SOURCE", "summary output cannot be the source ledger")
    try:
        if not path.parent.is_dir():
            raise _error("LOCAL_PATH_MISSING", "output parent must already exist")
        _assert_no_reparse_components(path.parent)
        if path.exists() or path.is_symlink():
            raise _error("OUTPUT_EXISTS", "summary output must be a new, absent file")
        resolved_parent = path.parent.resolve(strict=True)
        if _normalized_path(resolved_parent) != _normalized_path(path.parent):
            raise _error("UNSAFE_PATH", "resolved output parent differs from the explicit path")
    except LedgerError:
        raise
    except OSError as exc:
        raise _error("LOCAL_IO_ERROR", "cannot inspect the explicit output path") from exc
    if _is_template(path):
        raise _error("UNSAFE_PATH", "the reusable CSV template is not a summary output")
    return path


def _lock_path(path: Path) -> Path:
    return path.with_name(path.name + ".lock")


def _open_lock_file(path: Path):
    lock_path = _lock_path(path)
    _assert_no_reparse_components(lock_path.parent)
    flags = os.O_RDWR | getattr(os, "O_BINARY", 0)
    try:
        try:
            descriptor = os.open(
                lock_path,
                flags | os.O_CREAT | os.O_EXCL,
                0o600,
            )
        except FileExistsError:
            _assert_no_reparse_components(lock_path)
            descriptor = os.open(lock_path, flags)
        details = os.fstat(descriptor)
        _assert_no_reparse_components(lock_path)
        path_details = _assert_single_regular_file(lock_path, code="INVALID_LOCK_FILE")
        if (not stat.S_ISREG(details.st_mode) or details.st_size != 0
                or details.st_nlink != 1
                or _path_identity(details) != _path_identity(path_details)):
            raise _error(
                "INVALID_LOCK_FILE",
                "the persistent lock file must be an empty, singly linked regular file",
            )
        return lock_path, descriptor, _path_identity(details)
    except LedgerError:
        if "descriptor" in locals():
            os.close(descriptor)
        raise
    except OSError as exc:
        if "descriptor" in locals():
            os.close(descriptor)
        raise _error("LOCK_FILE_ERROR", "cannot open the persistent sibling lock file") from exc


@contextmanager
def _file_lock(
    log_path: str | os.PathLike[str],
    *,
    timeout: float = 10.0,
) -> Iterator[None]:
    """Use a persistent Windows byte-range lock; never delete or recycle it."""
    path = _validate_existing_log(log_path)
    if (not isinstance(timeout, (int, float)) or not math.isfinite(timeout)
            or timeout < 0):
        raise _error("INVALID_LOCK_TIMEOUT", "lock timeout must be a non-negative number")
    if msvcrt is None:
        raise _error(
            "UNSUPPORTED_STORAGE",
            "this host has no supported Windows native byte-range lock primitive",
        )
    lock_path, descriptor, identity = _open_lock_file(path)
    stream = os.fdopen(descriptor, "r+b", buffering=0)
    locked = False
    deadline = time.monotonic() + float(timeout)
    try:
        while True:
            stream.seek(0)
            try:
                msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
                locked = True
                break
            except OSError as exc:
                if exc.errno not in _LOCK_CONTENTION_ERRNOS:
                    raise _error("LOCK_UNAVAILABLE", "native local byte-range locking failed") from exc
                if time.monotonic() >= deadline:
                    raise _error("LOCK_TIMEOUT", "timed out waiting for another local writer")
                time.sleep(min(0.05, max(0.0, deadline - time.monotonic())))

        current = _assert_single_regular_file(lock_path, code="INVALID_LOCK_FILE")
        handle_details = os.fstat(stream.fileno())
        if (handle_details.st_size != 0
                or _path_identity(handle_details) != identity
                or _path_identity(current) != identity):
            raise _error("LOCK_OWNER_BYTES_CHANGED", "persistent lock-file identity or bytes changed")
        yield
        current = _assert_single_regular_file(lock_path, code="INVALID_LOCK_FILE")
        handle_details = os.fstat(stream.fileno())
        if (handle_details.st_size != 0
                or _path_identity(handle_details) != identity
                or _path_identity(current) != identity):
            raise _error("LOCK_OWNER_BYTES_CHANGED", "persistent lock-file identity or bytes changed")
    except LedgerError:
        raise
    except OSError as exc:
        raise _error("LOCAL_IO_ERROR", "local file locking or I/O failed") from exc
    finally:
        if locked:
            try:
                stream.seek(0)
                msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
            except OSError as exc:
                stream.close()
                raise _error("LOCK_RELEASE_FAILED", "native byte-range lock release failed") from exc
        stream.close()


def _read_log_bytes(path: Path) -> bytes:
    with path.open("rb") as source:
        return source.read()


def _parse_record(row: list[str], line_number: int) -> InteractionRecord:
    if len(row) != len(CSV_HEADER):
        raise _error(
            "INVALID_LOG_ROW",
            f"existing CSV row at line {line_number} has an unexpected field count",
        )
    if row[0] != SCHEMA_VERSION:
        raise _error(
            "INCOMPATIBLE_LOG_VERSION",
            f"existing CSV row at line {line_number} uses an unsupported schema version",
        )
    try:
        return _validated_record(
            InteractionRecord(
                record_id=row[1],
                recorded_at=row[2],
                tool_name=row[3],
                tool_version=row[4],
                task_ref=row[5],
                object_ref=row[6],
                object_baseline=row[7],
                operation_summary=row[8],
                decision_ref=row[9] or None,
                usage_value=row[10] or None,
                usage_unit=row[11] or None,
                usage_currency=row[12] or None,
                evidence_ref=row[13] or None,
            )
        )
    except LedgerError as exc:
        raise _error(
            "INVALID_LOG_ROW",
            f"existing CSV row at line {line_number} violates the v1 record contract",
        ) from exc


def _parse_log(raw: bytes) -> list[InteractionRecord]:
    try:
        text = raw.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise _error("INVALID_LOG", "existing CSV is not valid UTF-8") from exc
    try:
        reader = csv.reader(io.StringIO(text, newline=""), strict=True)
        header = next(reader, None)
        if header != list(CSV_HEADER):
            raise _error(
                "INCOMPATIBLE_LOG_HEADER",
                "existing CSV header does not exactly match schema version 1",
            )
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
        SCHEMA_VERSION,
        record.record_id,
        record.recorded_at,
        record.tool_name,
        record.tool_version,
        record.task_ref,
        record.object_ref,
        record.object_baseline,
        record.operation_summary,
        record.decision_ref or "",
        record.usage_value or "",
        record.usage_unit or "",
        record.usage_currency or "",
        record.evidence_ref or "",
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


def _append_bytes(path: Path, original: bytes, suffix: bytes, identity: tuple[int, int, int, int]) -> None:
    current_identity = _path_identity(_assert_single_regular_file(path, code="UNSAFE_PATH"))
    if current_identity != identity or _read_log_bytes(path) != original:
        raise _error(
            "OWNER_BYTES_CHANGED",
            "ledger bytes or file identity changed after the validated snapshot; no append was attempted",
        )

    flags = os.O_RDWR | os.O_APPEND | getattr(os, "O_BINARY", 0)
    try:
        descriptor = os.open(path, flags)
    except OSError as exc:
        raise _error("LOCAL_IO_ERROR", "cannot open the validated ledger for append") from exc
    bytes_written = 0
    try:
        details = os.fstat(descriptor)
        if _path_identity(details) != identity:
            raise _error("OWNER_BYTES_CHANGED", "ledger file identity changed before append")
        if _read_descriptor(descriptor) != original:
            raise _error(
                "OWNER_BYTES_CHANGED",
                "ledger owner bytes changed before append; no bytes were written",
            )
        try:
            while bytes_written < len(suffix):
                written = os.write(descriptor, suffix[bytes_written:])
                if written <= 0:
                    raise OSError("zero-byte append")
                bytes_written += written
            os.fsync(descriptor)
        except OSError as exc:
            observed = _read_descriptor(descriptor)
            partial = max(0, len(observed) - len(original))
            raise LedgerError(
                "APPEND_IO_RECOVERY_REQUIRED",
                "append I/O failed; preserve the ledger and inspect its final CSV row before retrying",
                exit_code=2,
                recovery_required=partial > 0,
                recovery={
                    "original_bytes": len(original),
                    "observed_bytes": len(observed),
                    "observed_delta_bytes": partial,
                    "expected_append_bytes": len(suffix),
                },
            ) from exc

        observed = _read_descriptor(descriptor)
        details = os.fstat(descriptor)
        path_details = _assert_single_regular_file(path, code="UNSAFE_PATH")
        if (_path_identity(details) != identity
                or _path_identity(path_details) != identity
                or observed != original + suffix):
            raise LedgerError(
                "OWNER_BYTES_CHANGED",
                "ledger changed during append; preserve all bytes and inspect before retrying",
                exit_code=2,
                recovery_required=True,
                recovery={
                    "original_bytes": len(original),
                    "observed_bytes": len(observed),
                    "observed_delta_bytes": max(0, len(observed) - len(original)),
                    "expected_append_bytes": len(suffix),
                },
            )
    except LedgerError:
        raise
    except OSError as exc:
        raise _error("LOCAL_IO_ERROR", "ledger append failed before completion") from exc
    finally:
        os.close(descriptor)


def _snapshot_version(path: Path) -> tuple:
    details = _assert_single_regular_file(path, code="UNSAFE_PATH")
    resolved = path.resolve(strict=True)
    if _normalized_path(resolved) != _normalized_path(path):
        raise _error("UNSAFE_PATH", "resolved ledger path differs from the explicit path")
    return (
        _path_identity(details),
        details.st_size,
        getattr(details, "st_mtime_ns", int(details.st_mtime * 1_000_000_000)),
        getattr(details, "st_ctime_ns", int(details.st_ctime * 1_000_000_000)),
    )


def _read_validated(path: Path) -> tuple[bytes, list[InteractionRecord]]:
    """Read a stable source snapshot without creating a lock or other sidecar."""
    current = _validate_existing_log(path)
    before = _snapshot_version(current)
    first = _read_log_bytes(current)
    middle = _snapshot_version(current)
    second = _read_log_bytes(current)
    after = _snapshot_version(current)
    if (before != middle or middle != after or first != second
            or len(second) != after[1]):
        raise _error(
            "OWNER_BYTES_CHANGED",
            "ledger bytes or file identity changed while the read snapshot was formed",
        )
    return second, _parse_log(second)


def append_record(
    log_path: str | os.PathLike[str],
    record: InteractionRecord,
    *,
    attest_local_storage: bool = False,
    lock_timeout: float = 10.0,
) -> AppendResult:
    """Append one exact record, or return a no-change result for an identical replay."""
    _require_write_attestation(attest_local_storage)
    path = _validate_existing_log(log_path)
    supplied = _validated_record(record)
    with _file_lock(path, timeout=lock_timeout):
        path = _validate_existing_log(path)
        details = _assert_single_regular_file(path, code="UNSAFE_PATH")
        identity = _path_identity(details)
        original = _read_log_bytes(path)
        if _path_identity(_assert_single_regular_file(path, code="UNSAFE_PATH")) != identity:
            raise _error("OWNER_BYTES_CHANGED", "ledger file identity changed while it was read")
        records = _parse_log(original)
        for existing in records:
            if existing.record_id == supplied.record_id:
                if existing == supplied:
                    return AppendResult(
                        "duplicate",
                        supplied.record_id,
                        len(records),
                        hashlib.sha256(original).hexdigest(),
                    )
                raise _error(
                    "RECORD_ID_CONFLICT",
                    "record ID already exists with different caller-supplied values",
                    exit_code=1,
                )

        row = _csv_row_bytes(supplied)
        separator = b"" if original.endswith((b"\n", b"\r")) else b"\r\n"
        suffix = separator + row
        _append_bytes(path, original, suffix, identity)
        return AppendResult(
            "appended",
            supplied.record_id,
            len(records) + 1,
            hashlib.sha256(original + suffix).hexdigest(),
        )


def _emit_error(error: LedgerError) -> None:
    payload = {
        "status": "error",
        "code": error.code,
        "message": str(error),
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
        "--attest-local-storage",
        action="store_true",
        help="caller assertion that the selected ledger is single-host local and not network/cloud-sync storage",
    )
    parser.add_argument("--lock-timeout", type=float, default=10.0)
    args = parser.parse_args(argv)

    record = InteractionRecord(
        record_id=args.record_id,
        recorded_at=args.recorded_at,
        tool_name=args.tool_name,
        tool_version=args.tool_version,
        task_ref=args.task_ref,
        object_ref=args.object_ref,
        object_baseline=args.object_baseline,
        operation_summary=args.operation_summary,
        decision_ref=args.decision_ref,
        usage_value=args.usage_value,
        usage_unit=args.usage_unit,
        usage_currency=args.usage_currency,
        evidence_ref=args.evidence_ref,
    )
    try:
        result = append_record(
            args.log,
            record,
            attest_local_storage=args.attest_local_storage,
            lock_timeout=args.lock_timeout,
        )
    except LedgerError as exc:
        _emit_error(exc)
        return exc.exit_code
    payload = {
        "status": result.status,
        "record_id": result.record_id,
        "record_count": result.record_count,
        "source_sha256": result.source_sha256,
    }
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
