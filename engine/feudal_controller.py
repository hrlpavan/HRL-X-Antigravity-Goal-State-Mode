"""Feudal Controller: High-Level Meta-Policy and Option DAG Orchestrator.

Implements the high-level policy π_high(g | s) for decomposing long-horizon
goals into a Directed Acyclic Graph (DAG) of subgoals, managing option lifecycles,
enforcing bounded retry budgets before backtracking, and gating volatile actions.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
import re
from typing import List, Dict, Optional, Set


class OptionState(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    BACKTRACKED = "BACKTRACKED"


class ActionVolatility(str, Enum):
    """Volatility and risk classification for agent actions."""
    LOW = "LOW"          # Standard file edits, compiles, tests -> Auto-Submit (0 prompts)
    MEDIUM = "MEDIUM"    # Backtracking, branch checkouts -> Auto-Submit (0 prompts)
    HIGH = "HIGH"        # Destructive deletions, drop table, force push -> Human Gate (1 prompt)


# Volatile action signatures requiring interactive confirmation
VOLATILE_PATTERNS = [
    re.compile(r"\bdrop\s+(table|database|schema)\b", re.IGNORECASE),
    re.compile(r"\btruncate\s+(table)?\b", re.IGNORECASE),
    re.compile(r"\bdelete\s+from\s+\w+\s*(;|where\s+1\s*=\s*1|$)", re.IGNORECASE),
    re.compile(r"\bgit\s+push\s+.*--force\b", re.IGNORECASE),
    re.compile(r"\brm\s+-(rf|fr)\s+/(tmp|home|var|usr)?\s*$", re.IGNORECASE),
    re.compile(r"\b(gcloud|aws|az)\s+.*delete\b", re.IGNORECASE),
]


@dataclass
class Subgoal:
    id: str
    title: str
    description: str
    dependencies: List[str] = field(default_factory=list)
    retry_budget: int = 3
    retry_count: int = 0
    state: OptionState = OptionState.PENDING
    assigned_worker: Optional[str] = None
    state_delta: Optional[Dict] = None

    def record_attempt(self, success: bool, delta: Optional[Dict] = None) -> bool:
        """Records an execution attempt.

        Returns True if successful, False if retry needed or backtrack triggered.
        """
        self.state_delta = delta
        if success:
            self.state = OptionState.COMPLETED
            return True

        self.retry_count += 1
        if self.retry_count >= self.retry_budget:
            self.state = OptionState.BACKTRACKED
            return False

        self.state = OptionState.FAILED
        return False

    def can_retry(self) -> bool:
        return self.retry_count < self.retry_budget and self.state != OptionState.COMPLETED

    def reset_for_backtrack(self) -> None:
        self.retry_count = 0
        self.state = OptionState.PENDING
        self.state_delta = None


@dataclass
class TaskDAG:
    subgoals: Dict[str, Subgoal] = field(default_factory=dict)

    def add_subgoal(self, subgoal: Subgoal) -> None:
        self.subgoals[subgoal.id] = subgoal

    def get_ready_subgoals(self) -> List[Subgoal]:
        ready = []
        for sg in self.subgoals.values():
            if sg.state == OptionState.PENDING:
                deps_satisfied = all(
                    self.subgoals[d].state == OptionState.COMPLETED
                    for d in sg.dependencies
                    if d in self.subgoals
                )
                if deps_satisfied:
                    ready.append(sg)
        return ready

    def all_completed(self) -> bool:
        return all(sg.state == OptionState.COMPLETED for sg in self.subgoals.values())

    def has_backtracked(self) -> bool:
        return any(sg.state == OptionState.BACKTRACKED for sg in self.subgoals.values())


class FeudalController:
    """Manager Tier: High-level policy orchestrating Task DAG and worker dispatch."""

    def __init__(self, objective: str, workspace: str):
        self.objective = objective
        self.workspace = workspace
        self.dag = TaskDAG()
        self.history: List[Dict] = []
        self.auto_submit_count: int = 0
        self.volatile_prompt_count: int = 0

    def assess_action_volatility(self, action_command: str) -> ActionVolatility:
        """Classifies the volatility of a candidate action.

        Returns HIGH if destructive patterns match (requiring human confirmation),
        otherwise LOW or MEDIUM (eligible for Auto-Submit).
        """
        for pattern in VOLATILE_PATTERNS:
            if pattern.search(action_command):
                return ActionVolatility.HIGH
        return ActionVolatility.LOW

    def should_auto_submit(self, action_command: str) -> bool:
        """Determines whether an action can proceed automatically without prompting."""
        volatility = self.assess_action_volatility(action_command)
        if volatility == ActionVolatility.HIGH:
            self.volatile_prompt_count += 1
            return False
        self.auto_submit_count += 1
        return True

    def build_plan_from_spec(self, milestones: List[Dict]) -> None:
        """Initializes the task DAG from structured milestone specifications."""
        for m in milestones:
            sg = Subgoal(
                id=m["id"],
                title=m["title"],
                description=m["description"],
                dependencies=m.get("dependencies", []),
                retry_budget=m.get("retry_budget", 3),
            )
            self.dag.add_subgoal(sg)

    def dispatch_next_option(self) -> Optional[Subgoal]:
        """Selects the next runnable option from the DAG according to π_high."""
        ready = self.dag.get_ready_subgoals()
        if not ready:
            return None
        selected = ready[0]
        selected.state = OptionState.RUNNING
        return selected

    def handle_worker_result(self, subgoal_id: str, success: bool, delta: Optional[Dict] = None) -> Dict:
        """Processes worker execution differential (Δs) and updates state."""
        sg = self.dag.subgoals.get(subgoal_id)
        if not sg:
            return {"status": "ERROR", "message": f"Subgoal {subgoal_id} not found"}

        ok = sg.record_attempt(success=success, delta=delta)
        self.history.append({
            "subgoal_id": subgoal_id,
            "success": success,
            "retry_count": sg.retry_count,
            "state": sg.state.value,
            "delta": delta,
        })

        if ok:
            return {
                "status": "CONTINUE",
                "message": f"Subgoal {subgoal_id} completed successfully.",
                "all_completed": self.dag.all_completed(),
            }

        if sg.state == OptionState.BACKTRACKED:
            return self.trigger_backtracking(subgoal_id)

        return {
            "status": "RETRY",
            "message": f"Subgoal {subgoal_id} failed. Remaining retries: {sg.retry_budget - sg.retry_count}",
            "retry_count": sg.retry_count,
        }

    def trigger_backtracking(self, failed_subgoal_id: str) -> Dict:
        """Executes the credit assignment and backtracking protocol.

        Reverts changes associated with the failed branch and resets option state.
        """
        failed_sg = self.dag.subgoals[failed_subgoal_id]
        rollback_files = []
        if failed_sg.state_delta and "modified_files" in failed_sg.state_delta:
            rollback_files = failed_sg.state_delta["modified_files"]

        # Reset the failed subgoal and dependents
        failed_sg.reset_for_backtrack()
        for sg in self.dag.subgoals.values():
            if failed_subgoal_id in sg.dependencies and sg.state != OptionState.PENDING:
                sg.reset_for_backtrack()

        return {
            "status": "BACKTRACK",
            "message": f"Retry budget exhausted on {failed_subgoal_id}. Backtracking triggered.",
            "rollback_targets": rollback_files,
            "instruction": "Revert uncommitted modifications via git checkout and reformulate branch DAG.",
        }
