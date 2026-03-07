from __future__ import annotations

from typing import Any, Dict, List


def failure_analysis_schema() -> Dict[str, Any]:
    """JSON schema used for structured output.

    This is mirrored in the repo root as `schema.json` for judge-facing review.
    """
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "reason": {"type": "string"},
            # Make 'details' optional (AI may omit it)
            "details": {"type": "string"},
            "fixes": {
                "type": "array",
                "maxItems": 3,
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "command": {"type": "string"},
                        # allow "high" as well
                        "risk": {"type": "string", "enum": ["low", "medium", "high"]},
                        "explanation": {"type": "string"},
                    },
                    "required": ["command", "risk", "explanation"],
                },
            },
        },
        # require reason + fixes; details optional
        "required": ["reason", "fixes"],
    }


def validate_failure_analysis_payload(payload: Any) -> Dict[str, Any]:
    """Lightweight validator (no extra dependencies).

    Returns a cleaned dict on success; raises ValueError on invalid structure.
    """
    if not isinstance(payload, dict):
        raise ValueError("payload must be an object")

    allowed_top = {"reason", "details", "fixes"}
    extra = set(payload.keys()) - allowed_top
    if extra:
        raise ValueError(f"unexpected top-level keys: {sorted(extra)}")

    reason = payload.get("reason")
    details = payload.get("details", "")
    fixes = payload.get("fixes")

    if not isinstance(reason, str) or not reason.strip():
        raise ValueError("reason must be a non-empty string")
    if not isinstance(details, str):
        raise ValueError("details must be a string")
    if not isinstance(fixes, list):
        raise ValueError("fixes must be an array")

    cleaned_fixes: List[Dict[str, Any]] = []
    for f in fixes[:3]:
        if not isinstance(f, dict):
            raise ValueError("each fix must be an object")
        allowed_fix = {"command", "risk", "explanation"}
        extra_fix = set(f.keys()) - allowed_fix
        if extra_fix:
            raise ValueError(f"unexpected fix keys: {sorted(extra_fix)}")

        cmd = f.get("command")
        risk = f.get("risk")
        expl = f.get("explanation")

        if not isinstance(cmd, str) or not cmd.strip():
            raise ValueError("fix.command must be a non-empty string")
        if not isinstance(risk, str):
            raise ValueError("fix.risk must be a string")
        risk_l = risk.strip().lower()
        if risk_l not in {"low", "medium", "high"}:
            raise ValueError("fix.risk must be 'low', 'medium', or 'high'")
        if not isinstance(expl, str):
            raise ValueError("fix.explanation must be a string")

        cleaned_fixes.append({"command": cmd.strip(), "risk": risk_l, "explanation": expl.strip()})

    return {"reason": reason.strip(), "details": details.strip(), "fixes": cleaned_fixes}