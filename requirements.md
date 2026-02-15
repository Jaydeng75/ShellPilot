# ShellPilot – Requirements Specification

## 1. Overview

ShellPilot is a failure-aware AI terminal copilot that activates only when a shell command fails.  
Its primary goal is to **diagnose failures, explain root causes, and suggest safe fixes using real execution context**, without disrupting normal terminal workflows.

This document defines the functional and non-functional requirements of the project.

---

## 2. Goals

- Reduce time spent debugging terminal command failures
- Eliminate copy-paste workflows to external AI tools
- Improve developer understanding of failures
- Ensure safety when suggesting or executing fixes
- Operate reliably with or without AI access

---

## 3. Functional Requirements

### 3.1 Command Execution
- The system SHALL execute arbitrary shell commands via a wrapper (`ai-run <command>`).
- The system SHALL preserve standard shell behavior.
- The system SHALL exit silently if the command succeeds.

---

### 3.2 Failure Detection
- The system SHALL detect command failure using non-zero exit codes.
- The system SHALL trigger analysis only on failure.
- The system SHALL avoid invoking AI for successful commands.

---

### 3.3 Context Collection
On failure, the system SHALL collect:
- Executed command string
- Exit code
- Standard error output (trimmed)
- Current working directory
- Recent shell command history (last N commands)
- Execution timestamp

---

### 3.4 Environment Detection
The system SHALL attempt to detect:
- Python version and virtual environment status
- Node.js version (if available)
- Docker daemon status
- Git repository state (if applicable)

Detection MUST be best-effort and non-blocking.

---

### 3.5 Root-Cause Analysis
- The system SHALL analyze the failure cause using:
  - Heuristic pattern matching (default)
  - AI-based analysis (optional)
- The system SHALL explain failures in plain English.
- The system SHALL avoid speculative or hallucinated explanations.

---

### 3.6 Fix Recommendation
- The system SHALL suggest a maximum of three fixes.
- Each fix SHALL include:
  - Exact command(s)
  - Risk level (Low / Medium)
  - Explanation of the fix
- The system SHALL prioritize non-destructive fixes.

---

### 3.7 Safety Guardrails
- The system SHALL block destructive commands by default.
- The system SHALL warn about risky operations (e.g., `sudo`, recursive deletes).
- The system SHALL never auto-execute fixes without user approval.

---

### 3.8 User Confirmation
- The system SHALL request explicit user confirmation before executing any fix.
- The system SHALL support a dry-run mode.
- The system SHALL exit gracefully if the user declines.

---

### 3.9 AI Integration (Optional)
- The system SHALL support a single LLM provider.
- The system SHALL use structured JSON output from the AI.
- The system SHALL function without AI if no API key is present.

---

### 3.10 Learning Mode (Optional)
- The system SHALL provide an optional learning mode.
- In learning mode, the system SHALL explain what each suggested command does.
- Learning mode SHALL be opt-in.

---

## 4. Non-Functional Requirements

### 4.1 Reliability
- The system SHALL not interfere with normal shell execution.
- Failures in analysis MUST NOT crash the tool.

---

### 4.2 Performance
- The system SHOULD add minimal latency to command execution.
- AI calls SHOULD be limited to failure scenarios only.

---

### 4.3 Security & Safety
- No command SHALL be executed without explicit user consent.
- No sensitive data SHALL be logged or stored persistently.
- Environment data SHALL remain local to the execution context.

---

### 4.4 Portability
- The system SHOULD support Linux and macOS.
- The system SHALL be shell-agnostic (bash / zsh).

---

## 5. Out of Scope

The following are intentionally excluded:
- General-purpose AI chat
- Agent-based task execution
- Long-term memory or telemetry
- Web UI or dashboards
- Multi-LLM provider support

---

## 6. Success Criteria

The project is considered successful if:
- Common terminal failures are correctly diagnosed
- Safe fixes are suggested and applied successfully
- Users gain understanding of the failure
- The tool remains predictable and safe

