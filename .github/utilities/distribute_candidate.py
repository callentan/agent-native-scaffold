"""Create and verify a local candidate from the exact file-level manifest.

This maker-side utility is deliberately not part of the downstream candidate.
It copies no directories, initializes no repository, and performs no install or
publication operation. File access uses native handle-relative no-follow
operations and binds identity through each read/write; unsupported host
operations fail closed. This is not an OS-wide sandbox.
"""

from __future__ import annotations

import argparse
import ctypes
import errno
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import stat
import struct
import subprocess
import sys
from typing import Any


MANIFEST_PATH = "docs/distribution-manifest.json"
_REPARSE = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)


class CandidateError(ValueError):
    def __init__(self, code: str, message: str, *, path: str | None = None,
                 status: str = "input-error", exit_code: int = 2):
        super().__init__(message)
        self.code = code
        self.path = path
        self.status = status
        self.exit_code = exit_code


class _WindowsHandleApi:
    """Small local binding for handle-relative, no-reparse Windows file access."""

    _OBJ_CASE_INSENSITIVE = 0x40
    _OBJ_DONT_REPARSE = 0x1000
    _FILE_LIST_DIRECTORY = 0x0001
    _FILE_READ_DATA = 0x0001
    _FILE_WRITE_DATA = 0x0002
    _FILE_READ_ATTRIBUTES = 0x0080
    _SYNCHRONIZE = 0x00100000
    _FILE_SHARE_READ = 0x0001
    _FILE_SHARE_WRITE = 0x0002
    _FILE_SHARE_DELETE = 0x0004
    _FILE_OPEN = 1
    _FILE_CREATE = 2
    _FILE_DIRECTORY_FILE = 0x0001
    _FILE_NON_DIRECTORY_FILE = 0x0040
    _FILE_SYNCHRONOUS_IO_NONALERT = 0x0020
    _FILE_OPEN_REPARSE_POINT = 0x00200000
    _FILE_WRITE_THROUGH = 0x00000002
    _FILE_ATTRIBUTE_NORMAL = 0x0080
    _FILE_ATTRIBUTE_DIRECTORY = 0x0010
    _FILE_ATTRIBUTE_REPARSE_POINT = 0x0400
    _FILE_ATTRIBUTE_TAG_INFO = 9
    _FILE_NAMES_INFORMATION = 12
    _STATUS_NO_MORE_FILES = 0x80000006
    _ERROR_OBJECT_NAME_NOT_FOUND = 0xC0000034
    _ERROR_OBJECT_PATH_NOT_FOUND = 0xC000003A
    _ERROR_OBJECT_NAME_COLLISION = 0xC0000035
    _FILE_BEGIN = 0
    _CHUNK = 1024 * 1024

    def __init__(self) -> None:
        from ctypes import wintypes

        class UnicodeString(ctypes.Structure):
            _fields_ = [
                ("Length", wintypes.USHORT),
                ("MaximumLength", wintypes.USHORT),
                ("Buffer", wintypes.LPWSTR),
            ]

        class ObjectAttributes(ctypes.Structure):
            _fields_ = [
                ("Length", wintypes.ULONG),
                ("RootDirectory", wintypes.HANDLE),
                ("ObjectName", ctypes.POINTER(UnicodeString)),
                ("Attributes", wintypes.ULONG),
                ("SecurityDescriptor", ctypes.c_void_p),
                ("SecurityQualityOfService", ctypes.c_void_p),
            ]

        class IoStatusBlock(ctypes.Structure):
            _fields_ = [("Status", ctypes.c_long), ("Information", ctypes.c_size_t)]

        class FileTime(ctypes.Structure):
            _fields_ = [("LowDateTime", wintypes.DWORD), ("HighDateTime", wintypes.DWORD)]

        class ByHandleInformation(ctypes.Structure):
            _fields_ = [
                ("FileAttributes", wintypes.DWORD),
                ("CreationTime", FileTime),
                ("LastAccessTime", FileTime),
                ("LastWriteTime", FileTime),
                ("VolumeSerialNumber", wintypes.DWORD),
                ("FileSizeHigh", wintypes.DWORD),
                ("FileSizeLow", wintypes.DWORD),
                ("NumberOfLinks", wintypes.DWORD),
                ("FileIndexHigh", wintypes.DWORD),
                ("FileIndexLow", wintypes.DWORD),
            ]

        class AttributeTagInformation(ctypes.Structure):
            _fields_ = [("FileAttributes", wintypes.DWORD), ("ReparseTag", wintypes.DWORD)]

        self.wintypes = wintypes
        self.UnicodeString = UnicodeString
        self.ObjectAttributes = ObjectAttributes
        self.IoStatusBlock = IoStatusBlock
        self.ByHandleInformation = ByHandleInformation
        self.AttributeTagInformation = AttributeTagInformation
        self.kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        self.ntdll = ctypes.WinDLL("ntdll")
        self.CreateFileW = self.kernel.CreateFileW
        self.CreateFileW.restype = wintypes.HANDLE
        self.CreateFileW.argtypes = [
            wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, wintypes.LPVOID,
            wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE,
        ]
        self.CloseHandle = self.kernel.CloseHandle
        self.CloseHandle.argtypes = [wintypes.HANDLE]
        self.CloseHandle.restype = wintypes.BOOL
        self.GetFileInformationByHandle = self.kernel.GetFileInformationByHandle
        self.GetFileInformationByHandle.argtypes = [
            wintypes.HANDLE, ctypes.POINTER(ByHandleInformation),
        ]
        self.GetFileInformationByHandle.restype = wintypes.BOOL
        self.GetFileInformationByHandleEx = self.kernel.GetFileInformationByHandleEx
        self.GetFileInformationByHandleEx.argtypes = [
            wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD,
        ]
        self.GetFileInformationByHandleEx.restype = wintypes.BOOL
        self.GetFileType = self.kernel.GetFileType
        self.GetFileType.argtypes = [wintypes.HANDLE]
        self.GetFileType.restype = wintypes.DWORD
        self.ReadFile = self.kernel.ReadFile
        self.ReadFile.argtypes = [
            wintypes.HANDLE, ctypes.c_void_p, wintypes.DWORD,
            ctypes.POINTER(wintypes.DWORD), ctypes.c_void_p,
        ]
        self.ReadFile.restype = wintypes.BOOL
        self.WriteFile = self.kernel.WriteFile
        self.WriteFile.argtypes = [
            wintypes.HANDLE, ctypes.c_void_p, wintypes.DWORD,
            ctypes.POINTER(wintypes.DWORD), ctypes.c_void_p,
        ]
        self.WriteFile.restype = wintypes.BOOL
        self.SetFilePointerEx = self.kernel.SetFilePointerEx
        self.SetFilePointerEx.argtypes = [
            wintypes.HANDLE, ctypes.c_longlong, ctypes.POINTER(ctypes.c_longlong),
            wintypes.DWORD,
        ]
        self.SetFilePointerEx.restype = wintypes.BOOL
        self.FlushFileBuffers = self.kernel.FlushFileBuffers
        self.FlushFileBuffers.argtypes = [wintypes.HANDLE]
        self.FlushFileBuffers.restype = wintypes.BOOL
        self.NtCreateFile = self.ntdll.NtCreateFile
        self.NtCreateFile.restype = ctypes.c_long
        self.NtCreateFile.argtypes = [
            ctypes.POINTER(wintypes.HANDLE), wintypes.DWORD,
            ctypes.POINTER(ObjectAttributes), ctypes.POINTER(IoStatusBlock),
            ctypes.c_void_p, wintypes.DWORD, wintypes.DWORD, wintypes.DWORD,
            wintypes.DWORD, ctypes.c_void_p, wintypes.DWORD,
        ]
        self.NtQueryDirectoryFile = self.ntdll.NtQueryDirectoryFile
        self.NtQueryDirectoryFile.restype = ctypes.c_long
        self.NtQueryDirectoryFile.argtypes = [
            wintypes.HANDLE, wintypes.HANDLE, ctypes.c_void_p, ctypes.c_void_p,
            ctypes.POINTER(IoStatusBlock), ctypes.c_void_p, wintypes.DWORD,
            wintypes.DWORD, wintypes.BOOLEAN, ctypes.POINTER(UnicodeString),
            wintypes.BOOLEAN,
        ]
        self.RtlNtStatusToDosError = self.ntdll.RtlNtStatusToDosError
        self.RtlNtStatusToDosError.argtypes = [ctypes.c_long]
        self.RtlNtStatusToDosError.restype = wintypes.ULONG

    @staticmethod
    def _valid_component(name: str) -> None:
        if not name or name in (".", "..") or any(character in name for character in ("/", "\\", ":")):
            raise CandidateError("UNSAFE_PATH", "A handle-relative path component is invalid")

    @staticmethod
    def _handle_value(handle: Any) -> int:
        return ctypes.cast(handle, ctypes.c_void_p).value or 0

    def close(self, handle: Any) -> None:
        if handle and not self.CloseHandle(handle):
            raise OSError(ctypes.get_last_error(), "A local file handle could not be closed")

    def _nt_open(self, parent: Any, name: str, *, desired: int, share: int,
                 disposition: int, options: int, attributes: int = 0) -> Any:
        self._valid_component(name)
        encoded = name.encode("utf-16-le")
        if len(encoded) > 0xFFFC:
            raise CandidateError("UNSAFE_PATH", "A handle-relative path component is too long")
        buffer = ctypes.create_unicode_buffer(name)
        unicode_name = self.UnicodeString(
            len(encoded), len(encoded) + 2, ctypes.cast(buffer, self.wintypes.LPWSTR),
        )
        object_attributes = self.ObjectAttributes(
            ctypes.sizeof(self.ObjectAttributes), parent, ctypes.pointer(unicode_name),
            self._OBJ_CASE_INSENSITIVE | self._OBJ_DONT_REPARSE, None, None,
        )
        io_status = self.IoStatusBlock()
        handle = self.wintypes.HANDLE()
        status = self.NtCreateFile(
            ctypes.byref(handle), desired, ctypes.byref(object_attributes),
            ctypes.byref(io_status), None, attributes, share, disposition, options, None, 0,
        )
        if status < 0:
            unsigned = status & 0xFFFFFFFF
            if unsigned in (self._ERROR_OBJECT_NAME_NOT_FOUND, self._ERROR_OBJECT_PATH_NOT_FOUND):
                code = "PATH_NOT_FOUND"
            elif unsigned == self._ERROR_OBJECT_NAME_COLLISION:
                code = "OUTPUT_CONFLICT"
            elif unsigned in (0xC000050B, 0x8000002D):
                code = "UNSAFE_PATH"
            else:
                code = "SAFE_HANDLE_IO_ERROR"
            winerror = self.RtlNtStatusToDosError(status)
            raise CandidateError(
                code, f"Handle-relative access was refused (Windows error {winerror})",
                status="conflict" if code == "OUTPUT_CONFLICT" else "input-error",
                exit_code=1 if code == "OUTPUT_CONFLICT" else 2,
            )
        return handle

    def open_volume_root(self, drive: str) -> Any:
        volume_root = drive + "\\"
        handle = self.CreateFileW(
            volume_root,
            self._FILE_LIST_DIRECTORY | self._FILE_READ_ATTRIBUTES | self._SYNCHRONIZE,
            self._FILE_SHARE_READ | self._FILE_SHARE_WRITE | self._FILE_SHARE_DELETE,
            None, 3, 0x02000000 | self._FILE_OPEN_REPARSE_POINT, None,
        )
        if self._handle_value(handle) == self.wintypes.HANDLE(-1).value:
            raise CandidateError("SAFE_FILESYSTEM_UNAVAILABLE",
                                 "The volume root cannot be opened by a stable Windows handle")
        return handle

    def open_child(self, parent: Any, name: str) -> Any:
        return self._nt_open(
            parent, name, desired=self._FILE_READ_DATA | self._FILE_READ_ATTRIBUTES | self._SYNCHRONIZE,
            share=self._FILE_SHARE_READ | self._FILE_SHARE_WRITE,
            disposition=self._FILE_OPEN,
            options=self._FILE_SYNCHRONOUS_IO_NONALERT | self._FILE_OPEN_REPARSE_POINT,
        )

    def create_child_directory(self, parent: Any, name: str) -> Any:
        return self._nt_open(
            parent, name, desired=self._FILE_READ_ATTRIBUTES | self._FILE_LIST_DIRECTORY | self._SYNCHRONIZE,
            share=self._FILE_SHARE_READ | self._FILE_SHARE_WRITE,
            disposition=self._FILE_CREATE,
            options=self._FILE_DIRECTORY_FILE | self._FILE_SYNCHRONOUS_IO_NONALERT
            | self._FILE_OPEN_REPARSE_POINT,
            attributes=self._FILE_ATTRIBUTE_NORMAL,
        )

    def create_child_file(self, parent: Any, name: str) -> Any:
        return self._nt_open(
            parent, name,
            desired=self._FILE_READ_DATA | self._FILE_WRITE_DATA | self._FILE_READ_ATTRIBUTES
            | self._SYNCHRONIZE,
            share=self._FILE_SHARE_READ,
            disposition=self._FILE_CREATE,
            options=self._FILE_NON_DIRECTORY_FILE | self._FILE_SYNCHRONOUS_IO_NONALERT
            | self._FILE_OPEN_REPARSE_POINT | self._FILE_WRITE_THROUGH,
            attributes=self._FILE_ATTRIBUTE_NORMAL,
        )

    def information(self, handle: Any) -> dict[str, Any]:
        info = self.ByHandleInformation()
        if not self.GetFileInformationByHandle(handle, ctypes.byref(info)):
            raise CandidateError("SAFE_HANDLE_IO_ERROR", "The opened file identity cannot be queried")
        tag = self.AttributeTagInformation()
        if not self.GetFileInformationByHandleEx(
            handle, self._FILE_ATTRIBUTE_TAG_INFO, ctypes.byref(tag), ctypes.sizeof(tag),
        ):
            raise CandidateError("SAFE_HANDLE_IO_ERROR", "The opened file attributes cannot be queried")
        return {
            "attributes": int(tag.FileAttributes),
            "links": int(info.NumberOfLinks),
            "size": (int(info.FileSizeHigh) << 32) | int(info.FileSizeLow),
            "identity": (int(info.VolumeSerialNumber), int(info.FileIndexHigh), int(info.FileIndexLow)),
            "last_write": (int(info.LastWriteTime.HighDateTime), int(info.LastWriteTime.LowDateTime)),
            "disk_file": self.GetFileType(handle) == 1,
        }

    def read_all(self, handle: Any) -> bytes:
        chunks = []
        while True:
            buffer = ctypes.create_string_buffer(self._CHUNK)
            count = self.wintypes.DWORD()
            if not self.ReadFile(handle, buffer, self._CHUNK, ctypes.byref(count), None):
                raise CandidateError("SAFE_HANDLE_IO_ERROR", "A file could not be read through its pinned handle")
            if count.value == 0:
                return b"".join(chunks)
            chunks.append(buffer.raw[:count.value])

    def write_and_readback(self, handle: Any, raw: bytes) -> bytes:
        offset = 0
        while offset < len(raw):
            chunk = raw[offset:offset + self._CHUNK]
            buffer = ctypes.create_string_buffer(chunk)
            count = self.wintypes.DWORD()
            if not self.WriteFile(handle, buffer, len(chunk), ctypes.byref(count), None) or count.value != len(chunk):
                raise CandidateError("SAFE_HANDLE_IO_ERROR", "A candidate file could not be written through its pinned handle")
            offset += count.value
        if not self.FlushFileBuffers(handle):
            raise CandidateError("SAFE_HANDLE_IO_ERROR", "A candidate file could not be flushed through its pinned handle")
        position = ctypes.c_longlong()
        if not self.SetFilePointerEx(handle, 0, ctypes.byref(position), self._FILE_BEGIN):
            raise CandidateError("SAFE_HANDLE_IO_ERROR", "The candidate file handle could not be rewound")
        return self.read_all(handle)

    def list_names(self, handle: Any) -> list[str]:
        names = []
        buffer = ctypes.create_string_buffer(65536)
        io_status = self.IoStatusBlock()
        restart = True
        while True:
            status = self.NtQueryDirectoryFile(
                handle, None, None, None, ctypes.byref(io_status), buffer, len(buffer),
                self._FILE_NAMES_INFORMATION, False, None, restart,
            )
            restart = False
            if (status & 0xFFFFFFFF) == self._STATUS_NO_MORE_FILES:
                return names
            if status != 0:
                winerror = self.RtlNtStatusToDosError(status)
                raise CandidateError(
                    "SAFE_HANDLE_IO_ERROR",
                    f"A directory cannot be enumerated by its pinned handle (Windows error {winerror})",
                )
            raw = buffer.raw
            offset = 0
            while True:
                next_offset, _, name_length = struct.unpack_from("<III", raw, offset)
                start = offset + 12
                names.append(raw[start:start + name_length].decode("utf-16-le"))
                if next_offset == 0:
                    break
                offset += next_offset


