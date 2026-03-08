"""Compatibility facade for React anti-pattern detectors."""

from __future__ import annotations

from desloppify.languages.typescript.detectors.react_cli import cmd_react
from desloppify.languages.typescript.detectors.react_context import (
    detect_context_nesting,
)
from desloppify.languages.typescript.detectors.react_hook_bloat import (
    _count_return_fields,
    detect_boolean_state_explosion,
    detect_hook_return_bloat,
)
from desloppify.languages.typescript.detectors.react_state_sync import (
    MAX_EFFECT_BODY,
    detect_state_sync,
)

__all__ = [
    "MAX_EFFECT_BODY",
    "_count_return_fields",
    "cmd_react",
    "detect_boolean_state_explosion",
    "detect_context_nesting",
    "detect_hook_return_bloat",
    "detect_state_sync",
]
