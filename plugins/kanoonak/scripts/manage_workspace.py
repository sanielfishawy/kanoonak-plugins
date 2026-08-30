#!/usr/bin/env python3
"""Initialize Kanoonak files beneath the host-provided current directory.

The helper accepts no workspace path. The desktop host chooses one connected
folder and starts it with that folder as its process CWD.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import stat
import sys
import unicodedata
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Mapping, Sequence


CONVENTION = "2026-07-21"
PARENT_VERSION = "2026-08-28.1"
DATE_TOKEN = b"{{TODAY}}"
ASSET_DIRECTORY = Path(__file__).resolve().parents[1] / "assets" / "workspace"
CANONICAL_ROOT_FILES = ("README.md", "أسلوبي.md")
CANONICAL_CASE_FILES = ("الملخص.md", "المواعيد.md")
CANONICAL_CASE_DIRECTORIES = (
    "الوارد",
    "الحكم-المستأنف",
    "الصحف",
    "المذكرات",
    "تقارير-الخبرة",
    "اللائحة",
    "المسودات",
    "الأحكام",
)
DRAFTS_DIRECTORY = "المسودات"
MAX_SUMMARY_BYTES = 4 * 1024 * 1024

_SUMMARY_BODY_KEYS = ("الوقائع", "المسار الإجرائي", "ملاحظات")
_CASE_TYPES = {"استئناف", "التماس"}
_APPEAL_ROLES = {"أصلي", "منضم", "فرعي", "ضمني"}
_MEMBER_ROLES = _APPEAL_ROLES | {"التماس"}
_ROLE_ORDER = {"أصلي": 0, "منضم": 1, "فرعي": 2, "ضمني": 3}
_CAPACITIES = {"عامل", "صاحب-عمل", "أخرى"}
_FIRST_INSTANCE_ROLES = {"مدعي", "مدعى-عليه"}
_PARTY_APPEAL_ROLES = {"مستأنف", "مستأنف-ضده"}
_PARTY_PETITION_ROLES = {"ملتمس", "ملتمس-ضده"}
_STATUSES = {"منظورة", "محجوزة-للحكم", "محكومة", "مشطوبة", "مضمومة"}
_DEADLINE_KINDS = {"جلسة", "تقرير-خبير", "ميعاد-طعن", "تجديد", "أخرى"}
_DEADLINE_STATUSES = {"قادم", "تم", "ملغي"}
_NO_DEADLINES = "لا-مواعيد"

_PETITION_LEAF_RE = re.compile(
    r"التماس-(?P<number>[1-9][0-9]*)-لسنة-(?P<year>[0-9]{2})ق\Z"
)
_APPEAL_GROUP_RE = re.compile(
    r"(?P<numbers>[1-9][0-9]*(?:-و-[1-9][0-9]*)*)"
    r"-لسنة-(?P<year>[0-9]{2})ق(?P<separator>-و-|\Z)"
)
_LEGACY_MEMBER_RE = re.compile(
    r"  - case: \{number: (?P<number>[1-9][0-9]*), "
    r"judicial_year: (?P<year>[0-9]{1,2})\}\Z"
)
_LEGACY_ROLE_RE = re.compile(
    r"    role: (?P<role>أصلي|منضم|فرعي|ضمني|التماس)\Z"
)
MatterIdentity = tuple[
    str,
    int,
    int,
    str,
    str,
    tuple[tuple[int, int, str], ...],
]


@dataclass(frozen=True)
class WorkspaceResult:
    """The closed public result envelope; it never includes submitted content."""

    status: str
    reason: str
    blocking_item: str | None = None
    preserved_items: tuple[str, ...] = ()

    def public(self) -> dict[str, object]:
        result: dict[str, object] = {"status": self.status, "reason": self.reason}
        if self.blocking_item is not None:
            result["blocking_item"] = self.blocking_item
        if self.preserved_items:
            result["preserved_items"] = list(self.preserved_items)
        return result


class _RequestError(ValueError):
    """A constant, non-payload-bearing request rejection."""


class _NameCollision(ValueError):
    def __init__(self, name: str):
        super().__init__("normalization_collision")
        self.name = name


class _CreationFailure(OSError):
    """Creation failed before this invocation made the target visible."""


class _UncertainCreation(OSError):
    """Creation started, so the target is preserved as possibly visible."""


def _is_int(value: object) -> bool:
    return type(value) is int


def _is_number(value: object) -> bool:
    return (_is_int(value) or type(value) is float) and math.isfinite(value)


def _require_clean_strings(value: object) -> None:
    if isinstance(value, str):
        if (
            "\r" in value
            or "\x00" in value
            or unicodedata.normalize("NFC", value) != value
        ):
            raise _RequestError("invalid_request")
        return
    if type(value) is dict:
        for key, child in value.items():
            if not isinstance(key, str):
                raise _RequestError("invalid_request")
            _require_clean_strings(key)
            _require_clean_strings(child)
        return
    if type(value) is list:
        for child in value:
            _require_clean_strings(child)
        return
    if type(value) is float and not math.isfinite(value):
        raise _RequestError("invalid_request")


def _require_exact_mapping(
    value: object,
    required: set[str],
    optional: set[str] | None = None,
) -> dict[str, object]:
    if type(value) is not dict:
        raise _RequestError("invalid_request")
    optional = optional or set()
    actual = set(value)
    if not required <= actual or not actual <= required | optional:
        raise _RequestError("invalid_request")
    return value


def _require_nonempty_string(value: object) -> str:
    if not isinstance(value, str) or not value.strip():
        raise _RequestError("invalid_request")
    return value


def _require_positive_int(value: object) -> int:
    if not _is_int(value) or value <= 0:
        raise _RequestError("invalid_request")
    return value


def _require_judicial_year(value: object) -> int:
    if not _is_int(value) or value < 0 or value > 99:
        raise _RequestError("invalid_request")
    return value


def _require_iso_date(value: object) -> str:
    text = _require_nonempty_string(value)
    try:
        parsed = date.fromisoformat(text)
    except ValueError as exc:
        raise _RequestError("invalid_request") from exc
    if parsed.isoformat() != text:
        raise _RequestError("invalid_request")
    return text


def _valid_party_slug(value: str) -> bool:
    if value.startswith("-") or value.endswith("-") or "--" in value:
        return False
    return all(
        character == "-"
        or "0" <= character <= "9"
        or unicodedata.name(character, "").startswith("ARABIC LETTER")
        for character in value
    )


def _validate_year_tuple(
    value: object,
    *,
    include_type: bool,
    require_judicial: bool = False,
) -> dict[str, object]:
    if type(value) is not dict:
        raise _RequestError("invalid_request")
    year_type = value.get("year_type")
    if year_type not in {"قضائية", "ميلادية"}:
        raise _RequestError("invalid_request")
    if require_judicial and year_type != "قضائية":
        raise _RequestError("invalid_request")
    year_key = "judicial_year" if year_type == "قضائية" else "year"
    required = {"number", year_key, "year_type"}
    required.add("type" if include_type else "forum")
    mapping = _require_exact_mapping(value, required)
    _require_positive_int(mapping["number"])
    if year_key == "judicial_year":
        _require_judicial_year(mapping[year_key])
    elif not _is_int(mapping[year_key]) or not 1000 <= mapping[year_key] <= 9999:
        raise _RequestError("invalid_request")
    if include_type:
        if mapping["type"] != "استئناف":
            raise _RequestError("invalid_request")
    else:
        _require_nonempty_string(mapping["forum"])
    return mapping


def _validate_top_case(value: object) -> dict[str, object]:
    mapping = _require_exact_mapping(
        value, {"type", "number", "judicial_year", "year_type", "forum"}
    )
    if mapping["type"] not in _CASE_TYPES or mapping["year_type"] != "قضائية":
        raise _RequestError("invalid_request")
    _require_positive_int(mapping["number"])
    _require_judicial_year(mapping["judicial_year"])
    _require_nonempty_string(mapping["forum"])
    return mapping


def _validate_member_case(value: object) -> dict[str, object]:
    mapping = _require_exact_mapping(value, {"number", "judicial_year"})
    _require_positive_int(mapping["number"])
    _require_judicial_year(mapping["judicial_year"])
    return mapping


def _validate_summary_front_matter(value: object) -> MatterIdentity:
    summary = _require_exact_mapping(
        value,
        {
            "kanoonak",
            "convention",
            "case",
            "appeals",
            "petition_target",
            "parties",
            "claims",
            "valuation",
            "posture",
            "status",
            "updated",
        },
        {"sessions"},
    )
    if summary["kanoonak"] != "matter-summary" or summary["convention"] != CONVENTION:
        raise _RequestError("invalid_request")
    case = _validate_top_case(summary["case"])
    appeals = summary["appeals"]
    if type(appeals) is not list or not appeals:
        raise _RequestError("invalid_request")

    members: list[tuple[int, int, str]] = []
    member_keys: set[tuple[int, int]] = set()
    for entry_value in appeals:
        entry = _require_exact_mapping(entry_value, {"case", "role", "first_instance"})
        member_case = _validate_member_case(entry["case"])
        role = entry["role"]
        if role not in _MEMBER_ROLES:
            raise _RequestError("invalid_request")
        member_key = (member_case["number"], member_case["judicial_year"])
        if member_key in member_keys:
            raise _RequestError("duplicate_case_member")
        member_keys.add(member_key)
        members.append((member_key[0], member_key[1], role))
        first_instance = _require_exact_mapping(
            entry["first_instance"], {"case", "outcome", "date"}
        )
        _validate_year_tuple(first_instance["case"], include_type=False)
        _require_nonempty_string(first_instance["outcome"])
        _require_iso_date(first_instance["date"])

    top_key = (case["number"], case["judicial_year"])
    if case["type"] == "التماس":
        if len(members) != 1 or members[0] != (top_key[0], top_key[1], "التماس"):
            raise _RequestError("invalid_request")
        _validate_year_tuple(
            summary["petition_target"], include_type=True, require_judicial=True
        )
    else:
        if any(member[2] == "التماس" for member in members):
            raise _RequestError("invalid_request")
        originals = [member for member in members if member[2] == "أصلي"]
        if len(originals) != 1 or originals[0][:2] != top_key:
            raise _RequestError("invalid_request")
        if summary["petition_target"] is not None:
            raise _RequestError("invalid_request")

    compacts = {f"{number}-{year}" for number, year, _role in members}
    parties = summary["parties"]
    if type(parties) is not list or not parties:
        raise _RequestError("invalid_request")
    folders: set[str] = set()
    allowed_party_roles = (
        _PARTY_PETITION_ROLES if case["type"] == "التماس" else _PARTY_APPEAL_ROLES
    )
    for party_value in parties:
        party = _require_exact_mapping(
            party_value,
            {"name", "folder", "capacity", "first_instance_role", "appeal_roles"},
        )
        _require_nonempty_string(party["name"])
        folder = _require_nonempty_string(party["folder"])
        if not _valid_party_slug(folder) or folder in folders:
            raise _RequestError("invalid_request")
        folders.add(folder)
        if party["capacity"] not in _CAPACITIES:
            raise _RequestError("invalid_request")
        if party["first_instance_role"] not in _FIRST_INSTANCE_ROLES:
            raise _RequestError("invalid_request")
        roles = party["appeal_roles"]
        if type(roles) is not dict or set(roles) != compacts:
            raise _RequestError("invalid_request")
        if any(role not in allowed_party_roles for role in roles.values()):
            raise _RequestError("invalid_request")

    claims = summary["claims"]
    if type(claims) is not list or not claims:
        raise _RequestError("invalid_request")
    claim_ids: set[int] = set()
    for claim_value in claims:
        claim = _require_exact_mapping(
            claim_value, {"id", "text", "amount"}, {"appeal"}
        )
        claim_id = _require_positive_int(claim["id"])
        if claim_id in claim_ids:
            raise _RequestError("invalid_request")
        claim_ids.add(claim_id)
        _require_nonempty_string(claim["text"])
        if claim["amount"] is not None and not _is_number(claim["amount"]):
            raise _RequestError("invalid_request")
        if "appeal" in claim and claim["appeal"] not in compacts:
            raise _RequestError("invalid_request")

    valuation = _require_exact_mapping(
        summary["valuation"], {"total", "basis"}, {"per_appeal"}
    )
    if valuation["total"] != "غير-مقدرة" and not _is_number(valuation["total"]):
        raise _RequestError("invalid_request")
    _require_nonempty_string(valuation["basis"])
    if "per_appeal" in valuation:
        per_appeal = valuation["per_appeal"]
        if type(per_appeal) is not dict or not set(per_appeal) <= compacts:
            raise _RequestError("invalid_request")
        if any(not _is_number(amount) for amount in per_appeal.values()):
            raise _RequestError("invalid_request")

    _require_nonempty_string(summary["posture"])
    if summary["status"] not in _STATUSES:
        raise _RequestError("invalid_request")
    _require_iso_date(summary["updated"])
    if "sessions" in summary:
        sessions = summary["sessions"]
        if type(sessions) is not list:
            raise _RequestError("invalid_request")
        for session_value in sessions:
            session = _require_exact_mapping(session_value, {"date", "note"})
            _require_iso_date(session["date"])
            _require_nonempty_string(session["note"])

    return (
        case["type"],
        case["number"],
        case["judicial_year"],
        case["year_type"],
        case["forum"],
        tuple(members),
    )


def _validate_deadlines_front_matter(value: object) -> None:
    deadlines = _require_exact_mapping(
        value,
        {"kanoonak", "convention", "next_deadline", "updated"},
        {"next_deadline_id", "entries"},
    )
    if deadlines["kanoonak"] != "deadlines" or deadlines["convention"] != CONVENTION:
        raise _RequestError("invalid_request")
    _require_iso_date(deadlines["updated"])
    entries_value = deadlines.get("entries", [])
    if type(entries_value) is not list:
        raise _RequestError("invalid_request")
    entries: list[dict[str, object]] = []
    ids: set[str] = set()
    for entry_value in entries_value:
        entry = _require_exact_mapping(
            entry_value, {"id", "kind", "date", "status"}, {"source", "note"}
        )
        entry_id = _require_nonempty_string(entry["id"])
        if entry_id in ids:
            raise _RequestError("invalid_request")
        ids.add(entry_id)
        if entry["kind"] not in _DEADLINE_KINDS or entry["status"] not in _DEADLINE_STATUSES:
            raise _RequestError("invalid_request")
        _require_iso_date(entry["date"])
        for optional_text in ("source", "note"):
            if optional_text in entry and not isinstance(entry[optional_text], str):
                raise _RequestError("invalid_request")
        entries.append(entry)

    next_deadline = deadlines["next_deadline"]
    open_entries = [entry for entry in entries if entry["status"] == "قادم"]
    if next_deadline == _NO_DEADLINES:
        if "next_deadline_id" in deadlines or open_entries:
            raise _RequestError("invalid_request")
        return
    next_date = _require_iso_date(next_deadline)
    next_id = _require_nonempty_string(deadlines.get("next_deadline_id"))
    if not open_entries:
        raise _RequestError("invalid_request")
    earliest = min(entry["date"] for entry in open_entries)
    if next_date != earliest:
        raise _RequestError("invalid_request")
    target = next((entry for entry in open_entries if entry["id"] == next_id), None)
    if target is None or target["date"] != next_date:
        raise _RequestError("invalid_request")
    tied = [entry for entry in open_entries if entry["date"] == next_date]
    if len(tied) > 1:
        def id_key(entry: dict[str, object]) -> tuple[int, int | str]:
            match = re.fullmatch(r"m([0-9]+)", str(entry["id"]))
            return (0, int(match[1])) if match is not None else (1, str(entry["id"]))

        if min(tied, key=id_key)["id"] != next_id:
            raise _RequestError("invalid_request")


def parse_case_leaf(case_leaf: str) -> tuple[str, tuple[tuple[int, int], ...]]:
    """Parse one canonical NFC case leaf without accepting a path."""

    if (
        not isinstance(case_leaf, str)
        or not case_leaf
        or case_leaf in {".", ".."}
        or "/" in case_leaf
        or "\\" in case_leaf
        or "\x00" in case_leaf
        or unicodedata.normalize("NFC", case_leaf) != case_leaf
    ):
        raise ValueError("invalid_case_leaf")
    petition = _PETITION_LEAF_RE.fullmatch(case_leaf)
    if petition is not None:
        return "التماس", ((int(petition["number"]), int(petition["year"])),)
    prefix = "استئناف-"
    if not case_leaf.startswith(prefix):
        raise ValueError("invalid_case_leaf")
    suffix = case_leaf[len(prefix) :]
    position = 0
    members: list[tuple[int, int]] = []
    while position < len(suffix):
        match = _APPEAL_GROUP_RE.match(suffix, position)
        if match is None:
            raise ValueError("invalid_case_leaf")
        year = int(match["year"])
        members.extend((int(number), year) for number in match["numbers"].split("-و-"))
        position = match.end()
    if not members or len(set(members)) != len(members):
        raise ValueError("invalid_case_leaf")
    if _emit_case_leaf("استئناف", tuple(members)) != case_leaf:
        raise ValueError("invalid_case_leaf")
    return "استئناف", tuple(members)


def _emit_case_leaf(
    case_type: str, members: tuple[tuple[int, int], ...]
) -> str:
    if case_type == "التماس":
        if len(members) != 1:
            raise ValueError("invalid_case_leaf")
        number, judicial_year = members[0]
        return f"التماس-{number}-لسنة-{judicial_year:02d}ق"
    groups: list[str] = []
    index = 0
    while index < len(members):
        year = members[index][1]
        numbers: list[str] = []
        while index < len(members) and members[index][1] == year:
            numbers.append(str(members[index][0]))
            index += 1
        groups.append(f"{'-و-'.join(numbers)}-لسنة-{year:02d}ق")
    return "استئناف-" + "-و-".join(groups)


def _project_identity(identity: MatterIdentity) -> str:
    case_type, number, judicial_year, _year_type, _forum, members = identity
    if case_type == "التماس":
        return _emit_case_leaf(case_type, ((number, judicial_year),))
    ordered = sorted(
        members,
        key=lambda member: (_ROLE_ORDER[member[2]], member[0], member[1]),
    )
    return _emit_case_leaf(
        case_type, tuple((member[0], member[1]) for member in ordered)
    )


def _identity_from_mapping(
    value: object, *, minimal: bool = False
) -> MatterIdentity:
    try:
        if minimal:
            mapping = _require_exact_mapping(
                value, {"kanoonak", "convention", "case", "appeals"}
            )
        elif type(value) is dict:
            mapping = value
        else:
            raise _RequestError("invalid_request")
        if (
            mapping.get("kanoonak") != "matter-summary"
            or mapping.get("convention") != CONVENTION
        ):
            raise _RequestError("invalid_request")
        case = _validate_top_case(mapping.get("case"))
        appeals = mapping.get("appeals")
        if type(appeals) is not list or not appeals:
            raise _RequestError("invalid_request")
        members: list[tuple[int, int, str]] = []
        member_keys: set[tuple[int, int]] = set()
        for entry_value in appeals:
            if minimal:
                entry = _require_exact_mapping(entry_value, {"case", "role"})
            elif type(entry_value) is dict:
                entry = entry_value
            else:
                raise _RequestError("invalid_request")
            member_case = _validate_member_case(entry.get("case"))
            role = entry.get("role")
            if role not in _MEMBER_ROLES:
                raise _RequestError("invalid_request")
            member_key = (member_case["number"], member_case["judicial_year"])
            if member_key in member_keys:
                raise _RequestError("invalid_request")
            member_keys.add(member_key)
            members.append((member_key[0], member_key[1], role))
        top_key = (case["number"], case["judicial_year"])
        if case["type"] == "التماس":
            if len(members) != 1 or members[0] != (
                top_key[0],
                top_key[1],
                "التماس",
            ):
                raise _RequestError("invalid_request")
        else:
            if any(member[2] == "التماس" for member in members):
                raise _RequestError("invalid_request")
            originals = [member for member in members if member[2] == "أصلي"]
            if len(originals) != 1 or originals[0][:2] != top_key:
                raise _RequestError("invalid_request")
        return (
            case["type"],
            case["number"],
            case["judicial_year"],
            case["year_type"],
            case["forum"],
            tuple(members),
        )
    except _RequestError as exc:
        raise ValueError("unreadable_case_identity") from exc


def canonical_case_leaf(summary_front_matter: Mapping[str, object]) -> str:
    """Project the unchanged H3 folder grammar from a summary identity surface."""

    return _project_identity(_identity_from_mapping(summary_front_matter))


def _strip_legacy_comment(line: str) -> str:
    return line.split(" #", 1)[0].rstrip()


def _legacy_identity(front_matter: str) -> MatterIdentity:
    lines = [_strip_legacy_comment(line) for line in front_matter.split("\n")]
    top_scalars: dict[str, str] = {}
    for line in lines:
        if line.startswith(" ") or not line or ":" not in line:
            continue
        key, raw = line.split(":", 1)
        if raw.strip():
            if key in top_scalars:
                raise ValueError("unreadable_case_identity")
            top_scalars[key] = raw.strip()
    if top_scalars.get("kanoonak") != "matter-summary" or top_scalars.get("convention") != CONVENTION:
        raise ValueError("unreadable_case_identity")

    try:
        case_start = lines.index("case:") + 1
    except ValueError as exc:
        raise ValueError("unreadable_case_identity") from exc
    case_fields: dict[str, str] = {}
    for line in lines[case_start:]:
        if line and not line.startswith(" "):
            break
        match = re.fullmatch(r"  ([a-z_]+): (.+)", line)
        if match is None:
            if line.strip():
                raise ValueError("unreadable_case_identity")
            continue
        key, scalar = match.groups()
        if key in case_fields:
            raise ValueError("unreadable_case_identity")
        case_fields[key] = scalar
    if set(case_fields) != {"type", "number", "judicial_year", "year_type", "forum"}:
        raise ValueError("unreadable_case_identity")
    try:
        case_type = case_fields["type"]
        number = int(case_fields["number"])
        judicial_year = int(case_fields["judicial_year"])
    except ValueError as exc:
        raise ValueError("unreadable_case_identity") from exc
    if (
        case_type not in _CASE_TYPES
        or number <= 0
        or not 0 <= judicial_year <= 99
        or case_fields["year_type"] != "قضائية"
        or not case_fields["forum"]
    ):
        raise ValueError("unreadable_case_identity")

    try:
        appeals_start = lines.index("appeals:") + 1
    except ValueError as exc:
        raise ValueError("unreadable_case_identity") from exc
    members: list[tuple[int, int, str]] = []
    current_member: tuple[int, int] | None = None
    for line in lines[appeals_start:]:
        if line and not line.startswith(" "):
            break
        member_match = _LEGACY_MEMBER_RE.fullmatch(line)
        if member_match is not None:
            if current_member is not None:
                raise ValueError("unreadable_case_identity")
            current_member = (
                int(member_match["number"]),
                int(member_match["year"]),
            )
            continue
        role_match = _LEGACY_ROLE_RE.fullmatch(line)
        if role_match is not None:
            if current_member is None:
                raise ValueError("unreadable_case_identity")
            members.append(
                (current_member[0], current_member[1], role_match["role"])
            )
            current_member = None
    if current_member is not None or not members:
        raise ValueError("unreadable_case_identity")
    return (
        case_type,
        number,
        judicial_year,
        case_fields["year_type"],
        case_fields["forum"],
        tuple(members),
    )


def _normalize_crlf(payload: bytes) -> bytes:
    """Accept ordinary Windows text while continuing to reject lone CR bytes."""

    normalized = payload.replace(b"\r\n", b"\n")
    if b"\r" in normalized:
        raise ValueError("invalid_line_endings")
    return normalized


def _fenced_front_matter(payload: bytes) -> str:
    if len(payload) > MAX_SUMMARY_BYTES:
        raise ValueError("unreadable_case_identity")
    payload = _normalize_crlf(payload)
    try:
        text = payload.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("unreadable_case_identity") from exc
    lines = text.split("\n")
    if not lines or lines[0] != "---":
        raise ValueError("unreadable_case_identity")
    try:
        closing = lines.index("---", 1)
    except ValueError as exc:
        raise ValueError("unreadable_case_identity") from exc
    return "\n".join(lines[1:closing])


def _existing_summary_identity(path: Path) -> MatterIdentity:
    if not path.is_file():
        raise ValueError("unreadable_case_identity")
    front_matter = _fenced_front_matter(path.read_bytes())
    try:
        parsed = load_strict_json(front_matter)
    except json.JSONDecodeError:
        return _legacy_identity(front_matter)
    return _identity_from_mapping(parsed)


def _ordered_json(value: object) -> object:
    if type(value) is dict:
        keys = sorted(value, key=lambda key: (key != "kanoonak", key))
        return {key: _ordered_json(value[key]) for key in keys}
    if type(value) is list:
        return [_ordered_json(child) for child in value]
    return value


def _render_front_matter(value: Mapping[str, object]) -> str:
    return json.dumps(
        _ordered_json(dict(value)), ensure_ascii=False, allow_nan=False, indent=2
    )


def _render_summary(
    front_matter: Mapping[str, object], body: Mapping[str, str]
) -> bytes:
    sections = "\n\n".join(
        f"## {heading}\n\n{body[heading]}" for heading in _SUMMARY_BODY_KEYS
    )
    return (
        f"---\n{_render_front_matter(front_matter)}\n---\n\n{sections}\n"
    ).encode("utf-8")


def _render_deadlines(front_matter: Mapping[str, object], notes: str) -> bytes:
    text = f"---\n{_render_front_matter(front_matter)}\n---\n"
    if notes:
        text += f"\n{notes}\n"
    return text.encode("utf-8")


def _validate_request(value: object) -> tuple[str, MatterIdentity, bytes, bytes]:
    request = _require_exact_mapping(
        value,
        {
            "case_leaf",
            "summary_front_matter",
            "summary_body",
            "deadlines_front_matter",
            "deadlines_notes",
        },
    )
    _require_clean_strings(request)
    case_leaf = _require_nonempty_string(request["case_leaf"])
    try:
        parse_case_leaf(case_leaf)
    except ValueError as exc:
        raise _RequestError("invalid_request") from exc
    identity = _validate_summary_front_matter(request["summary_front_matter"])
    summary_body = _require_exact_mapping(
        request["summary_body"], set(_SUMMARY_BODY_KEYS)
    )
    for heading in _SUMMARY_BODY_KEYS:
        if not isinstance(summary_body[heading], str):
            raise _RequestError("invalid_request")
    _validate_deadlines_front_matter(request["deadlines_front_matter"])
    if not isinstance(request["deadlines_notes"], str):
        raise _RequestError("invalid_request")
    if _project_identity(identity) != case_leaf:
        raise _RequestError("case_identity_mismatch")
    try:
        summary_payload = _render_summary(request["summary_front_matter"], summary_body)
        deadlines_payload = _render_deadlines(
            request["deadlines_front_matter"], request["deadlines_notes"]
        )
    except (TypeError, ValueError) as exc:
        raise _RequestError("invalid_request") from exc
    return case_leaf, identity, summary_payload, deadlines_payload


def _target_entries(directory: Path, targets: Sequence[str]) -> dict[str, str]:
    matches: dict[str, str] = {}
    target_set = set(targets)
    for raw_name in os.listdir(directory):
        normalized = unicodedata.normalize("NFC", raw_name)
        if normalized not in target_set:
            continue
        if normalized in matches and matches[normalized] != raw_name:
            raise _NameCollision(normalized)
        matches[normalized] = raw_name
    return matches


def _is_expected_kind(path: Path, expected: str) -> bool:
    return path.is_file() if expected == "file" else path.is_dir()


def _write_file_exclusive(path: Path, payload: bytes) -> None:
    try:
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_BINARY", 0)
        descriptor = os.open(path, flags, 0o600)
    except FileExistsError:
        raise
    except OSError as exc:
        raise _CreationFailure("exclusive_create_failed") from exc
    try:
        offset = 0
        while offset < len(payload):
            written = os.write(descriptor, payload[offset:])
            if written <= 0:
                raise OSError("short_write")
            offset += written
        os.fsync(descriptor)
        written_stat = os.fstat(descriptor)
        if not stat.S_ISREG(written_stat.st_mode) or written_stat.st_size != len(payload):
            raise OSError("incomplete_write")
    except OSError as exc:
        raise _UncertainCreation("exclusive_create_uncertain") from exc
    finally:
        try:
            os.close(descriptor)
        except OSError as exc:
            raise _UncertainCreation("exclusive_create_uncertain") from exc
    try:
        final = os.lstat(path)
    except OSError as exc:
        raise _UncertainCreation("exclusive_create_uncertain") from exc
    if not stat.S_ISREG(final.st_mode) or stat.S_ISLNK(final.st_mode) or final.st_size != len(payload):
        raise _UncertainCreation("exclusive_create_uncertain")


def _create_directory_exclusive(path: Path) -> None:
    try:
        os.mkdir(path, 0o700)
    except FileExistsError:
        raise
    except OSError as exc:
        raise _CreationFailure("exclusive_create_failed") from exc
    try:
        value = os.lstat(path)
    except OSError as exc:
        raise _UncertainCreation("exclusive_create_uncertain") from exc
    if not stat.S_ISDIR(value.st_mode) or stat.S_ISLNK(value.st_mode):
        raise _UncertainCreation("exclusive_create_uncertain")


def _failure_result(
    *,
    reason: str,
    blocking_item: str,
    preserved: list[str],
    uncertain: bool = False,
) -> WorkspaceResult:
    if uncertain and blocking_item not in preserved:
        preserved.append(blocking_item)
    return WorkspaceResult(
        status="partial_failure" if preserved else "conflict",
        reason=reason,
        blocking_item=blocking_item,
        preserved_items=tuple(preserved),
    )


def _render_assets(today: date, names: Sequence[str]) -> dict[str, bytes]:
    rendered: dict[str, bytes] = {}
    stamp = today.isoformat().encode("ascii")
    expected_tokens = {"README.md": 0, "أسلوبي.md": 1}
    for name in names:
        path = ASSET_DIRECTORY / name
        value = os.lstat(path)
        if not stat.S_ISREG(value.st_mode) or stat.S_ISLNK(value.st_mode):
            raise RuntimeError("packaged_asset_invalid")
        payload = path.read_bytes()
        try:
            payload = _normalize_crlf(payload)
        except ValueError as exc:
            raise RuntimeError("packaged_asset_invalid") from exc
        if payload.count(DATE_TOKEN) != expected_tokens[name]:
            raise RuntimeError("packaged_asset_invalid")
        payload = payload.replace(DATE_TOKEN, stamp)
        text = payload.decode("utf-8")
        if not text.startswith("---\n"):
            raise RuntimeError("packaged_asset_invalid")
        if name == "أسلوبي.md" and f"parent_version: {PARENT_VERSION}\n" not in text:
            raise RuntimeError("packaged_asset_invalid")
        rendered[name] = payload
    return rendered


def bootstrap_workspace(*, today: date | None = None) -> WorkspaceResult:
    """Exclusively create only missing optional root assets."""

    root = Path.cwd()
    try:
        if not root.is_dir():
            raise OSError("root_unavailable")
        entries = _target_entries(root, CANONICAL_ROOT_FILES)
    except _NameCollision as exc:
        return WorkspaceResult(
            status="conflict", reason="normalization_collision", blocking_item=exc.name
        )
    except OSError:
        return WorkspaceResult(status="conflict", reason="root_unavailable")
    for name in CANONICAL_ROOT_FILES:
        raw_name = entries.get(name)
        if raw_name is not None and not _is_expected_kind(root / raw_name, "file"):
            return WorkspaceResult(
                status="conflict", reason="wrong_kind", blocking_item=name
            )
    missing = [name for name in CANONICAL_ROOT_FILES if name not in entries]
    if not missing:
        return WorkspaceResult(status="ready", reason="workspace_ready")
    try:
        payloads = _render_assets(today or date.today(), missing)
    except (OSError, UnicodeError, RuntimeError):
        return WorkspaceResult(status="conflict", reason="packaged_assets_unavailable")

    preserved: list[str] = []
    for name in missing:
        try:
            _write_file_exclusive(root / name, payloads[name])
            preserved.append(name)
        except FileExistsError:
            return _failure_result(
                reason="creation_collision", blocking_item=name, preserved=preserved
            )
        except _UncertainCreation:
            return _failure_result(
                reason="bootstrap_failed",
                blocking_item=name,
                preserved=preserved,
                uncertain=True,
            )
        except _CreationFailure:
            return _failure_result(
                reason="bootstrap_failed", blocking_item=name, preserved=preserved
            )
    return WorkspaceResult(
        status="initialized",
        reason="workspace_initialized",
        preserved_items=tuple(preserved),
    )


def create_case(request: object) -> WorkspaceResult:
    """Initialize exactly one validated canonical case beneath process CWD."""

    try:
        case_leaf, incoming_identity, summary_payload, deadlines_payload = _validate_request(
            request
        )
    except _RequestError as exc:
        reason = str(exc)
        if reason not in {
            "invalid_request",
            "duplicate_case_member",
            "case_identity_mismatch",
        }:
            reason = "invalid_request"
        return WorkspaceResult(status="conflict", reason=reason)

    root = Path.cwd()
    try:
        if not root.is_dir():
            raise OSError("root_unavailable")
        root_entries = _target_entries(root, (case_leaf,))
    except _NameCollision:
        return WorkspaceResult(
            status="conflict", reason="normalization_collision", blocking_item=case_leaf
        )
    except OSError:
        return WorkspaceResult(status="conflict", reason="root_unavailable")

    raw_case_leaf = root_entries.get(case_leaf)
    case_directory = root / (raw_case_leaf or case_leaf)
    case_preexists = raw_case_leaf is not None
    if case_preexists and not _is_expected_kind(case_directory, "directory"):
        return WorkspaceResult(
            status="conflict", reason="wrong_kind", blocking_item=case_leaf
        )

    child_names = CANONICAL_CASE_FILES + CANONICAL_CASE_DIRECTORIES
    child_entries: dict[str, str] = {}
    if case_preexists:
        try:
            child_entries = _target_entries(case_directory, child_names)
        except _NameCollision as exc:
            return WorkspaceResult(
                status="conflict",
                reason="normalization_collision",
                blocking_item=f"{case_leaf}/{exc.name}",
            )
        raw_summary = child_entries.get("الملخص.md")
        if raw_summary is None:
            try:
                is_empty = not os.listdir(case_directory)
            except OSError:
                return WorkspaceResult(status="conflict", reason="case_unavailable")
            if not is_empty:
                return WorkspaceResult(
                    status="conflict",
                    reason="existing_case_identity_unverifiable",
                    blocking_item=f"{case_leaf}/الملخص.md",
                )
        else:
            try:
                existing_identity = _existing_summary_identity(case_directory / raw_summary)
            except (OSError, ValueError, UnicodeError):
                return WorkspaceResult(
                    status="conflict",
                    reason="existing_case_identity_mismatch",
                    blocking_item=f"{case_leaf}/الملخص.md",
                )
            if existing_identity != incoming_identity:
                return WorkspaceResult(
                    status="conflict",
                    reason="existing_case_identity_mismatch",
                    blocking_item=f"{case_leaf}/الملخص.md",
                )
        for name in child_names:
            raw_name = child_entries.get(name)
            if raw_name is None:
                continue
            expected = "file" if name in CANONICAL_CASE_FILES else "directory"
            if not _is_expected_kind(case_directory / raw_name, expected):
                return WorkspaceResult(
                    status="conflict",
                    reason="wrong_kind",
                    blocking_item=f"{case_leaf}/{name}",
                )

    preserved: list[str] = []
    if not case_preexists:
        try:
            _create_directory_exclusive(case_directory)
            preserved.append(case_leaf)
        except FileExistsError:
            return _failure_result(
                reason="creation_collision", blocking_item=case_leaf, preserved=preserved
            )
        except _UncertainCreation:
            return _failure_result(
                reason="create_case_failed",
                blocking_item=case_leaf,
                preserved=preserved,
                uncertain=True,
            )
        except _CreationFailure:
            return _failure_result(
                reason="create_case_failed", blocking_item=case_leaf, preserved=preserved
            )

    creations: list[tuple[str, str, bytes | None]] = [
        ("الملخص.md", "file", summary_payload),
        ("المواعيد.md", "file", deadlines_payload),
        *((name, "directory", None) for name in CANONICAL_CASE_DIRECTORIES),
    ]
    for name, expected, payload in creations:
        if name in child_entries:
            continue
        relative = f"{case_leaf}/{name}"
        try:
            if expected == "file":
                assert payload is not None
                _write_file_exclusive(case_directory / name, payload)
            else:
                _create_directory_exclusive(case_directory / name)
            preserved.append(relative)
        except FileExistsError:
            return _failure_result(
                reason="creation_collision", blocking_item=relative, preserved=preserved
            )
        except _UncertainCreation:
            return _failure_result(
                reason="create_case_failed",
                blocking_item=relative,
                preserved=preserved,
                uncertain=True,
            )
        except _CreationFailure:
            return _failure_result(
                reason="create_case_failed", blocking_item=relative, preserved=preserved
            )
    if not preserved:
        return WorkspaceResult(status="ready", reason="case_ready")
    return WorkspaceResult(
        status="initialized",
        reason="case_initialized",
        preserved_items=tuple(preserved),
    )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Initialize Kanoonak files in the current project folder."
    )
    parser.add_argument("command", choices=("bootstrap", "create-case"))
    return parser


def _reject_json_constant(_value: str) -> object:
    raise ValueError("invalid_json_constant")


def _reject_duplicate_pairs(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate_json_key")
        result[key] = value
    return result


def load_strict_json(text: str) -> object:
    """Parse standards-compliant JSON with no duplicate object keys."""

    return json.loads(
        text,
        object_pairs_hook=_reject_duplicate_pairs,
        parse_constant=_reject_json_constant,
    )


def _read_stdin_utf8() -> str:
    binary = getattr(sys.stdin, "buffer", None)
    if binary is None:
        value = sys.stdin.read()
        if not isinstance(value, str):
            raise UnicodeError("stdin is unavailable")
        return value
    return binary.read().decode("utf-8", errors="strict")


def main(argv: Sequence[str] | None = None) -> int:
    arguments = _parser().parse_args(argv)
    try:
        if arguments.command == "bootstrap":
            result = bootstrap_workspace()
        else:
            try:
                request = load_strict_json(_read_stdin_utf8())
            except (UnicodeError, ValueError):
                result = WorkspaceResult(status="conflict", reason="invalid_request")
            else:
                result = create_case(request)
    except Exception:
        # The CLI must never expose submitted case content through a traceback.
        result = WorkspaceResult(status="conflict", reason="operation_failed")
    print(json.dumps(result.public(), ensure_ascii=True, sort_keys=True))
    return 0 if result.status in {"ready", "initialized"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