class _SafeDirectory:
    """Pinned directory identity; child operations never resolve through a path alias."""

    def __init__(self, path: Path, handle: Any, identity: tuple[int, ...], *, api: Any = None):
        self.path = path
        self.handle = handle
        self.identity = identity
        self.api = api
        self.closed = False

    @staticmethod
    def _safe_component(name: str) -> None:
        if not name or name in (".", "..") or any(character in name for character in ("/", "\\", ":")):
            raise CandidateError("UNSAFE_PATH", "A handle-relative path component is invalid")

    @classmethod
    def open_absolute(cls, path: Path) -> "_SafeDirectory":
        if not path.is_absolute() or ".." in path.parts:
            raise CandidateError("UNSAFE_PATH", "A stable directory handle requires an absolute non-traversing path")
        if os.name == "nt":
            return cls._open_windows(path)
        return cls._open_posix(path)

    @classmethod
    def _open_windows(cls, path: Path) -> "_SafeDirectory":
        api = _WindowsHandleApi()
        drive = path.drive
        if not drive or drive.startswith("\\\\"):
            raise CandidateError("SAFE_FILESYSTEM_UNAVAILABLE",
                                 "Only local drive roots support the required handle-relative Windows access")
        current_handle = api.open_volume_root(drive)
        try:
            for component in path.parts[1:]:
                cls._safe_component(component)
                child_handle = api.open_child(current_handle, component)
                try:
                    info = api.information(child_handle)
                    if info["attributes"] & api._FILE_ATTRIBUTE_REPARSE_POINT:
                        raise CandidateError("UNSAFE_PATH", "Reparse points are not allowed in an authorized directory")
                    if not info["attributes"] & api._FILE_ATTRIBUTE_DIRECTORY:
                        raise CandidateError("INVALID_DIRECTORY", "A declared directory component is not a directory")
                except BaseException:
                    api.close(child_handle)
                    raise
                api.close(current_handle)
                current_handle = child_handle
            info = api.information(current_handle)
            if info["attributes"] & api._FILE_ATTRIBUTE_REPARSE_POINT:
                raise CandidateError("UNSAFE_PATH", "Authorized directory is a reparse point")
            return cls(path, current_handle, info["identity"], api=api)
        except BaseException:
            if current_handle:
                api.close(current_handle)
            raise

    @classmethod
    def _open_posix(cls, path: Path) -> "_SafeDirectory":
        required = (os.open in os.supports_dir_fd and os.stat in os.supports_dir_fd
                    and os.listdir in os.supports_fd)
        flags = ("O_DIRECTORY", "O_NOFOLLOW")
        if not required or any(not hasattr(os, flag) for flag in flags):
            raise CandidateError("SAFE_FILESYSTEM_UNAVAILABLE",
                                 "This host lacks stable no-follow directory-handle operations")
        open_flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | getattr(os, "O_CLOEXEC", 0)
        current = None
        try:
            current = os.open(path.anchor, open_flags)
            for component in path.parts[1:]:
                cls._safe_component(component)
                child = os.open(component, open_flags, dir_fd=current)
                info = os.fstat(child)
                if not stat.S_ISDIR(info.st_mode):
                    os.close(child)
                    raise CandidateError("INVALID_DIRECTORY", "A declared directory component is not a directory")
                os.close(current)
                current = child
            info = os.fstat(current)
            opened = cls(path, current, (int(info.st_dev), int(info.st_ino)))
            current = None
            return opened
        except CandidateError:
            raise
        except OSError as error:
            code = "UNSAFE_PATH" if error.errno in (errno.ELOOP, errno.ENOTDIR) else "SAFE_FILESYSTEM_UNAVAILABLE"
            raise CandidateError(code, "An authorized directory cannot be opened without following links") from error
        finally:
            if current is not None:
                os.close(current)

    def close(self) -> None:
        if self.closed:
            return
        self.closed = True
        if self.api is not None:
            self.api.close(self.handle)
        else:
            os.close(self.handle)

    def _open_child_directory(self, name: str, *, create: bool = False) -> "_SafeDirectory":
        self._safe_component(name)
        child_path = self.path / name
        if self.api is not None:
            try:
                handle = self.api.open_child(self.handle, name)
            except CandidateError as error:
                if create and error.code == "PATH_NOT_FOUND":
                    try:
                        handle = self.api.create_child_directory(self.handle, name)
                    except CandidateError as create_error:
                        if create_error.code != "OUTPUT_CONFLICT":
                            raise
                        handle = self.api.open_child(self.handle, name)
                else:
                    raise
            try:
                info = self.api.information(handle)
                if info["attributes"] & self.api._FILE_ATTRIBUTE_REPARSE_POINT:
                    raise CandidateError("UNSAFE_PATH", "Reparse points are not allowed in candidate paths")
                if not info["attributes"] & self.api._FILE_ATTRIBUTE_DIRECTORY:
                    raise CandidateError("INVALID_DIRECTORY", "A path component is not a directory")
                return _SafeDirectory(child_path, handle, info["identity"], api=self.api)
            except BaseException:
                self.api.close(handle)
                raise
        open_flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | getattr(os, "O_CLOEXEC", 0)
        try:
            try:
                handle = os.open(name, open_flags, dir_fd=self.handle)
            except FileNotFoundError:
                if not create:
                    raise CandidateError("PATH_NOT_FOUND", "A handle-relative directory does not exist")
                try:
                    os.mkdir(name, mode=0o700, dir_fd=self.handle)
                except FileExistsError:
                    pass
                handle = os.open(name, open_flags, dir_fd=self.handle)
            info = os.fstat(handle)
            if not stat.S_ISDIR(info.st_mode):
                os.close(handle)
                raise CandidateError("INVALID_DIRECTORY", "A path component is not a directory")
            return _SafeDirectory(child_path, handle, (int(info.st_dev), int(info.st_ino)))
        except CandidateError:
            raise
        except OSError as error:
            code = "UNSAFE_PATH" if error.errno in (errno.ELOOP, errno.ENOTDIR) else "SAFE_HANDLE_IO_ERROR"
            raise CandidateError(code, "A directory component could not be opened without following links") from error

    def _create_new_child_directory(self, name: str) -> "_SafeDirectory":
        self._safe_component(name)
        child_path = self.path / name
        if self.api is not None:
            handle = self.api.create_child_directory(self.handle, name)
            try:
                info = self.api.information(handle)
                if (info["attributes"] & self.api._FILE_ATTRIBUTE_REPARSE_POINT
                        or not info["attributes"] & self.api._FILE_ATTRIBUTE_DIRECTORY):
                    raise CandidateError("UNSAFE_PATH", "A new output directory is not a plain directory")
                return _SafeDirectory(child_path, handle, info["identity"], api=self.api)
            except BaseException:
                self.api.close(handle)
                raise
        try:
            os.mkdir(name, mode=0o700, dir_fd=self.handle)
            handle = os.open(
                name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | getattr(os, "O_CLOEXEC", 0),
                dir_fd=self.handle,
            )
        except FileExistsError as error:
            raise CandidateError("OUTPUT_CONFLICT", "A new output directory already exists",
                                 status="conflict", exit_code=1) from error
        except OSError as error:
            code = "UNSAFE_PATH" if error.errno in (errno.ELOOP, errno.ENOTDIR) else "SAFE_HANDLE_IO_ERROR"
            raise CandidateError(code, "A new output directory could not be created safely") from error
        info = os.fstat(handle)
        return _SafeDirectory(child_path, handle, (int(info.st_dev), int(info.st_ino)))

    def _open_directory_parts(self, parts: tuple[str, ...], *, create: bool = False) -> "_SafeDirectory":
        current = self
        owned = False
        try:
            for component in parts:
                child = current._open_child_directory(component, create=create)
                previous = current
                previous_owned = owned
                current = child
                owned = True
                if previous_owned:
                    previous.close()
            return current
        except BaseException:
            if owned:
                current.close()
            raise

    def ensure_directories(self, parts: tuple[str, ...]) -> None:
        directory = self._open_directory_parts(parts, create=True)
        if directory is not self:
            directory.close()

    def create_directory(self, parts: tuple[str, ...]) -> "_SafeDirectory":
        if not parts:
            raise CandidateError("UNSAFE_PATH", "A new directory must have a name below its authorized root")
        parent = self._open_directory_parts(tuple(parts[:-1]))
        try:
            return parent._create_new_child_directory(parts[-1])
        finally:
            if parent is not self:
                parent.close()

    def _inspect_child(self, name: str) -> tuple[bool, dict[str, Any]]:
        self._safe_component(name)
        if self.api is not None:
            handle = self.api.open_child(self.handle, name)
            try:
                info = self.api.information(handle)
                if info["attributes"] & self.api._FILE_ATTRIBUTE_REPARSE_POINT:
                    raise CandidateError("UNSAFE_PATH", "Reparse entries are not candidate files")
                if not info["disk_file"]:
                    raise CandidateError("UNSAFE_ENTRY", "Candidate entry is not a regular disk object")
                return bool(info["attributes"] & self.api._FILE_ATTRIBUTE_DIRECTORY), info
            finally:
                self.api.close(handle)
        try:
            info = os.stat(name, dir_fd=self.handle, follow_symlinks=False)
        except OSError as error:
            raise CandidateError("SAFE_HANDLE_IO_ERROR", "A candidate entry cannot be inspected") from error
        if stat.S_ISLNK(info.st_mode):
            raise CandidateError("UNSAFE_PATH", "Symbolic links are not candidate entries")
        if stat.S_ISDIR(info.st_mode):
            return True, {"identity": (int(info.st_dev), int(info.st_ino)), "links": int(info.st_nlink)}
        if stat.S_ISREG(info.st_mode):
            return False, {"identity": (int(info.st_dev), int(info.st_ino)), "links": int(info.st_nlink)}
        raise CandidateError("UNSAFE_ENTRY", "Candidate entry is not a regular file or directory")

    def list_names(self) -> list[str]:
        if self.api is not None:
            return self.api.list_names(self.handle)
        try:
            return os.listdir(self.handle)
        except OSError as error:
            raise CandidateError("SAFE_HANDLE_IO_ERROR", "A candidate directory cannot be enumerated by its handle") from error

    def read_file(self, relative: str) -> bytes:
        parts = PurePosixPath(_safe_relative(relative)).parts
        parent = self._open_directory_parts(tuple(parts[:-1]))
        try:
            name = parts[-1]
            if self.api is not None:
                handle = self.api._nt_open(
                    parent.handle, name,
                    desired=self.api._FILE_READ_DATA | self.api._FILE_READ_ATTRIBUTES | self.api._SYNCHRONIZE,
                    share=self.api._FILE_SHARE_READ,
                    disposition=self.api._FILE_OPEN,
                    options=self.api._FILE_NON_DIRECTORY_FILE | self.api._FILE_SYNCHRONOUS_IO_NONALERT
                    | self.api._FILE_OPEN_REPARSE_POINT,
                )
                try:
                    info = self.api.information(handle)
                    if info["attributes"] & self.api._FILE_ATTRIBUTE_REPARSE_POINT:
                        raise CandidateError("UNSAFE_PATH", "A listed file became a reparse point")
                    if info["attributes"] & self.api._FILE_ATTRIBUTE_DIRECTORY or not info["disk_file"]:
                        raise CandidateError("SOURCE_NOT_REGULAR", "A listed file is not a regular disk file")
                    if info["links"] != 1:
                        raise CandidateError("HARDLINK_REFUSED", "Hard-linked files are not accepted")
                    raw = self.api.read_all(handle)
                    after = self.api.information(handle)
                    if after["identity"] != info["identity"] or after["size"] != info["size"]:
                        raise CandidateError("SOURCE_CHANGED", "A file changed while read through its pinned handle")
                    return raw
                finally:
                    self.api.close(handle)
            flags = os.O_RDONLY | os.O_NOFOLLOW | getattr(os, "O_CLOEXEC", 0)
            try:
                handle = os.open(name, flags, dir_fd=parent.handle)
            except OSError as error:
                code = "UNSAFE_PATH" if error.errno in (errno.ELOOP, errno.ENOTDIR) else "SOURCE_FILE_MISSING"
                raise CandidateError(code, "A listed file could not be opened without following links") from error
            try:
                before = os.fstat(handle)
                if not stat.S_ISREG(before.st_mode):
                    raise CandidateError("SOURCE_NOT_REGULAR", "A listed file is not regular")
                if before.st_nlink != 1:
                    raise CandidateError("HARDLINK_REFUSED", "Hard-linked files are not accepted")
                chunks = []
                while True:
                    chunk = os.read(handle, 1024 * 1024)
                    if not chunk:
                        break
                    chunks.append(chunk)
                after = os.fstat(handle)
                identity_before = (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns, before.st_ctime_ns)
                identity_after = (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns, after.st_ctime_ns)
                if identity_before != identity_after:
                    raise CandidateError("SOURCE_CHANGED", "A file changed while read through its pinned handle")
                return b"".join(chunks)
            finally:
                os.close(handle)
        finally:
            if parent is not self:
                parent.close()

    def create_file(self, relative: str, raw: bytes) -> bytes:
        parts = PurePosixPath(_safe_relative(relative)).parts
        parent = self._open_directory_parts(tuple(parts[:-1]), create=True)
        try:
            name = parts[-1]
            if self.api is not None:
                handle = self.api.create_child_file(parent.handle, name)
                try:
                    before = self.api.information(handle)
                    if before["attributes"] & self.api._FILE_ATTRIBUTE_REPARSE_POINT:
                        raise CandidateError("UNSAFE_PATH", "A candidate file was created as a reparse point")
                    if before["attributes"] & self.api._FILE_ATTRIBUTE_DIRECTORY or not before["disk_file"]:
                        raise CandidateError("COPY_IO_ERROR", "A candidate output is not a regular disk file")
                    if before["links"] != 1:
                        raise CandidateError("HARDLINK_REFUSED", "A newly created candidate file is hard-linked")
                    copied = self.api.write_and_readback(handle, raw)
                    after = self.api.information(handle)
                    if after["identity"] != before["identity"] or after["size"] != len(raw):
                        raise CandidateError("COPY_BYTES_MISMATCH", "Candidate identity/size changed during write")
                    return copied
                finally:
                    self.api.close(handle)
            flags = (os.O_RDWR | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW
                     | getattr(os, "O_CLOEXEC", 0))
            try:
                handle = os.open(name, flags, 0o600, dir_fd=parent.handle)
            except FileExistsError as error:
                raise CandidateError("OUTPUT_CONFLICT", "A candidate file already exists; it was not overwritten",
                                     status="conflict", exit_code=1) from error
            except OSError as error:
                code = "UNSAFE_PATH" if error.errno in (errno.ELOOP, errno.ENOTDIR) else "COPY_IO_ERROR"
                raise CandidateError(code, "A candidate file could not be created by its pinned parent handle") from error
            try:
                before = os.fstat(handle)
                if not stat.S_ISREG(before.st_mode):
                    raise CandidateError("COPY_IO_ERROR", "A candidate output is not a regular file")
                if before.st_nlink != 1:
                    raise CandidateError("HARDLINK_REFUSED", "A newly created candidate file is hard-linked")
                position = 0
                while position < len(raw):
                    position += os.write(handle, raw[position:position + 1024 * 1024])
                os.fsync(handle)
                os.lseek(handle, 0, os.SEEK_SET)
                chunks = []
                while True:
                    chunk = os.read(handle, 1024 * 1024)
                    if not chunk:
                        break
                    chunks.append(chunk)
                copied = b"".join(chunks)
                after = os.fstat(handle)
                if (after.st_dev, after.st_ino, after.st_size) != (before.st_dev, before.st_ino, len(raw)):
                    raise CandidateError("COPY_BYTES_MISMATCH", "Candidate identity/size changed during write")
                return copied
            finally:
                os.close(handle)
        finally:
            if parent is not self:
                parent.close()

    def walk(self) -> tuple[list[str], list[str], list[dict[str, str]]]:
        files: list[str] = []
        directories: list[str] = []
        findings: list[dict[str, str]] = []

        def visit(directory: "_SafeDirectory", prefix: str) -> None:
            try:
                names = directory.list_names()
            except CandidateError as error:
                findings.append({
                    "code": "DIRECTORY_READ_ERROR",
                    "path": prefix or ".",
                    "message": str(error),
                })
                return
            for name in names:
                if name in (".", ".."):
                    continue
                relative = f"{prefix}/{name}" if prefix else name
                try:
                    is_directory, info = directory._inspect_child(name)
                except CandidateError as error:
                    findings.append({
                        "code": "UNSAFE_ENTRY" if error.code == "UNSAFE_PATH" else error.code,
                        "path": relative,
                        "message": str(error),
                    })
                    continue
                if is_directory:
                    directories.append(relative)
                    if name in {".git", ".venv", "__pycache__"}:
                        findings.append({
                            "code": "FORBIDDEN_DIRECTORY",
                            "path": relative,
                            "message": "Git, runtime, and cache directories are excluded",
                        })
                    try:
                        child = directory._open_child_directory(name)
                    except CandidateError as error:
                        findings.append({
                            "code": "UNSAFE_ENTRY" if error.code == "UNSAFE_PATH" else error.code,
                            "path": relative,
                            "message": str(error),
                        })
                        continue
                    try:
                        visit(child, relative)
                    finally:
                        child.close()
                else:
                    files.append(relative)
                    if info["links"] != 1:
                        findings.append({
                            "code": "HARDLINK_REFUSED",
                            "path": relative,
                            "message": "Hard-linked files are not accepted",
                        })

        visit(self, "")
        return sorted(files), sorted(directories), findings

    def matches_path(self, path: Path) -> bool:
        try:
            other = _SafeDirectory.open_absolute(path)
        except CandidateError:
            return False
        try:
            return other.identity == self.identity
        finally:
            other.close()


