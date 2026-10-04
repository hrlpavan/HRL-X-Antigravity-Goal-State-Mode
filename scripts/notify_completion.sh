#!/usr/bin/env bash
# ==============================================================================
# HRL X Antigravity: Multi-Platform Dual-Signal Completion Dispatcher
# ==============================================================================
set -euo pipefail

TASK_NAME="${1:-Antigravity Autonomous Goal Task}"

echo ">>> Emitting Dual-Signal Alert for: ${TASK_NAME}"

# 1. Audible Terminal Bell
printf '\a'

# 2. Platform-Specific Desktop IPC
if [[ "$OSTYPE" == "darwin"* ]]; then
  # macOS
  osascript -e "display notification \"${TASK_NAME} completed successfully with β(s) = 1!\" with title \"Antigravity Goal Engine\" sound name \"Glass\"" 2>/dev/null || true
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
  # Linux
  if command -v notify-send >/dev/null 2>&1; then
    notify-send "Antigravity Goal Engine" "${TASK_NAME} completed successfully (β(s) = 1)!" --urgency=normal || true
  fi
fi

echo ">>> Notification dispatched successfully."
