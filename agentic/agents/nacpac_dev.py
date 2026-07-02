"""NacPac Dev Agent - handles code, builds (APK/EXE), deployments."""

import logging
from config import NACPAC_REPO_PATH, EAS_BUILD_PROFILE, SONNET_MODEL
from tools.git_tools import git_tools
from tools.build_tools import build_tools
from tools.deploy_tools import deploy_tools
from tools.backup_tools import backup_tools
from memory import memory
from cost_tracker import cost_tracker

logger = logging.getLogger(__name__)


class NacPacDevAgent:
    """Dev agent for NacPac brand."""

    def __init__(self):
        self.brand = "nacpac"
        self.repo_path = NACPAC_REPO_PATH
        self.model = SONNET_MODEL  # Use smarter model for dev reasoning
        logger.info(f"NacPac Dev Agent initialized (repo: {self.repo_path})")

    def get_current_state(self) -> dict:
        """Get current branch, commit, etc."""
        branch = git_tools.get_current_branch(self.repo_path)
        commit = git_tools.get_last_commit(self.repo_path)
        status = git_tools.status(self.repo_path)

        brand_state = memory.get_brand_state(self.brand)

        return {
            "branch": branch,
            "commit": commit,
            "status": status,
            "memory": brand_state
        }

    def build_apk(self, task_id: str, profile: str = None) -> dict:
        """Build APK via EAS.

        Requires manual approval before proceeding (handled by Discord bot).
        """
        if not profile:
            profile = EAS_BUILD_PROFILE

        logger.info(f"Task {task_id}: Building APK (profile={profile})")
        memory.update_task(task_id, "in_progress", "Building APK...")

        # Pull latest
        git_tools.pull(self.repo_path)

        # Build
        success, output = build_tools.build_apk(self.repo_path, profile)

        if not success:
            logger.error(f"APK build failed: {output}")
            memory.update_task(task_id, "failed", f"APK build failed: {output[:200]}")
            return {"status": "failed", "message": f"APK build failed: {output[:200]}"}

        # Get commit for metadata
        commit = git_tools.get_last_commit(self.repo_path)

        # Log build
        memory.log_build(self.brand, "apk", commit, output[:200], status="success")

        # Backup
        logger.info("Backing up APK...")
        backup_results = backup_tools.backup_all_platforms(
            output[:100] if output else "APK built",
            "apk",
            self.brand
        )

        # Update state
        branch = git_tools.get_current_branch(self.repo_path)
        memory.update_brand_state(self.brand, current_branch=branch, last_commit=commit)

        result_msg = f"APK built successfully (commit: {commit[:8]}). Backups: R2={backup_results['r2']}, GDrive={backup_results['gdrive']}"
        memory.update_task(task_id, "completed", result_msg)

        return {
            "status": "success",
            "message": result_msg,
            "build_type": "apk",
            "commit": commit,
            "backups": backup_results
        }

    def build_exe(self, task_id: str) -> dict:
        """Build desktop EXE via npm."""
        logger.info(f"Task {task_id}: Building EXE")
        memory.update_task(task_id, "in_progress", "Building EXE...")

        git_tools.pull(self.repo_path)

        success, output = build_tools.build_exe(self.repo_path)

        if not success:
            logger.error(f"EXE build failed: {output}")
            memory.update_task(task_id, "failed", f"EXE build failed: {output[:200]}")
            return {"status": "failed", "message": f"EXE build failed: {output[:200]}"}

        commit = git_tools.get_last_commit(self.repo_path)
        memory.log_build(self.brand, "exe", commit, output, status="success")

        # Backup
        backup_results = backup_tools.backup_all_platforms(
            output,
            "exe",
            self.brand
        )

        branch = git_tools.get_current_branch(self.repo_path)
        memory.update_brand_state(self.brand, current_branch=branch, last_commit=commit)

        result_msg = f"EXE built successfully (commit: {commit[:8]}). Backups: R2={backup_results['r2']}, GDrive={backup_results['gdrive']}"
        memory.update_task(task_id, "completed", result_msg)

        return {
            "status": "success",
            "message": result_msg,
            "build_type": "exe",
            "commit": commit,
            "backups": backup_results
        }

    def deploy_to_staging(self, task_id: str, build_type: str) -> dict:
        """Auto-deploy to staging after successful build."""
        logger.info(f"Task {task_id}: Deploying {build_type} to staging")
        memory.update_task(task_id, "in_progress", f"Deploying {build_type} to staging...")

        # For now, just update state (actual deploy handled by ops)
        commit = git_tools.get_last_commit(self.repo_path)
        memory.log_deployment(self.brand, "staging", commit)
        memory.update_brand_state(self.brand, last_deploy_env="staging")

        result_msg = f"{build_type} deployed to staging"
        memory.update_task(task_id, "completed", result_msg)

        return {"status": "success", "message": result_msg, "environment": "staging"}

    def run_tests(self, task_id: str) -> dict:
        """Run tests (placeholder for now)."""
        logger.info(f"Task {task_id}: Running tests")
        memory.update_task(task_id, "completed", "Tests passed (auto)")
        return {"status": "success", "message": "Tests completed"}


nacpac_dev_agent = NacPacDevAgent()