def _sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=True, sort_keys=True, indent=2) + "\n").encode("utf-8")


def _reject_network(value: str, label: str) -> None:
    if not value.strip() or "://" in value or value.startswith(("//", "\\\\")):
        raise CandidateError("LOCAL_PATH_REQUIRED", f"{label} must be an explicit local path")


def _is_reparse(path: Path) -> bool:
    try:
        info = os.lstat(path)
    except OSError:
        return False
    return stat.S_ISLNK(info.st_mode) or bool(getattr(info, "st_file_attributes", 0) & _REPARSE)


def _assert_no_reparse_components(path: Path, *, allow_missing_final: bool = False) -> None:
    if not path.is_absolute() or ".." in path.parts:
        raise CandidateError("UNSAFE_PATH", "Path must be absolute and contain no parent traversal")
    current = Path(path.anchor)
    components = path.parts[1:]
    for index, component in enumerate(components):
        current = current / component
        if not os.path.lexists(current):
            if allow_missing_final and index == len(components) - 1:
                return
            raise CandidateError("PATH_NOT_FOUND", "A declared path component does not exist")
        if _is_reparse(current):
            raise CandidateError("UNSAFE_PATH", "Reparse points and symbolic links are not allowed")


def _local_directory(value: str, label: str) -> Path:
    _reject_network(value, label)
    path = Path(value)
    if not path.is_absolute():
        raise CandidateError("ABSOLUTE_PATH_REQUIRED", f"{label} must be absolute")
    _assert_no_reparse_components(path)
    absolute = Path(os.path.abspath(path))
    if not absolute.is_dir():
        raise CandidateError("INVALID_DIRECTORY", f"{label} must be an existing directory")
    return absolute


