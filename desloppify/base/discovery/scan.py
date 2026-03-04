"""Canonical public source-discovery and file-cache API."""

from __future__ import annotations

from pathlib import Path

from . import source as source_discovery_mod

DEFAULT_EXCLUSIONS = source_discovery_mod.DEFAULT_EXCLUSIONS


def _normalize_patterns(patterns: list[str]) -> list[str]:
    normalized: list[str] = []
    seen: set[str] = set()
    for raw in patterns:
        text = str(raw).strip()
        if not text or text in seen:
            continue
        seen.add(text)
        normalized.append(text)
    return normalized


def _normalize_extensions(extensions: list[str]) -> list[str]:
    normalized: list[str] = []
    seen: set[str] = set()
    for raw in extensions:
        text = str(raw).strip()
        if not text:
            continue
        if not text.startswith("."):
            text = "." + text
        text = text.lower()
        if text in seen:
            continue
        seen.add(text)
        normalized.append(text)
    return normalized


def set_exclusions(patterns: list[str]) -> None:
    source_discovery_mod.set_exclusions(_normalize_patterns(patterns))


def get_exclusions() -> tuple[str, ...]:
    return source_discovery_mod.get_exclusions()


def enable_file_cache() -> None:
    source_discovery_mod.enable_file_cache()


def disable_file_cache() -> None:
    source_discovery_mod.disable_file_cache()


def is_file_cache_enabled() -> bool:
    return source_discovery_mod.is_file_cache_enabled()


def read_file_text(filepath: str) -> str | None:
    return source_discovery_mod.read_file_text(filepath)


def clear_source_file_cache_for_tests() -> None:
    source_discovery_mod.clear_source_file_cache_for_tests()


def collect_exclude_dirs(scan_root: Path) -> list[str]:
    return source_discovery_mod.collect_exclude_dirs(scan_root.resolve())


def find_source_files(
    path: str | Path,
    extensions: list[str],
    exclusions: list[str] | None = None,
) -> list[str]:
    normalized_exts = _normalize_extensions(extensions)
    if not normalized_exts:
        return []
    normalized_exclusions = (
        _normalize_patterns(exclusions) if exclusions is not None else None
    )
    return source_discovery_mod.find_source_files(
        path,
        normalized_exts,
        normalized_exclusions,
    )


def find_ts_files(path: str | Path) -> list[str]:
    return find_source_files(path, [".ts", ".tsx"])


def find_tsx_files(path: str | Path) -> list[str]:
    return find_source_files(path, [".tsx"])


def find_py_files(path: str | Path) -> list[str]:
    return find_source_files(path, [".py"])


__all__ = [
    "DEFAULT_EXCLUSIONS",
    "clear_source_file_cache_for_tests",
    "collect_exclude_dirs",
    "disable_file_cache",
    "enable_file_cache",
    "find_py_files",
    "find_source_files",
    "find_ts_files",
    "find_tsx_files",
    "get_exclusions",
    "is_file_cache_enabled",
    "read_file_text",
    "set_exclusions",
]
