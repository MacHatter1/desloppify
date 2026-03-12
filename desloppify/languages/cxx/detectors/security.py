"""C/C++-specific security detectors."""

from __future__ import annotations

import logging
import re
from pathlib import Path

from desloppify.engine.detectors.security import rules as security_detector_mod
from desloppify.engine.policy.zones import FileZoneMap, Zone
from desloppify.languages._framework.base.types import LangSecurityResult

logger = logging.getLogger(__name__)

_COMMAND_INJECTION_RE = re.compile(r"\b(?:std::)?system\s*\(")
_UNSAFE_C_STRING_RE = re.compile(
    r"\b(?:strcpy|strcat|sprintf|vsprintf|gets|scanf|sscanf|fscanf)\s*\("
)
_INSECURE_RANDOM_RE = re.compile(
    r"\b(?:std::)?rand\s*\([^)]*\).*(?:token|password|secret|key|nonce|salt|otp)",
    re.IGNORECASE,
)
_WEAK_HASH_RE = re.compile(r"\b(?:MD5|SHA1)\b", re.IGNORECASE)


def _iter_security_entries(filepath: str, content: str) -> list[dict]:
    entries: list[dict] = []
    for line_num, line in enumerate(content.splitlines(), 1):
        stripped = line.lstrip()
        if stripped.startswith("//"):
            continue

        if _COMMAND_INJECTION_RE.search(line):
            entries.append(
                security_detector_mod.make_security_entry(
                    filepath,
                    line_num,
                    line,
                    security_detector_mod.SecurityRule(
                        check_id="command_injection",
                        summary="Shell command execution may enable command injection",
                        severity="high",
                        confidence="high",
                        remediation="Avoid system(); use explicit process APIs with validated arguments.",
                    ),
                )
            )

        if _UNSAFE_C_STRING_RE.search(line):
            entries.append(
                security_detector_mod.make_security_entry(
                    filepath,
                    line_num,
                    line,
                    security_detector_mod.SecurityRule(
                        check_id="unsafe_c_string",
                        summary="Unsafe C string API may cause buffer overflow",
                        severity="high",
                        confidence="high",
                        remediation="Use bounded APIs or std::string/std::array with explicit size checks.",
                    ),
                )
            )

        if _INSECURE_RANDOM_RE.search(line):
            entries.append(
                security_detector_mod.make_security_entry(
                    filepath,
                    line_num,
                    line,
                    security_detector_mod.SecurityRule(
                        check_id="insecure_random",
                        summary="Insecure random used in a security-sensitive context",
                        severity="medium",
                        confidence="medium",
                        remediation="Use a cryptographic RNG instead of rand() for secrets or tokens.",
                    ),
                )
            )

        if _WEAK_HASH_RE.search(line):
            entries.append(
                security_detector_mod.make_security_entry(
                    filepath,
                    line_num,
                    line,
                    security_detector_mod.SecurityRule(
                        check_id="weak_crypto_hash",
                        summary="Weak hash algorithm detected",
                        severity="medium",
                        confidence="medium",
                        remediation="Use a modern hash or password-hashing algorithm appropriate to the use case.",
                    ),
                )
            )

    return entries


def detect_cxx_security(
    files: list[str],
    zone_map: FileZoneMap | None,
) -> LangSecurityResult:
    """Detect C/C++-specific security issues with a normalized result contract."""
    entries: list[dict] = []
    files_scanned = 0

    for filepath in files:
        if not filepath.endswith((".c", ".cc", ".cpp", ".cxx", ".h", ".hpp")):
            continue

        if zone_map is not None:
            zone = zone_map.get(filepath)
            if zone in (Zone.GENERATED, Zone.VENDOR):
                continue

        try:
            content = Path(filepath).read_text(errors="replace")
        except OSError as exc:
            logger.debug("Skipping unreadable C/C++ file %s in security detector: %s", filepath, exc)
            continue

        files_scanned += 1
        entries.extend(_iter_security_entries(filepath, content))

    return LangSecurityResult(entries=entries, files_scanned=files_scanned)


__all__ = ["detect_cxx_security"]
