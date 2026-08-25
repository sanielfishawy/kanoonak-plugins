#!/usr/bin/env python3
"""Publish one checked, judge-editable Kanoonak draft without overwriting.

The host supplies one exact existing delivery directory and truthfully labels
the grant. This helper neither finds nor creates a case or download folder,
never touches an issued-rulings folder, and never changes the checked text.
"""

from __future__ import annotations

import argparse
import ctypes
import hashlib
import importlib.util
import io
import json
import os
import re
import secrets
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable


ALLOWED_GRANT_LABELS = {"drafts", "library-download"}
ALLOWED_STORAGE_CLASSIFICATIONS = {"local-unsynchronized"}
ALLOWED_KINDS = {"حكم", "حكم-تمهيدي", "قرار"}
ALLOWED_ROLES = {"title", "transition", "substantive", "plain"}
DOCX_DRAFT_RE = re.compile(r"مسودة-(حكم-تمهيدي|حكم|قرار)-([0-9]{2})\.docx\Z")
SIDECAR_DRAFT_RE = re.compile(
    r"مسودة-(حكم-تمهيدي|حكم|قرار)-([0-9]{2})\.metadata\.yaml\Z"
)
DIGEST_RE = re.compile(r"[0-9a-f]{64}\Z")
WINDOWS_MAX_PATH_UTF16 = 32767
WINDOWS_MAX_COMPONENT_UTF16 = 255
EXPECTED_UNIVERSAL_VERSION = "2026-08-24.1"


class _WindowsFileInformation(ctypes.Structure):
    from ctypes import wintypes as _wintypes

    _fields_ = [
        ("dwFileAttributes", _wintypes.DWORD),
        ("ftCreationTime", _wintypes.FILETIME),
        ("ftLastAccessTime", _wintypes.FILETIME),
        ("ftLastWriteTime", _wintypes.FILETIME),
        ("dwVolumeSerialNumber", _wintypes.DWORD),
        ("nFileSizeHigh", _wintypes.DWORD),
        ("nFileSizeLow", _wintypes.DWORD),
        ("nNumberOfLinks", _wintypes.DWORD),
        ("nFileIndexHigh", _wintypes.DWORD),
        ("nFileIndexLow", _wintypes.DWORD),
    ]


class _WindowsFileDispositionInfo(ctypes.Structure):
    from ctypes import wintypes as _wintypes

    _fields_ = [("DeleteFile", _wintypes.BOOLEAN)]


class DraftCreationError(ValueError):
    """A fail-closed input, formatting, or publication error."""


@dataclass(frozen=True)
class PublicationResult:
    docx: Path
    metadata: Path
    docx_identity: tuple[int, int]
    metadata_identity: tuple[int, int]
    ruling_text_sha256: str
    artifact_sha256: str


def _load_universal_module():
    """Load only the reviewed sibling checker, never an ambient module."""
    path = Path(__file__).with_name("check_ruling_universal.py")
    spec = importlib.util.spec_from_file_location(
        "_kanoonak_check_ruling_universal_2026_08_24_1", path
    )
    if spec is None or spec.loader is None:
        raise DraftCreationError("universal ruling checker is unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if getattr(module, "UNIVERSAL_VERSION", None) != EXPECTED_UNIVERSAL_VERSION:
        raise DraftCreationError(
            f"universal ruling checker version must be {EXPECTED_UNIVERSAL_VERSION}"
        )
    for name in ("check_ruling_text", "parse_paragraphs"):
        if not callable(getattr(module, name, None)):
            raise DraftCreationError(f"universal ruling checker lacks required API {name}")
    return module


def _universal_api() -> tuple[Callable[[str], dict[str, Any]], Callable[[str], list[str]]]:
    module = _load_universal_module()
    return module.check_ruling_text, module.parse_paragraphs


def _identity(path: Path | str, *, dir_fd: int | None = None) -> tuple[int, int]:
    stat = os.stat(path, dir_fd=dir_fd, follow_symlinks=False)
    return stat.st_dev, stat.st_ino


def _relative_when_anchored(path: Path, dir_fd: int | None) -> Path | str:
    return path.name if dir_fd is not None else path


def _read_bytes(path: Path | str, *, dir_fd: int | None = None) -> bytes:
    if dir_fd is None:
        return Path(path).read_bytes()
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(path, flags, dir_fd=dir_fd)
    try:
        chunks: list[bytes] = []
        while chunk := os.read(fd, 1024 * 1024):
            chunks.append(chunk)
        return b"".join(chunks)
    finally:
        os.close(fd)


def _read_exact(path: Path | str, expected: bytes, *, dir_fd: int | None = None) -> None:
    if _read_bytes(path, dir_fd=dir_fd) != expected:
        raise DraftCreationError(f"staged payload reread mismatch: {Path(path).name}")


def _write_complete_exclusive(
    path: Path | str, payload: bytes, *, dir_fd: int | None = None
) -> tuple[int, int]:
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600, dir_fd=dir_fd)
    try:
        offset = 0
        while offset < len(payload):
            written = os.write(fd, payload[offset:])
            if written <= 0:
                raise DraftCreationError("staged write was short")
            offset += written
        os.fsync(fd)
        if os.fstat(fd).st_size != len(payload):
            raise DraftCreationError("staged write was short")
        identity = (os.fstat(fd).st_dev, os.fstat(fd).st_ino)
    finally:
        os.close(fd)
    _read_exact(path, payload, dir_fd=dir_fd)
    return identity


