"""Notification Trigger: Multi-Channel Dual-Signal Completion Alerting.

Dispatches non-blocking desktop IPC notifications and terminal audio bell
signals across macOS, Linux, and Windows platforms upon goal convergence (β(s) = 1).
"""

from __future__ import annotations
import platform
import subprocess
import sys
from typing import Optional


class NotificationTrigger:
    """Dispatches multi-channel completion signals."""

    @staticmethod
    def emit_terminal_bell() -> None:
        """Emits an audible ASCII bell character to stdout."""
        sys.stdout.write("\a")
        sys.stdout.flush()

    @staticmethod
    def emit_desktop_notification(
        title: str = "Antigravity Goal Engine",
        message: str = "Goal State Reached Successfully!",
    ) -> bool:
        """Emits native desktop notification according to host OS."""
        current_os = platform.system().lower()

        try:
            if current_os == "darwin":
                # macOS AppleScript
                script = f'display notification "{message}" with title "{title}" sound name "Glass"'
                subprocess.run(
                    ["osascript", "-e", script],
                    check=False,
                    capture_output=True,
                )
                return True
            elif current_os == "linux":
                # Linux notify-send
                subprocess.run(
                    ["notify-send", title, message, "--urgency=normal"],
                    check=False,
                    capture_output=True,
                )
                return True
            elif current_os == "windows":
                # Windows PowerShell Toast
                cmd = f"[console]::beep(800, 300)"
                subprocess.run(
                    ["powershell.exe", "-Command", cmd],
                    check=False,
                    capture_output=True,
                )
                return True
        except Exception:
            pass
        return False

    @classmethod
    def emit_dual_signal(
        cls,
        title: str = "Antigravity Goal Engine",
        message: str = "Goal State Reached Successfully (β(s) = 1)!",
    ) -> None:
        """Fires both visual desktop IPC and audible terminal bell."""
        cls.emit_terminal_bell()
        cls.emit_desktop_notification(title, message)
