from __future__ import annotations

import os
import json
from typing import Any, Dict, Optional

import requests

from ..heuristics import heuristic_analysis


def analyze_with_bedrock(
    context: Dict[str, Any], *, learning_mode: bool = False
) -> Optional[Dict[str, Any]]:
    """
    Analyze a terminal failure.

    Modes:
    1) Backend API (Lambda → Embeddings + Llama)
    2) Stub fallback (heuristics)
    """

    backend_url = (os.getenv("SHELLPILOT_BACKEND_URL") or "").strip()

    if backend_url:
        return _call_backend(backend_url, context=context)

    return _stub_payload(context)


# ---------------------------------------------------------------------
# Backend mode (API Gateway → Lambda)
# ---------------------------------------------------------------------
def _call_backend(url: str, *, context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Send command failure to Lambda endpoint.
    """

    payload = {
        "command": context.get("command", ""),
        "stderr": context.get("stderr_tail", ""),
        "exit_code": context.get("exit_code", 1),
    }

    resp = requests.post(url, json=payload, timeout=45)
    resp.raise_for_status()

    data = resp.json()

    if not isinstance(data, dict):
        raise RuntimeError("Backend returned non-object JSON")

    # API Gateway wraps Lambda response
    if "body" in data:
        body = data["body"]

        if isinstance(body, str):
            body = json.loads(body)

        return body

    return data


# ---------------------------------------------------------------------
# Stub fallback (no AI)
# ---------------------------------------------------------------------
def _stub_payload(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Local heuristic fallback when backend is not configured.
    """

    h = heuristic_analysis(
        str(context.get("command", "")),
        str(context.get("stderr_tail", "")),
    )

    if h and h.fixes:
        return {
            "reason": h.reason,
            "fixes": [
                {
                    "command": "\n".join(fx.commands),
                    "risk": str(fx.risk),
                    "explanation": fx.explanation,
                }
                for fx in h.fixes[:3]
            ],
        }

    return {
        "reason": "Command failed (stub mode)",
        "fixes": [],
    }