def _validate_formatting(
    formatting: dict[str, Any], paragraphs: list[str]
) -> list[dict[str, str | None]]:
    if not isinstance(formatting, dict) or set(formatting) != {"paragraphs"}:
        raise DraftCreationError("formatting JSON must contain exactly 'paragraphs'")
    items = formatting["paragraphs"]
    if not isinstance(items, list) or len(items) != len(paragraphs):
        raise DraftCreationError("formatting paragraph count must match checked text")
    result: list[dict[str, str | None]] = []
    for index, (item, paragraph) in enumerate(zip(items, paragraphs), start=1):
        if not isinstance(item, dict) or set(item) != {"role", "opening_phrase"}:
            raise DraftCreationError(f"formatting paragraph {index} has unknown or missing keys")
        role = item["role"]
        opening = item["opening_phrase"]
        if role not in ALLOWED_ROLES:
            raise DraftCreationError(f"formatting paragraph {index} has unsupported role")
        if role == "substantive":
            if not isinstance(opening, str) or not opening or not paragraph.startswith(opening):
                raise DraftCreationError(
                    f"formatting paragraph {index} needs an exact non-empty opening prefix"
                )
        elif opening is not None:
            raise DraftCreationError(
                f"formatting paragraph {index} opening_phrase must be null for role {role}"
            )
        result.append({"role": role, "opening_phrase": opening})
    return result


def _set_run_format(run, *, bold: bool) -> None:
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    from docx.shared import Pt

    run.font.name = "Arial"
    run.font.size = Pt(16)
    run.bold = bold
    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.get_or_add_rFonts()
    for slot in ("ascii", "hAnsi", "eastAsia", "cs"):
        rfonts.set(qn(f"w:{slot}"), "Arial")
    for tag in ("sz", "szCs"):
        element = rpr.find(qn(f"w:{tag}"))
        if element is None:
            element = OxmlElement(f"w:{tag}")
            rpr.append(element)
        element.set(qn("w:val"), "32")
    rtl = rpr.find(qn("w:rtl"))
    if rtl is None:
        rtl = OxmlElement("w:rtl")
        rpr.append(rtl)
    rtl.set(qn("w:val"), "1")


def _set_paragraph_format(paragraph, role: str) -> None:
    from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    from docx.shared import Pt, Twips

    paragraph.alignment = (
        WD_ALIGN_PARAGRAPH.CENTER
        if role in {"title", "transition"}
        else WD_ALIGN_PARAGRAPH.JUSTIFY
    )
    fmt = paragraph.paragraph_format
    fmt.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    fmt.space_after = Pt(0)
    fmt.first_line_indent = Twips(360) if role in {"transition", "substantive"} else None
    ppr = paragraph._p.get_or_add_pPr()
    bidi = ppr.find(qn("w:bidi"))
    if bidi is None:
        bidi = OxmlElement("w:bidi")
        ppr.append(bidi)
    bidi.set(qn("w:val"), "1")


def _docx_bytes(
    paragraphs: list[str], formatting: list[dict[str, str | None]]
) -> bytes:
    try:
        from docx import Document
        from docx.oxml import OxmlElement
        from docx.oxml.ns import qn
        from docx.shared import Inches, Pt
    except ImportError as exc:  # pragma: no cover - guarded by declared dev dependency
        raise DraftCreationError("the host Documents runtime must provide python-docx") from exc

    document = Document()
    section = document.sections[0]
    section.top_margin = Inches(1)
    section.bottom_margin = Inches(1)
    section.left_margin = Inches(1)
    section.right_margin = Inches(1)

    style = document.styles["Normal"]
    style.font.name = "Arial"
    style.font.size = Pt(16)
    rpr = style._element.get_or_add_rPr()
    rfonts = rpr.get_or_add_rFonts()
    for slot in ("ascii", "hAnsi", "eastAsia", "cs"):
        rfonts.set(qn(f"w:{slot}"), "Arial")
    for tag in ("sz", "szCs"):
        element = rpr.find(qn(f"w:{tag}"))
        if element is None:
            element = OxmlElement(f"w:{tag}")
            rpr.append(element)
        element.set(qn("w:val"), "32")

    for text, item in zip(paragraphs, formatting):
        role = str(item["role"])
        opening = item["opening_phrase"]
        paragraph = document.add_paragraph()
        _set_paragraph_format(paragraph, role)
        if role == "substantive":
            assert isinstance(opening, str)
            lead = paragraph.add_run(opening)
            _set_run_format(lead, bold=True)
            if remainder := text[len(opening):]:
                tail = paragraph.add_run(remainder)
                _set_run_format(tail, bold=False)
        else:
            run = paragraph.add_run(text)
            _set_run_format(run, bold=role in {"title", "transition"})

    stream = io.BytesIO()
    document.save(stream)
    return stream.getvalue()


def _extract_docx_text(payload: bytes) -> str:
    from xml.etree import ElementTree as ET

    try:
        with zipfile.ZipFile(io.BytesIO(payload)) as archive:
            if archive.testzip() is not None:
                raise DraftCreationError("DOCX ZIP CRC verification failed")
            root = ET.fromstring(archive.read("word/document.xml"))
    except (KeyError, ValueError, ET.ParseError, zipfile.BadZipFile) as exc:
        raise DraftCreationError("DOCX structural reopen failed") from exc
    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    return "\n\n".join(
        "".join(node.text or "" for node in paragraph.findall(".//w:t", ns))
        for paragraph in root.findall(".//w:body/w:p", ns)
    )


def _verify_docx_text(payload: bytes, expected: str) -> None:
    if _extract_docx_text(payload) != expected:
        raise DraftCreationError("DOCX XML extraction did not preserve the checked ruling")
    try:
        from docx import Document

        reopened = Document(io.BytesIO(payload))
    except Exception as exc:
        raise DraftCreationError("python-docx structural reopen failed") from exc
    if "\n\n".join(paragraph.text for paragraph in reopened.paragraphs) != expected:
        raise DraftCreationError("python-docx reopen did not preserve the checked ruling")


