"""Canonical public path and file-write helpers for non-core layers."""

from __future__ import annotations

from pathlib import Path

from desloppify.core.discovery import file_paths as file_paths_mod


def matches_exclusion(rel_path: str, exclusion: str) -> bool:
    """Return True when *rel_path* matches exclusion pattern."""
    return file_paths_mod.matches_exclusion(rel_path, exclusion)


def rel(path: str) -> str:
    """Return slash-normalized project-relative path when possible."""
    return file_paths_mod.rel(path)


def resolve_path(filepath: str) -> str:
    """Resolve *filepath* against project root when it is relative."""
    return file_paths_mod.resolve_path(filepath)


def resolve_scan_file(
    filepath: str | Path,
    *,
    scan_root: str | Path | None = None,
) -> Path:
    """Resolve scan-time file paths with scan-root-first semantics."""
    return file_paths_mod.resolve_scan_file(filepath, scan_root=scan_root)


def safe_write_text(filepath: str | Path, content: str) -> None:
    """Atomically write UTF-8 text via temp+rename."""
    file_paths_mod.safe_write_text(filepath, content)


__all__ = [
    "matches_exclusion",
    "rel",
    "resolve_path",
    "resolve_scan_file",
    "safe_write_text",
]
