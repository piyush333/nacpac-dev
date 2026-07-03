"""Preview System - render apps locally and take screenshots."""

import logging
import subprocess
import time
from pathlib import Path
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


class PreviewSystem:
    """Run apps locally and capture screenshots using Playwright."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def start_dev_server(self, repo_path: str, command: str, timeout: int = 30) -> Tuple[bool, str]:
        """Start a dev server in the background.

        Args:
            repo_path: Path to repository
            command: Command to run (e.g., "npm start", "expo start")
            timeout: Maximum time to wait for server to be ready

        Returns:
            (success, pid_or_error)
        """
        try:
            self.logger.info(f"Starting dev server: {command} in {repo_path}")

            # Start process in background
            process = subprocess.Popen(
                command.split(),
                cwd=repo_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # Wait for server to be ready
            time.sleep(timeout)

            if process.poll() is not None:
                # Process exited unexpectedly
                stdout, stderr = process.communicate()
                self.logger.error(f"Dev server failed to start: {stderr}")
                return False, stderr

            self.logger.info(f"✅ Dev server started (PID: {process.pid})")
            return True, str(process.pid)

        except Exception as e:
            self.logger.error(f"❌ Failed to start dev server: {e}")
            return False, str(e)

    def take_screenshot(
        self,
        url: str = "http://localhost:3000",
        output_path: str = "/tmp/preview.png",
        viewport_width: int = 1280,
        viewport_height: int = 800
    ) -> Tuple[bool, str]:
        """Take screenshot using Playwright.

        Args:
            url: URL to screenshot
            output_path: Where to save screenshot
            viewport_width: Screenshot width
            viewport_height: Screenshot height

        Returns:
            (success, path_or_error)
        """
        try:
            # Check if Playwright is available
            try:
                from playwright.sync_api import sync_playwright
            except ImportError:
                self.logger.error("Playwright not installed. Run: pip install playwright")
                return False, "Playwright not installed"

            self.logger.info(f"Taking screenshot: {url} → {output_path}")

            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page(
                    viewport={"width": viewport_width, "height": viewport_height}
                )

                # Navigate to URL
                page.goto(url, wait_until="networkidle", timeout=30000)

                # Wait a bit for content to render
                page.wait_for_timeout(2000)

                # Take screenshot
                page.screenshot(path=output_path)

                browser.close()

            self.logger.info(f"✅ Screenshot saved: {output_path}")
            return True, output_path

        except Exception as e:
            self.logger.error(f"❌ Screenshot failed: {e}")
            return False, str(e)

    def stop_dev_server(self, pid: str) -> bool:
        """Stop a dev server process.

        Args:
            pid: Process ID

        Returns:
            True if successful
        """
        try:
            import signal
            import os

            pid_int = int(pid)
            os.kill(pid_int, signal.SIGTERM)
            time.sleep(2)

            self.logger.info(f"✅ Dev server (PID: {pid}) stopped")
            return True

        except Exception as e:
            self.logger.error(f"❌ Failed to stop dev server: {e}")
            return False

    def preview_feature(
        self,
        repo_path: str,
        dev_command: str,
        preview_url: str,
        output_path: str = "/tmp/preview.png"
    ) -> Tuple[bool, str]:
        """Complete preview workflow: start server, screenshot, stop server.

        Args:
            repo_path: Repository path
            dev_command: Command to start dev server
            preview_url: URL to screenshot
            output_path: Where to save screenshot

        Returns:
            (success, screenshot_path_or_error)
        """
        self.logger.info(f"Starting preview workflow for {repo_path}")

        # Start dev server
        success, pid_or_error = self.start_dev_server(repo_path, dev_command)
        if not success:
            return False, f"Dev server failed: {pid_or_error}"

        pid = pid_or_error

        try:
            # Take screenshot
            screenshot_success, screenshot_path = self.take_screenshot(
                url=preview_url,
                output_path=output_path
            )

            if not screenshot_success:
                return False, f"Screenshot failed: {screenshot_path}"

            return True, screenshot_path

        finally:
            # Always stop dev server
            self.stop_dev_server(pid)


preview = PreviewSystem()
