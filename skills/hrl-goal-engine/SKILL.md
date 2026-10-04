---
name: hrl-goal-engine
description: Autonomous Goal Engine v2.1 based on Feudal Hierarchical Reinforcement Learning (HRL). Enforces temporal abstraction, worker context compression via subagents, bounded credit assignment with backtracking, deterministic verification oracles (β(s) = 1), and dual-signal completion triggers. Activate when executing long-horizon autonomous tasks, /goal workflows, or goal-state execution.
---

# Antigravity Autonomous Goal Engine v2.1 (Feudal HRL Framework)

This skill formalizes autonomous task execution in Google Antigravity using **Feudal Hierarchical Reinforcement Learning (HRL)** principles. It eliminates context pollution, prevents premature task exits, and guards against infinite retry loops.

---

## 1. Core HRL Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│              ANTIGRAVITY GOAL STATE ENGINE v2.1 (HRL LOOP)             │
│                                                                         │
│   [User Goal Request] ──► [Meta-Controller: π_high(g|s)]               │
│                                      │                                  │
│                                      ▼                                  │
│   [Completion Signal] ◄── [Verification Oracle β(s) = 1?]              │
│            ▲                         │                                  │
│            │ (PASS)                  │ (FAIL: β(s) = 0)                 │
│            │                         ▼                                  │
│            │            [Worker Policy: π_low(a|s,g)]                   │
│            │                         │                                  │
│            │                         ▼                                  │
│            └──────────── [State Transition Δs]                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Execution Protocol

### Step 1: Meta-Controller Formulation ($\pi_{\text{high}}$)
1. Read the user's objective and inspect target directory structure.
2. Build an explicit **Task Dependency Directed Acyclic Graph (DAG)**.
3. Define 2 to 5 isolated subgoals ($g_1, g_2, \dots, g_n \in \mathcal{G}$).
4. Assign a strict retry budget (default: 3) to each subgoal.

### Step 2: Worker Option Dispatch ($\pi_{\text{low}}$)
1. Dispatch subgoals to dedicated subagents using `invoke_subagent`.
2. Restrict each worker's scope strictly to its assigned option.
3. The worker performs primitive tool actions (`replace_file_content`, `write_to_file`, `run_command`).
4. The worker tests its own code before returning.

### Step 3: Context Compression ($\Delta s$)
1. Workers MUST NOT return long raw execution logs or stack traces to the parent agent.
2. Workers MUST return only the **State Differential ($\Delta s$)**:
   - Files created or modified.
   - Status (SUCCESS or FAILED).
   - Brief 1-2 line summary of diff.

### Step 4: Bounded Credit Assignment & Backtracking
1. If a worker succeeds, advance the DAG to the next ready subgoal.
2. If a worker fails, decrement retry budget ($k \leftarrow k - 1$).
3. **Trigger Backtracking when $k = 0$**:
   - Do NOT continue local patching.
   - Revert invalid modifications: `git checkout -- <modified_files>`.
   - Log the architectural failure and formulate an alternative path in the DAG.

### Step 5: Deterministic Verification Oracles ($\beta(s) = 1$)
Before declaring completion, run ALL verification oracles:
- `Oracle 1 (Build)`: Verify compilation exits with code 0.
- `Oracle 2 (Tests)`: Verify unit/integration tests pass with 0 failures.
- `Oracle 3 (Lint)`: Verify linter and type-checker exit with 0 errors.
- `Oracle 4 (Git State)`: Verify git diff is clean and formatted.

**Crucial Invariant**: If any oracle fails ($\beta(s) = 0$), the agent CANNOT stop. It must fix or backtrack.

### Step 6: Auto-Submit vs. Volatile Action Safety Gating
- **Auto-Submit (0 Prompts)**: Standard coding tasks (file edits, builds, tests, local commits) execute without asking the user to press Enter or submit.
- **Interactive Human Gate (1 Prompt)**: If an action is HIGHLY VOLATILE (e.g., dropping DB tables, force-pushing to remote branches, cloud infrastructure destruction), the engine must pause and prompt for user confirmation.

### Step 7: Dual-Signal Completion Notification
When $\beta(s) = 1$ across all oracles:
1. Generate the final completion markdown artifact.
2. Sound system audio bell: `printf '\a'`.
3. Dispatch OS desktop notification:
   - macOS: `osascript -e 'display notification "Goal Reached!" with title "Antigravity Engine"'`
   - Linux: `notify-send "Antigravity Engine" "Goal Reached!"`
