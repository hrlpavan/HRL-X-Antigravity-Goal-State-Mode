# User Guide: Operating HRL X Antigravity Goal State Mode

Welcome to the definitive user manual for **HRL X Antigravity Goal State Mode**. This guide will teach you how to install, configure, and orchestrate long-horizon autonomous software projects with mathematical predictability and zero context thrashing.

---

## 1. Prerequisites

Before using Goal State Mode, ensure you have:
1. **Google Antigravity CLI (`agy`)** or **Antigravity IDE / Desktop App 2.0**.
2. **Python 3.10+** (for offline verification runners and simulation tools).
3. A Git-controlled workspace repository.

---

## 2. Installation & Setup

You can install the HRL Goal Engine globally (applies to all projects) or per-workspace (committed to your team's repo).

### Option A: Global Installation (Recommended)
Install the skill into your user configuration directory:
```bash
# 1. Create skill directory
mkdir -p ~/.gemini/config/skills/hrl-goal-engine

# 2. Copy the skill file
cp skills/hrl-goal-engine/SKILL.md ~/.gemini/config/skills/hrl-goal-engine/

# 3. Optional: Install persistent rule
mkdir -p ~/.gemini/config/rules
cp rules/hrl_goal_engine.md ~/.gemini/config/rules/
```

### Option B: Workspace Installation
For repository-specific team sharing:
```bash
# In your project root:
mkdir -p .agents/skills/hrl-goal-engine
cp /path/to/skills/hrl-goal-engine/SKILL.md .agents/skills/hrl-goal-engine/
git add .agents/
git commit -m "chore: install hrl-goal-engine antigravity skill"
```

---

## 3. How to Launch a Goal Session (`/goal`)

Whenever you have a complex, multi-stage task (e.g., refactoring an authentication service, migrating databases, building a new API feature), use the `/goal` command with the structured prompt template.

### The Standard Prompt Anatomy

```markdown
/goal
================================================================================
AUTONOMOUS GOAL ENGINE v2.1 — FEUDAL HRL INSTRUCTION SET
================================================================================

[CONTEXT & OBJECTIVE]
Target Workspace: <PROJECT_DIRECTORY>
Primary Objective: <HIGH_LEVEL_GOAL_DESCRIPTION>

--------------------------------------------------------------------------------
[1. CONSTRAINTS & WORKER BOUNDARIES]
- Autonomy Level: FULL-AUTONOMY (Do not prompt for interactive confirmation).
- Execution Scope: Restrict mutations strictly to `<TARGET_DIRECTORIES>`.
- Coding Standards: Zero unneeded dependencies, strict types, conform to existing code styles.

--------------------------------------------------------------------------------
[2. META-CONTROLLER & OPTION DISPATCH]
1. Construct dependency DAG across subgoals (g ∈ G).
2. Offload noisy work to subagents to compress context (Δs).
3. Max retry budget: 3 attempts per subgoal before rollback and meta-replanning.

--------------------------------------------------------------------------------
[3. DETERMINISTIC VERIFICATION ORACLES β(s)]
Target Goal State is reached ONLY IF all oracles exit with code 0:
[ ] Oracle 1 (Build): <BUILD_COMMAND>
[ ] Oracle 2 (Tests): <TEST_COMMAND>
[ ] Oracle 3 (Lint): <LINT_COMMAND>
[ ] Oracle 4 (Clean Stage): git diff --check

--------------------------------------------------------------------------------
[4. DUAL-SIGNAL COMPLETION TRIGGER]
Upon β(s) = 1:
1. Summarize final diff in an artifact.
2. Emit desktop notification and audible bell signal.
================================================================================
```

---

## 4. Real-World Execution Walkthrough

### Scenario: Implementing Rate Limiting in an Express API Gateway

#### 1. Formulate the Goal Request
```markdown
/goal
Target Workspace: /projects/api-gateway
Primary Objective: Add sliding-window rate limiting middleware backed by Redis.

[1. CONSTRAINTS]
- Only edit files in src/middleware/ and tests/.
- Dependencies: Use existing ioredis package. Do not add unapproved npm packages.

[2. META-CONTROLLER DAG]
- g₁: Redis client abstraction & sliding window script.
- g₂: Express middleware wrapping sliding window logic.
- g₃: Integration test suite covering standard, edge-case, and burst requests.

[3. DETERMINISTIC ORACLES β(s)]
- Oracle 1: npx tsc --noEmit (exit code 0)
- Oracle 2: npm test tests/rateLimiter.test.ts (exit code 0, 0 failures)
- Oracle 3: npm run lint (exit code 0)
- Oracle 4: git diff --check (exit code 0)
```

#### 2. What Antigravity Does Under the Hood
1. **DAG Initialization**: Antigravity's Meta-Controller builds the dependency tree.
2. **Worker Option 1 Dispatched**: Subagent creates `src/middleware/rateLimiter.ts`. It runs local linting and tests internally. The parent context receives only the modified file summary ($\Delta s$).
3. **Worker Option 2 Dispatched**: Subagent wires the middleware into the server router.
4. **Worker Option 3 Dispatched**: Subagent writes comprehensive test cases in `tests/rateLimiter.test.ts`.
5. **Oracle Verification Gate**: Antigravity executes all four oracles sequentially.
6. **Convergence**: All oracles exit code 0 ($\beta(s) = 1$). Antigravity emits the desktop notification, sounds the terminal bell, writes the completion artifact, and halts.

---

## 5. Offline Simulation & Testing Tools

This repository bundles a reference Python engine to simulate and verify your setup before running autonomous jobs:

### 1. Verification Oracle Runner
Run your oracles locally:
```bash
python3 engine/verification_oracle.py \
  --build "python3 -m py_compile engine/feudal_controller.py" \
  --test "python3 -m unittest discover tests" \
  --lint "ruff check ."
```

### 2. Notification Dispatcher Test
Verify that your OS notification and audio bell are working:
```bash
bash scripts/notify_completion.sh "Test Task"
```

---

## 6. Best Practices for Maximum Reliability

1. **Be Specific with Oracles**: An oracle with vague output is useless. Always use commands that exit with code 0 on success and non-zero on failure.
2. **Enforce Clean Git Stages**: Including `git diff --check` prevents trailing whitespace, conflict markers, or unfinished code blocks from slipping in.
3. **Keep Options Small**: Break complex tasks into subgoals that each take 1–3 file changes. Smaller options have higher first-try success rates.
4. **Never Disable the 3-Retry Threshold**: If a fix fails 3 times, the low-level hypothesis is wrong. Backtracking saves the agent from entering an infinite loop.