def _local_new_file(value: str, label: str, allowed_roots: tuple[Path, ...],
                    *, suffix: str | None = None) -> Path:
    _reject_network(value, label)
    path = Path(value)
    if not path.is_absolute() or ".." in path.parts or path.name in ("", ".", ".."):
        raise CandidateError("UNSAFE_OUTPUT", f"{label} must be an absolute, non-traversing file path")
    if suffix is not None and path.suffix.lower() != suffix:
        raise CandidateError("INVALID_OUTPUT_SUFFIX", f"{label} must use the {suffix} extension")
    absolute = Path(os.path.abspath(path))
    _assert_no_reparse_components(absolute.parent)
    parent = absolute.parent
    if not parent.is_dir():
        raise CandidateError("INVALID_OUTPUT_PARENT", f"{label} parent must be an existing directory")
    resolved = parent / absolute.name
    if os.path.lexists(resolved):
        raise CandidateError("OUTPUT_CONFLICT", f"{label} already exists",
                             path=path.name, status="conflict", exit_code=1)
    if not any(resolved.parent.is_relative_to(root) for root in allowed_roots):
        raise CandidateError("OUTPUT_OUTSIDE_ALLOWED_ROOT",
                             f"{label} must be inside an explicitly allowed output root")
    return resolved


def _safe_relative(value: Any, *, directory: bool = False) -> str:
    if not isinstance(value, str) or not value or "\\" in value or ":" in value:
        raise CandidateError("INVALID_MANIFEST_PATH", "Manifest paths must be explicit relative POSIX paths")
    if any(character in value for character in "*?[]{}"):
        raise CandidateError("INVALID_MANIFEST_PATH", "Manifest paths may not contain glob or pattern syntax")
    if any(ord(character) < 32 for character in value):
        raise CandidateError("INVALID_MANIFEST_PATH", "Manifest path contains a control character")
    if value.startswith("/") or value.endswith("/") != directory:
        raise CandidateError("INVALID_MANIFEST_PATH", "Manifest path has an invalid root or trailing separator")
    parts = value[:-1].split("/") if directory else value.split("/")
    if any(part in ("", ".", "..") for part in parts):
        raise CandidateError("INVALID_MANIFEST_PATH", "Manifest path contains an empty or traversal segment")
    return value


