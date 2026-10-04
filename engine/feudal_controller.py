"""Feudal Controller: High-Level Meta-Policy and Option DAG Orchestrator.

Implements the high-level policy π_high(g | s) for decomposing long-horizon
goals into a Directed Acyclic Graph (DAG) of subgoals, managing option lifecycles,
and enforcing bounded retry budgets before backtracking.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional, Set


class OptionState(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    BACKTRACKED = "BACKTRACKED"


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
            self.state = OptionState.FAILED
            return False

        self.state = OptionState.PENDING
        return False


class TaskDAG:
    """Directed Acyclic Graph of subgoals representing options."""

    def __init__(self) -> None:
        self.nodes: Dict[str, Subgoal] = {}

    def add_subgoal(self, subgoal: Subgoal) -> None:
        self.nodes[subgoal.id] = subgoal

    def get_ready_subgoals(self) -> List[Subgoal]:
        """Returns subgoals whose dependencies are all COMPLETED and are currently PENDING."""
        ready: List[Subgoal] = []
        for sg in self.nodes.values():
            if sg.state != OptionState.PENDING:
                continue
            deps_satisfied = all(
                self.nodes.get(dep) is not None
                and self.nodes[dep].state == OptionState.COMPLETED
                for dep in sg.dependencies
            )
            if deps_satisfied:
                ready.append(sg)
        return ready

    def is_complete(self) -> bool:
        return len(self.nodes) > 0 and all(
            sg.state == OptionState.COMPLETED for sg in self.nodes.values()
        )

    def has_failures(self) -> bool:
        return any(sg.state == OptionState.FAILED for sg in self.nodes.values())

    def topological_sort(self) -> List[str]:
        """Returns topologically sorted list of subgoal IDs."""
        in_degree: Dict[str, int] = {k: 0 for k in self.nodes}
        adj: Dict[str, List[str]] = {k: [] for k in self.nodes}

        for node_id, node in self.nodes.items():
            for dep in node.dependencies:
                if dep in adj:
                    adj[dep].append(node_id)
                    in_degree[node_id] += 1

        queue = [k for k, deg in in_degree.items() if deg == 0]
        order: List[str] = []

        while queue:
            curr = queue.pop(0)
            order.append(curr)
            for neighbor in adj[curr]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        if len(order) != len(self.nodes):
            raise ValueError("Cycle detected in TaskDAG specification!")

        return order


class FeudalController:
    """Meta-Controller managing long-horizon execution and backtracking."""

    def __init__(self, objective: str, dag: TaskDAG) -> None:
        self.objective = objective
        self.dag = dag
        self.execution_history: List[Dict] = []
        self.backtrack_count = 0

    def get_next_option(self) -> Optional[Subgoal]:
        """Retrieves next executable subgoal option."""
        ready = self.dag.get_ready_subgoals()
        if not ready:
            return None
        selected = ready[0]
        selected.state = OptionState.RUNNING
        return selected

    def submit_option_result(
        self, subgoal_id: str, success: bool, delta: Optional[Dict] = None
    ) -> bool:
        """Processes worker option completion."""
        subgoal = self.dag.nodes.get(subgoal_id)
        if not subgoal:
            raise KeyError(f"Subgoal {subgoal_id} not found in DAG")

        passed = subgoal.record_attempt(success, delta)
        self.execution_history.append(
            {
                "subgoal_id": subgoal_id,
                "attempt": subgoal.retry_count,
                "success": success,
                "delta": delta,
            }
        )

        if not passed and subgoal.state == OptionState.FAILED:
            self._trigger_backtrack(subgoal)

        return passed

    def _trigger_backtrack(self, failed_subgoal: Subgoal) -> None:
        """Backtracks failed option: resets dependent states and marks for replanning."""
        self.backtrack_count += 1
        failed_subgoal.state = OptionState.BACKTRACKED

        # Reset any dependent subgoals
        for sg in self.dag.nodes.values():
            if failed_subgoal.id in sg.dependencies:
                sg.state = OptionState.PENDING
                sg.retry_count = 0

    def is_goal_achieved(self) -> bool:
        """Returns True if all subgoals in the DAG have successfully completed."""
        return self.dag.is_complete()
