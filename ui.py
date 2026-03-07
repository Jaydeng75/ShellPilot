from __future__ import annotations

from typing import Iterable, List, Optional

from .models import FailureAnalysis, FixSuggestion


def _indent(lines: Iterable[str], prefix: str = "  ") -> str:
    return "\n".join(prefix + ln for ln in lines)


def print_failure_header(command: str, exit_code: int) -> None:
    print("❌ Command Failed")
    print(f"  Command: {command}")
    print(f"  Exit code: {exit_code}")
    print("")


def print_analysis(analysis: FailureAnalysis, *, learning_mode: bool) -> None:
    print("Reason:")
    print(_indent([analysis.reason]))
    print("")
    print("Details:")
    print(_indent([analysis.details]))
    print("")
    if analysis.provider:
        print(f"(Provider: {analysis.provider})")
        print("")

    if not analysis.fixes:
        print("No safe fixes were suggested.")
        return

    print("Suggested Fixes:")
    for i, fix in enumerate(analysis.fixes, start=1):
        print(f"  {i}) ({fix.risk} Risk)")
        print(_indent(fix.commands, prefix="     "))
        if learning_mode:
            print("     Explanation:")
            print(_indent([fix.explanation], prefix="       "))
        else:
            print("     Explanation: " + fix.explanation)
        print("")


def prompt_choice(num_fixes: int) -> Optional[int]:
    if num_fixes <= 0:
        return None
    if num_fixes == 1:
        ans = input("Apply fix? (y/n): ").strip().lower()
        return 1 if ans in {"y", "yes"} else None

    ans = input(f"Choose a fix to apply (1-{num_fixes}) or 'n' to skip: ").strip().lower()
    if ans in {"n", "no"}:
        return None
    try:
        idx = int(ans)
        if 1 <= idx <= num_fixes:
            return idx
    except ValueError:
        pass
    return None


def print_safety_messages(msgs: List[str]) -> None:
    for m in msgs:
        print(f"⚠️  {m}")
