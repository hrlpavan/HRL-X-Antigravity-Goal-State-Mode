# Multi-Platform Dual-Signal Notification Protocol

When an autonomous agent runs overnight or during long work cycles, the operator needs an unambiguous, non-intrusive alert when the target goal state is reached.

The **HRL X Antigravity Goal State Engine** enforces a **Dual-Signal Protocol**:
1. **Visual Signal**: Native desktop notification popup.
2. **Auditory Signal**: Terminal bell (`\a`) or system audio tone.

---

## 1. Operating System Implementation Matrix

| Platform | Visual Signal Command | Audio Signal Command |
| :--- | :--- | :--- |
| **macOS** | `osascript -e 'display notification "Goal State Reached!" with title "Antigravity Engine"'` | `printf '\a'` or `afplay /System/Library/Sounds/Glass.aiff` |
| **Linux (X11 / Wayland)** | `notify-send "Antigravity Engine" "Goal State Reached!"` | `printf '\a'` or `paplay /usr/share/sounds/freedesktop/stereo/complete.oga` |
| **Windows (WSL2 / PowerShell)** | `powershell.exe -Command "[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime]..."` | `powershell.exe -Command "[console]::beep(800, 300)"` |

---

## 2. Shell Dispatcher Script

The repository bundles a portable cross-platform dispatcher at `scripts/notify_completion.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail

TASK_NAME="${1:-Autonomous Task}"

echo ">>> Emitting Dual-Signal Alert for: ${TASK_NAME}"

# 1. Audible Terminal Bell
printf '\a'

# 2. Platform-Specific Desktop IPC
if [[ "$OSTYPE" == "darwin"* ]]; then
  # macOS
  osascript -e "display notification \"${TASK_NAME} completed successfully with β(s) = 1!\" with title \"Antigravity Engine\" sound name \"Glass\"" 2>/dev/null || true
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
  # Linux
  if command -v notify-send >/dev/null 2>&1; then
    notify-send "Antigravity Engine" "${TASK_NAME} completed successfully!" --urgency=normal || true
  fi
fi

echo ">>> Notification dispatched."
```

---

## 3. Webhook Integration (Optional Remote Alerting)

If you are running Antigravity on a headless server or cloud VM, you can dispatch an external webhook alert (e.g. to Slack, Discord, or Telegram).

> [!WARNING]
> **Sandbox Boundary Note**: Antigravity runs terminal commands inside an isolated sandbox (`BypassSandbox: false`) by default. External outbound HTTP calls like `curl` to third-party endpoints will be blocked unless the sandbox is granted network permissions.

### Example Webhook Command
```bash
curl -s -X POST -H 'Content-Type: application/json' \
  -d '{"text":"🚀 Antigravity Autonomous Goal State Reached: All oracles passed β(s) = 1."}' \
  https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```
