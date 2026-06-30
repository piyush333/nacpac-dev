#!/usr/bin/env python3
"""
JICO System Main Entry Point
Orchestrates all components: Discord Bot, Task Router, Managers, Scheduler
"""

import asyncio
import logging
import sys
from discord_manager import run_discord_manager
from config import Config

# Setup logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/jico-system.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


async def main():
    """Main entry point"""
    logger.info("=" * 60)
    logger.info("JICO System Starting")
    logger.info("=" * 60)

    # Validate configuration
    required_configs = [
        'DISCORD_TOKEN',
        'ANTHROPIC_API_KEY',
        'TELEGRAM_BOT_TOKEN',
        'ORACLE_VM_IP'
    ]

    missing = [cfg for cfg in required_configs if not getattr(Config, cfg)]
    if missing:
        logger.error(f"Missing configuration: {missing}")
        sys.exit(1)

    logger.info("Configuration validated ✓")
    logger.info(f"Discord Token: {'*' * 20}...{Config.DISCORD_TOKEN[-4:]}")
    logger.info(f"Anthropic API: {'*' * 20}...{Config.ANTHROPIC_API_KEY[-4:]}")
    logger.info(f"Oracle VM: {Config.ORACLE_VM_IP}")

    try:
        # Start Discord Manager
        logger.info("Starting Discord Manager Bot...")
        await run_discord_manager()

    except KeyboardInterrupt:
        logger.info("Shutdown requested")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutdown...")
        sys.exit(0)
