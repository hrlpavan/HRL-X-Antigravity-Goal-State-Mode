/goal
================================================================================
AUTONOMOUS GOAL ENGINE v2.1 — FEUDAL HRL INSTRUCTION SET
================================================================================

[CONTEXT & OBJECTIVE]
Target Workspace: <PROJECT_DIRECTORY>
Primary Objective: <HIGH_LEVEL_GOAL_DESCRIPTION>

--------------------------------------------------------------------------------
[1. CONSTRAINTS & WORKER BOUNDARIES]
- Autonomy Level: FULL-AUTONOMY (Auto-Submit simple tasks; gate only HIGH volatility actions).
- Execution Scope: Restrict code changes strictly to `<TARGET_DIRECTORY>`. Do not mutate out-of-scope files.
- Code Base Standards: Maintain existing design patterns, typing constraints, and architectural guidelines.

--------------------------------------------------------------------------------
[2. META-CONTROLLER & OPTION DISPATCH (PLAN & EXECUTE)]
1. FEUDAL DECOMPOSITION:
   - Parse workspace dependencies and construct a task Directed Acyclic Graph (DAG).
   - Divide objective into isolated options (subgoals g ∈ G).

2. WORKER SANDBOX EXECUTION:
   - Offload heavy exploration and multi-step mutations to subagents (`invoke_subagent`).
   - Compress noisy observation traces; return only state differential (Δs) to the primary context.

3. INTRINSIC CREDIT ASSIGNMENT & BACKTRACKING:
   - Allocate a maximum retry budget of 3 local iterations per subgoal.
   - If a subgoal fails after 3 retries, force a Meta-Controller backtrack: revert the invalid branch state (`git checkout -- <files>`) and formulate an alternative execution path.

--------------------------------------------------------------------------------
[3. DETERMINISTIC VERIFICATION ORACLES β(s)]
The Goal State is considered 100% REACHED ONLY IF β(s) = 1 across ALL criteria:
[ ] Oracle 1 (Build Verification): `<BUILD_COMMAND>` exits with code 0.
[ ] Oracle 2 (Test Suite): `<TEST_COMMAND>` passes all test suites (0 failures).
[ ] Oracle 3 (Lint & Type Safety): `<LINT_COMMAND>` executes with zero errors.
[ ] Oracle 4 (Git State): `git diff --check` executes with zero whitespace/merge errors.

--------------------------------------------------------------------------------
[4. DUAL-SIGNAL NOTIFICATION & SUBMISSION]
When β(s) = 1 for all Oracles:
1. ARTIFACT SUBMISSION: Apply final file changes, update workspace status, and auto-submit completed task.
2. DISPATCH NOTIFICATIONS:
   - Terminal & System Sound: `printf '\a'`
   - Desktop Notification:
     macOS: `osascript -e 'display notification "Goal State Reached!" with title "Antigravity Engine"'`
     Linux: `notify-send "Antigravity Agent" "Goal State Reached Successfully!"`
   - Webhook Alert (Optional): `curl -s -X POST -H 'Content-Type: application/json' -d '{"text":"✅ Task completed successfully for <PROJECT_NAME>"}' <WEBHOOK_URL>`
================================================================================
