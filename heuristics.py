from __future__ import annotations

import re
from typing import List, Optional

from .analyzer import extract_port_from_error
from .models import FailureAnalysis, FixSuggestion
from .patterns import pip_editable_missing_arg_analysis


def heuristic_analysis(command: str, stderr: str) -> Optional[FailureAnalysis]:
    """Fallback analysis when no LLM is configured.

    Handles a small set of common demo failures:
    - Python missing module/import
    - Port already in use
    - Git rebase/merge conflicts
    - Command not found / permission denied
    """
    s = stderr.lower()

    # 0) pip editable (-e/--editable) missing argument (guaranteed demo)
    pip_editable = pip_editable_missing_arg_analysis(command, stderr)
    if pip_editable is not None:
        return pip_editable

    # 1) Python missing module
    m = re.search(r"modulenotfounderror: no module named ['\"]([^'\"]+)['\"]", stderr, re.I)
    if m:
        pkg = m.group(1)
        fixes: List[FixSuggestion] = [
            FixSuggestion(
                risk="low",
                commands=[f"python3 -m pip install {pkg}"],
                explanation=f"Installs the missing Python package '{pkg}' into the current Python environment.",
            )
        ]
        return FailureAnalysis(
            reason="Python module is missing",
            details=(
                f"Python raised ModuleNotFoundError for '{pkg}'. The package is not installed in the active environment."
            ),
            fixes=fixes,
            provider="heuristic",
        )

    # 2) pip permission + venv guidance
    if "pip" in command and ("permission denied" in s or "not permitted" in s):
        return FailureAnalysis(
            reason="Permission error while installing packages",
            details="The install attempted to write to a location your user cannot modify.",
            fixes=[
                FixSuggestion(
                    risk="low",
                    commands=["python3 -m pip install --user <package>"],
                    explanation="Installs the package into your user site-packages instead of system directories.",
                ),
                FixSuggestion(
                    risk="low",
                    commands=["python3 -m venv .venv", "source .venv/bin/activate"],
                    explanation="Creates and activates an isolated virtual environment (recommended).",
                ),
            ],
            provider="heuristic",
        )


    # 3) Port already in use
    if "address already in use" in s or "eaddrinuse" in s:
        # Prefer parsing the port from the command (e.g. `python -m http.server 8000`).
        port = None
        cm = re.search(r"\bhttp\.server\s+(?P<port>\d{2,5})\b", command)
        if cm:
            port = int(cm.group("port"))
        if port is None:
            # Try stderr extraction (filters out Errno like [Errno 98]).
            port = extract_port_from_error(stderr)
        # If we still can't extract a port reliably, default to a common dev port for guidance.
        port = port or 8000
        alt_port = port + 1

        # Try to preserve the original command when possible.
        alt_cmd = command.replace(str(port), str(alt_port)) if str(port) in command else f"{command}  # try port {alt_port}"

        return FailureAnalysis(
            reason="Port is already in use",
            details=f"Another process is already listening on port {port}.",
            fixes=[
                FixSuggestion(
                    risk="low",
                    commands=[alt_cmd],
                    explanation="Re-run the server on a different port to avoid the conflict.",
                ),
                FixSuggestion(
                    risk="medium",
                    commands=[
                        f"lsof -nP -iTCP:{port} -sTCP:LISTEN",
                        "kill -TERM <PID>",
                    ],
                    explanation="Identify the process holding the port and stop it (only if you recognize it).",
                ),
            ],
            provider="heuristic",
        )

# 4) Git conflicts
    if "conflict" in s and ("git rebase" in command or "rebase" in s):
        return FailureAnalysis(
            reason="Git rebase has conflicts",
            details="Git stopped the rebase because it encountered conflicting changes that require manual resolution.",
            fixes=[
                FixSuggestion(
                    risk="low",
                    commands=[
                        "git status",
                        "# edit conflicted files and resolve conflict markers",
                        "git add <resolved-files>",
                        "git rebase --continue",
                    ],
                    explanation="Resolve conflicts, stage the resolved files, then continue the rebase.",
                ),
                FixSuggestion(
                    risk="low",
                    commands=["git rebase --abort"],
                    explanation="Safely aborts the rebase and returns to the pre-rebase state.",
                ),
            ],
            provider="heuristic",
        )

    # 5) Command not found
    if "command not found" in s or "not recognized as an internal" in s:
        return FailureAnalysis(
            reason="Command not found",
            details="The shell could not find the program in PATH.",
            fixes=[
                FixSuggestion(
                    risk="low",
                    commands=["which <command>", "echo $PATH"],
                    explanation="Verify whether the program is installed and whether it is on your PATH.",
                )
            ],
            provider="heuristic",
        )

    # 6) Permission denied
    if "permission denied" in s:
        return FailureAnalysis(
            reason="Permission denied",
            details="The command attempted an action your user is not permitted to do.",
            fixes=[
                FixSuggestion(
                    risk="low",
                    commands=["ls -l <path>", "chmod u+rw <path>"],
                    explanation="Inspect permissions and grant your user access if appropriate.",
                )
            ],
            provider="heuristic",
        )

    return None
