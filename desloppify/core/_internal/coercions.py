"""Pure coercion helpers for CLI/config input parsing."""

from __future__ import annotations


def coerce_positive_int(value: object, *, default: int, minimum: int = 1) -> int:
    """Parse positive integer CLI/config inputs with a safe default."""
    if value is None:
        return default
    if not isinstance(value, int | float | str):
        return default
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    return parsed if parsed >= minimum else default


def coerce_positive_float(value: object, *, default: float, minimum: float = 0.1) -> float:
    """Parse positive float CLI/config inputs with a safe default."""
    if value is None:
        return default
    if not isinstance(value, int | float | str):
        return default
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return default
    return parsed if parsed >= minimum else default


def coerce_non_negative_float(value: object, *, default: float) -> float:
    """Parse non-negative float CLI/config inputs with a safe default."""
    if value is None:
        return default
    if not isinstance(value, int | float | str):
        return default
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return default
    return parsed if parsed >= 0.0 else default


def coerce_non_negative_int(value: object, *, default: int) -> int:
    """Parse non-negative integer CLI/config inputs with a safe default."""
    if value is None:
        return default
    if not isinstance(value, int | float | str):
        return default
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    return parsed if parsed >= 0 else default


def coerce_confidence(value: object, *, default: float = 1.0) -> float:
    """Coerce a value to a confidence float clamped to [0.0, 1.0]."""
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return default
    return max(0.0, min(1.0, parsed))


def option_value(
    *,
    options: object | None,
    legacy_options: dict[str, object],
    name: str,
    default: object,
) -> object:
    """Resolve option value from legacy kwargs first, then options object."""
    if isinstance(legacy_options, dict) and name in legacy_options:
        return legacy_options[name]

    if options is None:
        return default

    if isinstance(options, dict) and name in options:
        return options[name]

    missing = object()
    value = getattr(options, name, missing)
    if value is not missing:
        return value
    return default


__all__ = [
    "coerce_confidence",
    "coerce_non_negative_float",
    "coerce_non_negative_int",
    "option_value",
    "coerce_positive_float",
    "coerce_positive_int",
]