def _metadata_yaml(metadata: dict[str, Any], filename: str) -> bytes:
    required = {
        "kanoonak", "state", "case", "kind", "based_on", "directive_version",
        "local_persona_updated", "artifact_sha256", "ruling_text_sha256",
    }
    missing = required - set(metadata)
    if missing:
        raise DraftCreationError(f"metadata missing required fields: {sorted(missing)}")
    if metadata["kanoonak"] != "draft" or metadata["state"] != "مسودة":
        raise DraftCreationError("DOCX helper creates drafts only")
    if metadata["kind"] not in ALLOWED_KINDS:
        raise DraftCreationError("metadata kind is unsupported")
    if not isinstance(metadata["case"], dict) or not metadata["case"]:
        raise DraftCreationError("metadata case tuple is required")
    for field in ("artifact_sha256", "ruling_text_sha256"):
        if not DIGEST_RE.fullmatch(str(metadata[field])):
            raise DraftCreationError(f"metadata {field} is invalid")
    fields = [
        ("kanoonak", metadata["kanoonak"]), ("state", metadata["state"]),
        ("case", metadata["case"]), ("kind", metadata["kind"]),
    ]
    if "subject" in metadata:
        fields.append(("subject", metadata["subject"]))
    fields.extend([
        ("based_on", metadata["based_on"]),
        ("directive_version", metadata["directive_version"]),
        ("local_persona_updated", metadata["local_persona_updated"]),
        ("ruling_text_sha256", metadata["ruling_text_sha256"]),
        ("artifact_sha256", metadata["artifact_sha256"]),
        ("artifact", filename),
    ])
    try:
        lines = [
            f"{key}: {json.dumps(value, ensure_ascii=False, separators=(',', ':'))}"
            for key, value in fields
        ]
    except (TypeError, ValueError) as exc:
        raise DraftCreationError("metadata contains a non-JSON value") from exc
    return ("---\n" + "\n".join(lines) + "\n---\n").encode("utf-8")


def _verify_metadata_payload(
    payload: bytes, *, filename: str, ruling_digest: str, artifact_digest: str
) -> None:
    try:
        text = payload.decode("utf-8", errors="strict")
        lines = text.splitlines()
        if len(lines) < 3 or lines[0] != "---" or lines[-1] != "---":
            raise ValueError("front-matter fence missing")
        parsed: dict[str, Any] = {}
        for line in lines[1:-1]:
            key, separator, raw = line.partition(": ")
            if not separator or not key or key in parsed:
                raise ValueError("invalid or duplicate sidecar field")
            parsed[key] = json.loads(raw)
    except (UnicodeError, ValueError, json.JSONDecodeError) as exc:
        raise DraftCreationError("metadata sidecar structural reopen failed") from exc
    expected = {
        "artifact": filename,
        "ruling_text_sha256": ruling_digest,
        "artifact_sha256": artifact_digest,
    }
    if any(parsed.get(key) != value for key, value in expected.items()):
        raise DraftCreationError("metadata sidecar digest or artifact binding mismatch")


def _windows_extended(path: Path) -> str:
    raw = str(path)
    absolute = raw if raw.startswith("\\\\?\\") else str(path.absolute())
    if absolute.startswith("\\\\?\\"):
        extended = absolute
    elif absolute.startswith("\\\\"):
        extended = "\\\\?\\UNC\\" + absolute[2:]
    else:
        extended = "\\\\?\\" + absolute
    if len(extended.encode("utf-16-le")) // 2 + 1 > WINDOWS_MAX_PATH_UTF16:
        raise DraftCreationError(
            "unsupported-path-length: مسار مجلد التسليم أطول من الحد الذي يدعمه هذا الناشر."
        )
    for component in Path(absolute).parts[1:]:
        if len(component.encode("utf-16-le")) // 2 > WINDOWS_MAX_COMPONENT_UTF16:
            raise DraftCreationError(
                "unsupported-path-length: مسار مجلد التسليم أطول من الحد الذي يدعمه هذا الناشر."
            )
    return extended


def _configure_kernel32(kernel32):
    """Pin every Windows ABI used by the publisher before the first call."""
    from ctypes import wintypes

    signatures = {
        "GetVolumePathNameW": (
            [wintypes.LPCWSTR, wintypes.LPWSTR, wintypes.DWORD],
            wintypes.BOOL,
        ),
        "GetVolumeInformationW": (
            [
                wintypes.LPCWSTR,
                wintypes.LPWSTR,
                wintypes.DWORD,
                wintypes.LPDWORD,
                wintypes.LPDWORD,
                wintypes.LPDWORD,
                wintypes.LPWSTR,
                wintypes.DWORD,
            ],
            wintypes.BOOL,
        ),
        "GetDriveTypeW": ([wintypes.LPCWSTR], wintypes.UINT),
        "GetFileAttributesW": ([wintypes.LPCWSTR], wintypes.DWORD),
        "CreateFileW": (
            [
                wintypes.LPCWSTR,
                wintypes.DWORD,
                wintypes.DWORD,
                wintypes.LPVOID,
                wintypes.DWORD,
                wintypes.DWORD,
                wintypes.HANDLE,
            ],
            wintypes.HANDLE,
        ),
        "CreateHardLinkW": (
            [wintypes.LPCWSTR, wintypes.LPCWSTR, wintypes.LPVOID],
            wintypes.BOOL,
        ),
        "WriteFile": (
            [wintypes.HANDLE, wintypes.LPCVOID, wintypes.DWORD, wintypes.LPDWORD, wintypes.LPVOID],
            wintypes.BOOL,
        ),
        "ReadFile": (
            [wintypes.HANDLE, wintypes.LPVOID, wintypes.DWORD, wintypes.LPDWORD, wintypes.LPVOID],
            wintypes.BOOL,
        ),
        "FlushFileBuffers": ([wintypes.HANDLE], wintypes.BOOL),
        "SetFilePointerEx": (
            [wintypes.HANDLE, ctypes.c_longlong, ctypes.POINTER(ctypes.c_longlong), wintypes.DWORD],
            wintypes.BOOL,
        ),
        "GetFileInformationByHandle": (
            [wintypes.HANDLE, ctypes.POINTER(_WindowsFileInformation)],
            wintypes.BOOL,
        ),
        "SetFileInformationByHandle": (
            [wintypes.HANDLE, ctypes.c_int, wintypes.LPVOID, wintypes.DWORD],
            wintypes.BOOL,
        ),
        "CreateSymbolicLinkW": (
            [wintypes.LPCWSTR, wintypes.LPCWSTR, wintypes.DWORD],
            wintypes.BOOLEAN,
        ),
        "CloseHandle": ([wintypes.HANDLE], wintypes.BOOL),
    }
    for name, (argtypes, restype) in signatures.items():
        function = getattr(kernel32, name)
        function.argtypes = argtypes
        function.restype = restype
    return kernel32


