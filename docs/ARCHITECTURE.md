# Execution Architecture: Feudal HRL for Google Antigravity

This document outlines the rigorous mathematical and systems architecture underpinning **HRL X Antigravity Goal State Mode**.

---

## 1. Problem Formulation: The Long-Horizon Horizon Dilemma

In autonomous coding agents, long-horizon software engineering is framed as sequential decision-making over an environment with enormous state spaces (ASTs, dependencies, compilers, file trees, test runners).

Standard single-agent architectures suffer from three fatal pathologies:

```
[Traditional Agent] ──► Action 1 ──► [Huge Raw Logs] ──► Action 2 ──► [Huge Build Errors] ──► [Context Window Collapse]
```

1. **Context Window Collapse (Attention Dilution)**: The ratio of informative signals to noisy intermediate output decays exponentially as execution traces accumulate.
2. **Hallucinatory Termination**: Because the agent acts as its own critic, it easily hallucinates completion when fatigued or confused.
3. **Unbounded Thrashing**: When an error occurs, the agent enters localized hill-climbing on broken assumptions without backtracking to the branch point.

---

## 2. Theoretical Framework

HRL X Antigravity formalizes autonomous development as a **Semi-Markov Decision Process (SMDP)** governed by a two-tiered **Feudal Hierarchy**.

```mermaid
flowchart TD
    subgraph HighLevel ["Tier 1: Meta-Controller (Manager Policy π_high)"]
        S["State s_t"] --> MP["π_high(g | s_t)"]
        MP --> G["Abstract Subgoal g ∈ G"]
        G --> Delay["Hold for τ steps"]
        Delay --> S_tau["State s_{t+τ}"]
        S_tau --> ExtReward["Extrinsic Reward R(s, g)"]
    end

    subgraph LowLevel ["Tier 2: Worker Policy (Low-Level Option π_low)"]
        G --> WP["π_low(a | s, g)"]
        WP --> Act["Primitive Action a ∈ A (Tools)"]
        Act --> Env["Environment Transition"]
        Env --> IntReward["Intrinsic Reward: -||φ(s) - g||"]
        IntReward --> WP
    end
```

