"""Git tools for repo operations."""

import subprocess
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class GitTools:
    """Git operations wrapper."""

    @staticmethod
    def run_git(cmd: list, cwd: str) -> tuple[bool, str, str]:
        """Run git command."""
        try:
            result = subprocess.run(
                cmd,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
        except Exception as e:
            return False, "", str(e)

    @staticmethod
    def get_current_branch(repo_path: str) -> str:
        """Get current branch name."""
        success, output, _ = GitTools.run_git(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            repo_path
        )
        return output if success else "unknown"

    @staticmethod
    def get_last_commit(repo_path: str) -> Optional[str]:
        """Get last commit hash."""
        success, output, _ = GitTools.run_git(
            ["git", "rev-parse", "HEAD"],
            repo_path
        )
        return output if success else None

    @staticmethod
    def checkout_branch(repo_path: str, branch: str) -> bool:
        """Checkout a branch."""
        success, _, _ = GitTools.run_git(
            ["git", "checkout", branch],
            repo_path
        )
        return success

    @staticmethod
    def pull(repo_path: str) -> bool:
        """Pull latest changes."""
        success, _, _ = GitTools.run_git(
            ["git", "pull", "origin"],
            repo_path
        )
        return success

    @staticmethod
    def status(repo_path: str) -> str:
        """Get repo status."""
        success, output, _ = GitTools.run_git(
            ["git", "status", "--short"],
            repo_path
        )
        return output if success else "error"

    @staticmethod
    def commit_and_push(repo_path: str, message: str, branch: str = "main") -> bool:
        """Commit and push changes."""
        GitTools.run_git(["git", "add", "."], repo_path)
        success, _, _ = GitTools.run_git(
            ["git", "commit", "-m", message],
            repo_path
        )
        if not success:
            return False

        success, _, _ = GitTools.run_git(
            ["git", "push", "origin", branch],
            repo_path
        )
        return success

    @staticmethod
    def get_diff(repo_path: str, branch1: str = "main", branch2: str = "HEAD") -> str:
        """Get diff between branches."""
        success, output, _ = GitTools.run_git(
            ["git", "diff", branch1, branch2],
            repo_path
        )
        return output if success else ""


git_tools = GitTools()