def _kernel32():
    return _configure_kernel32(ctypes.WinDLL("kernel32", use_last_error=True))


@dataclass
class _WindowsLeaf:
    path: Path
    handle: object
    identity: tuple[int, int]


def _windows_invalid_handle(handle: object) -> bool:
    from ctypes import wintypes

    return handle == wintypes.HANDLE(-1).value


def _windows_handle_identity(kernel32, handle: object) -> tuple[int, int]:
    info = _WindowsFileInformation()
    if not kernel32.GetFileInformationByHandle(handle, ctypes.byref(info)):
        raise OSError(ctypes.get_last_error(), "GetFileInformationByHandle failed")
    file_index = (int(info.nFileIndexHigh) << 32) | int(info.nFileIndexLow)
    return int(info.dwVolumeSerialNumber), file_index


def _windows_handle_bytes(kernel32, handle: object) -> bytes:
    from ctypes import wintypes

    if not kernel32.SetFilePointerEx(handle, 0, None, 0):
        raise OSError(ctypes.get_last_error(), "SetFilePointerEx failed")
    chunks: list[bytes] = []
    while True:
        buffer = ctypes.create_string_buffer(1024 * 1024)
        read = wintypes.DWORD()
        if not kernel32.ReadFile(handle, buffer, len(buffer), ctypes.byref(read), None):
            raise OSError(ctypes.get_last_error(), "ReadFile failed")
        if read.value == 0:
            return b"".join(chunks)
        chunks.append(buffer.raw[: read.value])


def _windows_write_handle(kernel32, handle: object, payload: bytes) -> None:
    from ctypes import wintypes

    offset = 0
    while offset < len(payload):
        chunk = payload[offset : offset + 1024 * 1024]
        buffer = ctypes.create_string_buffer(chunk)
        written = wintypes.DWORD()
        if not kernel32.WriteFile(handle, buffer, len(chunk), ctypes.byref(written), None):
            raise OSError(ctypes.get_last_error(), "WriteFile failed")
        if written.value == 0:
            raise DraftCreationError("Windows staged write was short")
        offset += written.value
    if not kernel32.FlushFileBuffers(handle):
        raise OSError(ctypes.get_last_error(), "FlushFileBuffers failed")
    if _windows_handle_bytes(kernel32, handle) != payload:
        raise DraftCreationError("Windows staged payload reread mismatch")


def _windows_set_disposition(kernel32, leaf: _WindowsLeaf) -> bool:
    disposition = _WindowsFileDispositionInfo(True)
    return bool(
        kernel32.SetFileInformationByHandle(
            leaf.handle,
            4,  # FileDispositionInfo
            ctypes.byref(disposition),
            ctypes.sizeof(disposition),
        )
    )


def _windows_close_leaf(kernel32, leaf: _WindowsLeaf, *, delete_link: bool) -> bool:
    disposed = True
    if delete_link:
        disposed = _windows_set_disposition(kernel32, leaf)
    closed = bool(kernel32.CloseHandle(leaf.handle))
    leaf.handle = None
    return disposed and closed


def _windows_create_stage_leaf(
    delivery_dir: Path, suffix: str, payload: bytes
) -> _WindowsLeaf:
    from ctypes import wintypes

    kernel32 = _kernel32()
    desired_access = 0x80000000 | 0x40000000 | 0x00010000  # READ | WRITE | DELETE
    share_read_only = 0x00000001
    create_new = 1
    flags = 0x00000100 | 0x00200000 | 0x80000000  # TEMPORARY | OPEN_REPARSE | WRITE_THROUGH
    for _ in range(16):
        path = delivery_dir / f".kanoonak-stage-{secrets.token_hex(12)}{suffix}"
        _windows_extended(path)
        handle = kernel32.CreateFileW(
            _windows_extended(path),
            desired_access,
            share_read_only,
            None,
            create_new,
            flags,
            None,
        )
        if _windows_invalid_handle(handle):
            error = ctypes.get_last_error()
            if error in {80, 183}:
                continue
            raise OSError(error, "CreateFileW CREATE_NEW stage leaf failed", path)
        leaf = _WindowsLeaf(path, handle, _windows_handle_identity(kernel32, handle))
        try:
            attributes = kernel32.GetFileAttributesW(_windows_extended(path))
            if attributes == 0xFFFFFFFF or attributes & 0x400:
                raise DraftCreationError("Windows stage leaf is missing or reparse-backed")
            _windows_write_handle(kernel32, handle, payload)
            return leaf
        except Exception:
            _windows_close_leaf(kernel32, leaf, delete_link=True)
            raise
    raise DraftCreationError("could not allocate a native Windows stage leaf")


def _windows_open_final_leaf(path: Path, *, deny_mutation: bool) -> _WindowsLeaf:
    kernel32 = _kernel32()
    desired_access = 0x80000000  # GENERIC_READ
    share = 0x00000001 if deny_mutation else 0x00000001 | 0x00000002 | 0x00000004
    handle = kernel32.CreateFileW(
        _windows_extended(path),
        desired_access,
        share,
        None,
        3,  # OPEN_EXISTING
        0x00200000,  # FILE_FLAG_OPEN_REPARSE_POINT
        None,
    )
    if _windows_invalid_handle(handle):
        raise OSError(ctypes.get_last_error(), "CreateFileW final leaf failed", path)
    leaf = _WindowsLeaf(path, handle, _windows_handle_identity(kernel32, handle))
    attributes = kernel32.GetFileAttributesW(_windows_extended(path))
    if attributes == 0xFFFFFFFF or attributes & 0x400:
        _windows_close_leaf(kernel32, leaf, delete_link=False)
        raise DraftCreationError("Windows final leaf is missing or reparse-backed")
    return leaf