### 2.1 Semi-Markov Decision Process (SMDP)
An SMDP is defined by the tuple $\langle \mathcal{S}, \mathcal{O}, \mathcal{P}, \mathcal{R}, \gamma \rangle$:
* $\mathcal{S}$: State space representing the file tree, ASTs, git status, and environment variables.
* $\mathcal{O}$: Set of temporally extended options $\omega = \langle \mathcal{I}_\omega, \pi_\omega, \beta_\omega \rangle$.
* $\mathcal{P}(s', \tau \mid s, \omega)$: Probability of transitioning to state $s'$ after duration $\tau$ under option $\omega$.
* $\mathcal{R}(s, \omega)$: Expected cumulative reward incurred over the option's execution.
* $\gamma \in (0, 1]$: Temporal discount factor.

### 2.2 The Options Framework
Each sub-task is encapsulated as an option $\omega$:
1. **Initiation Set $\mathcal{I}_\omega \subseteq \mathcal{S}$**: Preconditions required before the option can fire (e.g., dependencies installed, branch checked out).
2. **Internal Policy $\pi_\omega: \mathcal{S} \times \mathcal{A} \rightarrow [0, 1]$**: The local policy dispatched to execute atomic actions (file edits, sandboxed shell runs).
3. **Termination Condition $\beta_\omega: \mathcal{S} \rightarrow [0, 1]$**: The probability that option $\omega$ halts at state $s$.

---

## 3. Systems Realization in Google Antigravity

| Theoretical Element | Antigravity Native Equivalent | Behavioral Mechanics |
| :--- | :--- | :--- |
| **Meta-Controller** | Primary Session Planner | Constructs DAG of milestones, defines verification gates, routes tasks. |
| **Option Policy** | Subagents (`invoke_subagent`) | Forked agent conversations executing isolated tool sequences. |
| **Primitive Actions** | Native Tools | `replace_file_content`, `write_to_file`, sandboxed `run_command`. |
| **State Projection $\phi(s)$** | File System & Git State | AST parsing, uncommitted git diffs, directory trees. |
| **Intrinsic Reward** | Local Subgoal Validation | Unit tests and compiler checks specific to the active option. |
| **Extrinsic Reward** | Global Goal Oracle $\beta(s) = 1$ | Full test suite pass, lint pass, build pass, clean git tree. |

---

## 4. Context Isolation & State Differential ($\Delta s$)

The defining feature of this architecture is **Worker Sandboxing with State Compression**.

Instead of running long terminal exploratory tasks in the root context, the Meta-Controller delegates work to subagents. Subagents run in isolated scratchpads:

```
Root Context:  [Target Goal] ──► [Dispatch Subgoal 1] ───► [Receive Δs₁] ──► [Dispatch Subgoal 2]
                                      │
Subagent Context:              [ls -la]
                               [read 20 files]
                               [compile error]
                               [fix syntax]
                               [tests pass]
                                      │
                               Returns only: Δs = {files_modified: [...], status: "PASS", tests_passed: 12}
```

### Mathematical Formulation of $\Delta s$
$$\Delta s = \langle \mathcal{M}, \mathcal{D}, \mathcal{V} \rangle$$
* $\mathcal{M}$: Set of mutated file paths $\{p_1, p_2, \dots, p_k\}$.
* $\mathcal{D}$: Unified git diff representing the transformation $s \rightarrow s'$.
* $\mathcal{V}$: Vector of local oracle evaluations $[v_1, v_2, \dots, v_m] \in \{0, 1\}^m$.

---

## 5. Bounded Credit Assignment & Backtracking

When an agent fails, standard behavior is to enter a cycle of reactionary patching (*"fix symptom A, create bug B"*). 

HRL X Antigravity enforces **Bounded Credit Assignment**:

```mermaid
stateDiagram-v2
    [*] --> SubgoalExecution
    SubgoalExecution --> OracleCheck: Option Finishes
    OracleCheck --> SubgoalSuccess: Exit Code == 0
    OracleCheck --> RetryCounter: Exit Code != 0
    
    RetryCounter --> SubgoalExecution: Retry Budget < 3
    RetryCounter --> Backtrack: Retry Budget == 3
    
    Backtrack --> RollbackState: git checkout -- <files>
    RollbackState --> MetaReplanning: Reformulate DAG
    MetaReplanning --> SubgoalExecution: New Option Selected
    SubgoalSuccess --> [*]
```

### The Backtracking Protocol
1. **Local Retry Counter**: Each subgoal tracks $k \in \{0, 1, 2, 3\}$.
2. **Budget Threshold**: If $k = 3$ without oracle clearance:
   * **Reversion**: Immediate clean rollback of all changes made during option $\omega$:
     ```bash
     git checkout -- <modified_files>
     ```
   * **Meta-Replanning**: The failure is credited to the *option strategy* rather than low-level implementation. The Meta-Controller generates an alternative pathway in the task DAG.

---

## 6. Deterministic Verification Gate ($\beta(s) = 1$)

LLMs are prone to sycophantic or hallucinatory self-assessment. To eliminate this, completion is gated behind four deterministic environment oracles:

$$\beta(s) = \mathbb{I}(\text{Build} == 0) \times \mathbb{I}(\text{Tests} == 0) \times \mathbb{I}(\text{Lint} == 0) \times \mathbb{I}(\text{Stage} == 0)$$

If $\beta(s) = 0$, the session is **forbidden from terminating**. It must either self-repair or trigger the backtracking protocol.

---

## 7. Dual-Signal Notification Protocol

Upon satisfying $\beta(s) = 1$, the agent triggers a non-blocking dual-signal completion alert:
1. **Visual / Desktop IPC**: Dispatches an OS desktop alert (`osascript` on macOS, `notify-send` on Linux).
2. **Auditory Signal**: Emits an audible terminal ASCII bell (`printf '\a'`).
3. **Artifact Convergence**: Emits a structured summary markdown artifact in Antigravity's persistent artifact storage.
