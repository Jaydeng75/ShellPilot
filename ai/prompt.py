from __future__ import annotations

import json
from typing import Any, Dict


def build_prompt(context: Dict[str, Any], *, learning_mode: bool, schema: Dict[str, Any]) -> str:
    rules = [
        "You are ShellPilot, a failure-aware terminal copilot.",
        "You only activate when a command fails.",
        "You MUST only use the provided context. If info is missing, say so explicitly.",
        "Avoid generic advice. Be specific to the command, stderr, cwd, and environment signals.",
        "Never suggest destructive commands (e.g., rm -rf /), recursive deletes, or hard resets unless absolutely necessary (prefer safer alternatives).",
        "Never suggest sudo unless you explain why elevated privileges are needed.",
        "Return valid JSON ONLY, matching the provided schema. No markdown, no extra keys.",
        "Provide at most 3 fixes. Each fix must be actionable and relevant to the context.",
        "If possible, include a short 'details' field that echoes the stderr or concrete diagnostic info."
    ]
    if learning_mode:
        rules.append("Learning mode is enabled: make explanations slightly more educational, but keep them concise.")

    return (
        "SYSTEM RULES:\n"
        + "\n".join(f"- {r}" for r in rules)
        + "\n\n"
        + "OUTPUT JSON SCHEMA (JSON Schema):\n"
        + json.dumps(schema, indent=2, sort_keys=True)
        + "\n\n"
        + "FAILURE CONTEXT (JSON):\n"
        + json.dumps(context, indent=2, sort_keys=True)
        + "\n\n"
        + "Now produce the JSON output."
    )