from __future__ import annotations

import sys
import os
from typing import List

from .runner import run_command
from .context import build_context
from .ai import analyze_failure
from .safety import filter_safe_fixes
from .ui import (
    print_failure_header,
    print_analysis,
    prompt_choice,
    print_safety_messages,
)

# Only auto-test safe commands
SAFE_TEST_PREFIXES = ["pip", "npm", "python", "cargo", "go"]


# -------------------------------------------------
# Safe fix verification
# -------------------------------------------------
def verify_fix(command: str) -> bool:
    """
    Optionally test a fix command before suggesting it.
    Only runs for safe command prefixes.
    """

    try:

        prefix = command.split()[0]

        if prefix not in SAFE_TEST_PREFIXES:
            return True

        print("🔎 Verifying fix...")

        result = run_command(command.split())

        if result.exit_code == 0:
            print("✔ Fix verified")
            return True

        print("✖ Fix failed during verification")
        return False

    except Exception:
        return False


# -------------------------------------------------
# Stats command
# -------------------------------------------------
def print_stats() -> None:

    print("ShellPilot Stats")
    print("----------------")

    try:

        import boto3

        table_name = os.getenv("SHELLPILOT_MEMORY_TABLE", "shellpilot-memory")

        dynamodb = boto3.resource("dynamodb", region_name="ap-south-1")
        table = dynamodb.Table(table_name)

        items = []
        resp = table.scan()

        items.extend(resp.get("Items", []))

        while "LastEvaluatedKey" in resp:
            resp = table.scan(ExclusiveStartKey=resp["LastEvaluatedKey"])
            items.extend(resp.get("Items", []))

        print(f"Errors learned: {len(items)}")

        fix_counts = {}

        for item in items:

            fix = item.get("fix")

            if fix:
                fix_counts[fix] = fix_counts.get(fix, 0) + 1

        if fix_counts:

            print("")
            print("Top learned fixes:")

            top = sorted(
                fix_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )[:3]

            for fix, count in top:
                print(f"• {fix} ({count} times)")

    except Exception as e:

        print("Unable to fetch stats.")
        print(str(e))


# -------------------------------------------------
# Main CLI
# -------------------------------------------------
def main() -> None:

    argv: List[str] = sys.argv[1:]

    if not argv:

        print("Usage:")
        print("  ai-run <command>")
        print("  ai-run stats")

        sys.exit(1)

    # -----------------------------
    # Stats command
    # -----------------------------
    if len(argv) == 1 and argv[0] == "stats":

        print_stats()
        return

    # -----------------------------
    # Run the command
    # -----------------------------
    result = run_command(argv)

    if result.exit_code == 0:
        return

    print_failure_header(result.command, result.exit_code)

    context = build_context(result)

    learning_mode = os.getenv("SHELLPILOT_MODE") == "aws"

    analysis = analyze_failure(context, learning_mode=learning_mode)

    if not analysis:

        print("ShellPilot could not analyze this failure.")
        return

    filtered, safety_msgs = filter_safe_fixes(analysis)

    if safety_msgs:
        print_safety_messages(safety_msgs)

    print_analysis(filtered, learning_mode=learning_mode)

    if not filtered.fixes:
        return

    # -----------------------------
    # Optional verification
    # -----------------------------
    verified_fixes = []

    for fix in filtered.fixes:

        if not fix.commands:
            continue

        if verify_fix(fix.commands[0]):
            verified_fixes.append(fix)

    if verified_fixes:
        from dataclasses import replace

        filtered = replace(filtered, fixes=verified_fixes)

    choice = prompt_choice(len(filtered.fixes))

    if choice is None:
        return

    fix = filtered.fixes[choice - 1]

    print("")
    print(f"Executing fix #{choice}:")

    for cmd in fix.commands:

        print(f"  $ {cmd}")

        cp = run_command(cmd.split())

        if cp.exit_code != 0:

            print("❌ Fix failed")
            return

    print("")
    print("✅ Fix completed successfully")
    print("")
    print("🧠 ShellPilot learned this error pattern for faster fixes next time.")

    # -----------------------------
    # Optional rerun
    # -----------------------------
    try:

        rerun = input("Re-run original command now? (y/n): ").strip().lower()

        if rerun in {"y", "yes"}:
            run_command(argv)

    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()