"""Git operations for both brands."""

import subprocess
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class GitTools:
    """Git operations: clone, pull, branch, commit, push."""

    @staticmethod
    def run_git(repo_path: str, *args) -> tuple[bool, str]:
        """Run a git command. Returns (success, output)."""
        try:
            result = subprocess.run(
                ["git", "-C", repo_path] + list(args),
                capture_output=True,
                text=True,
                timeout=30
            )
            success = result.returncode == 0
            output = result.stdout or result.stderr
            return success, output
        except Exception as e:
            logger.error(f"Git command failed: {e}")
            return False, str(e)

    @staticmethod
    def get_current_branch(repo_path: str) -> Optional[str]:
        """Get current branch name."""
        success, output = GitTools.run_git(repo_path, "branch", "--show-current")
        return output.strip() if success else None

    @staticmethod
    def get_last_commit(repo_path: str) -> Optional[str]:
        """Get last commit hash."""
        success, output = GitTools.run_git(repo_path, "rev-parse", "HEAD")
        return output.strip() if success else None

    @staticmethod
    def checkout_branch(repo_path: str, branch: str, create: bool = False) -> bool:
        """Checkout a branch. If create=True, create it first."""
        if create:
            success, _ = GitTools.run_git(repo_path, "checkout", "-b", branch)
        else:
            success, _ = GitTools.run_git(repo_path, "checkout", branch)
        return success

    @staticmethod
    def pull(repo_path: str) -> bool:
        """Pull latest from origin."""
        success, output = GitTools.run_git(repo_path, "pull", "origin", "HEAD")
        if success:
            logger.info(f"Pulled latest: {output[:100]}")
        return success

    @staticmethod
    def status(repo_path: str) -> str:
        """Get git status."""
        _, output = GitTools.run_git(repo_path, "status", "--short")
        return output or "(clean)"

    @staticmethod
    def commit_and_push(repo_path: str, message: str, branch: str = None) -> bool:
        """Stage all, commit, and push."""
        if not branch:
            branch = GitTools.get_current_branch(repo_path)

        success, _ = GitTools.run_git(repo_path, "add", ".")
        if not success:
            logger.error("Failed to stage changes")
            return False

        success, _ = GitTools.run_git(repo_path, "commit", "-m", message)
        if not success:
            logger.error("Failed to commit")
            return False

        success, _ = GitTools.run_git(repo_path, "push", "-u", "origin", branch)
        if success:
            logger.info(f"Pushed to {branch}")
        return success

    @staticmethod
    def get_diff(repo_path: str, base_branch: str = "main") -> str:
        """Get diff between current and base branch."""
        _, output = GitTools.run_git(repo_path, "diff", base_branch + "..HEAD")
        return output or "(no changes)"


git_tools = GitTools()
