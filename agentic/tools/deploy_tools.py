"""Deployment tools for staging and production."""

import subprocess
import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)


class DeployTools:
    """Deploy built artifacts to staging/production."""

    @staticmethod
    def deploy_to_netlify(repo_path: str, branch: str = "staging") -> tuple[bool, str]:
        """Deploy Jico Life AR to Netlify by pushing to a branch.
        Netlify webhook auto-deploys when branch is pushed.
        """
        logger.info(f"Deploying Jico Life AR to Netlify (branch: {branch})...")

        # Git push to staging branch triggers Netlify webhook
        from tools.git_tools import git_tools

        current_branch = git_tools.get_current_branch(repo_path)
        success = git_tools.checkout_branch(repo_path, branch, create=False)

        if not success:
            return False, f"Failed to checkout {branch}"

        success = git_tools.commit_and_push(repo_path, f"Deploy to {branch}", branch)

        if success:
            logger.info(f"Pushed to {branch}; Netlify webhook triggered")
            return True, f"Deployed to {branch}; Netlify auto-deploying"
        else:
            return False, "Failed to push to Netlify branch"

    @staticmethod
    def deploy_firebase(repo_path: str, project: str = "nacpac-production-4134a") -> tuple[bool, str]:
        """Deploy to Firebase (for NacPac web or backend rules)."""
        logger.info(f"Deploying to Firebase project: {project}...")

        cmd = [
            "firebase", "deploy",
            "--project", project,
            "--only", "firestore,storage"
        ]

        try:
            result = subprocess.run(
                cmd,
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=300
            )

            if result.returncode == 0:
                logger.info("Firebase deploy succeeded")
                return True, result.stdout[-200:] if result.stdout else "Deployed"
            else:
                logger.error(f"Firebase deploy failed: {result.stderr}")
                return False, result.stderr
        except Exception as e:
            logger.error(f"Firebase deploy error: {e}")
            return False, str(e)

    @staticmethod
    def deploy_to_staging_server(
        artifact_path: str,
        target_host: str = "staging.nacpac.app",
        target_path: str = "/opt/nacpac/builds",
        ssh_key: str = None
    ) -> tuple[bool, str]:
        """Deploy artifact to staging server via SCP and restart service."""
        logger.info(f"Deploying {artifact_path} to {target_host}...")

        # SCP the artifact
        cmd = ["scp"]
        if ssh_key:
            cmd.extend(["-i", ssh_key])
        cmd.extend([artifact_path, f"ubuntu@{target_host}:{target_path}/"])

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

            if result.returncode != 0:
                logger.error(f"SCP failed: {result.stderr}")
                return False, result.stderr

            logger.info("Artifact uploaded to staging")
            return True, f"Deployed to {target_host}"
        except Exception as e:
            logger.error(f"Deploy failed: {e}")
            return False, str(e)

    @staticmethod
    def deploy_to_production(
        artifact_path: str,
        target_host: str = "prod.nacpac.app",
        target_path: str = "/opt/nacpac/builds",
        require_approval: bool = True,
        ssh_key: str = None
    ) -> tuple[bool, str]:
        """Deploy to production (with safety checks)."""
        if require_approval:
            logger.warning("PRODUCTION DEPLOY: Requires explicit approval (not auto-executing)")
            return False, "Production deploy requires explicit user approval via Discord"

        logger.info(f"DEPLOYING TO PRODUCTION: {artifact_path}...")

        # Same as staging but with extra logging
        return DeployTools.deploy_to_staging_server(
            artifact_path,
            target_host=target_host,
            target_path=target_path,
            ssh_key=ssh_key
        )

    @staticmethod
    def verify_deployment(target_host: str, health_check_url: str) -> bool:
        """Verify deployment succeeded via health check."""
        logger.info(f"Checking deployment health at {health_check_url}...")

        try:
            result = subprocess.run(
                ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", health_check_url],
                capture_output=True,
                text=True,
                timeout=10
            )

            status_code = result.stdout.strip()
            if status_code == "200":
                logger.info("Health check passed")
                return True
            else:
                logger.warning(f"Health check returned {status_code}")
                return False
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False


deploy_tools = DeployTools()
