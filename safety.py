from __future__ import annotations

from typing import List, Tuple

from .models import FailureAnalysis, FixSuggestion


DANGEROUS_PATTERNS = [
    "rm -rf /",
    "mkfs",
    "shutdown",
    "reboot",
]


def is_safe_command(cmd: str) -> bool:
    for pattern in DANGEROUS_PATTERNS:
        if pattern in cmd:
            return False
    return True


def filter_safe_fixes(
    analysis: FailureAnalysis,
) -> Tuple[FailureAnalysis, List[str]]:
    """
    Filters unsafe fixes but keeps the FailureAnalysis structure.
    """

    safe: List[FixSuggestion] = []
    messages: List[str] = []

    for fix in analysis.fixes:
        allowed = True

        for cmd in fix.commands:
            if not is_safe_command(cmd):
                allowed = False
                messages.append(f"Blocked dangerous command: {cmd}")
                break

        if allowed:
            safe.append(fix)

    # Create NEW FailureAnalysis (dataclass is frozen)
    filtered = FailureAnalysis(
        reason=analysis.reason,
        details=analysis.details,
        fixes=safe,
        provider=analysis.provider,
    )

    return filtered, messages
