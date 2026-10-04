# Rule: Feudal HRL Autonomous Goal Engine Execution Protocol

When executing autonomous tasks, `/goal` workflows, or long-horizon coding tasks, the agent MUST adhere strictly to the following Feudal HRL execution protocol:

1. **Deconstruct Before Mutating**:
   - Parse project dependencies.
   - Construct an explicit Directed Acyclic Graph (DAG) of subgoals.
   - Establish the 4 deterministic verification oracles before generating code.

2. **Isolate Worker Execution**:
   - Offload exploratory file searches, build runs, and stack traces to subagents (`invoke_subagent`).
   - Keep root conversation context clean by receiving only the state differential (Δs).

3. **Enforce the 3-Retry Threshold**:
   - Limit local bug patching to a maximum of 3 attempts per subgoal.
   - On the 3rd consecutive failure, immediately roll back changes (`git checkout -- <files>`) and escalate to the Meta-Controller to replan an alternative strategy.

4. **Deterministic Exit Gate (β(s) = 1)**:
   - Never claim task completion based on self-evaluation or text output alone.
   - Verify that all defined oracles exit with code 0 (Build, Tests, Lint, Clean Git stage).

5. **Emit Dual-Signal Completion**:
   - Trigger desktop IPC alert (`osascript` or `notify-send`) and sound the terminal bell (`printf '\a'`).
   - Create a clean summary diff artifact in the session artifact store.
