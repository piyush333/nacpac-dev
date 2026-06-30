#!/usr/bin/env python3
"""
GIT SYNC - Automatic repository updates with backup/restore
Keeps code up-to-date and provides rollback capability
"""

import asyncio
import logging
import subprocess
import shutil
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from pathlib import Path

logger = logging.getLogger(__name__)

class GitSync:
    """Manage automatic git syncing and versioning"""

    def __init__(self, token: str = None, base_path: str = "/home/user/jico-system"):
        self.token = token
        self.base_path = Path(base_path)
        self.backups_path = self.base_path / "backups"
        self.backups_path.mkdir(exist_ok=True)

        self.repos = {
            "jico-workspace": "https://github.com/jico-org/jico-workspace.git",
            "nacpac-workspace": "https://github.com/jico-org/nacpac-workspace.git",
        }

        self.sync_history: List[Dict[str, Any]] = []
        self.last_sync = {}

    async def start_sync_scheduler(self, interval_minutes: int = 60):
        """Start automatic sync on schedule"""
        logger.info(f"🔄 Git Sync scheduler started (interval: {interval_minutes}m)")

        while True:
            try:
                await self.sync_all_repos()
                await asyncio.sleep(interval_minutes * 60)
            except Exception as e:
                logger.error(f"Sync scheduler error: {e}")
                await asyncio.sleep(60)  # Retry after 1 minute

    async def sync_all_repos(self) -> Dict[str, Any]:
        """Sync all configured repositories"""
        results = {}

        for repo_name, repo_url in self.repos.items():
            logger.info(f"Syncing {repo_name}...")
            result = await self.sync_repo(repo_name, repo_url)
            results[repo_name] = result

        self.sync_history.append({
            "timestamp": datetime.now().isoformat(),
            "results": results
        })

        logger.info(f"✅ Sync completed: {json.dumps(results)}")
        return results

    async def sync_repo(self, repo_name: str, repo_url: str) -> Dict[str, Any]:
        """Sync a single repository with backup"""
        try:
            repo_path = self.base_path / repo_name

            # Create backup before sync
            backup_path = await self.create_backup(repo_name, repo_path)
            logger.info(f"Backup created: {backup_path}")

            if repo_path.exists():
                # Existing repo - pull latest
                return await self.git_pull(repo_path, repo_name)
            else:
                # New repo - clone it
                return await self.git_clone(repo_url, repo_path, repo_name)

        except Exception as e:
            logger.error(f"Sync failed for {repo_name}: {e}")
            # Restore from backup on failure
            await self.restore_backup(repo_name)
            return {
                "status": "failed",
                "error": str(e),
                "rolled_back": True
            }

    async def git_clone(self, repo_url: str, target_path: Path, repo_name: str) -> Dict[str, Any]:
        """Clone a repository"""
        try:
            # Authenticate with token if available
            if self.token:
                auth_url = repo_url.replace(
                    "https://github.com/",
                    f"https://{self.token}@github.com/"
                )
            else:
                auth_url = repo_url

            cmd = ["git", "clone", auth_url, str(target_path)]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            if result.returncode == 0:
                logger.info(f"✅ Cloned {repo_name}")
                return {
                    "status": "cloned",
                    "repo": repo_name,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                raise Exception(result.stderr)

        except Exception as e:
            logger.error(f"Clone failed for {repo_name}: {e}")
            return {
                "status": "clone_failed",
                "error": str(e)
            }

    async def git_pull(self, repo_path: Path, repo_name: str) -> Dict[str, Any]:
        """Pull latest changes from repository"""
        try:
            cmd = ["git", "-C", str(repo_path), "pull"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            if result.returncode == 0:
                # Get latest commit info
                cmd_log = ["git", "-C", str(repo_path), "log", "-1", "--oneline"]
                log_result = subprocess.run(cmd_log, capture_output=True, text=True)
                latest = log_result.stdout.strip()

                logger.info(f"✅ Pulled {repo_name}: {latest}")
                return {
                    "status": "updated",
                    "repo": repo_name,
                    "latest_commit": latest,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                if "Already up to date" in result.stdout:
                    logger.info(f"⏸️ {repo_name} already up to date")
                    return {
                        "status": "up_to_date",
                        "repo": repo_name,
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    raise Exception(result.stderr)

        except Exception as e:
            logger.error(f"Pull failed for {repo_name}: {e}")
            return {
                "status": "pull_failed",
                "error": str(e)
            }

    async def create_backup(self, repo_name: str, repo_path: Path) -> Optional[str]:
        """Create timestamped backup of repository"""
        try:
            if not repo_path.exists():
                return None

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{repo_name}_{timestamp}"
            backup_path = self.backups_path / backup_name

            shutil.copytree(repo_path, backup_path)
            logger.info(f"Backup created: {backup_path}")

            # Keep only last 10 backups
            await self.cleanup_old_backups(repo_name, keep=10)

            return str(backup_path)

        except Exception as e:
            logger.error(f"Backup creation failed: {e}")
            return None

    async def cleanup_old_backups(self, repo_name: str, keep: int = 10):
        """Remove old backups, keep only recent ones"""
        try:
            backups = sorted(self.backups_path.glob(f"{repo_name}_*"))
            if len(backups) > keep:
                for old_backup in backups[:-keep]:
                    shutil.rmtree(old_backup)
                    logger.info(f"Removed old backup: {old_backup}")
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")

    async def restore_backup(self, repo_name: str) -> bool:
        """Restore latest backup of a repository"""
        try:
            backups = sorted(self.backups_path.glob(f"{repo_name}_*"))
            if not backups:
                logger.error(f"No backups found for {repo_name}")
                return False

            latest_backup = backups[-1]
            repo_path = self.base_path / repo_name

            # Remove current repo
            if repo_path.exists():
                shutil.rmtree(repo_path)

            # Restore from backup
            shutil.copytree(latest_backup, repo_path)
            logger.info(f"✅ Restored {repo_name} from {latest_backup}")
            return True

        except Exception as e:
            logger.error(f"Restore failed: {e}")
            return False

    async def get_backup_history(self, repo_name: str) -> List[Dict[str, Any]]:
        """Get list of available backups"""
        try:
            backups = sorted(self.backups_path.glob(f"{repo_name}_*"))
            return [
                {
                    "name": backup.name,
                    "path": str(backup),
                    "timestamp": backup.name.split("_")[-2:],
                    "size_mb": sum(f.stat().st_size for f in backup.rglob("*")) / (1024 * 1024)
                }
                for backup in backups
            ]
        except Exception as e:
            logger.error(f"History retrieval failed: {e}")
            return []

    async def get_sync_status(self) -> Dict[str, Any]:
        """Get current sync status"""
        status = {}
        for repo_name in self.repos.keys():
            repo_path = self.base_path / repo_name
            if repo_path.exists():
                cmd = ["git", "-C", str(repo_path), "log", "-1", "--oneline"]
                result = subprocess.run(cmd, capture_output=True, text=True)
                latest = result.stdout.strip() if result.returncode == 0 else "unknown"

                cmd_remote = ["git", "-C", str(repo_path), "log", "origin/main", "-1", "--oneline"]
                remote_result = subprocess.run(cmd_remote, capture_output=True, text=True)
                remote_latest = remote_result.stdout.strip() if remote_result.returncode == 0 else "unknown"

                status[repo_name] = {
                    "exists": True,
                    "latest_local": latest,
                    "latest_remote": remote_latest,
                    "in_sync": latest == remote_latest
                }
            else:
                status[repo_name] = {
                    "exists": False,
                    "message": "Not cloned yet"
                }

        return {
            "timestamp": datetime.now().isoformat(),
            "repositories": status,
            "last_sync": self.sync_history[-1] if self.sync_history else None
        }

    async def manual_sync(self, repo_name: Optional[str] = None) -> Dict[str, Any]:
        """Manually trigger sync"""
        if repo_name:
            repo_url = self.repos.get(repo_name)
            if not repo_url:
                return {"error": f"Unknown repo: {repo_name}"}
            return await self.sync_repo(repo_name, repo_url)
        else:
            return await self.sync_all_repos()
