#!/usr/bin/env python3
"""Inspect or initialize only the host-provided Kanoonak project root.

The CLI deliberately has no path input. The host establishes one exact primary
folder and starts this helper with that folder as its current working directory.
Internal functions accept a ``Path`` solely so synthetic tests can exercise the
same logic without touching a real workspace.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import stat
import sys
import unicodedata
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Callable, Sequence


MARKER_NAME = ".kanoonak-workspace.yaml"
MARKER_BYTES = b"kanoonak_workspace: true\nschema_version: 1\n"
CONVENTION = "2026-07-21"
PARENT_VERSION = "2026-08-21.1"
DATE_TOKEN = b"{{TODAY}}"
ASSET_DIRECTORY = Path(__file__).resolve().parents[1] / "assets" / "workspace"
CANONICAL_FILES = ("README.md", "الفهرس.md", "أسلوبي.md")
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
MAX_ROOT_FILE_BYTES = 1024 * 1024


@dataclass(frozen=True)
class StorageAssessment:
    """Mechanically visible storage result; sync remains unprovable when accepted."""

    accepted: bool
    reason: str


@dataclass(frozen=True)
class WorkspaceResult:
    """A closed workspace decision with no raw local path in its public form."""

    status: str
    reason: str
    kind: str | None = None
    blocking_item: str | None = None
    preserved_items: tuple[str, ...] = ()
    root_identity: tuple[int, int] | None = None

    def public(self) -> dict[str, object]:
        result: dict[str, object] = {"status": self.status, "reason": self.reason}
        if self.kind is not None:
            result["kind"] = self.kind
        if self.blocking_item is not None:
            result["blocking_item"] = self.blocking_item
        if self.preserved_items:
            result["preserved_items"] = list(self.preserved_items)
        return result


StorageProbe = Callable[[int], StorageAssessment]


class _NameCollision(ValueError):
    def __init__(self, name: str, *, marked: bool):
        super().__init__("normalization_collision")
        self.name = name
        self.marked = marked


def _identity(value: os.stat_result) -> tuple[int, int]:
    return value.st_dev, value.st_ino


def _open_root(root: Path) -> tuple[int, tuple[int, int]]:
    """Open one real directory without following it or a symlinked ancestor."""

    absolute = Path(os.path.abspath(os.fspath(root)))
    current = absolute
    while True:
        if stat.S_ISLNK(os.lstat(current).st_mode):
            raise ValueError("root_or_ancestor_is_symlink")
        if current.parent == current:
            break
        current = current.parent
    root_stat = os.lstat(root)
    if not stat.S_ISDIR(root_stat.st_mode):
        raise ValueError("root_is_not_directory")
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(root, flags)
    opened_stat = os.fstat(descriptor)
    if not stat.S_ISDIR(opened_stat.st_mode) or _identity(opened_stat) != _identity(root_stat):
        os.close(descriptor)
        raise ValueError("root_identity_changed")
    return descriptor, _identity(opened_stat)


def _root_path_names_identity(root: Path, expected: tuple[int, int]) -> bool:
    """Use a pathname only to verify/display the already-held root identity."""

    descriptor = -1
    try:
        descriptor, observed = _open_root(root)
        return observed == expected
    except (OSError, ValueError):
        return False
    finally:
        if descriptor >= 0:
            os.close(descriptor)


def _open_inherited_cwd() -> tuple[Path, int, tuple[int, int]]:
    """Hold the host-attached CWD before resolving its display pathname."""

    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(".", flags)
    try:
        opened = os.fstat(descriptor)
        if not stat.S_ISDIR(opened.st_mode):
            raise ValueError("root_is_not_directory")
        identity = _identity(opened)
        root = Path(os.getcwd())
        if not _root_path_names_identity(root, identity):
            raise ValueError("root_identity_changed")
        return root, descriptor, identity
    except Exception:
        os.close(descriptor)
        raise


def _reopen_held_directory(root_fd: int) -> tuple[int, tuple[int, int]]:
    """Reopen only the directory already named by a trusted descriptor."""

    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    if os.open in getattr(os, "supports_dir_fd", ()):
        descriptor = os.open(".", flags, dir_fd=root_fd)
    else:
        descriptor = os.dup(root_fd)
    opened = os.fstat(descriptor)
    held = os.fstat(root_fd)
    if (
        not stat.S_ISDIR(opened.st_mode)
        or _identity(opened) != _identity(held)
    ):
        os.close(descriptor)
        raise ValueError("root_identity_changed")
    return descriptor, _identity(opened)


def _read_regular_leaf(root_fd: int, name: str) -> tuple[bytes, tuple[int, int]]:
    leaf_stat = os.stat(name, dir_fd=root_fd, follow_symlinks=False)
    if not stat.S_ISREG(leaf_stat.st_mode):
        raise ValueError("canonical_item_not_regular")
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(name, flags, dir_fd=root_fd)
    try:
        opened_stat = os.fstat(descriptor)
        if not stat.S_ISREG(opened_stat.st_mode) or _identity(opened_stat) != _identity(leaf_stat):
            raise ValueError("canonical_item_identity_changed")
        chunks: list[bytes] = []
        remaining = MAX_ROOT_FILE_BYTES + 1
        while remaining:
            chunk = os.read(descriptor, min(64 * 1024, remaining))
            if not chunk:
                break
            chunks.append(chunk)
            remaining -= len(chunk)
        payload = b"".join(chunks)
        if len(payload) > MAX_ROOT_FILE_BYTES:
            raise ValueError("canonical_item_too_large")
        return payload, _identity(opened_stat)
    finally:
        os.close(descriptor)


def _normalized_entries(root_fd: int) -> dict[str, str]:
    """Map NFC contract names to raw directory entries, rejecting ambiguity."""

    entries: dict[str, str] = {}
    raw_names = os.listdir(root_fd)
    marked = MARKER_NAME in raw_names
    for raw_name in raw_names:
        normalized = unicodedata.normalize("NFC", raw_name)
        if normalized in entries and entries[normalized] != raw_name:
            raise _NameCollision(normalized, marked=marked)
        entries[normalized] = raw_name
    return entries


def _known_cloud_provider_path(root: Path) -> bool:
    parts = tuple(part.casefold() for part in Path(os.path.abspath(root)).parts)
    return any(
        part == "library"
        and parts[index + 1] in {"cloudstorage", "mobile documents"}
        for index, part in enumerate(parts[:-1])
    )


def _front_matter(payload: bytes) -> dict[str, str]:
    try:
        lines = payload.decode("utf-8").splitlines()
    except UnicodeDecodeError as exc:
        raise ValueError("canonical_item_not_utf8") from exc
    if not lines or lines[0] != "---":
        raise ValueError("canonical_front_matter_missing")
    try:
        closing = lines.index("---", 1)
    except ValueError as exc:
        raise ValueError("canonical_front_matter_unclosed") from exc
    fields: dict[str, str] = {}
    for line in lines[1:closing]:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        match = re.fullmatch(r"([A-Za-z_][A-Za-z0-9_-]*):\s*(.*)", stripped)
        if match is None:
            raise ValueError("canonical_front_matter_malformed")
        key, value = match.groups()
        value = value.split(" #", 1)[0].strip()
        if key in fields:
            raise ValueError("canonical_front_matter_duplicate")
        fields[key] = value
    return fields


def _validate_canonical_payload(name: str, payload: bytes) -> None:
    fields = _front_matter(payload)
    expected = {
        "README.md": {"kanoonak": "readme", "convention": CONVENTION},
        "الفهرس.md": {"kanoonak": "index", "convention": CONVENTION},
        "أسلوبي.md": {
            "kanoonak": "local-persona",
            "convention": CONVENTION,
            "parent_version": PARENT_VERSION,
        },
    }[name]
    if any(fields.get(key) != value for key, value in expected.items()):
        raise ValueError("canonical_front_matter_incompatible")
    if name == "الفهرس.md" and not fields.get("forum"):
        raise ValueError("canonical_forum_missing")
    if name in {"الفهرس.md", "أسلوبي.md"} and re.fullmatch(
        r"\d{4}-\d{2}-\d{2}", fields.get("updated", "")
    ) is None:
        raise ValueError("canonical_updated_invalid")


def _render_assets(today: date) -> dict[str, bytes]:
    rendered: dict[str, bytes] = {}
    stamp = today.isoformat().encode("ascii")
    for name in CANONICAL_FILES:
        path = ASSET_DIRECTORY / name
        file_stat = os.lstat(path)
        if not stat.S_ISREG(file_stat.st_mode):
            raise RuntimeError(f"packaged workspace asset is not a regular file: {name}")
        payload = path.read_bytes()
        count = payload.count(DATE_TOKEN)
        expected_count = 0 if name == "README.md" else 1
        if count != expected_count:
            raise RuntimeError(f"packaged workspace asset has invalid date token count: {name}")
        payload = payload.replace(DATE_TOKEN, stamp)
        _validate_canonical_payload(name, payload)
        rendered[name] = payload
    return rendered


def production_storage_probe(root_fd: int) -> StorageAssessment:
    """Accept only the opened macOS system-data device; sync stays unprovable."""

    if sys.platform != "darwin":
        return StorageAssessment(False, "storage_platform_not_verified")
    data_root = Path("/System/Volumes/Data")
    if not data_root.is_dir():
        data_root = Path("/")
    data_fd = -1
    try:
        data_fd = os.open(
            data_root,
            os.O_RDONLY
            | getattr(os, "O_DIRECTORY", 0)
            | getattr(os, "O_NOFOLLOW", 0),
        )
        root_device = os.fstat(root_fd).st_dev
        system_data_device = os.fstat(data_fd).st_dev
        filesystem_flags = os.fstatvfs(root_fd).f_flag
    except OSError:
        return StorageAssessment(False, "storage_inspection_failed")
    finally:
        if data_fd >= 0:
            os.close(data_fd)
    if root_device != system_data_device:
        return StorageAssessment(False, "storage_not_internal_fixed")
    if filesystem_flags & getattr(os, "ST_RDONLY", 1):
        return StorageAssessment(False, "storage_read_only")
    try:
        writable = os.access(
            ".", os.W_OK, dir_fd=root_fd, effective_ids=True, follow_symlinks=False
        )
    except (NotImplementedError, TypeError):
        writable = os.access(".", os.W_OK, dir_fd=root_fd)
    if not writable:
        return StorageAssessment(False, "workspace_not_writable")
    return StorageAssessment(True, "local_native_sync_unprovable")


def _result_for_root_error(reason: str) -> WorkspaceResult:
    status = "unsupported" if reason == "root_or_ancestor_is_symlink" else "unavailable"
    return WorkspaceResult(status=status, reason=reason)


def inspect_workspace(
    root: Path,
    *,
    storage_probe: StorageProbe | None = None,
    _root_fd: int | None = None,
) -> WorkspaceResult:
    """Shallowly classify one exact root without mutation or recursive reads."""

    owns_root_fd = _root_fd is None
    try:
        if _root_fd is None:
            root_fd, root_identity = _open_root(root)
        else:
            root_fd = _root_fd
            opened = os.fstat(root_fd)
            if not stat.S_ISDIR(opened.st_mode):
                raise ValueError("root_is_not_directory")
            root_identity = _identity(opened)
    except ValueError as exc:
        return _result_for_root_error(str(exc))
    except OSError:
        return WorkspaceResult(status="unavailable", reason="root_unavailable")
    try:
        if not _root_path_names_identity(root, root_identity):
            return WorkspaceResult(
                status="unavailable",
                reason="root_identity_changed",
                root_identity=root_identity,
            )
        if _known_cloud_provider_path(root):
            return WorkspaceResult(
                status="unsupported", reason="known_cloud_provider_path"
            )
        probe = storage_probe or production_storage_probe
        try:
            storage = probe(root_fd)
        except Exception:
            return WorkspaceResult(status="unsupported", reason="storage_inspection_failed")
        if not storage.accepted:
            return WorkspaceResult(status="unsupported", reason=storage.reason)
        try:
            entries = _normalized_entries(root_fd)
        except _NameCollision as exc:
            return WorkspaceResult(
                status="invalid" if exc.marked else "conflict",
                reason="normalization_collision",
                blocking_item=exc.name,
                root_identity=root_identity,
            )
        except OSError:
            return WorkspaceResult(status="unavailable", reason="root_unreadable")
        names = set(entries)

        if MARKER_NAME in names:
            try:
                marker, _marker_identity = _read_regular_leaf(
                    root_fd, entries[MARKER_NAME]
                )
            except (OSError, ValueError):
                return WorkspaceResult(
                    status="invalid",
                    reason="marker_invalid",
                    blocking_item=MARKER_NAME,
                    root_identity=root_identity,
                )
            if marker != MARKER_BYTES:
                return WorkspaceResult(
                    status="invalid",
                    reason="marker_malformed",
                    blocking_item=MARKER_NAME,
                    root_identity=root_identity,
                )
            for name in CANONICAL_FILES:
                if name not in names:
                    return WorkspaceResult(
                        status="invalid",
                        reason="canonical_item_missing",
                        blocking_item=name,
                        root_identity=root_identity,
                    )
                try:
                    payload, _leaf_identity = _read_regular_leaf(
                        root_fd, entries[name]
                    )
                    _validate_canonical_payload(name, payload)
                except (OSError, ValueError):
                    return WorkspaceResult(
                        status="invalid",
                        reason="canonical_item_invalid",
                        blocking_item=name,
                        root_identity=root_identity,
                    )
            return WorkspaceResult(
                status="ready",
                reason="workspace_ready",
                root_identity=root_identity,
            )

        unfamiliar = sorted(names - set(CANONICAL_FILES))
        if unfamiliar:
            return WorkspaceResult(
                status="conflict",
                reason="unfamiliar_root_content",
                blocking_item=entries[unfamiliar[0]],
                root_identity=root_identity,
            )
        for name in sorted(names):
            try:
                payload, _leaf_identity = _read_regular_leaf(root_fd, entries[name])
                _validate_canonical_payload(name, payload)
            except (OSError, ValueError):
                return WorkspaceResult(
                    status="conflict",
                    reason="canonical_item_conflict",
                    blocking_item=name,
                    root_identity=root_identity,
                )
        return WorkspaceResult(
            status="confirmation_required",
            reason="sync_confirmation_required",
            kind="empty" if not names else "compatible_unmarked",
            root_identity=root_identity,
        )
    finally:
        if owns_root_fd:
            os.close(root_fd)


class _IncompleteExclusiveWrite(OSError):
    pass


def _write_complete_exclusive(root_fd: int, name: str, payload: bytes) -> tuple[int, int]:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(name, flags, 0o600, dir_fd=root_fd)
    identity: tuple[int, int] | None = None
    try:
        offset = 0
        while offset < len(payload):
            written = os.write(descriptor, payload[offset:])
            if written <= 0:
                raise OSError("exclusive workspace write was short")
            offset += written
        os.fsync(descriptor)
        written_stat = os.fstat(descriptor)
        if not stat.S_ISREG(written_stat.st_mode) or written_stat.st_size != len(payload):
            raise OSError("exclusive workspace write was incomplete")
        identity = _identity(written_stat)
    except OSError as exc:
        os.close(descriptor)
        descriptor = -1
        # A short or failed write leaves an uncertain payload. Preserve it even
        # when this invocation created the inode; another writer may have
        # changed it before the failure became visible.
        raise _IncompleteExclusiveWrite("exclusive workspace write failed") from exc
    finally:
        if descriptor >= 0:
            os.close(descriptor)
    assert identity is not None
    try:
        reopened, reopened_identity = _read_regular_leaf(root_fd, name)
        if reopened_identity != identity or reopened != payload:
            raise OSError("exclusive workspace write did not reopen exactly")
    except (OSError, ValueError) as exc:
        raise _IncompleteExclusiveWrite(
            "exclusive workspace write did not reopen exactly"
        ) from exc
    return identity


def bootstrap_workspace(
    root: Path,
    *,
    confirmed: bool,
    storage_probe: StorageProbe | None = None,
    today: date | None = None,
    _root_fd: int | None = None,
) -> WorkspaceResult:
    """Create missing canonical files and marker last; never delete on failure.

    A pathname cannot be atomically proven to still name the inode previously
    checked at unlink time. Partial leaves therefore remain visible and are
    reported for separate repair instead of risking deletion of a replacement.
    """

    try:
        if _root_fd is None:
            root_fd, root_identity = _open_root(root)
        else:
            root_fd, root_identity = _reopen_held_directory(_root_fd)
    except ValueError as exc:
        return _result_for_root_error(str(exc))
    except OSError:
        return WorkspaceResult(status="unavailable", reason="root_unavailable")

    probe = storage_probe or production_storage_probe
    created_or_uncertain: list[str] = []
    failed_name: str | None = None
    failure_reason = "bootstrap_failed"
    try:
        initial = inspect_workspace(root, storage_probe=probe, _root_fd=root_fd)
        if initial.status != "confirmation_required":
            return initial
        if not confirmed:
            return initial
        try:
            payloads = _render_assets(today or date.today())
        except (OSError, RuntimeError, ValueError):
            return WorkspaceResult(status="unavailable", reason="packaged_assets_invalid")
        payloads[MARKER_NAME] = MARKER_BYTES

        if initial.root_identity != root_identity:
            return WorkspaceResult(status="unavailable", reason="root_identity_changed")
        try:
            storage = probe(root_fd)
        except Exception:
            return WorkspaceResult(status="unsupported", reason="storage_inspection_failed")
        if not storage.accepted:
            return WorkspaceResult(status="unsupported", reason=storage.reason)
        try:
            entries = _normalized_entries(root_fd)
        except _NameCollision as exc:
            return WorkspaceResult(
                status="conflict",
                reason="normalization_collision",
                blocking_item=exc.name,
            )
        except OSError:
            return WorkspaceResult(status="unavailable", reason="root_unreadable")
        current_names = set(entries)
        if MARKER_NAME in current_names:
            return WorkspaceResult(status="conflict", reason="creation_collision", blocking_item=MARKER_NAME)
        unfamiliar = current_names - set(CANONICAL_FILES)
        if unfamiliar:
            return WorkspaceResult(
                status="conflict",
                reason="root_changed_during_bootstrap",
                blocking_item=entries[sorted(unfamiliar)[0]],
            )
        # Revalidate every pre-existing canonical item before the first write.
        # A concurrent replacement after the initial inspection must not turn
        # a compatible root into a partly initialized one.
        for name in sorted(current_names):
            try:
                existing, _existing_identity = _read_regular_leaf(
                    root_fd, entries[name]
                )
                _validate_canonical_payload(name, existing)
            except (OSError, ValueError):
                return WorkspaceResult(
                    status="conflict",
                    reason="canonical_item_conflict",
                    blocking_item=name,
                )
        if not _root_path_names_identity(root, root_identity):
            return WorkspaceResult(status="unavailable", reason="root_identity_changed")
        try:
            for name in CANONICAL_FILES:
                if name in current_names:
                    continue
                failed_name = name
                _write_complete_exclusive(root_fd, name, payloads[name])
                created_or_uncertain.append(name)
            names_before_marker = set(_normalized_entries(root_fd))
            if names_before_marker != set(CANONICAL_FILES):
                changed = (names_before_marker - set(CANONICAL_FILES)) or (
                    set(CANONICAL_FILES) - names_before_marker
                )
                failed_name = sorted(changed)[0]
                raise FileExistsError("workspace root changed during bootstrap")
            failed_name = MARKER_NAME
            _write_complete_exclusive(root_fd, MARKER_NAME, MARKER_BYTES)
            created_or_uncertain.append(MARKER_NAME)
            os.fsync(root_fd)
        except _NameCollision as exc:
            failed_name = exc.name
            failure_reason = "normalization_collision"
        except FileExistsError:
            failure_reason = "creation_collision"
        except _IncompleteExclusiveWrite:
            if failed_name is not None and failed_name not in created_or_uncertain:
                created_or_uncertain.append(failed_name)
            failure_reason = "bootstrap_failed"
        except OSError:
            failure_reason = "bootstrap_failed"
        else:
            final_fd = -1
            try:
                final_fd, final_identity = _reopen_held_directory(root_fd)
                final = inspect_workspace(
                    root,
                    storage_probe=probe,
                    _root_fd=final_fd,
                )
                if final.status == "ready" and final_identity == root_identity:
                    return WorkspaceResult(
                        status="initialized", reason="workspace_initialized"
                    )
                failure_reason = (
                    "root_identity_changed"
                    if final.reason == "root_identity_changed"
                    else "reopen_validation_failed"
                )
            except (OSError, ValueError):
                failure_reason = "reopen_validation_failed"
            finally:
                if final_fd >= 0:
                    os.close(final_fd)
        return WorkspaceResult(
            status="partial_failure" if created_or_uncertain else "conflict",
            reason=failure_reason,
            blocking_item=failed_name,
            preserved_items=tuple(created_or_uncertain),
        )
    finally:
        os.close(root_fd)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Inspect or initialize the current Kanoonak project folder."
    )
    parser.add_argument("command", choices=("inspect", "bootstrap"))
    parser.add_argument(
        "--confirmed",
        action="store_true",
        help="confirm use/adoption and the disclosed residual sync uncertainty",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    arguments = _parser().parse_args(argv)
    if arguments.command == "inspect" and arguments.confirmed:
        _parser().error("--confirmed is valid only with bootstrap")
    root_fd = -1
    try:
        root, root_fd, _root_identity = _open_inherited_cwd()
        if arguments.command == "inspect":
            result = inspect_workspace(root, _root_fd=root_fd)
        else:
            result = bootstrap_workspace(
                root,
                confirmed=arguments.confirmed,
                _root_fd=root_fd,
            )
    except ValueError as exc:
        result = _result_for_root_error(str(exc))
    except OSError:
        result = WorkspaceResult(status="unavailable", reason="root_unavailable")
    finally:
        if root_fd >= 0:
            os.close(root_fd)
    print(json.dumps(result.public(), ensure_ascii=False, sort_keys=True))
    return 0 if result.status in {"ready", "initialized"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
