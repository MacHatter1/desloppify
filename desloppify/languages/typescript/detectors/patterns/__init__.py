"""Pattern-analysis detectors and CLI helpers for TypeScript."""

from .analysis import detect_pattern_anomalies
from .catalog import PATTERN_FAMILIES
from .cli import cmd_patterns

__all__ = ["PATTERN_FAMILIES", "cmd_patterns", "detect_pattern_anomalies"]
