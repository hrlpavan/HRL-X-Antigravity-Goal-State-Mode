/goal
================================================================================
AUTONOMOUS GOAL ENGINE v2.1 — FEUDAL HRL INSTRUCTION SET
================================================================================

[CONTEXT & OBJECTIVE]
Target Workspace: <PROJECT_NAME_OR_DIRECTORY>
Primary Objective: <HIGH_LEVEL_GOAL_DESCRIPTION>

--------------------------------------------------------------------------------
[1. CONSTRAINTS & WORKER BOUNDARIES]
- Autonomy Level: FULL-AUTONOMY (Do not prompt for interactive user confirmation).
- Execution Scope: Restrict code changes strictly to `<TARGET_DIRECTORY>`. Do not mutate out-of-scope files or uncommitted git states.
- Code Base Standards: Maintain existing design patterns, typing constraints, and architectural guidelines.

--------------------------------------------------------------------------------
[2. META-CONTROLLER & OPTION DISPATCH (PLAN & EXECUTE)]
1. FEUDAL DECOMPOSITION:
   - Parse workspace dependencies and construct a task Directed Acyclic Graph (DAG).
   - Divide objective into isolated options (subgoals g ∈ G).

2. WORKER SANDBOX EXECUTION (STATE COMPRESSION):
   - Offload exploratory file scans and noisy build cycles to subagent threads (`invoke_subagent`) to preserve root context capacity.
   - Return only state differential (Δs) to the primary context.

3. INTRINSIC CREDIT ASSIGNMENT & BACKTRACKING:
   - Allocate a maximum retry budget of 3 local iterations per subgoal.
   - If a subgoal fails after 3 retries, force a Meta-Controller backtrack: revert the invalid branch state (`git checkout -- <files>`) and formulate an alternative execution path.

--------------------------------------------------------------------------------
[3. DETERMINISTIC VERIFICATION ORACLES β(s)]
The Goal State is considered 100% REACHED ONLY IF β(s) = 1 across ALL criteria:
[ ] Oracle 1 (Build Verification): `<BUILD_COMMAND>` exits with code 0.
[ ] Oracle 2 (Test Suite): `<TEST_COMMAND>` passes all test suites (0 failures, exit code 0).
[ ] Oracle 3 (Lint & Type Safety): `<LINT_COMMAND>` executes with zero errors (exit code 0).
[ ] Oracle 4 (Git State): `git diff --check` executes with zero errors.

--------------------------------------------------------------------------------
[4. DUAL-SIGNAL NOTIFICATION TRIGGER]
When β(s) = 1 for all Oracles:
1. ARTIFACT CONVERGENCE: Generate final summary diff in an artifact file.
2. DISPATCH NOTIFICATIONS:
   - macOS: `osascript -e 'display notification "Goal State Reached!" with title "Antigravity Engine"' && printf '\a'`
   - Linux: `notify-send "Antigravity Engine" "Goal State Reached!" && printf '\a'`
================================================================================
