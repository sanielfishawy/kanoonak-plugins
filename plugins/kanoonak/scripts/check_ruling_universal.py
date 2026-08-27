#!/usr/bin/env python3
"""Check ruling text for universal, mechanically observable invariants."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import unicodedata
from pathlib import Path
from typing import Any


UNIVERSAL_VERSION = "2026-08-26.1"
MAX_RULING_CODEPOINTS = 10_000

NOT_CHECKED = [
    "judicial-voice",
    "arabic-register",
    "legal-correctness",
    "factual-truth",
    "disposition-correctness",
    "exemplar-closeness",
    "source-review-completion",
    "approval",
    "signature",
    "issuance",
]

_ERRORS = {
    "invalid-utf8": "يجب أن يكون نص الحكم بترميز UTF-8 صالح.",
    "empty-ruling": "نص الحكم فارغ.",
    "ruling-too-long": (
        "نص الحكم يتجاوز الحد الأقصى البالغ 10000 حرف Unicode."
    ),
}

_CHECKS = (
    (
        "unicode-nfc-lf",
        "noncanonical-unicode-or-layout",
        "يجب أن يكون نص الحكم بتكوين Unicode NFC، وألا يستخدم لفصل الأسطر إلا LF، وألا يبدأ أو ينتهي بفاصل، وأن يفصل بين الفقرات بعلامتي LF فقط.",
    ),
    (
        "working-literals-absent",
        "working-literal-present",
        "يتضمن نص الحكم علامات أو عناوين مخصصة لبيانات العمل ويجب فصلها عن جسم الحكم.",
    ),
    (
        "unsafe-controls-absent",
        "unsafe-control-present",
        "يتضمن نص الحكم محارف تحكم أو اتجاه غير مسموح بها.",
    ),
    (
        "manual-indent-absent",
        "manual-indent-present",
        "تبدأ فقرة بمسافة يدوية؛ يجب استخدام إزاحة Word الحقيقية.",
    ),
    (
        "western-digits-only",
        "nonwestern-decimal-digit",
        "يتضمن نص الحكم أرقاماً ليست من الأرقام الغربية 0–9 المعتمدة.",
    ),
    (
        "slash-dates-unpadded",
        "padded-slash-date",
        "يتضمن نص الحكم تاريخاً بصفر بادئ في اليوم أو الشهر.",
    ),
)

_WORKING_PREFIXES = (
    "case:",
    "template:",
    "directive_version:",
    "skill_version:",
    "preflight:",
    "audit:",
)
_SLASH_DATE_RE = re.compile(
    r"(?<![0-9/])([0-9]{1,2})/([0-9]{1,2})/([0-9]{4})(?![0-9/])"
)
_MANUAL_INDENT = frozenset(
    "\u0020\u00a0\u1680\u202f\u205f\u3000"
    + "".join(chr(codepoint) for codepoint in range(0x2000, 0x200B))
)


def parse_paragraphs(value: str) -> list[str]:
    """Split canonical ruling text without normalizing or trimming it."""
    return value.split("\n\n")


def _error(code: str) -> dict[str, Any]:
    return {"error": {"code": code, "message_ar": _ERRORS[code]}}


def _decode(value: str | bytes) -> str | dict[str, Any]:
    if isinstance(value, str):
        try:
            value.encode("utf-8", errors="strict")
        except UnicodeEncodeError:
            return _error("invalid-utf8")
        return value
    if isinstance(value, bytes):
        try:
            return value.decode("utf-8", errors="strict")
        except UnicodeDecodeError:
            return _error("invalid-utf8")
    raise TypeError("ruling text must be str or bytes")


def _canonical_layout(value: str) -> bool:
    if unicodedata.normalize("NFC", value) != value:
        return False
    if "\r" in value or "\u2028" in value or "\u2029" in value:
        return False
    if value.startswith("\n") or value.endswith("\n"):
        return False
    paragraphs = parse_paragraphs(value)
    return all(
        paragraph
        and not paragraph.isspace()
        and "\n" not in paragraph
        for paragraph in paragraphs
    )


def _working_literals_absent(value: str) -> bool:
    for line in value.split("\n"):
        stripped = line.strip(" ")
        lowered = stripped.lower()
        if (
            stripped in {"---", "..."}
            or stripped.startswith("#")
            or lowered.startswith(_WORKING_PREFIXES)
        ):
            return False
    return True


def _unsafe_controls_absent(value: str) -> bool:
    for character in value:
        codepoint = ord(character)
        if (
            0x0000 <= codepoint <= 0x0009
            or 0x000B <= codepoint <= 0x001F
            or codepoint == 0x007F
            or codepoint in {0x200E, 0x200F}
            or 0x202A <= codepoint <= 0x202E
            or 0x2066 <= codepoint <= 0x2069
        ):
            return False
    return True


def _manual_indent_absent(value: str) -> bool:
    return all(
        not paragraph or paragraph[0] not in _MANUAL_INDENT
        for paragraph in parse_paragraphs(value)
    )


def _western_digits_only(value: str) -> bool:
    return all(not character.isdecimal() or "0" <= character <= "9" for character in value)


def _slash_dates_unpadded(value: str) -> bool:
    for match in _SLASH_DATE_RE.finditer(value):
        day_text, month_text = match.group(1), match.group(2)
        day, month = int(day_text), int(month_text)
        if 1 <= day <= 31 and 1 <= month <= 12:
            if (len(day_text) > 1 and day_text.startswith("0")) or (
                len(month_text) > 1 and month_text.startswith("0")
            ):
                return False
    return True


def check_ruling_text(value: str | bytes) -> dict[str, Any]:
    """Return the exact reviewed envelope without echoing ruling text."""
    decoded = _decode(value)
    if isinstance(decoded, dict):
        return decoded
    if not decoded:
        return _error("empty-ruling")
    if len(decoded) > MAX_RULING_CODEPOINTS:
        return _error("ruling-too-long")

    passed_values = (
        _canonical_layout(decoded),
        _working_literals_absent(decoded),
        _unsafe_controls_absent(decoded),
        _manual_indent_absent(decoded),
        _western_digits_only(decoded),
        _slash_dates_unpadded(decoded),
    )
    checks = []
    for (check_id, failure_code, message_ar), passed in zip(_CHECKS, passed_values):
        checks.append(
            {
                "id": check_id,
                "passed": passed,
                "code": None if passed else failure_code,
                "message_ar": None if passed else message_ar,
            }
        )
    failures = [check for check in checks if not check["passed"]]
    return {
        "universal_version": UNIVERSAL_VERSION,
        "conforms": not failures,
        "ruling_sha256": hashlib.sha256(decoded.encode("utf-8")).hexdigest(),
        "checks": checks,
        "failures": failures,
        "not_checked": list(NOT_CHECKED),
    }


def _main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ruling-file", required=True, type=Path)
    arguments = parser.parse_args(argv)
    result = check_ruling_text(arguments.ruling_file.read_bytes())
    json.dump(result, sys.stdout, ensure_ascii=False, separators=(",", ":"))
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
