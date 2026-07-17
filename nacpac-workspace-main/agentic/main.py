"""Main entry point for Jico agentic system."""

import logging
import sys
import asyncio
from aiohttp import web

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


async def health_check(request):
    """Health check endpoint for DigitalOcean."""
    return web.Response(status=200, text="OK")


async def start_health_server():
    """Start HTTP health check server on port 8080."""
    app = web.Application()
    app.router.add_get('/health', health_check)
    app.router.add_get('/', health_check)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8080)
    await site.start()
    logger.info("✅ Health check server started on port 8080")


async def run_async():
    """Run both health server and Discord bot."""
    try:
        await asyncio.gather(
            start_health_server(),
            discord_main()
        )
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


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

    # Start Discord bot + health server
    logger.info("Starting system...")
    asyncio.run(run_async())


if __name__ == "__main__":
    main()
