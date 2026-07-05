"""Jico Life Dev Agent - handles code, AR model builds, Netlify deploys."""

import logging
from agentic.config import JICO_REPO_PATH, SONNET_MODEL
from agentic.tools.git_tools import git_tools
from agentic.tools.build_tools import build_tools
from agentic.tools.deploy_tools import deploy_tools
from agentic.tools.backup_tools import backup_tools
from agentic.memory import memory
from agentic.cost_tracker import cost_tracker

logger = logging.getLogger(__name__)


class JicoLifeDevAgent:
    """Dev agent for Jico Life brand."""

    def __init__(self):
        self.brand = "jico_life"
        self.repo_path = JICO_REPO_PATH
        self.model = SONNET_MODEL
        logger.info(f"Jico Life Dev Agent initialized (repo: {self.repo_path})")

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

    def build_glb_model(self, task_id: str, render_png_path: str) -> dict:
        """Build GLB 3D model from PNG render."""
        logger.info(f"Task {task_id}: Building GLB from {render_png_path}")
        memory.update_task(task_id, "in_progress", f"Building GLB model...")

        git_tools.pull(self.repo_path)

        success, output = build_tools.build_glb(self.repo_path, render_png_path)

        if not success:
            logger.error(f"GLB build failed: {output}")
            memory.update_task(task_id, "failed", f"GLB build failed: {output[:200]}")
            return {"status": "failed", "message": f"GLB build failed: {output[:200]}"}

        commit = git_tools.get_last_commit(self.repo_path)
        memory.log_build(self.brand, "glb", commit, output, status="success")

        # Backup the GLB
        backup_results = backup_tools.backup_all_platforms(
            output,
            "glb",
            self.brand
        )

        branch = git_tools.get_current_branch(self.repo_path)
        memory.update_brand_state(self.brand, current_branch=branch, last_commit=commit)

        result_msg = f"GLB model built (commit: {commit[:8]}). Backups: R2={backup_results['r2']}, GDrive={backup_results['gdrive']}"
        memory.update_task(task_id, "completed", result_msg)

        return {
            "status": "success",
            "message": result_msg,
            "build_type": "glb",
            "commit": commit,
            "backups": backup_results
        }

    def deploy_to_staging_branch(self, task_id: str) -> dict:
        """Auto-deploy to staging branch (Netlify auto-deploys on push)."""
        logger.info(f"Task {task_id}: Deploying to staging branch")
        memory.update_task(task_id, "in_progress", "Pushing to staging branch...")

        # Push to staging branch (not main)
        success = git_tools.commit_and_push(self.repo_path, "Auto-deploy to staging", "staging")

        if not success:
            logger.error("Failed to push to staging branch")
            memory.update_task(task_id, "failed", "Failed to push to staging")
            return {"status": "failed", "message": "Failed to push to staging branch"}

        commit = git_tools.get_last_commit(self.repo_path)
        memory.log_deployment(self.brand, "staging", commit)
        memory.update_brand_state(self.brand, last_deploy_env="staging")

        result_msg = "Deployed to staging branch; Netlify webhook triggered"
        memory.update_task(task_id, "completed", result_msg)

        return {"status": "success", "message": result_msg, "environment": "staging"}

    def deploy_to_production(self, task_id: str, require_approval: bool = True) -> dict:
        """Deploy to production (main branch).

        Requires explicit approval due to production safety.
        """
        if require_approval:
            logger.warning("Production deploy requested but requires approval")
            return {
                "status": "approval_required",
                "message": "Production deploy requires explicit approval",
                "next_step": "Show Discord approval buttons"
            }

        logger.info(f"Task {task_id}: Deploying to PRODUCTION")
        memory.update_task(task_id, "in_progress", "Deploying to PRODUCTION...")

        # Push to main
        success = git_tools.commit_and_push(self.repo_path, "Production release", "main")

        if not success:
            logger.error("Failed to push to main")
            memory.update_task(task_id, "failed", "Failed to push to production")
            return {"status": "failed", "message": "Failed to push to main branch"}

        commit = git_tools.get_last_commit(self.repo_path)
        memory.log_deployment(self.brand, "production", commit)
        memory.update_brand_state(self.brand, last_deploy_env="production")

        result_msg = "Deployed to PRODUCTION; Netlify auto-deploying..."
        memory.update_task(task_id, "completed", result_msg)

        return {
            "status": "success",
            "message": result_msg,
            "environment": "production",
            "commit": commit
        }


jico_life_dev_agent = JicoLifeDevAgent()