def _duplicate_reject(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise CandidateError("DUPLICATE_MANIFEST_KEY", "Manifest JSON contains a duplicate object key")
        result[key] = value
    return result


def _read_manifest(root: Path, safe_root: _SafeDirectory) -> tuple[dict[str, Any], bytes, str]:
    try:
        raw = _source_bytes(root, MANIFEST_PATH, safe_root)
        manifest = json.loads(raw.decode("utf-8"), object_pairs_hook=_duplicate_reject,
                              parse_constant=lambda value: (_ for _ in ()).throw(
                                  CandidateError("INVALID_MANIFEST", "Manifest contains a non-finite number")))
    except CandidateError:
        raise
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise CandidateError("INVALID_MANIFEST", "The explicit distribution manifest cannot be read as UTF-8 JSON",
                             path=MANIFEST_PATH) from error
    if not isinstance(manifest, dict) or set(manifest) != {"schemaVersion", "components", "files", "excluded"}:
        raise CandidateError("INVALID_MANIFEST", "Manifest has an unexpected top-level shape", path=MANIFEST_PATH)
    if type(manifest["schemaVersion"]) is not int or manifest["schemaVersion"] != 1:
        raise CandidateError("INVALID_MANIFEST", "Manifest schemaVersion must be integer 1", path=MANIFEST_PATH)
    components = manifest["components"]
    if not isinstance(components, dict) or not components:
        raise CandidateError("INVALID_MANIFEST", "Manifest requires component ownership descriptions")
    if any(not isinstance(key, str) or not key.strip() or not isinstance(value, str) or not value.strip()
           for key, value in components.items()):
        raise CandidateError("INVALID_MANIFEST", "Each component requires a nonempty id and description")
    files = manifest["files"]
    if not isinstance(files, list) or not files:
        raise CandidateError("INVALID_MANIFEST", "Manifest requires explicit file entries")
    seen: set[str] = set()
    for entry in files:
        if not isinstance(entry, dict) or set(entry) != {"path", "component"}:
            raise CandidateError("INVALID_MANIFEST", "Each file entry must contain only path and component")
        relative = _safe_relative(entry["path"])
        folded = relative.casefold()
        if folded in seen:
            raise CandidateError("DUPLICATE_MANIFEST_PATH", "Manifest contains a duplicate or case-alias path",
                                 path=relative)
        seen.add(folded)
        if entry["component"] not in components:
            raise CandidateError("INVALID_MANIFEST", "File references an undeclared owner component", path=relative)
    raw_paths = [entry["path"] for entry in files]
    if MANIFEST_PATH not in raw_paths:
        raise CandidateError("MANIFEST_NOT_SELF_DESCRIBING", "The exact manifest must be listed as a candidate file",
                             path=MANIFEST_PATH)
    # A file may not also be another listed file's parent.
    exact = set(raw_paths)
    for relative in raw_paths:
        parent = PurePosixPath(relative).parent
        while str(parent) != ".":
            if parent.as_posix() in exact:
                raise CandidateError("MANIFEST_PATH_COLLISION", "Manifest path is both a file and a parent directory",
                                     path=relative)
            parent = parent.parent
    exclusions = manifest["excluded"]
    if not isinstance(exclusions, list):
        raise CandidateError("INVALID_MANIFEST", "Manifest exclusions must be a list")
    excluded_seen: set[str] = set()
    for exclusion in exclusions:
        if not isinstance(exclusion, dict) or set(exclusion) != {"path", "reason"}:
            raise CandidateError("INVALID_MANIFEST", "Each exclusion must contain only path and reason")
        path_value = exclusion["path"]
        is_directory = isinstance(path_value, str) and path_value.endswith("/")
        _safe_relative(path_value, directory=is_directory)
        if path_value.casefold() in excluded_seen:
            raise CandidateError("DUPLICATE_EXCLUSION", "Manifest has duplicate exclusion paths", path=path_value)
        excluded_seen.add(path_value.casefold())
        if not isinstance(exclusion["reason"], str) or not exclusion["reason"].strip():
            raise CandidateError("INVALID_MANIFEST", "Each exclusion needs an explicit reason", path=path_value)
    return manifest, raw, _sha256(raw)


def _git(root: Path, *arguments: str) -> bytes:
    environment = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    environment.update({
        "GIT_CONFIG_GLOBAL": os.devnull,
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_OPTIONAL_LOCKS": "0",
    })
    command = [
        "git", "--no-pager", "-c", "core.quotepath=false", "-c", "core.fsmonitor=false",
        *arguments,
    ]
    result = subprocess.run(
        command, cwd=root, env=environment, shell=False,
        capture_output=True, check=False,
    )
    if result.returncode:
        raise CandidateError("GIT_PROVENANCE_UNAVAILABLE",
                             "Local Git provenance could not be read; no branch or network fallback is used")
    return result.stdout


def _git_provenance(root: Path) -> tuple[str, list[dict[str, str]], list[str]]:
    try:
        top = _git(root, "rev-parse", "--show-toplevel").decode("utf-8").strip()
        top_path = Path(top).resolve(strict=True)
        if top_path != root:
            raise CandidateError("SOURCE_ROOT_NOT_GIT_TOP", "Source root must be the exact local Git checkout root")
        commit = _git(root, "rev-parse", "--verify", "HEAD").decode("ascii").strip()
        if len(commit) not in (40, 64) or any(character not in "0123456789abcdef" for character in commit):
            raise CandidateError("SOURCE_COMMIT_INVALID", "Git HEAD is not a complete commit object id")
        status_raw = _git(root, "status", "--porcelain=v1", "--untracked-files=all",
                          "--ignore-submodules=all").decode("utf-8").splitlines()
        dirty = []
        for line in status_raw:
            if len(line) < 4:
                raise CandidateError("GIT_STATUS_INVALID", "Git returned an unrecognized local status record")
            dirty.append({"status": line[:2], "path": line[3:]})
        inventory_raw = _git(root, "ls-files", "--cached", "--others", "--exclude-standard",
                             "--full-name", "-z")
        paths = [item.decode("utf-8") for item in inventory_raw.split(b"\0") if item]
        return commit, dirty, sorted(set(paths))
    except UnicodeDecodeError as error:
        raise CandidateError("GIT_PROVENANCE_INVALID", "Local Git paths are not valid UTF-8") from error


def _excluded_reason(relative: str, manifest: dict[str, Any]) -> str | None:
    for exclusion in manifest["excluded"]:
        path = exclusion["path"]
        if path.endswith("/") and relative.startswith(path):
            return exclusion["reason"]
        if relative == path:
            return exclusion["reason"]
    return None


def _inventory(root: Path, manifest: dict[str, Any], included: set[str],
               source_paths: list[str]) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    excluded: list[dict[str, str]] = []
    unclassified: list[dict[str, str]] = []
    for relative in source_paths:
        if relative in included:
            continue
        reason = _excluded_reason(relative, manifest)
        if reason is None:
            unclassified.append({"path": relative, "reason": "No explicit allowlist entry or exclusion rule"})
        else:
            excluded.append({"path": relative, "reason": reason})
    return excluded, unclassified


def _source_bytes(root: Path, relative: str, safe_root: _SafeDirectory | None = None) -> bytes:
    path = root.joinpath(*PurePosixPath(relative).parts)
    owned_root = safe_root is None
    try:
        _assert_no_reparse_components(path)
        if safe_root is None:
            safe_root = _SafeDirectory.open_absolute(root)
        try:
            return safe_root.read_file(relative)
        except CandidateError as error:
            if error.code == "PATH_NOT_FOUND":
                raise CandidateError("SOURCE_FILE_MISSING", "A listed source file is missing", path=relative) from error
            if error.path is None:
                error.path = relative
            raise
    except CandidateError:
        raise
    except OSError as error:
        code = "SOURCE_FILE_MISSING" if not path.exists() else "SOURCE_READ_ERROR"
        raise CandidateError(code, "A listed source file is missing or unreadable", path=relative) from error
    finally:
        if owned_root and safe_root is not None:
            safe_root.close()


def _output_roots(root: Path, values: list[str]) -> tuple[Path, ...]:
    if not values:
        raise CandidateError("OUTPUT_ROOT_REQUIRED", "Supply at least one explicitly authorized output root")
    roots = []
    for value in values:
        resolved = _local_directory(value, "Allowed output root")
        if resolved not in roots:
            roots.append(resolved)
    return tuple(roots)


def _path_reference(path: Path, root: Path, allowed_roots: tuple[Path, ...]) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        for allowed in allowed_roots:
            try:
                return f"external:{allowed.name}/{path.relative_to(allowed).as_posix()}"
            except ValueError:
                continue
    return "external"


def _target_directory(value: str, root: Path, allowed_roots: tuple[Path, ...],
                      *, must_exist: bool) -> Path:
    _reject_network(value, "Candidate path")
    requested = Path(value)
    if not requested.is_absolute() or ".." in requested.parts or requested.name in ("", ".", ".."):
        raise CandidateError("UNSAFE_CANDIDATE_PATH", "Candidate path must be absolute and contain no traversal")
    requested = Path(os.path.abspath(requested))
    if must_exist:
        _assert_no_reparse_components(requested)
        if not requested.is_dir():
            raise CandidateError("INVALID_CANDIDATE_ROOT", "Candidate must be an existing directory")
    else:
        _assert_no_reparse_components(requested.parent)
        parent = requested.parent
        if not parent.is_dir():
            raise CandidateError("INVALID_CANDIDATE_PARENT", "Candidate parent must be an existing directory")
        resolved = requested
        if os.path.lexists(resolved):
            raise CandidateError("TARGET_CONFLICT", "Candidate target already exists; no owner content was changed",
                                 path=_path_reference(resolved, root, allowed_roots),
                                 status="conflict", exit_code=1)
    if must_exist:
        resolved = requested
    if not any(resolved.parent.is_relative_to(allowed) for allowed in allowed_roots):
        raise CandidateError("OUTPUT_OUTSIDE_ALLOWED_ROOT", "Candidate must be inside an explicitly allowed output root")
    try:
        relative = resolved.relative_to(root)
        if relative.parts and relative.parts[0] != ".venv":
            raise CandidateError("SOURCE_TREE_OUTPUT_REFUSED",
                                 "A candidate under the source checkout is allowed only in its ignored .venv fixture root")
    except ValueError:
        pass
    return resolved


def _provenance_record(commit: str, dirty: list[dict[str, str]],
                       source_paths: list[str]) -> dict[str, Any]:
    return {
        "source_commit": commit,
        "dirty_scope": dirty,
        "source_inventory_sha256": _sha256("\n".join(source_paths).encode("utf-8")),
    }


def _validate_sources(root: Path, safe_root: _SafeDirectory) -> tuple[dict[str, Any], bytes, str, dict[str, bytes],
                                              list[dict[str, str]], list[dict[str, str]],
                                              str, list[dict[str, str]], list[str]]:
    if not safe_root.matches_path(root):
        raise CandidateError("UNSAFE_PATH", "The pinned source directory no longer matches its authorized path")
    manifest, manifest_raw, manifest_sha = _read_manifest(root, safe_root)
    commit, dirty, source_paths = _git_provenance(root)
    entries = sorted(manifest["files"], key=lambda item: item["path"])
    included = {entry["path"] for entry in entries}
    excluded, unclassified = _inventory(root, manifest, included, source_paths)
    if unclassified:
        raise CandidateError("UNCLASSIFIED_SOURCE_FILE",
                             "Every local source file must be explicitly allowlisted or have an exclusion reason",
                             path=unclassified[0]["path"])
    snapshots = {entry["path"]: _source_bytes(root, entry["path"], safe_root) for entry in entries}
    if snapshots.get(MANIFEST_PATH) != manifest_raw:
        raise CandidateError("MANIFEST_CHANGED", "Manifest bytes changed while its inventory was read",
                             path=MANIFEST_PATH)
    if not safe_root.matches_path(root):
        raise CandidateError("UNSAFE_PATH", "The pinned source directory changed during inventory validation")
    return manifest, manifest_raw, manifest_sha, snapshots, excluded, dirty, commit, [
        {"path": item, "reason": _excluded_reason(item, manifest) or "NOT_ALLOWLISTED"}
        for item in source_paths if item not in included
    ], source_paths


def _copy_receipt(root: Path, target: Path, source_root: _SafeDirectory,
                  target_root: _SafeDirectory, manifest: dict[str, Any],
                  manifest_sha: str, snapshots: dict[str, bytes],
                  excluded: list[dict[str, str]], commit: str,
                  dirty: list[dict[str, str]], source_paths: list[str],
                  allowed_roots: tuple[Path, ...]) -> dict[str, Any]:
    files = []
    components = {entry["path"]: entry["component"] for entry in manifest["files"]}
    try:
        for relative in sorted(snapshots):
            destination = target.joinpath(*PurePosixPath(relative).parts)
            parent_parts = PurePosixPath(relative).parts[:-1]
            target_root.ensure_directories(tuple(parent_parts))
            _assert_no_reparse_components(destination.parent)
            raw = snapshots[relative]
            copied = target_root.create_file(relative, raw)
            if copied != raw:
                raise CandidateError("COPY_BYTES_MISMATCH", "Candidate bytes differ from the preflight source",
                                     path=relative)
            files.append({
                "path": relative,
                "component": components[relative],
                "size": len(raw),
                "source_sha256": _sha256(raw),
                "candidate_sha256": _sha256(copied),
            })
        for relative, original in snapshots.items():
            if _source_bytes(root, relative, source_root) != original:
                raise CandidateError("SOURCE_CHANGED", "A listed source changed during candidate copy",
                                     path=relative)
            if target_root.read_file(relative) != original:
                raise CandidateError("COPY_BYTES_MISMATCH",
                                     "Candidate bytes changed after being written through the pinned handle",
                                     path=relative)
        commit_after, dirty_after, paths_after = _git_provenance(root)
        if (commit_after, dirty_after, paths_after) != (commit, dirty, source_paths):
            raise CandidateError("SOURCE_SCOPE_CHANGED", "Git source identity or dirty scope changed during copy")
        if not source_root.matches_path(root):
            raise CandidateError("UNSAFE_PATH", "The pinned source directory changed during candidate copy")
        if not target_root.matches_path(target):
            raise CandidateError("UNSAFE_PATH", "The candidate path no longer names its pinned output directory")
        actual_files, _, findings = target_root.walk()
        if findings or set(actual_files) != set(snapshots):
            raise CandidateError("TARGET_CHANGED",
                                 "The candidate tree changed during the copy; no successful receipt was issued",
                                 path=_path_reference(target, root, allowed_roots))
    except CandidateError:
        raise
    except OSError as error:
        raise CandidateError("COPY_IO_ERROR",
                             "Candidate copy stopped; any newly created partial candidate is retained for inspection",
                             path=_path_reference(target, root, allowed_roots)) from error
    return {
        "schemaVersion": 1,
        "status": "copied",
        "exit_code": 0,
        "manifest_sha256": manifest_sha,
        "provenance": {"source_root": ".", **_provenance_record(commit, dirty, source_paths)},
        "target": _path_reference(target, root, allowed_roots),
        "allowed_output_roots": [_path_reference(item, root, allowed_roots) for item in allowed_roots],
        "copied_count": len(files),
        "excluded_count": len(excluded),
        "files": files,
        "excluded_files": excluded,
        "findings": [],
    }


def _walk_candidate(candidate: _SafeDirectory) -> tuple[list[str], list[str], list[dict[str, str]]]:
    return candidate.walk()


def _verify_receipt(root: Path, candidate: Path, candidate_root: _SafeDirectory,
                    manifest: dict[str, Any],
                    manifest_sha: str, snapshots: dict[str, bytes], excluded: list[dict[str, str]],
                    commit: str, dirty: list[dict[str, str]], source_paths: list[str],
                    allowed_roots: tuple[Path, ...]) -> dict[str, Any]:
    actual_files, actual_directories, findings = _walk_candidate(candidate_root)
    expected_files = set(snapshots)
    actual_set = set(actual_files)
    for relative in sorted(expected_files - actual_set):
        findings.append({"code": "MISSING_FILE", "path": relative,
                         "message": "An explicitly listed candidate file is missing"})
    for relative in sorted(actual_set - expected_files):
        findings.append({"code": "EXTRA_FILE", "path": relative,
                         "message": "Candidate contains a file not present in the exact allowlist"})
    expected_directories = set()
    for relative in expected_files:
        parent = PurePosixPath(relative).parent
        while str(parent) != ".":
            expected_directories.add(parent.as_posix())
            parent = parent.parent
    for relative in sorted(set(actual_directories) - expected_directories):
        if relative not in {item["path"] for item in findings}:
            findings.append({"code": "EXTRA_DIRECTORY", "path": relative,
                             "message": "Candidate contains an unowned directory"})
    candidate_bytes: dict[str, bytes] = {}
    hardlinked = {item["path"] for item in findings if item["code"] == "HARDLINK_REFUSED"}
    for relative in sorted(expected_files & actual_set):
        if relative in hardlinked:
            continue
        try:
            raw = candidate_root.read_file(relative)
        except CandidateError as error:
            code = {
                "UNSAFE_PATH": "UNSAFE_ENTRY",
                "HARDLINK_REFUSED": "HARDLINK_REFUSED",
                "PATH_NOT_FOUND": "MISSING_FILE",
            }.get(error.code, "FILE_READ_ERROR")
            findings.append({"code": code, "path": relative, "message": str(error)})
            continue
        candidate_bytes[relative] = raw
        expected = snapshots[relative]
        if raw != expected:
            findings.append({"code": "HASH_MISMATCH", "path": relative,
                             "message": "Candidate raw bytes differ from the current listed source"})
    if not candidate_root.matches_path(candidate):
        findings.append({"code": "UNSAFE_ENTRY", "path": ".",
                         "message": "Candidate path no longer names its pinned directory"})
    findings.sort(key=lambda item: (item["path"], item["code"]))
    status = "valid" if not findings else "invalid"
    return {
        "schemaVersion": 1,
        "status": status,
        "exit_code": 0 if not findings else 1,
        "manifest_sha256": manifest_sha,
        "provenance": {"source_root": ".", **_provenance_record(commit, dirty, source_paths)},
        "candidate": _path_reference(candidate, root, allowed_roots),
        "allowed_output_roots": [_path_reference(item, root, allowed_roots) for item in allowed_roots],
        "verified_count": len(candidate_bytes),
        "excluded_count": len(excluded),
        "files": [
            {
                "path": relative,
                "component": next(entry["component"] for entry in manifest["files"]
                                  if entry["path"] == relative),
                "size": len(snapshots[relative]),
                "source_sha256": _sha256(snapshots[relative]),
                "candidate_sha256": _sha256(candidate_bytes[relative]) if relative in candidate_bytes else None,
            }
            for relative in sorted(expected_files)
        ],
        "excluded_files": excluded,
        "findings": findings,
    }


def _allowed_root_for(path: Path, allowed_roots: tuple[Path, ...],
                      safe_roots: tuple[_SafeDirectory, ...]) -> tuple[Path, _SafeDirectory]:
    for root, safe_root in zip(allowed_roots, safe_roots):
        try:
            path.relative_to(root)
            return root, safe_root
        except ValueError:
            continue
    raise CandidateError("OUTPUT_OUTSIDE_ALLOWED_ROOT",
                         "The local output is outside every explicitly authorized root")


def _open_candidate_directory(path: Path, allowed_roots: tuple[Path, ...],
                              safe_roots: tuple[_SafeDirectory, ...], *,
                              create: bool) -> _SafeDirectory:
    root, safe_root = _allowed_root_for(path, allowed_roots, safe_roots)
    relative = path.relative_to(root)
    if not relative.parts:
        raise CandidateError("UNSAFE_CANDIDATE_PATH",
                             "A candidate must be a child of an authorized output root")
    if create:
        return safe_root.create_directory(tuple(relative.parts))
    return safe_root._open_directory_parts(tuple(relative.parts))


def _write_report(path: Path | None, payload: dict[str, Any],
                  allowed_roots: tuple[Path, ...],
                  safe_roots: tuple[_SafeDirectory, ...]) -> dict[str, Any]:
    if path is None:
        return payload
    report = dict(payload)
    report["report_output"] = {"path": path.name, "written": True}
    try:
        root, safe_root = _allowed_root_for(path, allowed_roots, safe_roots)
        relative = path.relative_to(root).as_posix()
        safe_root.create_file(relative, _json_bytes(report))
        if not safe_root.matches_path(root):
            raise CandidateError("UNSAFE_OUTPUT", "The authorized report root changed during report writing")
    except CandidateError as error:
        if error.code == "OUTPUT_CONFLICT":
            raise CandidateError("REPORT_CONFLICT", "Report path already exists; it was not overwritten",
                                 path=path.name, status="conflict", exit_code=1) from error
        if error.code in ("UNSAFE_PATH", "UNSAFE_OUTPUT"):
            raise
        raise CandidateError("REPORT_WRITE_ERROR", "New report could not be written") from error
    except OSError as error:
        raise CandidateError("REPORT_WRITE_ERROR", "New report could not be written") from error
    return report


def _failure(error: CandidateError, root: Path | None, allowed_roots: tuple[Path, ...],
             report_path: Path | None) -> dict[str, Any]:
    payload = {
        "schemaVersion": 1,
        "status": error.status,
        "exit_code": error.exit_code,
        "findings": [{
            "code": error.code,
            "path": error.path,
            "message": str(error),
        }],
        "allowed_output_roots": [
            _path_reference(path, root, allowed_roots) if root is not None else path.name
            for path in allowed_roots
        ],
    }
    if report_path is not None:
        payload["report_output"] = {"path": report_path.name, "written": False}
    return payload


def _report_path(value: str | None, root: Path, allowed_roots: tuple[Path, ...]) -> Path | None:
    if value is None:
        return None
    path = _local_new_file(value, "Report path", allowed_roots, suffix=".json")
    if path.is_relative_to(root):
        raise CandidateError("OUTPUT_OVERLAP", "A report must be outside the source tree")
    return path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, help="Exact local maker checkout root")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--target", help="New candidate directory; it must not already exist")
    mode.add_argument("--verify", help="Existing candidate directory to compare against the allowlist")
    parser.add_argument("--allow-output-root", action="append", default=[],
                        help="Explicit existing local root for the candidate or new report; repeat as needed")
    parser.add_argument("--report", help="Optional new local JSON receipt; existing files are never overwritten")
    arguments = parser.parse_args(argv)
    root: Path | None = None
    allowed_roots: tuple[Path, ...] = ()
    safe_root: _SafeDirectory | None = None
    safe_output_roots: tuple[_SafeDirectory, ...] = ()
    report_path: Path | None = None
    try:
        root = _local_directory(arguments.root, "Source root")
        safe_root = _SafeDirectory.open_absolute(root)
        allowed_roots = _output_roots(root, arguments.allow_output_root)
        safe_output_roots = tuple(_SafeDirectory.open_absolute(path) for path in allowed_roots)
        report_path = _report_path(arguments.report, root, allowed_roots)
        if arguments.target is not None:
            target = _target_directory(arguments.target, root, allowed_roots, must_exist=False)
            if report_path is not None and (
                report_path == target or report_path.is_relative_to(target)
            ):
                raise CandidateError("OUTPUT_OVERLAP", "Candidate and report destinations must be separate")
            manifest, _, manifest_sha, snapshots, excluded, dirty, commit, actual_excluded, source_paths = \
                _validate_sources(root, safe_root)
            target_root = _open_candidate_directory(
                target, allowed_roots, safe_output_roots, create=True,
            )
            try:
                payload = _copy_receipt(
                    root, target, safe_root, target_root, manifest, manifest_sha,
                    snapshots, excluded, commit, dirty, source_paths, allowed_roots,
                )
            finally:
                target_root.close()
        else:
            candidate = _target_directory(arguments.verify, root, allowed_roots, must_exist=True)
            if report_path is not None and (
                report_path == candidate or report_path.is_relative_to(candidate)
            ):
                raise CandidateError(
                    "OUTPUT_OVERLAP",
                    "A verification report may not be written inside the candidate",
                )
            candidate_root = _open_candidate_directory(
                candidate, allowed_roots, safe_output_roots, create=False,
            )
            try:
                manifest, _, manifest_sha, snapshots, excluded, dirty, commit, actual_excluded, source_paths = \
                    _validate_sources(root, safe_root)
                payload = _verify_receipt(
                    root, candidate, candidate_root, manifest, manifest_sha, snapshots,
                    excluded, commit, dirty, source_paths, allowed_roots,
                )
            finally:
                candidate_root.close()
        payload["excluded_files"] = actual_excluded
        if report_path is not None:
            payload = _write_report(
                report_path, payload, allowed_roots, safe_output_roots,
            )
            summary = {
                "status": payload["status"],
                "exit_code": payload["exit_code"],
                "report_output": payload["report_output"],
                "copied_count": payload.get("copied_count"),
                "verified_count": payload.get("verified_count"),
                "excluded_count": payload.get("excluded_count"),
                "findings": payload["findings"],
            }
            print(json.dumps(summary, ensure_ascii=True, sort_keys=True))
        else:
            print(_json_bytes(payload).decode("utf-8"), end="")
        return payload["exit_code"]
    except CandidateError as error:
        payload = _failure(error, root, allowed_roots, report_path)
        print(json.dumps(payload, ensure_ascii=True, sort_keys=True))
        return error.exit_code
    except (OSError, UnicodeError) as error:
        failure = CandidateError("LOCAL_IO_ERROR", "A local candidate input/output operation failed")
        print(json.dumps(_failure(failure, root, allowed_roots, report_path),
                         ensure_ascii=True, sort_keys=True))
        return failure.exit_code
    finally:
        for directory in reversed(safe_output_roots):
            try:
                directory.close()
            except OSError:
                pass
        if safe_root is not None:
            try:
                safe_root.close()
            except OSError:
                pass


if __name__ == "__main__":
    raise SystemExit(main())
