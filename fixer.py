from __future__ import annotations

import os
import shlex
import subprocess
from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class FixRun:
    command: str
    exit_code: int
    stdout: str
    stderr: str


def _pick_shell() -> List[str]:
    shell = os.environ.get("SHELL") or ""
    if shell.endswith("zsh"):
        return [shell, "-lc"]
    if shell.endswith("bash"):
        return [shell, "-lc"]
    # fall back
    return ["bash", "-lc"]


def run_fix_commands(commands: List[str]) -> List[FixRun]:
    """Execute commands sequentially. Stop on failure."""
    results: List[FixRun] = []
    shell_prefix = _pick_shell()

    for cmd in commands:
        cp = subprocess.run(
            shell_prefix + [cmd],
            text=True,
            capture_output=True,
            env=os.environ.copy(),
        )
        results.append(
            FixRun(
                command=cmd,
                exit_code=int(cp.returncode),
                stdout=cp.stdout or "",
                stderr=cp.stderr or "",
            )
        )
        if cp.returncode != 0:
            break

    return results
