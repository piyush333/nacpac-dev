"""NacPac Dev Agent - handles code, builds (APK/EXE), deployments."""

import logging
import os
import subprocess
from agentic.config import NACPAC_REPO_PATH, EAS_BUILD_PROFILE, SONNET_MODEL
from agentic.tools.git_tools import git_tools
from agentic.tools.build_tools import build_tools
from agentic.tools.deploy_tools import deploy_tools
from agentic.tools.backup_tools import backup_tools
from agentic.memory import memory
from agentic.cost_tracker import cost_tracker

logger = logging.getLogger(__name__)


class NacPacDevAgent:
    """Dev agent for NacPac brand."""

    def __init__(self):
        self.brand = "nacpac"
        self.repo_path = NACPAC_REPO_PATH
        self.model = SONNET_MODEL
        self._ensure_repo_cloned()
        logger.info(f"NacPac Dev Agent initialized (repo: {self.repo_path})")

    def _ensure_repo_cloned(self):
        """If repo_path is a GitHub URL, clone it to local /tmp path."""
        if self.repo_path.startswith("http://") or self.repo_path.startswith("https://"):
            logger.info(f"Repo path is URL: {self.repo_path}, cloning to local...")
            local_path = "/tmp/nacpac-workspace"
            if not os.path.exists(local_path):
                try:
                    subprocess.run(["git", "clone", self.repo_path, local_path], check=True, capture_output=True, timeout=300)
                    logger.info(f"✅ Cloned to {local_path}")
                except Exception as e:
                    logger.error(f"Failed to clone repo: {e}")
                    return
            self.repo_path = local_path
            logger.info(f"Updated repo_path to local: {self.repo_path}")

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

        git_tools.pull(self.repo_path)

        success, output = build_tools.build_apk(self.repo_path, profile)

        if not success:
            logger.error(f"APK build failed: {output}")
            memory.update_task(task_id, "failed", f"APK build failed: {output[:200]}")
            return {"status": "failed", "message": f"APK build failed: {output[:200]}"}

        commit = git_tools.get_last_commit(self.repo_path) or "unknown-commit"
        memory.log_build(self.brand, "apk", commit, output, status="success")

        backup_results = backup_tools.backup_all_platforms(
            output,
            "apk",
            self.brand
        )

        branch = git_tools.get_current_branch(self.repo_path)
        memory.update_brand_state(self.brand, current_branch=branch, last_commit=commit)

        result_msg = f"APK built (commit: {commit[:8]}). Backups: R2={backup_results['r2']}, GDrive={backup_results['gdrive']}"
        memory.update_task(task_id, "completed", result_msg)

        return {
            "status": "success",
            "message": result_msg,
            "build_type": "apk",
            "commit": commit,
            "link": output,
            "backups": backup_results
        }

    def build_exe(self, task_id: str) -> dict:
        """Build EXE for Windows (Desktop app)."""
        logger.info(f"Task {task_id}: Building EXE")
        memory.update_task(task_id, "in_progress", "Building EXE...")

        git_tools.pull(self.repo_path)

        success, output = build_tools.build_exe(self.repo_path)

        if not success:
            logger.error(f"EXE build failed: {output}")
            memory.update_task(task_id, "failed", f"EXE build failed: {output[:200]}")
            return {"status": "failed", "message": f"EXE build failed: {output[:200]}"}

        commit = git_tools.get_last_commit(self.repo_path) or "unknown-commit"
        memory.log_build(self.brand, "exe", commit, output, status="success")

        backup_results = backup_tools.backup_all_platforms(
            output,
            "exe",
            self.brand
        )

        branch = git_tools.get_current_branch(self.repo_path)
        memory.update_brand_state(self.brand, current_branch=branch, last_commit=commit)

        result_msg = f"EXE built (commit: {commit[:8]}). Backups: R2={backup_results['r2']}, GDrive={backup_results['gdrive']}"
        memory.update_task(task_id, "completed", result_msg)

        return {
            "status": "success",
            "message": result_msg,
            "build_type": "exe",
            "commit": commit,
            "link": output,
            "backups": backup_results
        }

    def deploy_to_staging(self, task_id: str, artifact: str = "apk") -> dict:
        """Deploy to staging environment."""
        logger.info(f"Task {task_id}: Deploying {artifact} to staging")
        memory.update_task(task_id, "in_progress", f"Deploying {artifact} to staging...")

        result = deploy_tools.deploy_to_env(self.repo_path, "staging", artifact)

        if not result.get("success"):
            memory.update_task(task_id, "failed", result.get("message", "Deploy failed"))
            return {"status": "failed", "message": result.get("message", "Deploy failed")}

        commit = git_tools.get_last_commit(self.repo_path)
        memory.log_deployment(self.brand, "staging", commit)
        memory.update_brand_state(self.brand, last_deploy_env="staging")
        memory.update_task(task_id, "completed", f"Deployed to staging")

        return {
            "status": "success",
            "message": f"Deployed {artifact} to staging",
            "environment": "staging"
        }


nacpac_dev_agent = NacPacDevAgent()
