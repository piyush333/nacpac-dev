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
    test_mode = os.getenv("BUILD_TEST_MODE", "false").lower() == "true"
    return test_mode


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
    def build_apk(repo_path: str, profile: str = "preview", branch: str = None) -> tuple[bool, str]:
        """Build NacPac APK using EAS or return pre-built version. Returns (success, output_path_or_url)."""
        logger.info(f"Building APK with profile '{profile}' from branch '{branch or 'main'}'...")

        if is_test_mode():
            logger.info("TEST MODE: Returning pre-built NacPac APK from R2...")
            apk_url = "https://pub-20409ad971be41a48b6e0042388c6da3.r2.dev/mobile/nacpac-production.apk"
            logger.info(f"✅ APK ready (from {branch or 'main'}): {apk_url}")
            return True, apk_url

        logger.warning(f"🟢 RUNNING REAL EAS BUILD (not test mode)")
        mobile_path = os.path.join(repo_path, "mobile")
        env = os.environ.copy()
        logger.info(f"Mobile path: {mobile_path}")
        logger.info(f"EAS command: eas build --platform android --profile {profile}")

        success, stdout, stderr = BuildTools.run_command(
            ["eas", "build", "--platform", "android", "--profile", profile, "--non-interactive", "-v"],
            cwd=mobile_path,
            env=env,
            timeout=1800
        )

        if success:
            logger.info(f"✅ EAS build succeeded: {stdout[:500]}")
            return True, stdout
        else:
            logger.error(f"❌ EAS build failed")
            logger.error(f"EAS stderr: {stderr[:500]}")
            logger.error(f"EAS stdout: {stdout[:500]}")
            return False, stderr or stdout or "EAS build failed"

    @staticmethod
    def build_exe(repo_path: str) -> tuple[bool, str]:
        """Build NacPac EXE for Windows or return pre-built version. Returns (success, output_path_or_url)."""
        logger.info("Building EXE...")

        if is_test_mode():
            logger.info("TEST MODE: Returning pre-built NacPac EXE from R2...")
            exe_url = "https://pub-20409ad971be41a48b6e0042388c6da3.r2.dev/desktop/NACPAC%20Production%201.0.0.exe"
            logger.info(f"✅ EXE ready: {exe_url}")
            return True, exe_url

        logger.info("RUNNING REAL NPM BUILD (not test mode)")
        desktop_path = os.path.join(repo_path, "desktop")
        success, stdout, stderr = BuildTools.run_command(
            ["npm", "run", "build"],
            cwd=desktop_path,
            timeout=1800
        )

        if success:
            logger.info(f"✅ NPM build succeeded: {stdout[:500]}")
            return True, stdout
        else:
            logger.error(f"❌ NPM build failed: {stderr[:500]}")
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
