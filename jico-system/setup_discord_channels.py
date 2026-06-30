#!/usr/bin/env python3
"""
Setup Discord channels for JICO Manager system.
Run this once to create all required channels.
"""

import asyncio
import discord
from discord.ext import commands
from config import Config

CHANNELS_TO_CREATE = [
    {
        "name": "general",
        "topic": "🗣️ Talk to Manager here - type anything, Manager routes to appropriate brand",
        "description": "User interaction with JICO Manager"
    },
    {
        "name": "nacpac-dev",
        "topic": "📱 Nacpac task updates and worker communication - internal bot routing",
        "description": "Nacpac development updates"
    },
    {
        "name": "jico-dev",
        "topic": "🎨 Jico task updates and worker communication - internal bot routing",
        "description": "Jico development updates"
    },
    {
        "name": "logs",
        "topic": "📋 Worker output, errors, and debugging information",
        "description": "System logs and error output"
    },
    {
        "name": "reports",
        "topic": "📊 Scheduled reports - builds, analytics, SEO results",
        "description": "Scheduled reports and analytics"
    },
]

async def setup_channels():
    """Create Discord channels for JICO system"""

    intents = discord.Intents.default()
    intents.message_content = True
    intents.guilds = True

    bot = commands.Bot(command_prefix='!', intents=intents)

    @bot.event
    async def on_ready():
        print(f"✅ Bot logged in as {bot.user}")

        # Get guild
        if not Config.DISCORD_GUILD_ID:
            print("❌ ERROR: DISCORD_GUILD_ID not set in .env")
            await bot.close()
            return

        guild_id = int(Config.DISCORD_GUILD_ID)
        guild = bot.get_guild(guild_id)

        if not guild:
            print(f"❌ ERROR: Could not find guild with ID {guild_id}")
            print("Make sure DISCORD_GUILD_ID is correct in .env")
            await bot.close()
            return

        print(f"📍 Setting up channels in guild: {guild.name}")
        print()

        # Create channels
        for channel_info in CHANNELS_TO_CREATE:
            channel_name = channel_info["name"]

            # Check if channel exists
            existing = discord.utils.get(guild.channels, name=channel_name)
            if existing:
                print(f"✅ #{channel_name} - Already exists")
                continue

            try:
                # Create channel
                channel = await guild.create_text_channel(
                    name=channel_name,
                    topic=channel_info["topic"],
                )
                print(f"✅ #{channel_name} - Created")

            except discord.Forbidden:
                print(f"❌ #{channel_name} - Permission denied (bot needs manage_channels)")
            except discord.HTTPException as e:
                print(f"❌ #{channel_name} - Error: {e}")

        print()
        print("🎉 Channel setup complete!")
        print()
        print("Next steps:")
        print("1. Make sure bot has these permissions in the guild:")
        print("   - View Channels")
        print("   - Read Messages/View Channels")
        print("   - Send Messages")
        print("   - Add Reactions")
        print("   - Manage Channels (for setup)")
        print()
        print("2. In .env, set DISCORD_GUILD_ID if not already set")
        print()
        print("3. Run: python main.py")
        print()

        await bot.close()

    try:
        await bot.start(Config.DISCORD_TOKEN)
    except discord.LoginFailure:
        print("❌ ERROR: Invalid Discord token in .env")
        print("Make sure DISCORD_TOKEN is correct")

if __name__ == "__main__":
    print("🚀 JICO Discord Channel Setup")
    print("=" * 50)
    print()

    if not Config.DISCORD_TOKEN:
        print("❌ ERROR: DISCORD_TOKEN not set in .env")
        print("Add your bot token to .env and try again")
        exit(1)

    print("Starting setup...")
    print("(This will create channels in your Discord server)")
    print()

    try:
        asyncio.run(setup_channels())
    except KeyboardInterrupt:
        print("\n⏹️  Setup cancelled")
    except Exception as e:
        print(f"❌ Setup failed: {e}")
