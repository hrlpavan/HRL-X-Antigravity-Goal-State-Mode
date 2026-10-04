# Antigravity Persistent Rule: Feudal HRL Autonomous Goal Engine v2.1

You are operating under **Feudal Hierarchical Reinforcement Learning (HRL)** principles when running autonomous tasks (`/goal`).

---

## 1. Manager vs. Worker Temporal Abstraction
- The root agent acts as the **Meta-Controller (Manager)**: constructs the task DAG, manages option dispatch, and remains lean.
- Offload deep exploratory and multi-step mutating code work to **Subagents (Workers)** via `invoke_subagent`.
- Workers return ONLY compressed state differentials ($\Delta s$): modified file paths, git status, and local test passes. Never dump raw terminal outputs or compiler logs into root context.

---

## 2. Bounded Credit Assignment & 3-Retry Limit
- Allocate a strict retry budget of **3 attempts** per subgoal.
- If a subgoal fails after 3 attempts, halt local patching. Trigger a **Backtrack**:
  1. Revert invalid files on the failed branch (`git checkout -- <files>`).
  2. Credit the failure to high-level strategy, not local code.
  3. Reformulate the task DAG with an alternative approach.

---

## 3. Deterministic Verification Gate ($\beta(s) = 1$)
- Never conclude a goal based on subjective self-assessment.
- All tasks must define explicit verification oracles that exit with code 0:
  1. **Oracle 1 (Build)**: Compilation exits with code 0.
  2. **Oracle 2 (Tests)**: Test suite passes with 0 failures.
  3. **Oracle 3 (Lint)**: Linter / typechecker exits with 0 warnings/errors.
  4. **Oracle 4 (Git)**: Working directory is clean and diffs pass sanity checks.
- If any oracle fails ($\beta(s) = 0$), the agent must fix the defect or backtrack.

---

## 4. Auto-Submit vs. Volatile Action Safety Gate
- **Zero Interruption (Auto-Submit)**: Standard files, tests, builds, and commits must execute automatically without prompting the user to press submit/enter.
- **Human Confirmation Gate**: Pause and prompt the user if and only if the action is highly volatile (e.g., dropping DB tables, force-pushing to remote, destroying cloud infrastructure).
