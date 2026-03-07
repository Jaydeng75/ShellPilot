from __future__ import annotations

import os
import shlex
import subprocess
from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class RunResult:
    command: str
    exit_code: int
    stdout: str
    stderr: str
    interrupted: bool = False


def _stringify_command(argv: List[str]) -> str:
    return " ".join(shlex.quote(a) for a in argv)


def run_command(argv: List[str], *, timeout_s: Optional[int] = None) -> RunResult:
    """Run a command and capture stdout/stderr.

    - Uses text mode.
    - Normalizes common shell failures (e.g. command not found).
    - Returns exit code + output. Marks interrupted on KeyboardInterrupt.
    """
    cmd_str = _stringify_command(argv)

    try:
        cp = subprocess.run(
            argv,
            text=True,
            capture_output=True,
            timeout=timeout_s,
            env=os.environ.copy(),
        )
        return RunResult(
            command=cmd_str,
            exit_code=int(cp.returncode),
            stdout=cp.stdout or "",
            stderr=cp.stderr or "",
            interrupted=False,
        )

    except FileNotFoundError:
        # ✅ Normalize "command not found"
        return RunResult(
            command=cmd_str,
            exit_code=127,  # POSIX convention
            stdout="",
            stderr=f"{argv[0]}: command not found",
            interrupted=False,
        )

    except KeyboardInterrupt:
        return RunResult(
            command=cmd_str,
            exit_code=130,  # conventional for SIGINT
            stdout="",
            stderr="Command interrupted (SIGINT).",
            interrupted=True,
        )