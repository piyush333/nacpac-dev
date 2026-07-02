"""Build tools for APK, EXE, and AR models."""

import subprocess
import logging
import os
from typing import Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class BuildTools:
    """Build APK, EXE, GLB models."""

    @staticmethod
    def run_command(cmd: list, cwd: str = None, timeout: int = 600) -> tuple[bool, str, str]:
        """Run a shell command. Returns (success, stdout, stderr)."""
        try:
            result = subprocess.run(
                cmd,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return result.returncode == 0, result.stdout, result.stderr
        except Exception as e:
            logger.error(f"Command failed: {e}")
            return False, "", str(e)

    @staticmethod
    def build_apk(repo_path: str, profile: str = "preview") -> tuple[bool, str]:
        """Build NacPac APK using EAS. Returns (success, output_path_or_error)."""
        logger.info(f"Building APK with profile '{profile}'...")

        cmd = [
            "eas", "build",
            "--platform", "android",
            "--profile", profile,
            "--non-interactive"
        ]

        success, stdout, stderr = BuildTools.run_command(cmd, cwd=repo_path, timeout=1800)

        if success:
            logger.info("APK build succeeded")
            # EAS outputs download URL in stdout
            return True, stdout[-500:] if stdout else "Build completed"
        else:
            logger.error(f"APK build failed: {stderr}")
            return False, stderr

    @staticmethod
    def build_exe(repo_path: str) -> tuple[bool, str]:
        """Build NacPac desktop EXE using npm. Returns (success, output_path_or_error)."""
        logger.info("Building EXE...")

        desktop_path = os.path.join(repo_path, "desktop")

        # First: npm install (if needed)
        success, _, stderr = BuildTools.run_command(["npm", "install"], cwd=desktop_path, timeout=300)
        if not success:
            logger.warning(f"npm install had issues (may be OK): {stderr[:200]}")

        # Build
        cmd = ["npm", "run", "build"]
        success, stdout, stderr = BuildTools.run_command(cmd, cwd=desktop_path, timeout=600)

        if success:
            logger.info("EXE build succeeded")
            # Find dist directory
            dist_path = os.path.join(desktop_path, "dist")
            if os.path.exists(dist_path):
                return True, dist_path
            return True, desktop_path
        else:
            logger.error(f"EXE build failed: {stderr}")
            return False, stderr

    @staticmethod
    def build_glb(repo_path: str, render_png_path: str) -> tuple[bool, str]:
        """Build GLB model from PNG render. Returns (success, output_glb_path_or_error)."""
        logger.info(f"Building GLB from {render_png_path}...")

        # Assume there's a scripts/build_glb.py in the repo
        script_path = os.path.join(repo_path, "scripts", "build_glb.py")

        if not os.path.exists(script_path):
            logger.error(f"build_glb.py not found at {script_path}")
            return False, f"Script not found: {script_path}"

        cmd = ["python", script_path, render_png_path]
        success, stdout, stderr = BuildTools.run_command(cmd, cwd=repo_path, timeout=120)

        if success:
            logger.info("GLB build succeeded")
            # Try to find the output GLB file
            assets_dir = os.path.join(repo_path, "assets")
            if os.path.exists(assets_dir):
                glb_files = list(Path(assets_dir).glob("*.glb"))
                if glb_files:
                    return True, str(glb_files[-1])  # Latest GLB
            return True, stdout
        else:
            logger.error(f"GLB build failed: {stderr}")
            return False, stderr

    @staticmethod
    def verify_build_output(output_path: str) -> bool:
        """Verify that build output exists."""
        if not output_path or not os.path.exists(output_path):
            logger.error(f"Build output not found: {output_path}")
            return False
        return True


build_tools = BuildTools()