def _windows_remove_final_leaf(kernel32, anchor: _WindowsLeaf) -> bool:
    """Delete only the currently opened link when its identity still matches."""
    cleanup_access = 0x80000000 | 0x00010000  # READ | DELETE
    share_all = 0x00000001 | 0x00000002 | 0x00000004
    handle = kernel32.CreateFileW(
        _windows_extended(anchor.path),
        cleanup_access,
        share_all,
        None,
        3,
        0x00200000,
        None,
    )
    if _windows_invalid_handle(handle):
        return False
    cleanup = _WindowsLeaf(
        anchor.path, handle, _windows_handle_identity(kernel32, handle)
    )
    attributes = kernel32.GetFileAttributesW(_windows_extended(anchor.path))
    if attributes == 0xFFFFFFFF or attributes & 0x400 or cleanup.identity != anchor.identity:
        _windows_close_leaf(kernel32, cleanup, delete_link=False)
        return False
    return _windows_close_leaf(kernel32, cleanup, delete_link=True)


def _windows_publish_pair(
    *,
    delivery_dir: Path,
    target: Path,
    sidecar: Path,
    payload: bytes,
    metadata_payload: bytes,
    ruling_text: str,
    ruling_digest: str,
    artifact_digest: str,
) -> tuple[tuple[int, int], tuple[int, int]] | None:
    kernel32 = _kernel32()
    staged_sidecar = _windows_create_stage_leaf(delivery_dir, ".metadata", metadata_payload)
    staged_docx: _WindowsLeaf | None = None
    final_sidecar: _WindowsLeaf | None = None
    final_docx: _WindowsLeaf | None = None
    locked_sidecar: _WindowsLeaf | None = None
    locked_docx: _WindowsLeaf | None = None
    success = False
    try:
        staged_docx = _windows_create_stage_leaf(delivery_dir, ".docx", payload)
        _verify_metadata_payload(
            _windows_handle_bytes(kernel32, staged_sidecar.handle),
            filename=target.name,
            ruling_digest=ruling_digest,
            artifact_digest=artifact_digest,
        )
        _verify_docx_text(_windows_handle_bytes(kernel32, staged_docx.handle), ruling_text)
        try:
            _link_noreplace(staged_sidecar.path, sidecar)
        except FileExistsError:
            return None
        final_sidecar = _windows_open_final_leaf(sidecar, deny_mutation=False)
        if final_sidecar.identity != staged_sidecar.identity:
            raise DraftCreationError("published Windows sidecar identity mismatch")
        try:
            _link_noreplace(staged_docx.path, target)
        except FileExistsError:
            return None
        final_docx = _windows_open_final_leaf(target, deny_mutation=False)
        if final_docx.identity != staged_docx.identity:
            raise DraftCreationError("published Windows DOCX identity mismatch")

        if not _windows_close_leaf(kernel32, staged_sidecar, delete_link=True):
            raise DraftCreationError("could not remove native Windows sidecar stage link")
        if not _windows_close_leaf(kernel32, staged_docx, delete_link=True):
            raise DraftCreationError("could not remove native Windows DOCX stage link")
        staged_docx = None

        locked_sidecar = _windows_open_final_leaf(sidecar, deny_mutation=True)
        locked_docx = _windows_open_final_leaf(target, deny_mutation=True)
        if locked_sidecar.identity != final_sidecar.identity or locked_docx.identity != final_docx.identity:
            raise DraftCreationError("published Windows leaf changed during stage cleanup")

        final_metadata = _windows_handle_bytes(kernel32, locked_sidecar.handle)
        final_payload = _windows_handle_bytes(kernel32, locked_docx.handle)
        if hashlib.sha256(final_payload).hexdigest() != artifact_digest:
            raise DraftCreationError("published Windows DOCX digest mismatch")
        _verify_docx_text(final_payload, ruling_text)
        _verify_metadata_payload(
            final_metadata,
            filename=target.name,
            ruling_digest=ruling_digest,
            artifact_digest=artifact_digest,
        )
        success = True
        return locked_docx.identity, locked_sidecar.identity
    finally:
        # A stage handle names exactly the link this invocation created. A
        # separately opened cleanup handle is identity-compared with the held
        # final handle before disposition, so a replacement is never removed.
        cleanup_failed: list[Path] = []
        for leaf in (staged_docx, staged_sidecar):
            if leaf is not None and leaf.handle is not None:
                if not _windows_close_leaf(kernel32, leaf, delete_link=True):
                    cleanup_failed.append(leaf.path)
        for locked, opened in (
            (locked_docx, final_docx),
            (locked_sidecar, final_sidecar),
        ):
            if success:
                for leaf in (locked, opened):
                    if leaf is not None and leaf.handle is not None:
                        _windows_close_leaf(kernel32, leaf, delete_link=False)
                continue
            # A mutation-denying verification handle cannot share the DELETE
            # access needed by cleanup. Close it, retain the permissive handle
            # as the stable identity anchor, then compare a new DELETE handle
            # with that anchor before setting disposition.
            if locked is not None and locked.handle is not None:
                _windows_close_leaf(kernel32, locked, delete_link=False)
            if opened is not None and opened.handle is not None:
                if not _windows_remove_final_leaf(kernel32, opened):
                    cleanup_failed.append(opened.path)
                _windows_close_leaf(kernel32, opened, delete_link=False)
            elif locked is not None:
                cleanup_failed.append(locked.path)
        if cleanup_failed and not success:
            raise DraftCreationError(
                "Windows publication failed; preserved unprovable orphan(s): "
                + ", ".join(str(path) for path in cleanup_failed)
            )


