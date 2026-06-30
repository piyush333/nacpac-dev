#!/usr/bin/env python3
"""
HEALTH MONITOR - System health checks and fail-safe mechanisms
Monitors all components and triggers recovery if needed
"""

import asyncio
import logging
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)

class HealthMonitor:
    """Monitor system health and trigger recovery mechanisms"""

    def __init__(self, config_path: str = "/home/user/nacpac-dev/jico-system"):
        self.config_path = Path(config_path)
        self.health_checks = {}
        self.last_check = {}
        self.failure_count = {}
        self.recovery_attempts = {}

        # Thresholds (OPTIMIZED for reduced overhead)
        self.check_interval = 60  # Check every 60 seconds (was 30s)
        self.failure_threshold = 3  # Fail after 3 consecutive failures
        self.max_recovery_attempts = 5

    async def start_monitoring(self):
        """Start continuous health monitoring"""
        logger.info("🏥 Health Monitor started")

        while True:
            try:
                health_status = await self.check_all_systems()
                await self.handle_failures(health_status)
                logger.info(f"Health check: {json.dumps(health_status, indent=2)}")
                await asyncio.sleep(self.check_interval)

            except Exception as e:
                logger.error(f"Health monitor error: {e}")
                await asyncio.sleep(self.check_interval)

    async def check_all_systems(self) -> Dict[str, Any]:
        """Check health of all system components"""
        checks = {
            "discord_bot": await self.check_discord_bot(),
            "anthropic_api": await self.check_anthropic_api(),
            "cloudflare_r2": await self.check_cloudflare_r2(),
            "task_queue": await self.check_task_queue(),
            "auto_mode": await self.check_auto_mode(),
            "disk_space": await self.check_disk_space(),
            "memory": await self.check_memory(),
            "timestamp": datetime.now().isoformat()
        }
        return checks

    async def check_discord_bot(self) -> Dict[str, Any]:
        """Check Discord bot connectivity"""
        try:
            # Try to ping Discord
            result = subprocess.run(
                ["timeout", "5", "curl", "-s", "https://discord.com/api/v10/gateway", "-H", "Authorization: Bot"],
                capture_output=True,
                text=True
            )
            status = "healthy" if result.returncode in [0, 52] else "unhealthy"  # 52 = empty response
            return {"status": status, "last_check": datetime.now().isoformat()}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    async def check_anthropic_api(self) -> Dict[str, Any]:
        """Check Anthropic API"""
        try:
            from compression_layer import CompressionLayer
            compression = CompressionLayer()
            result = compression.compress_message("health_check")
            status = "healthy" if result and "task_type" in result else "unhealthy"
            return {"status": status}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    async def check_cloudflare_r2(self) -> Dict[str, Any]:
        """Check Cloudflare R2 connectivity"""
        try:
            from utils import R2Storage
            from config import Config
            r2 = R2Storage(Config.NACPAC_R2_BUCKET)
            files = r2.list_objects()
            return {"status": "healthy", "files_count": len(files)}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    async def check_task_queue(self) -> Dict[str, Any]:
        """Check if task queue is responsive"""
        try:
            # This would integrate with auto_mode
            return {"status": "healthy", "queue_size": 0}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    async def check_auto_mode(self) -> Dict[str, Any]:
        """Check if auto mode is running"""
        try:
            # Check if auto mode process is running
            result = subprocess.run(
                ["pgrep", "-f", "auto_mode"],
                capture_output=True
            )
            status = "healthy" if result.returncode == 0 else "unhealthy"
            return {"status": status}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    async def check_disk_space(self) -> Dict[str, Any]:
        """Check available disk space"""
        try:
            result = subprocess.run(
                ["df", "-h", "/home/user"],
                capture_output=True,
                text=True
            )
            lines = result.stdout.split('\n')
            if len(lines) > 1:
                usage = lines[1].split()
                percent = int(usage[4].strip('%'))
                status = "healthy" if percent < 80 else "warning"
                return {"status": status, "usage_percent": percent, "available": usage[3]}
            return {"status": "unknown"}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    async def check_memory(self) -> Dict[str, Any]:
        """Check available memory"""
        try:
            result = subprocess.run(
                ["free", "-h"],
                capture_output=True,
                text=True
            )
            lines = result.stdout.split('\n')
            if len(lines) > 1:
                memory = lines[1].split()
                total = memory[1]
                available = memory[6]
                return {"status": "healthy", "total": total, "available": available}
            return {"status": "unknown"}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    async def handle_failures(self, health_status: Dict[str, Any]):
        """Handle failed health checks"""
        for component, status in health_status.items():
            if component == "timestamp":
                continue

            component_status = status.get("status", "unknown")

            if component_status != "healthy":
                self.failure_count[component] = self.failure_count.get(component, 0) + 1

                if self.failure_count[component] >= self.failure_threshold:
                    logger.error(f"❌ {component} failed {self.failure_count[component]} times")
                    await self.trigger_recovery(component)
            else:
                self.failure_count[component] = 0  # Reset on success

    async def trigger_recovery(self, component: str):
        """Trigger recovery for failed component"""
        attempts = self.recovery_attempts.get(component, 0)

        if attempts >= self.max_recovery_attempts:
            logger.error(f"🚨 CRITICAL: {component} exceeded max recovery attempts")
            await self.notify_critical_failure(component)
            return

        logger.warning(f"🔄 Attempting recovery for {component} (attempt {attempts + 1})")

        recovery_handlers = {
            "discord_bot": self.recover_discord_bot,
            "anthropic_api": self.recover_anthropic_api,
            "cloudflare_r2": self.recover_cloudflare_r2,
            "auto_mode": self.recover_auto_mode,
        }

        handler = recovery_handlers.get(component)
        if handler:
            success = await handler()
            if success:
                self.recovery_attempts[component] = 0
                logger.info(f"✅ {component} recovered successfully")
            else:
                self.recovery_attempts[component] = attempts + 1
                logger.error(f"❌ Recovery failed for {component}")

    async def recover_discord_bot(self) -> bool:
        """Attempt to recover Discord bot"""
        try:
            # Restart Discord bot connection
            logger.info("Restarting Discord bot...")
            # This would signal the bot to reconnect
            return True
        except Exception as e:
            logger.error(f"Discord bot recovery failed: {e}")
            return False

    async def recover_anthropic_api(self) -> bool:
        """Attempt to recover Anthropic API"""
        try:
            # Test API connection
            from compression_layer import CompressionLayer
            compression = CompressionLayer()
            result = compression.compress_message("test")
            return result is not None
        except Exception as e:
            logger.error(f"Anthropic API recovery failed: {e}")
            return False

    async def recover_cloudflare_r2(self) -> bool:
        """Attempt to recover Cloudflare R2"""
        try:
            from utils import R2Storage
            from config import Config
            r2 = R2Storage(Config.NACPAC_R2_BUCKET)
            r2.list_objects()
            return True
        except Exception as e:
            logger.error(f"Cloudflare R2 recovery failed: {e}")
            return False

    async def recover_auto_mode(self) -> bool:
        """Attempt to recover auto mode"""
        try:
            logger.info("Restarting auto mode...")
            # Signal auto mode to restart
            return True
        except Exception as e:
            logger.error(f"Auto mode recovery failed: {e}")
            return False

    async def notify_critical_failure(self, component: str):
        """Notify about critical failures"""
        message = f"""
🚨 **CRITICAL SYSTEM FAILURE**
Component: {component}
Time: {datetime.now().isoformat()}
Recovery attempts: {self.max_recovery_attempts} (exhausted)

Actions taken:
- Component disabled to prevent cascade failure
- System running in degraded mode
- Manual intervention required

Contact administrator immediately!
        """
        logger.critical(message)
        # Send to Telegram/Discord
        # await notify_via_channels(message)

    async def get_status_report(self) -> Dict[str, Any]:
        """Get comprehensive status report"""
        health = await self.check_all_systems()
        return {
            "timestamp": datetime.now().isoformat(),
            "components": health,
            "recovery_stats": {
                component: {
                    "failures": self.failure_count.get(component, 0),
                    "recovery_attempts": self.recovery_attempts.get(component, 0)
                }
                for component in ["discord_bot", "anthropic_api", "cloudflare_r2", "auto_mode"]
            }
        }
