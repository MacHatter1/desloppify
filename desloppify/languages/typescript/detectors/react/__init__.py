"""React-specific TypeScript detectors grouped by concern."""

from .context import detect_context_nesting
from .hook_bloat import detect_boolean_state_explosion, detect_hook_return_bloat
from .state_sync import detect_state_sync

__all__ = [
    "detect_boolean_state_explosion",
    "detect_context_nesting",
    "detect_hook_return_bloat",
    "detect_state_sync",
]
