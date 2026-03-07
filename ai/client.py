from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

from ..models import FailureAnalysis, FixSuggestion
from .bedrock_client import analyze_with_bedrock
from .schemas import validate_failure_analysis_payload


def _split_commands(command_text: str) -> List[str]:
    if not command_text:
        return []
    lines = [c.strip() for c in command_text.splitlines() if c.strip()]
    return lines if lines else [command_text.strip()]


def analyze_failure(
    context: Dict[str, Any], *, learning_mode: bool = False
) -> Optional[FailureAnalysis]:
    """
    AI-FIRST analysis.

    Order:
    1️⃣ Lambda backend (embeddings + llama)
    2️⃣ Fallback handled elsewhere if needed
    """

    try:
        raw = analyze_with_bedrock(context, learning_mode=learning_mode)

        if raw is None:
            return None

        print("\n[ShellPilot] Backend response:")
        print(raw)

        if not isinstance(raw, dict):
            return FailureAnalysis(
                reason="Backend returned non-JSON output",
                details=str(raw),
                fixes=[],
                provider="bedrock",
            )

        validated = validate_failure_analysis_payload(raw)

        fixes = []
        for f in validated.get("fixes", []):
            commands = _split_commands(f.get("command", ""))

            fixes.append(
                FixSuggestion(
                    risk=str(f.get("risk", "low")),
                    commands=commands,
                    explanation=str(f.get("explanation", "")),
                )
            )

        return FailureAnalysis(
            reason=str(validated.get("reason", "Command failed")),
            details=str(validated.get("details", "")),
            fixes=fixes,
            provider="bedrock",
        )

    except Exception as e:
        return FailureAnalysis(
            reason="AI invocation failed",
            details=str(e),
            fixes=[],
            provider="bedrock",
        )