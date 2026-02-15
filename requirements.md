# Requirements Document

## Introduction

ShellPilot is a failure-aware AI terminal copilot that activates only when shell commands fail. It analyzes real execution context (exit code, stderr, environment signals, command history) to explain root causes and suggest safe, actionable fixes. All fixes require explicit user confirmation before execution.

The tool addresses the common developer pain point of debugging cryptic terminal errors by keeping the workflow inside the terminal, providing contextual analysis, and ensuring safety through mandatory confirmation of all suggested fixes.

## Glossary

- **ShellPilot**: The CLI-based developer productivity tool system
- **Command_Wrapper**: The CLI interface that executes user commands and detects failures
- **Context_Collector**: Component that captures execution environment and failure details
- **Analyzer**: Component that performs root-cause analysis using heuristics and optional AI
- **Fix_Suggester**: Component that generates and ranks potential fixes
- **Confirmation_Handler**: Component that manages user approval before executing fixes
- **Environment_Detector**: Component that identifies runtime environment characteristics
- **Heuristic_Engine**: Pattern-matching system for common failure scenarios
- **AI_Provider**: Optional external LLM service for advanced analysis
- **Risk_Level**: Classification of fix safety (Low, Medium)

## Requirements

### Requirement 1: Command Execution Wrapper

**User Story:** As a developer, I want to wrap my shell commands with an AI-aware tool, so that I can get automatic help when commands fail.

#### Acceptance Criteria

1. THE Command_Wrapper SHALL accept arbitrary shell commands via `ai-run <command>` syntax
2. WHEN a command is provided, THE Command_Wrapper SHALL execute it in the current shell environment
3. WHEN a command executes, THE Command_Wrapper SHALL preserve all standard output to the terminal
4. WHEN a command executes, THE Command_Wrapper SHALL preserve all standard error output to the terminal
5. WHEN a command completes, THE Command_Wrapper SHALL capture the exit code
6. THE Command_Wrapper SHALL support bash and zsh shells on Linux and macOS

### Requirement 2: Failure Detection

**User Story:** As a developer, I want the tool to automatically detect when my commands fail, so that I receive help only when needed.

#### Acceptance Criteria

1. WHEN a command exits with a non-zero exit code, THE Command_Wrapper SHALL classify it as a failure
2. WHEN a command exits with exit code 0, THE Command_Wrapper SHALL terminate without further action
3. WHEN a failure is detected, THE Command_Wrapper SHALL trigger the analysis workflow
4. THE Command_Wrapper SHALL not interfere with successful command execution

### Requirement 3: Execution Context Capture

**User Story:** As a developer, I want the tool to capture relevant execution context, so that failure analysis is accurate and contextual.

#### Acceptance Criteria

1. WHEN a failure occurs, THE Context_Collector SHALL capture the full command string
2. WHEN a failure occurs, THE Context_Collector SHALL capture the exit code
3. WHEN a failure occurs, THE Context_Collector SHALL capture all stderr output
4. WHEN a failure occurs, THE Context_Collector SHALL capture the current working directory
5. WHEN a failure occurs, THE Context_Collector SHALL capture recent command history from the shell
6. THE Context_Collector SHALL structure captured data for analysis consumption

### Requirement 4: Environment Detection

**User Story:** As a developer, I want the tool to detect my runtime environment, so that suggestions are relevant to my specific setup.

#### Acceptance Criteria

1. WHEN analyzing a failure, THE Environment_Detector SHALL attempt to detect the active Python version
2. WHEN analyzing a failure, THE Environment_Detector SHALL attempt to detect active Python virtual environments
3. WHEN analyzing a failure, THE Environment_Detector SHALL attempt to detect the active Node.js version
4. WHEN analyzing a failure, THE Environment_Detector SHALL attempt to detect Docker daemon availability
5. WHEN analyzing a failure, THE Environment_Detector SHALL attempt to detect Git repository status
6. IF environment detection fails for any component, THEN THE Environment_Detector SHALL continue without that information
7. THE Environment_Detector SHALL complete detection within 2 seconds

### Requirement 5: Root Cause Analysis

**User Story:** As a developer, I want to understand why my command failed, so that I can learn and avoid similar issues.

#### Acceptance Criteria

1. WHEN a failure is detected, THE Analyzer SHALL perform heuristic pattern matching against known failure patterns
2. WHEN heuristic analysis is insufficient, THE Analyzer SHALL optionally invoke the AI_Provider for advanced analysis
3. WHEN the AI_Provider is unavailable, THE Analyzer SHALL rely solely on heuristic results
4. THE Analyzer SHALL generate a plain-English explanation of the root cause
5. THE Analyzer SHALL identify the specific error type when possible
6. THE Analyzer SHALL complete analysis within 5 seconds for heuristic-only mode

### Requirement 6: Fix Suggestion Generation

**User Story:** As a developer, I want to receive actionable fix suggestions, so that I can quickly resolve failures.

#### Acceptance Criteria

1. WHEN analysis completes, THE Fix_Suggester SHALL generate up to 3 potential fixes
2. WHEN generating fixes, THE Fix_Suggester SHALL assign each fix a Risk_Level of Low or Medium
3. WHEN generating fixes, THE Fix_Suggester SHALL provide a plain-English explanation for each fix
4. WHEN generating fixes, THE Fix_Suggester SHALL include the exact command string to execute
5. THE Fix_Suggester SHALL prioritize fixes by likelihood of success and safety
6. THE Fix_Suggester SHALL not suggest fixes with destructive operations without clear warnings

