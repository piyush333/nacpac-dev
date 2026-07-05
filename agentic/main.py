"""Main entry point for Jico agentic system."""

import logging
import sys
import asyncio

from agentic.config import validate_config
from agentic.discord_bot import main as discord_main

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler("/tmp/jico-agentic.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def main():
    """Start the agentic system."""
    logger.info("=" * 60)
    logger.info("🤖 Jico Agentic System Starting (v2026-07-05T21:50)")
    logger.info("=" * 60)

    # Validate config
    try:
        validate_config()
        logger.info("✅ Config validated")
    except ValueError as e:
        logger.error(f"❌ Config error: {e}")
        sys.exit(1)

    # Start Discord bot
    try:
        logger.info("Starting Discord bot...")
        asyncio.run(discord_main())
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
