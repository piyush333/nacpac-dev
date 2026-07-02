"""Backup tools: R2, Google Drive, GitHub Releases."""

import logging
import os
import subprocess
from typing import Optional

logger = logging.getLogger(__name__)


class BackupTools:
    """Backup build artifacts to 3 platforms."""

    @staticmethod
    def backup_to_r2(
        file_path: str,
        bucket: str,
        key: str,
        region: str = "auto"
    ) -> tuple[bool, str]:
        """Upload file to Cloudflare R2 via AWS CLI.

        file_path: local path to file
        bucket: r2://bucket-name
        key: object key (path in bucket)
        """
        logger.info(f"Backing up {file_path} to R2 ({key})...")

        endpoint_url = f"https://{bucket.replace('r2://', '')}.r2.cloudflarestorage.com"

        cmd = [
            "aws", "s3", "cp",
            file_path,
            f"s3://{bucket}/{key}",
            "--endpoint-url", endpoint_url
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            if result.returncode == 0:
                logger.info(f"Backed up to R2: {key}")
                return True, f"R2: {key}"
            else:
                logger.error(f"R2 backup failed: {result.stderr}")
                return False, result.stderr
        except Exception as e:
            logger.error(f"R2 backup error: {e}")
            return False, str(e)

    @staticmethod
    def backup_to_google_drive(
        file_path: str,
        folder_id: str,
        credentials_json: str = None
    ) -> tuple[bool, str]:
        """Upload file to Google Drive.

        credentials_json: path to service account JSON or env var with JSON content
        """
        logger.info(f"Backing up {file_path} to Google Drive...")

        if not credentials_json:
            logger.error("Google Drive credentials not provided")
            return False, "No credentials"

        # Try using gdrive CLI (must be installed)
        try:
            cmd = [
                "gdrive", "upload",
                "--parent", folder_id,
                file_path
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

            if result.returncode == 0:
                logger.info(f"Backed up to Google Drive: {file_path}")
                return True, f"Google Drive: {result.stdout.strip()}"
            else:
                logger.warning(f"gdrive CLI not available or failed: {result.stderr}")
                return False, "gdrive CLI not available"
        except Exception as e:
            logger.warning(f"Google Drive backup failed: {e}")
            return False, str(e)

    @staticmethod
    def backup_to_github_release(
        file_path: str,
        repo: str,
        tag: str,
        github_token: str = None
    ) -> tuple[bool, str]:
        """Create GitHub release and upload artifact.

        repo: owner/repo
        tag: release tag (e.g., "v1.2.3-build-123")
        """
        logger.info(f"Backing up {file_path} to GitHub release {tag}...")

        if not github_token:
            github_token = os.getenv("GITHUB_TOKEN")

        if not github_token:
            logger.error("GitHub token not provided")
            return False, "No GitHub token"

        try:
            # Use GitHub CLI if available
            cmd = [
                "gh", "release", "create", tag,
                file_path,
                "--repo", repo,
                "--title", f"Build {tag}",
                "--notes", f"Automated build release"
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,
                env={**os.environ, "GITHUB_TOKEN": github_token}
            )

            if result.returncode == 0:
                logger.info(f"Created GitHub release: {tag}")
                return True, f"GitHub: {tag}"
            else:
                logger.warning(f"GitHub release failed: {result.stderr}")
                return False, result.stderr
        except Exception as e:
            logger.warning(f"GitHub release error: {e}")
            return False, str(e)

    @staticmethod
    def backup_all_platforms(
        file_path: str,
        build_type: str,
        brand: str,
        r2_bucket: str = None,
        gdrive_folder: str = None,
        github_repo: str = None,
        github_tag: str = None
    ) -> dict:
        """Backup to all 3 platforms. Returns dict with results."""
        logger.info(f"Backing up to all platforms: {file_path}")

        results = {
            "r2": False,
            "gdrive": False,
            "github": False
        }

        # R2 key: {brand}/{build_type}/{filename}
        if r2_bucket:
            filename = os.path.basename(file_path)
            r2_key = f"{brand}/{build_type}/{filename}"
            success, msg = BackupTools.backup_to_r2(file_path, r2_bucket, r2_key)
            results["r2"] = success
            logger.info(f"R2: {msg}")

        # Google Drive
        if gdrive_folder:
            success, msg = BackupTools.backup_to_google_drive(file_path, gdrive_folder)
            results["gdrive"] = success
            logger.info(f"Google Drive: {msg}")

        # GitHub Release
        if github_repo and github_tag:
            success, msg = BackupTools.backup_to_github_release(file_path, github_repo, github_tag)
            results["github"] = success
            logger.info(f"GitHub: {msg}")

        return results


backup_tools = BackupTools()
