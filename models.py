from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal, Optional


RiskLevel = Literal["low", "medium"]


@dataclass(frozen=True)
class FailureContext:
    command: str
    exit_code: int
    cwd: str
    timestamp_utc: str
    stderr_tail: str
    stdout_tail: str
    last_commands: List[str] = field(default_factory=list)
    env_signals: Dict[str, Any] = field(default_factory=dict)
    project_signals: Dict[str, Any] = field(default_factory=dict)

    def to_prompt_dict(self) -> Dict[str, Any]:
        return {
            "command": self.command,
            "exit_code": self.exit_code,
            "cwd": self.cwd,
            "timestamp_utc": self.timestamp_utc,
            "stderr_tail": self.stderr_tail,
            "stdout_tail": self.stdout_tail,
            "last_commands": self.last_commands,
            "env_signals": self.env_signals,
            "project_signals": self.project_signals,
        }


@dataclass(frozen=True)
class FixSuggestion:
    risk: RiskLevel
    commands: List[str]
    explanation: str


@dataclass(frozen=True)
class FailureAnalysis:
    reason: str
    details: str
    fixes: List[FixSuggestion] = field(default_factory=list)
    provider: Optional[str] = None
