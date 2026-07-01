import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from config import Config

logger = logging.getLogger(__name__)

class BuildBackup:
    """Backup and rollback system for builds"""

    BACKUP_DIR = Path(Config.NACPAC_DIR) / ".build-backups"
    METADATA_FILE = BACKUP_DIR / "builds.json"
    MAX_BACKUPS = 2

    def __init__(self):
        self.BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        self._ensure_metadata()

    def _ensure_metadata(self):
        """Ensure metadata file exists"""
        if not self.METADATA_FILE.exists():
            self.METADATA_FILE.write_text(json.dumps({"builds": []}, indent=2))

    def save_build(self, build_type: str, file_path: str, url: str, commit_hash: str = None) -> bool:
        """Save build info and keep last 2 versions"""
        try:
            metadata = json.loads(self.METADATA_FILE.read_text())

            build_info = {
                "type": build_type,  # apk or exe
                "timestamp": datetime.now().isoformat(),
                "file_path": file_path,
                "url": url,
                "commit_hash": commit_hash,
            }

            # Add to front of list
            metadata["builds"].insert(0, build_info)

            # Keep only last 2 builds per type
            builds_by_type = {}
            filtered_builds = []

            for build in metadata["builds"]:
                build_t = build["type"]
                if build_t not in builds_by_type:
                    builds_by_type[build_t] = 0

                if builds_by_type[build_t] < self.MAX_BACKUPS:
                    filtered_builds.append(build)
                    builds_by_type[build_t] += 1

            metadata["builds"] = filtered_builds
            self.METADATA_FILE.write_text(json.dumps(metadata, indent=2))

            logger.info(f"Backup saved: {build_type} - {url}")
            return True

        except Exception as e:
            logger.error(f"Failed to save build backup: {e}")
            return False

    def get_last_build(self, build_type: str) -> Optional[Dict[str, Any]]:
        """Get the last successful build of a type"""
        try:
            metadata = json.loads(self.METADATA_FILE.read_text())

            for build in metadata["builds"]:
                if build["type"] == build_type:
                    return build

            return None

        except Exception as e:
            logger.error(f"Failed to get last build: {e}")
            return None

    def get_build_history(self) -> Dict[str, Any]:
        """Get all build history"""
        try:
            return json.loads(self.METADATA_FILE.read_text())
        except Exception as e:
            logger.error(f"Failed to get build history: {e}")
            return {"builds": []}
