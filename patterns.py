from __future__ import annotations

import re
from typing import List, Optional

from .models import FailureAnalysis, FixSuggestion


def pip_editable_missing_arg_analysis(command: str, stderr: str) -> Optional[FailureAnalysis]:
    """Detects `pip install -e` invoked without a target path.

    Guaranteed demo target:
      python3 -m pip install -e
    Typical pip message:
      "ERROR: -e option requires 1 argument"
    """
    if "pip" not in command:
        return None

    # Don't use \b word boundaries ("-" is non-word). Just look for the flag token.
    if not re.search(r"(?:^|\s)(-e|--editable)(?:\s|$)", command):
        return None

    if not re.search(r"option\s+requires\s+1\s+argument", stderr, re.I):
        return None

    fixes: List[FixSuggestion] = [
        FixSuggestion(
            risk="low",
            commands=["python3 -m pip install -e ."],
            explanation=(
                "The -e/--editable flag requires a path (usually the current project). "
                "Using '.' installs the package in editable mode from the current directory."
            ),
        )
    ]

    return FailureAnalysis(
        reason="pip editable install is missing a target path",
        details="pip was run with -e/--editable but no path was provided (pip expects a directory like '.' or a VCS URL).",
        fixes=fixes,
        provider="heuristic",
    )
