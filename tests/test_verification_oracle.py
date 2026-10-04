"""Unit tests for the Deterministic Verification Oracle."""

import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from engine.verification_oracle import VerificationOracleSuite, OracleResult


class TestVerificationOracle(unittest.TestCase):

    def setUp(self):
        self.suite = VerificationOracleSuite(timeout_seconds=5)

    def test_passing_oracle(self):
        res = self.suite.run_single("Echo Check", "echo 'hello world'")
        self.assertTrue(res.passed)
        self.assertEqual(res.exit_code, 0)
        self.assertEqual(res.stdout, "hello world")

    def test_failing_oracle(self):
        res = self.suite.run_single("Failing Check", "exit 42")
        self.assertFalse(res.passed)
        self.assertEqual(res.exit_code, 42)

    def test_composite_predicate(self):
        self.suite.register_oracle("Check 1", "true")
        self.suite.register_oracle("Check 2", "true")
        results = self.suite.evaluate_all()
        self.assertTrue(self.suite.is_goal_state_satisfied(results))

    def test_composite_predicate_with_failure(self):
        self.suite.register_oracle("Check 1", "true")
        self.suite.register_oracle("Check 2", "false")
        results = self.suite.evaluate_all()
        self.assertFalse(self.suite.is_goal_state_satisfied(results))


if __name__ == "__main__":
    unittest.main()
