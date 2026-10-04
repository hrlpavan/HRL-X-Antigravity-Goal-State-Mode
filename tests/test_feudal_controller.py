"""Unit tests for the Feudal Controller and Task DAG."""

import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from engine.feudal_controller import (
    FeudalController,
    Subgoal,
    TaskDAG,
    OptionState,
)


class TestFeudalController(unittest.TestCase):

    def setUp(self):
        self.dag = TaskDAG()
        self.sg1 = Subgoal(id="g1", title="Setup", description="Init dependencies")
        self.sg2 = Subgoal(
            id="g2",
            title="Core Logic",
            description="Implement feature",
            dependencies=["g1"],
        )
        self.sg3 = Subgoal(
            id="g3",
            title="Integration Tests",
            description="Run full suite",
            dependencies=["g2"],
        )

        self.dag.add_subgoal(self.sg1)
        self.dag.add_subgoal(self.sg2)
        self.dag.add_subgoal(self.sg3)

        self.controller = FeudalController(
            objective="Test Feature Build", dag=self.dag
        )

    def test_topological_sort(self):
        order = self.dag.topological_sort()
        self.assertEqual(order, ["g1", "g2", "g3"])

    def test_cycle_detection(self):
        cyclic_dag = TaskDAG()
        cyclic_dag.add_subgoal(Subgoal(id="a", title="A", description="", dependencies=["b"]))
        cyclic_dag.add_subgoal(Subgoal(id="b", title="B", description="", dependencies=["a"]))
        with self.assertRaises(ValueError):
            cyclic_dag.topological_sort()

    def test_option_dispatch_and_progression(self):
        # First option should be g1
        opt1 = self.controller.get_next_option()
        self.assertIsNotNone(opt1)
        self.assertEqual(opt1.id, "g1")
        self.assertEqual(opt1.state, OptionState.RUNNING)

        # Complete g1
        passed = self.controller.submit_option_result("g1", success=True)
        self.assertTrue(passed)
        self.assertEqual(self.sg1.state, OptionState.COMPLETED)

        # Next option should be g2
        opt2 = self.controller.get_next_option()
        self.assertIsNotNone(opt2)
        self.assertEqual(opt2.id, "g2")

    def test_bounded_retry_and_backtracking(self):
        # Complete g1
        self.controller.submit_option_result("g1", success=True)

        # Attempt 1 fail on g2
        passed = self.controller.submit_option_result("g2", success=False)
        self.assertFalse(passed)
        self.assertEqual(self.sg2.retry_count, 1)
        self.assertEqual(self.sg2.state, OptionState.PENDING)

        # Attempt 2 fail on g2
        passed = self.controller.submit_option_result("g2", success=False)
        self.assertFalse(passed)
        self.assertEqual(self.sg2.retry_count, 2)

        # Attempt 3 fail on g2 (budget exhausted!)
        passed = self.controller.submit_option_result("g2", success=False)
        self.assertFalse(passed)
        self.assertEqual(self.sg2.retry_count, 3)
        self.assertEqual(self.sg2.state, OptionState.BACKTRACKED)
        self.assertEqual(self.controller.backtrack_count, 1)


if __name__ == "__main__":
    unittest.main()
