from __future__ import annotations

import os
from pathlib import Path
from typing import List


def _read_last_lines(path: Path, n: int) -> List[str]:
    try:
        with path.open("r", encoding="utf-8", errors="ignore") as f:
            lines = f.read().splitlines()
        return [ln for ln in lines[-n:] if ln.strip()]
    except Exception:
        return []


def get_last_commands(max_items: int = 3) -> List[str]:
    """Best-effort shell history capture.

    We try:
    1) $HISTFILE if set
    2) common bash/zsh history files

    Note: Many shells append history on exit, so this is inherently best-effort.
    """
    candidates: List[Path] = []

    histfile = os.environ.get("HISTFILE")
    if histfile:
        candidates.append(Path(histfile).expanduser())

    home = Path.home()
    candidates.extend(
        [
            home / ".zsh_history",
            home / ".bash_history",
        ]
    )

    seen = set()
    last: List[str] = []
    for p in candidates:
        if p in seen:
            continue
        seen.add(p)
        if not p.exists():
            continue
        # zsh history lines look like: ': 1700000000:0;cmd ...'
        raw = _read_last_lines(p, 200)
        for ln in reversed(raw):
            cmd = ln.strip()
            if cmd.startswith(": ") and ";" in cmd:
                cmd = cmd.split(";", 1)[1].strip()
            if not cmd:
                continue
            if cmd in last:
                continue
            last.append(cmd)
            if len(last) >= max_items:
                return list(reversed(last))
    return list(reversed(last))
