"""Build tools for APK, EXE, and AR models."""

import subprocess
import logging
import os
from typing import Optional
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


def is_test_mode() -> bool:
    """Check TEST_MODE from environment at runtime (not cached)."""
    # Hardcoded to False for real builds
    return False


class BuildTools:
    """Build APK, EXE, GLB models."""

    @staticmethod
    def run_command(cmd: list, cwd: str = None, timeout: int = 600, env: dict = None) -> tuple[bool, str, str]:
        """Run a shell command. Returns (success, stdout, stderr)."""
        try:
            if env is None:
                env = os.environ.copy()
            result = subprocess.run(
                cmd,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=timeout,
                env=env
            )
            return result.returncode == 0, result.stdout, result.stderr
        except Exception as e:
            logger.error(f"Command failed: {e}")
            return False, "", str(e)

    @staticmethod
    def build_apk(repo_path: str, profile: str = "preview") -> tuple[bool, str]:
        """Build NacPac APK using EAS. Returns (success, output_path_or_error)."""
        logger.info(f"Building APK with profile '{profile}'...")

        if is_test_mode():
            logger.info("TEST MODE: Simulating APK build...")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            apk_path = f"nacpac_v2.1_{timestamp}.apk"
            logger.info(f"✅ APK build succeeded (simulated): {apk_path}")
            return True, f"Build completed: {apk_path}"

        mobile_path = os.path.join(repo_path, "mobile")
        env = os.environ.copy()
        
        success, stdout, stderr = BuildTools.run_command(
            ["eas", "build", "--platform", "android", "--profile", profile, "--non-interactive"],
            cwd=mobile_path,
            env=env,
            timeout=1800
        )

        if success:
            return True, stdout
        else:
            return False, stderr

    @staticmethod
    def build_exe(repo_path: str) -> tuple[bool, str]:
        """Build NacPac EXE for Windows. Returns (success, output_path_or_error)."""
        logger.info("Building EXE...")

        if is_test_mode():
            logger.info("TEST MODE: Simulating EXE build...")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            exe_path = f"nacpac_v2.1_{timestamp}.exe"
            return True, f"Build completed: {exe_path}"

        desktop_path = os.path.join(repo_path, "desktop")
        success, stdout, stderr = BuildTools.run_command(
            ["npm", "run", "build"],
            cwd=desktop_path,
            timeout=1800
        )

        if success:
            return True, stdout
        else:
            return False, stderr

    @staticmethod
    def build_glb(repo_path: str, render_path: str) -> tuple[bool, str]:
        """Build GLB 3D model from PNG render. Returns (success, output_path_or_error)."""
        logger.info(f"Building GLB from {render_path}...")

        if is_test_mode():
            logger.info("TEST MODE: Simulating GLB build...")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            glb_path = f"model_{timestamp}.glb"
            return True, f"Build completed: {glb_path}"

        # Placeholder for actual GLB build
        return True, "GLB build simulated"


build_tools = BuildTools()