def _windows_capability_probe(path: Path) -> object:
    if os.name != "nt":
        return None
    from ctypes import wintypes

    kernel32 = _kernel32()
    extended = _windows_extended(path)
    volume_path = ctypes.create_unicode_buffer(32768)
    if not kernel32.GetVolumePathNameW(extended, volume_path, len(volume_path)):
        raise DraftCreationError("Windows volume capability probe failed")
    fs_name = ctypes.create_unicode_buffer(64)
    if not kernel32.GetVolumeInformationW(
        volume_path.value, None, 0, None, None, None, fs_name, len(fs_name)
    ):
        raise DraftCreationError("Windows volume capability probe failed")
    if fs_name.value.upper() != "NTFS":
        raise DraftCreationError("delivery requires a local NTFS filesystem")
    if kernel32.GetDriveTypeW(volume_path.value) != 3:  # DRIVE_FIXED
        raise DraftCreationError("delivery requires a fixed local NTFS filesystem")
    file_attribute_reparse_point = 0x400
    ancestors = (path, *path.parents)
    for ancestor in ancestors:
        attributes = kernel32.GetFileAttributesW(_windows_extended(ancestor))
        if attributes == 0xFFFFFFFF:
            raise DraftCreationError("Windows path capability probe failed")
        if attributes & file_attribute_reparse_point:
            raise DraftCreationError("reparse-backed delivery directories are unsupported")
        if ancestor.parent == ancestor:
            break
    create_file = kernel32.CreateFileW
    create_file.restype = wintypes.HANDLE
    handles: list[object] = []
    try:
        for ancestor in ancestors:
            handle = create_file(
                _windows_extended(ancestor), 0, 0x00000001 | 0x00000002, None, 3,
                0x02000000 | 0x00200000, None,
            )
            if handle == wintypes.HANDLE(-1).value:
                raise DraftCreationError(
                    "could not hold the Windows delivery ancestor identities"
                )
            handles.append(handle)
    except Exception:
        for handle in handles:
            kernel32.CloseHandle(handle)
        raise
    return handles


def _close_windows_handle(handle: object) -> None:
    if os.name == "nt" and handle is not None:
        kernel32 = _kernel32()
        for item in handle if isinstance(handle, list) else [handle]:
            kernel32.CloseHandle(item)


def _link_noreplace(
    source: Path,
    target: Path,
    *,
    source_dir_fd: int | None = None,
    target_dir_fd: int | None = None,
) -> None:
    if os.name != "nt":
        os.link(
            source if source_dir_fd is None else source.name,
            target if target_dir_fd is None else target.name,
            src_dir_fd=source_dir_fd,
            dst_dir_fd=target_dir_fd,
            follow_symlinks=False,
        )
        return
    kernel32 = _kernel32()
    if not kernel32.CreateHardLinkW(_windows_extended(target), _windows_extended(source), None):
        error = ctypes.get_last_error()
        if error in {80, 183}:
            raise FileExistsError(error, "publication target already exists", target)
        raise OSError(error, "CreateHardLinkW failed", target)


def _sync_directory(path: Path, *, dir_fd: int | None = None) -> None:
    if os.name == "nt":
        return
    if dir_fd is not None:
        os.fsync(dir_fd)
        return
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(path, flags)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def _remove_if_identity(
    path: Path, identity: tuple[int, int], *, dir_fd: int | None = None
) -> bool:
    try:
        candidate: Path | str = path if dir_fd is None else path.name
        if _identity(candidate, dir_fd=dir_fd) != identity:
            return False
        if dir_fd is None:
            path.unlink()
        else:
            os.unlink(path.name, dir_fd=dir_fd)
        return True
    except OSError:
        return False


def _occupied_numbers(
    delivery_dir: Path, kind: str, *, dir_fd: int | None = None
) -> set[int]:
    occupied: set[int] = set()
    names = os.listdir(dir_fd) if dir_fd is not None else [child.name for child in delivery_dir.iterdir()]
    for name in names:
        match = DOCX_DRAFT_RE.fullmatch(name) or SIDECAR_DRAFT_RE.fullmatch(name)
        if match and match.group(1) == kind:
            occupied.add(int(match.group(2)))
    return occupied


def _private_stage(delivery_dir: Path, *, dir_fd: int | None = None) -> Path:
    for _ in range(16):
        name = f".kanoonak-docx-stage-{secrets.token_hex(8)}"
        path = delivery_dir / name
        try:
            if dir_fd is None:
                path.mkdir(mode=0o700)
            else:
                os.mkdir(name, mode=0o700, dir_fd=dir_fd)
            return path
        except FileExistsError:
            continue
    raise DraftCreationError("could not allocate a private DOCX staging directory")


def _cleanup_stage(
    stage: Path, *, stage_fd: int | None = None, delivery_fd: int | None = None
) -> None:
    if stage_fd is not None and delivery_fd is not None:
        try:
            for name in os.listdir(stage_fd):
                os.unlink(name, dir_fd=stage_fd)
            stage_identity = (os.fstat(stage_fd).st_dev, os.fstat(stage_fd).st_ino)
            if _identity(stage.name, dir_fd=delivery_fd) == stage_identity:
                os.rmdir(stage.name, dir_fd=delivery_fd)
        except OSError:
            pass
        return
    try:
        for child in stage.iterdir():
            child.unlink()
        stage.rmdir()
    except OSError:
        pass


