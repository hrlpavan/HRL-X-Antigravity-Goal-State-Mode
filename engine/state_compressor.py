"""State Compressor: Context Isolation and State Differential (Δs) Extractor.

Extracts minimal state deltas from noisy subagent execution outputs, preventing
context window pollution in the parent Meta-Controller.
"""

from __future__ import annotations
import subprocess
from dataclasses import dataclass, field
from typing import List, Dict, Optional


@dataclass
class StateDifferential:
    files_modified: List[str]
    files_added: List[str]
    files_deleted: List[str]
    lines_added: int
    lines_deleted: int
    exit_code: int
    summary_message: str

    def to_dict(self) -> Dict:
        return {
            "files_modified": self.files_modified,
            "files_added": self.files_added,
            "files_deleted": self.files_deleted,
            "diff_stats": f"+{self.lines_added} / -{self.lines_deleted}",
            "exit_code": self.exit_code,
            "summary": self.summary_message,
        }


class StateCompressor:
    """Computes git differentials and generates compressed state representation."""

    @staticmethod
    def extract_git_differential(target_dir: str = ".") -> StateDifferential:
        """Inspects uncommitted workspace diffs and extracts structured metrics."""
        try:
            status_proc = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=target_dir,
                capture_output=True,
                text=True,
                check=False,
            )
            diff_proc = subprocess.run(
                ["git", "diff", "--shortstat"],
                cwd=target_dir,
                capture_output=True,
                text=True,
                check=False,
            )

            modified, added, deleted = [], [], []
            for line in status_proc.stdout.splitlines():
                if not line.strip():
                    continue
                code, path = line[:2].strip(), line[3:].strip()
                if "M" in code:
                    modified.append(path)
                elif "A" in code or "?" in code:
                    added.append(path)
                elif "D" in code:
                    deleted.append(path)

            lines_added, lines_deleted = 0, 0
            # Parse shortstat: " 2 files changed, 10 insertions(+), 2 deletions(-)"
            diff_text = diff_proc.stdout.strip()
            if "insertion" in diff_text:
                for part in diff_text.split(","):
                    if "insertion" in part:
                        lines_added = int(part.strip().split()[0])
                    elif "deletion" in part:
                        lines_deleted = int(part.strip().split()[0])

            summary = f"{len(modified) + len(added) + len(deleted)} files changed (+{lines_added}/-{lines_deleted})"

            return StateDifferential(
                files_modified=modified,
                files_added=added,
                files_deleted=deleted,
                lines_added=lines_added,
                lines_deleted=lines_deleted,
                exit_code=0,
                summary_message=summary,
            )
        except Exception as e:
            return StateDifferential(
                files_modified=[],
                files_added=[],
                files_deleted=[],
                lines_added=0,
                lines_deleted=0,
                exit_code=1,
                summary_message=f"Diff extraction error: {str(e)}",
            )
