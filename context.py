from __future__ import annotations

from typing import Dict
from .runner import RunResult


def _tail(text: str, n: int = 10) -> str:
    if not text:
        return ""
    lines = text.strip().splitlines()
    return "\n".join(lines[-n:])


def build_context(result: RunResult) -> Dict[str, str]:
    """
    Convert RunResult into AI context payload.
    """
    return {
        "command": result.command,
        "exit_code": result.exit_code,
        "stderr_tail": _tail(result.stderr),
        "stdout_tail": _tail(result.stdout),
    }
