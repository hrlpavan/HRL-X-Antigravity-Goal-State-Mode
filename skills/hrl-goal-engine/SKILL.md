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

| Component | Formal HRL Concept | Antigravity Runtime Implementation |
| :--- | :--- | :--- |
| **Meta-Controller** | High-level policy $\pi^{\text{high}}(g \mid s)$ | Primary agent constructing task dependency DAGs and milestones. |
| **Option Policy** | Sub-policy $\pi_\omega(a \mid s)$ over option $\omega$ | Subagents (`invoke_subagent`) executing isolated file/command tasks. |
| **State Compression** | Abstract state representation $\phi(s)$ | Subagents absorb noisy exploration logs; only compressed diff ($\Delta s$) enters main context. |
| **Verification Oracle** | Termination condition $\beta(s) \in \{0, 1\}$ | Deterministic checks (exit code 0, 0 test failures, clean git status). |
| **Credit Assignment** | Intrinsic penalty & replanning | Bounded local retry budget (3 attempts) before rolling back and reforming plan. |

---

## 2. Execution Protocol

### Step 1: Feudal Decomposition (Meta-Controller)
1. Parse workspace dependencies and construct a task DAG.
2. Formulate explicit subgoals ($g_1, g_2, \dots, g_n$).
3. Define the **Deterministic Verification Oracles $\beta(s)$** before mutating any file.

### Step 2: Worker Sandboxing & Context Compression ($\Delta s$)
1. Offload noisy code scans, package builds, and trial runs to isolated subagents (`invoke_subagent`).
2. Do not pollute the primary conversation context with multi-page stdout/stderr logs.
3. Bring only the resulting state transitions ($\Delta s$: modified files, passing status) back into the parent session.

### Step 3: Bounded Credit Assignment & Backtracking
1. **Local Budget**: Maximum 3 local fix attempts per subgoal.
2. **Backtrack Trigger**: If a subgoal is not achieved within 3 attempts, halt local patching.
3. **Rollback**: Revert uncommitted changes on the invalid branch:
   ```bash
   git checkout -- <modified_files>
   ```
4. **Meta-Replanning**: Escalate to the Meta-Controller to pick an alternative implementation strategy.

### Step 4: Deterministic Oracle Verification ($\beta(s) = 1$)
The task is **never** complete based on subjective LLM assessment. Completion requires $\beta(s) = 1$ across all four oracles:

1. **Oracle 1 (Build)**: Compilation/typecheck exits with code 0 (`tsc --noEmit`, `cargo check`, `go build`, etc.).
2. **Oracle 2 (Tests)**: Test suite exits with code 0 and zero failures (`pytest`, `npm test`, etc.).
3. **Oracle 3 (Lint & Formatting)**: Linters report 0 errors (`npm run lint`, `ruff check`, etc.).
4. **Oracle 4 (Git State)**: Clean workspace without broken merges or conflicts:
   ```bash
   test -z "$(git status --porcelain)" || git diff --check
   ```

### Step 5: Dual-Signal Completion Notification
When all oracles evaluate to true ($\beta(s) = 1$):
1. **Artifact Convergence**: Produce a concise markdown artifact summarizing the state changes.
2. **OS Notification Signal**:
   - macOS:
     ```bash
     osascript -e 'display notification "Goal State Reached Successfully!" with title "Antigravity Engine"' && printf '\a'
     ```
   - Linux:
     ```bash
     notify-send "Antigravity Engine" "Goal State Reached Successfully!" && printf '\a'
     ```