### Requirement 7: User Confirmation Requirement

**User Story:** As a developer, I want explicit control over which fixes are executed, so that I maintain safety and predictability.

#### Acceptance Criteria

1. WHEN fixes are suggested, THE Confirmation_Handler SHALL display all fixes with their risk levels
2. WHEN fixes are displayed, THE Confirmation_Handler SHALL wait for explicit user input
3. THE Confirmation_Handler SHALL not execute any fix without user confirmation
4. WHEN a user selects a fix, THE Confirmation_Handler SHALL display the exact command before execution
5. WHEN a user confirms a fix, THE Confirmation_Handler SHALL execute the selected command
6. WHEN a user rejects all fixes, THE Confirmation_Handler SHALL terminate without action

### Requirement 8: AI Integration

**User Story:** As a developer, I want the tool to leverage AI for complex failures, so that I get better analysis beyond simple pattern matching.

#### Acceptance Criteria

1. THE AI_Provider SHALL use a single LLM service for consistency
2. WHEN invoking the AI_Provider, THE ShellPilot SHALL send structured context data
3. WHEN receiving AI responses, THE ShellPilot SHALL expect structured JSON output
4. WHEN the AI_Provider is unavailable or times out, THE ShellPilot SHALL fall back to heuristic analysis
5. THE ShellPilot SHALL not store or transmit user data beyond the current session
6. THE AI_Provider SHALL complete requests within 10 seconds or timeout

### Requirement 9: Terminal Interface

**User Story:** As a developer, I want all interactions to happen in my terminal, so that I maintain my workflow without context switching.

#### Acceptance Criteria

1. THE ShellPilot SHALL display all output using terminal text formatting
2. THE ShellPilot SHALL use color coding to distinguish error messages, explanations, and suggestions
3. THE ShellPilot SHALL display fix options in a numbered list format
4. WHEN waiting for user input, THE ShellPilot SHALL provide clear prompts
5. THE ShellPilot SHALL not require or provide a web interface
6. THE ShellPilot SHALL respect terminal width for text wrapping

### Requirement 10: Learning Mode

**User Story:** As a developer learning command-line tools, I want optional explanations of commands, so that I can improve my understanding.

#### Acceptance Criteria

1. WHERE learning mode is enabled, THE ShellPilot SHALL provide detailed explanations of suggested fixes
2. WHERE learning mode is enabled, THE ShellPilot SHALL explain why each fix addresses the root cause
3. WHERE learning mode is disabled, THE ShellPilot SHALL provide concise fix descriptions
4. THE ShellPilot SHALL allow users to toggle learning mode via configuration

### Requirement 11: Performance and Overhead

**User Story:** As a developer, I want the tool to have minimal performance impact, so that my workflow remains efficient.

#### Acceptance Criteria

1. WHEN wrapping a successful command, THE Command_Wrapper SHALL add less than 50ms overhead
2. WHEN a failure occurs, THE ShellPilot SHALL begin displaying output within 1 second
3. THE ShellPilot SHALL not block command execution for context collection
4. THE ShellPilot SHALL not consume more than 100MB of memory during operation

### Requirement 12: Safety and Predictability

**User Story:** As a developer, I want the tool to be safe and predictable, so that I can trust it in production environments.

#### Acceptance Criteria

1. THE ShellPilot SHALL never execute commands without explicit user confirmation
2. WHEN suggesting fixes, THE ShellPilot SHALL clearly indicate destructive operations
3. THE ShellPilot SHALL not modify files or system state during analysis
4. THE ShellPilot SHALL not persist user commands or data between sessions
5. WHEN errors occur in ShellPilot itself, THE ShellPilot SHALL display the error and exit gracefully
6. THE ShellPilot SHALL provide deterministic behavior for identical inputs

### Requirement 13: Heuristic Fallback

**User Story:** As a developer, I want the tool to work without AI access, so that I can use it in restricted environments.

#### Acceptance Criteria

1. THE Heuristic_Engine SHALL recognize common error patterns without AI assistance
2. THE Heuristic_Engine SHALL match patterns for permission errors, missing dependencies, syntax errors, and network failures
3. WHEN AI is unavailable, THE ShellPilot SHALL provide analysis using only the Heuristic_Engine
4. THE ShellPilot SHALL clearly indicate when operating in heuristic-only mode
5. THE Heuristic_Engine SHALL be extensible for adding new patterns

### Requirement 14: Configuration Management

**User Story:** As a developer, I want to configure tool behavior, so that it matches my preferences and environment.

#### Acceptance Criteria

1. THE ShellPilot SHALL support configuration via a configuration file
2. THE ShellPilot SHALL allow enabling or disabling AI integration
3. THE ShellPilot SHALL allow configuring the AI provider endpoint
4. THE ShellPilot SHALL allow toggling learning mode
5. THE ShellPilot SHALL use sensible defaults when no configuration is provided
6. WHEN configuration is invalid, THE ShellPilot SHALL display an error and use defaults

