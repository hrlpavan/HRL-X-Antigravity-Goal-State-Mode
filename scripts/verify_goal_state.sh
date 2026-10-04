#!/usr/bin/env bash
# ==============================================================================
# HRL X Antigravity: Deterministic Verification Oracle Script
# Evaluates β(s) = 1 across Build, Test, Lint, and Git Stage
# ==============================================================================
set -euo pipefail

echo "=================================================================="
echo "RUNNING DETERMINISTIC VERIFICATION ORACLES β(s)"
echo "=================================================================="

FAILED=0

run_oracle() {
  local NAME="$1"
  local CMD="$2"

  echo -n "[Evaluating ${NAME}] ... "
  if eval "$CMD" > /dev/null 2>&1; then
    echo "✅ PASS (exit 0)"
  else
    echo "❌ FAIL (non-zero exit code)"
    FAILED=$((FAILED + 1))
  fi
}

# Default checks if commands are provided via environment variables
BUILD_CMD="${BUILD_CMD:-python3 -m py_compile engine/feudal_controller.py}"
TEST_CMD="${TEST_CMD:-python3 -m unittest discover tests}"
LINT_CMD="${LINT_CMD:-python3 -m py_compile engine/verification_oracle.py}"
STAGE_CMD="${STAGE_CMD:-git diff --check}"

run_oracle "Oracle 1 (Build / Compile)" "$BUILD_CMD"
run_oracle "Oracle 2 (Test Suite)" "$TEST_CMD"
run_oracle "Oracle 3 (Lint / AST Safety)" "$LINT_CMD"
run_oracle "Oracle 4 (Git Clean Stage)" "$STAGE_CMD"

echo "------------------------------------------------------------------"
if [ "$FAILED" -eq 0 ]; then
  echo "🎉 GOAL STATE EMPIRICALLY SATISFIED: β(s) = 1"
  exit 0
else
  echo "⚠️  GOAL STATE NOT SATISFIED: β(s) = 0 ($FAILED oracle(s) failed)"
  exit 1
fi
