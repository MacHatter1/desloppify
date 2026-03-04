"""Target-score normalization helpers for command modules."""

from __future__ import annotations

from desloppify.base.config import (  # noqa: F401 — re-export
    coerce_target_score,
    target_strict_score_from_config,
)

__all__ = [
    "coerce_target_score",
    "target_strict_score_from_config",
]