def create_draft(
    *,
    delivery_dir: Path,
    grant_label: str,
    storage_classification: str,
    kind: str,
    ruling_text: str,
    expected_ruling_sha256: str,
    formatting: dict[str, Any],
    metadata: dict[str, Any],
) -> PublicationResult:
    if grant_label not in ALLOWED_GRANT_LABELS:
        raise DraftCreationError("grant label must be drafts or library-download")
    if storage_classification not in ALLOWED_STORAGE_CLASSIFICATIONS:
        raise DraftCreationError("delivery directory must be classified local-unsynchronized")
    if kind not in ALLOWED_KINDS:
        raise DraftCreationError("kind must be حكم, حكم-تمهيدي, or قرار")
    if not isinstance(ruling_text, str):
        raise DraftCreationError("ruling_text must be a string")
    if not isinstance(expected_ruling_sha256, str) or not DIGEST_RE.fullmatch(expected_ruling_sha256):
        raise DraftCreationError("expected_ruling_sha256 is invalid")
    if not isinstance(formatting, dict) or not isinstance(metadata, dict):
        raise DraftCreationError("formatting and metadata must be objects")
    delivery_dir = Path(os.path.abspath(os.fspath(delivery_dir)))
    if not delivery_dir.is_dir() or delivery_dir.is_symlink():
        raise DraftCreationError("delivery directory must be one exact existing real directory")

    check_ruling_text, parse_paragraphs = _universal_api()
    checked = check_ruling_text(ruling_text)
    if not isinstance(checked, dict) or checked.get("conforms") is not True:
        raise DraftCreationError("ruling text did not pass the universal checker")
    actual_ruling_sha256 = hashlib.sha256(ruling_text.encode("utf-8")).hexdigest()
    if checked.get("ruling_sha256") != actual_ruling_sha256:
        raise DraftCreationError("universal checker returned an inconsistent ruling digest")
    if actual_ruling_sha256 != expected_ruling_sha256:
        raise DraftCreationError("checked ruling digest does not match expected_ruling_sha256")
    paragraphs = parse_paragraphs(ruling_text)
    format_items = _validate_formatting(formatting, paragraphs)
    payload = _docx_bytes(paragraphs, format_items)
    _verify_docx_text(payload, ruling_text)
    artifact_sha256 = hashlib.sha256(payload).hexdigest()

    metadata = dict(metadata)
    metadata["kind"] = kind
    metadata["ruling_text_sha256"] = actual_ruling_sha256
    metadata["artifact_sha256"] = artifact_sha256

    unix_delivery_fd: int | None = None
    windows_handle: object = None
    if os.name != "nt":
        if os.open not in getattr(os, "supports_dir_fd", ()) or os.link not in getattr(os, "supports_dir_fd", ()):
            raise DraftCreationError("host lacks descriptor-anchored publication primitives")
        flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
        unix_delivery_fd = os.open(delivery_dir, flags)
        directory_stat = os.fstat(unix_delivery_fd)
        directory_identity = (directory_stat.st_dev, directory_stat.st_ino)
    else:
        windows_handle = _windows_capability_probe(delivery_dir)
        directory_identity = _identity(delivery_dir)
    try:
        for number in range(1, 100):
            if number in _occupied_numbers(delivery_dir, kind, dir_fd=unix_delivery_fd):
                continue
            basename = f"مسودة-{kind}-{number:02d}"
            target = delivery_dir / f"{basename}.docx"
            sidecar = delivery_dir / f"{basename}.metadata.yaml"
            if os.name == "nt":
                _windows_extended(target)
                _windows_extended(sidecar)
                _windows_extended(
                    delivery_dir / (".kanoonak-stage-" + "0" * 24 + ".metadata")
                )
                _windows_extended(
                    delivery_dir / (".kanoonak-stage-" + "0" * 24 + ".docx")
                )
            metadata_payload = _metadata_yaml(metadata, target.name)
            _verify_metadata_payload(
                metadata_payload,
                filename=target.name,
                ruling_digest=actual_ruling_sha256,
                artifact_digest=artifact_sha256,
            )
            if os.name == "nt":
                published = _windows_publish_pair(
                    delivery_dir=delivery_dir,
                    target=target,
                    sidecar=sidecar,
                    payload=payload,
                    metadata_payload=metadata_payload,
                    ruling_text=ruling_text,
                    ruling_digest=actual_ruling_sha256,
                    artifact_digest=artifact_sha256,
                )
                if published is None:
                    continue
                docx_identity, sidecar_identity = published
                if _identity(delivery_dir) != directory_identity:
                    raise DraftCreationError("Windows delivery directory changed during publication")
                return PublicationResult(
                    docx=target,
                    metadata=sidecar,
                    docx_identity=docx_identity,
                    metadata_identity=sidecar_identity,
                    ruling_text_sha256=actual_ruling_sha256,
                    artifact_sha256=artifact_sha256,
                )
            stage = _private_stage(delivery_dir, dir_fd=unix_delivery_fd)
            staged_sidecar = stage / "metadata.yaml"
            staged_docx = stage / "artifact.docx"
            unix_stage_fd: int | None = None
            if unix_delivery_fd is not None:
                flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
                unix_stage_fd = os.open(stage.name, flags, dir_fd=unix_delivery_fd)
            sidecar_stage_identity: tuple[int, int] | None = None
            docx_stage_identity: tuple[int, int] | None = None
            created_sidecar_identity: tuple[int, int] | None = None
            try:
                sidecar_stage_identity = _write_complete_exclusive(
                    staged_sidecar.name if unix_stage_fd is not None else staged_sidecar,
                    metadata_payload,
                    dir_fd=unix_stage_fd,
                )
                docx_stage_identity = _write_complete_exclusive(
                    staged_docx.name if unix_stage_fd is not None else staged_docx,
                    payload,
                    dir_fd=unix_stage_fd,
                )
                _read_exact(
                    _relative_when_anchored(staged_sidecar, unix_stage_fd),
                    metadata_payload,
                    dir_fd=unix_stage_fd,
                )
                _read_exact(
                    _relative_when_anchored(staged_docx, unix_stage_fd),
                    payload,
                    dir_fd=unix_stage_fd,
                )
                staged_docx_bytes = _read_bytes(
                    _relative_when_anchored(staged_docx, unix_stage_fd),
                    dir_fd=unix_stage_fd,
                )
                if hashlib.sha256(staged_docx_bytes).hexdigest() != artifact_sha256:
                    raise DraftCreationError("staged DOCX digest mismatch")
                _verify_docx_text(staged_docx_bytes, ruling_text)
                _verify_metadata_payload(
                    _read_bytes(
                        _relative_when_anchored(staged_sidecar, unix_stage_fd),
                        dir_fd=unix_stage_fd,
                    ),
                    filename=target.name,
                    ruling_digest=actual_ruling_sha256,
                    artifact_digest=artifact_sha256,
                )
                if _identity(delivery_dir) != directory_identity:
                    raise DraftCreationError("delivery directory changed before publication")
                try:
                    _link_noreplace(
                        staged_sidecar,
                        sidecar,
                        source_dir_fd=unix_stage_fd,
                        target_dir_fd=unix_delivery_fd,
                    )
                except FileExistsError:
                    continue
                created_sidecar_identity = sidecar_stage_identity
                try:
                    _link_noreplace(
                        staged_docx,
                        target,
                        source_dir_fd=unix_stage_fd,
                        target_dir_fd=unix_delivery_fd,
                    )
                except FileExistsError:
                    if not _remove_if_identity(
                        sidecar, created_sidecar_identity, dir_fd=unix_delivery_fd
                    ):
                        raise DraftCreationError(f"concurrent collision left preserved orphan {sidecar}")
                    continue
                docx_identity = _identity(
                    _relative_when_anchored(target, unix_delivery_fd),
                    dir_fd=unix_delivery_fd,
                )
                sidecar_identity = _identity(
                    _relative_when_anchored(sidecar, unix_delivery_fd),
                    dir_fd=unix_delivery_fd,
                )
                if docx_identity != docx_stage_identity or sidecar_identity != sidecar_stage_identity:
                    raise DraftCreationError("published leaf identity mismatch")
                if _identity(delivery_dir) != directory_identity:
                    raise DraftCreationError("delivery directory changed during publication")
                _read_exact(
                    _relative_when_anchored(target, unix_delivery_fd),
                    payload,
                    dir_fd=unix_delivery_fd,
                )
                _read_exact(
                    _relative_when_anchored(sidecar, unix_delivery_fd),
                    metadata_payload,
                    dir_fd=unix_delivery_fd,
                )
                final_docx_bytes = _read_bytes(
                    _relative_when_anchored(target, unix_delivery_fd),
                    dir_fd=unix_delivery_fd,
                )
                if hashlib.sha256(final_docx_bytes).hexdigest() != artifact_sha256:
                    raise DraftCreationError("published DOCX digest mismatch")
                _verify_docx_text(final_docx_bytes, ruling_text)
                _verify_metadata_payload(
                    _read_bytes(
                        _relative_when_anchored(sidecar, unix_delivery_fd),
                        dir_fd=unix_delivery_fd,
                    ),
                    filename=target.name,
                    ruling_digest=actual_ruling_sha256,
                    artifact_digest=artifact_sha256,
                )
                _sync_directory(delivery_dir, dir_fd=unix_delivery_fd)
                return PublicationResult(
                    docx=target, metadata=sidecar,
                    docx_identity=docx_identity, metadata_identity=sidecar_identity,
                    ruling_text_sha256=actual_ruling_sha256,
                    artifact_sha256=artifact_sha256,
                )
            except Exception:
                orphaned: list[Path] = []
                for path, identity in ((target, docx_stage_identity), (sidecar, created_sidecar_identity)):
                    if identity is None:
                        continue
                    try:
                        _identity(
                            _relative_when_anchored(path, unix_delivery_fd),
                            dir_fd=unix_delivery_fd,
                        )
                    except OSError:
                        continue
                    if not _remove_if_identity(path, identity, dir_fd=unix_delivery_fd):
                        orphaned.append(path)
                if orphaned:
                    raise DraftCreationError(
                        "publication failed; preserved unprovable orphan(s): "
                        + ", ".join(str(path) for path in orphaned)
                    )
                raise
            finally:
                _cleanup_stage(
                    stage, stage_fd=unix_stage_fd, delivery_fd=unix_delivery_fd
                )
                if unix_stage_fd is not None:
                    os.close(unix_stage_fd)
        raise DraftCreationError("all two-digit draft numbers are already in use")
    finally:
        _close_windows_handle(windows_handle)
        if unix_delivery_fd is not None:
            os.close(unix_delivery_fd)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--delivery-dir", type=Path, required=True)
    parser.add_argument("--grant-label", choices=sorted(ALLOWED_GRANT_LABELS), required=True)
    parser.add_argument(
        "--storage-classification", choices=sorted(ALLOWED_STORAGE_CLASSIFICATIONS), required=True
    )
    parser.add_argument("--kind", choices=sorted(ALLOWED_KINDS), required=True)
    parser.add_argument("--ruling-file", type=Path, required=True)
    parser.add_argument("--expected-ruling-sha256", required=True)
    parser.add_argument("--formatting-json", type=Path, required=True)
    parser.add_argument("--metadata-json", type=Path, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        ruling_text = args.ruling_file.read_bytes().decode("utf-8", errors="strict")
        metadata = json.loads(args.metadata_json.read_text(encoding="utf-8"))
        formatting = json.loads(args.formatting_json.read_text(encoding="utf-8"))
        if not isinstance(metadata, dict) or not isinstance(formatting, dict):
            raise DraftCreationError("metadata and formatting JSON must be objects")
        result = create_draft(
            delivery_dir=args.delivery_dir,
            grant_label=args.grant_label,
            storage_classification=args.storage_classification,
            kind=args.kind,
            ruling_text=ruling_text,
            expected_ruling_sha256=args.expected_ruling_sha256,
            formatting=formatting,
            metadata=metadata,
        )
    except (OSError, UnicodeError, json.JSONDecodeError, DraftCreationError) as exc:
        print(f"DOCX draft creation refused: {exc}", file=sys.stderr)
        return 2
    print(json.dumps({
        "docx": str(result.docx), "metadata": str(result.metadata),
        "docx_identity": list(result.docx_identity),
        "metadata_identity": list(result.metadata_identity),
        "ruling_text_sha256": result.ruling_text_sha256,
        "artifact_sha256": result.artifact_sha256,
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
