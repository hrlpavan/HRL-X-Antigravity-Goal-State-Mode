import unittest
from engine.feudal_controller import (
    FeudalController,
    Subgoal,
    TaskDAG,
    OptionState,
    ActionVolatility,
)


class TestFeudalController(unittest.TestCase):
    def setUp(self):
        self.controller = FeudalController(
            objective="Build Redis Rate Limiter",
            workspace="/tmp/test_workspace",
        )
        self.controller.build_plan_from_spec([
            {
                "id": "sg_1",
                "title": "Redis Client Helper",
                "description": "Initialize Redis connection pool",
                "dependencies": [],
            },
            {
                "id": "sg_2",
                "title": "Rate Limiter Middleware",
                "description": "Implement sliding window middleware",
                "dependencies": ["sg_1"],
            },
            {
                "id": "sg_3",
                "title": "Integration Tests",
                "description": "Write comprehensive test suite",
                "dependencies": ["sg_2"],
            },
        ])

    def test_initial_ready_subgoals(self):
        ready = self.controller.dag.get_ready_subgoals()
        self.assertEqual(len(ready), 1)
        self.assertEqual(ready[0].id, "sg_1")

    def test_successful_subgoal_advancement(self):
        sg = self.controller.dispatch_next_option()
        self.assertEqual(sg.id, "sg_1")
        self.assertEqual(sg.state, OptionState.RUNNING)

        res = self.controller.handle_worker_result("sg_1", success=True, delta={"files": ["redis.ts"]})
        self.assertEqual(res["status"], "CONTINUE")
        self.assertFalse(res["all_completed"])

        ready = self.controller.dag.get_ready_subgoals()
        self.assertEqual(len(ready), 1)
        self.assertEqual(ready[0].id, "sg_2")

    def test_retry_budget_decrements(self):
        self.controller.dispatch_next_option()
        res1 = self.controller.handle_worker_result("sg_1", success=False)
        self.assertEqual(res1["status"], "RETRY")
        self.assertEqual(res1["retry_count"], 1)

        res2 = self.controller.handle_worker_result("sg_1", success=False)
        self.assertEqual(res2["status"], "RETRY")
        self.assertEqual(res2["retry_count"], 2)

    def test_backtracking_trigger_on_exhaustion(self):
        self.controller.dispatch_next_option()
        self.controller.handle_worker_result("sg_1", success=False)
        self.controller.handle_worker_result("sg_1", success=False)
        res = self.controller.handle_worker_result(
            "sg_1",
            success=False,
            delta={"modified_files": ["broken_redis.ts"]}
        )

        self.assertEqual(res["status"], "BACKTRACK")
        self.assertIn("broken_redis.ts", res["rollback_targets"])

        # Check that sg_1 was reset
        sg_1 = self.controller.dag.subgoals["sg_1"]
        self.assertEqual(sg_1.retry_count, 0)
        self.assertEqual(sg_1.state, OptionState.PENDING)

    def test_all_completed_convergence(self):
        self.controller.dispatch_next_option()
        self.controller.handle_worker_result("sg_1", success=True)
        self.controller.dispatch_next_option()
        self.controller.handle_worker_result("sg_2", success=True)
        self.controller.dispatch_next_option()
        res = self.controller.handle_worker_result("sg_3", success=True)

        self.assertEqual(res["status"], "CONTINUE")
        self.assertTrue(res["all_completed"])
        self.assertTrue(self.controller.dag.all_completed())

    def test_volatility_assessment_standard_actions(self):
        # File edits, tests, builds should be classified as LOW volatility
        self.assertEqual(
            self.controller.assess_action_volatility("npm test"),
            ActionVolatility.LOW,
        )
        self.assertEqual(
            self.controller.assess_action_volatility("python3 -m unittest discover tests"),
            ActionVolatility.LOW,
        )
        self.assertEqual(
            self.controller.assess_action_volatility("npx tsc --noEmit"),
            ActionVolatility.LOW,
        )

    def test_volatility_assessment_destructive_actions(self):
        # Destructive SQL / force pushes should be classified as HIGH volatility
        self.assertEqual(
            self.controller.assess_action_volatility("DROP TABLE users;"),
            ActionVolatility.HIGH,
        )
        self.assertEqual(
            self.controller.assess_action_volatility("git push origin main --force"),
            ActionVolatility.HIGH,
        )
        self.assertEqual(
            self.controller.assess_action_volatility("TRUNCATE order_items;"),
            ActionVolatility.HIGH,
        )
        self.assertEqual(
            self.controller.assess_action_volatility("gcloud projects delete prod-db"),
            ActionVolatility.HIGH,
        )

    def test_auto_submit_vs_prompt_decision(self):
        # Low volatility commands should auto-submit
        self.assertTrue(self.controller.should_auto_submit("npm test"))
        self.assertTrue(self.controller.should_auto_submit("git commit -m 'chore: update'"))
        self.assertEqual(self.controller.auto_submit_count, 2)
        self.assertEqual(self.controller.volatile_prompt_count, 0)

        # High volatility command should NOT auto-submit (prompts user)
        self.assertFalse(self.controller.should_auto_submit("DROP TABLE sensitive_data;"))
        self.assertEqual(self.controller.volatile_prompt_count, 1)


if __name__ == "__main__":
    unittest.main()
