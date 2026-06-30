import logging
import asyncio
import discord
from discord.ext import commands
from typing import Dict, Any
from compression_layer import CompressionLayer
from task_router import TaskRouter
from nacpac_manager import NacpacManager
from jico_manager import JicoManager
from utils import OracleVMConnector, TaskScheduler
from auto_mode import AutoTaskExecutor
from config import Config

logger = logging.getLogger(__name__)

class DiscordManager(commands.Cog):
    """Discord Bot Manager for JICO System"""

    def __init__(self, bot):
        self.bot = bot
        self.compression = CompressionLayer()
        self.nacpac_mgr = NacpacManager()
        self.jico_mgr = JicoManager()
        self.oracle_vm = OracleVMConnector()
        self.scheduler = TaskScheduler(self.oracle_vm)
        self.router = TaskRouter(self.nacpac_mgr, self.jico_mgr, self.scheduler)

        # Auto Mode - Autonomous task execution
        self.auto_executor = AutoTaskExecutor(self.compression, self.router, self)
        self.auto_mode_task = None

        # Cache for Discord channels
        self.logs_channel = None
        self.reports_channel = None

    @commands.Cog.listener()
    async def on_ready(self):
        """Bot is ready"""
        logger.info(f"Discord bot logged in as {self.bot.user}")

        # Get channel references
        if Config.DISCORD_GUILD_ID:
            guild = self.bot.get_guild(int(Config.DISCORD_GUILD_ID))
            if guild:
                self.logs_channel = discord.utils.get(guild.channels, name=Config.DISCORD_LOGS_CHANNEL)
                self.reports_channel = discord.utils.get(guild.channels, name=Config.DISCORD_REPORTS_CHANNEL)

        # Start auto mode automatically
        if not self.auto_mode_task:
            self.auto_mode_task = asyncio.create_task(self.auto_executor.start_auto_mode())
            logger.info("🤖 Auto mode started automatically")

    @commands.Cog.listener()
    async def on_message(self, message):
        """Handle incoming messages"""
        # Ignore bot messages
        if message.author == self.bot.user:
            return

        # Only process messages from allowed user or in specific channels
        if message.author.id != Config.ALLOWED_USER_ID:
            logger.warning(f"Message from unauthorized user: {message.author.id}")
            return

        # Process command
        try:
            await self.process_message(message)
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            await message.channel.send(f"❌ Error: {str(e)}")

        # Process commands
        await self.bot.process_commands(message)

    async def process_message(self, message):
        """Process user message through the pipeline - QUEUES TO AUTO MODE"""
        user_input = message.content.strip()

        if not user_input:
            return

        logger.info(f"Processing message from {message.author}: {user_input}")

        # Step 1: Compress message
        await message.add_reaction('⏳')
        task = self.compression.compress_message(user_input)
        logger.info(f"Compressed task: {task}")

        # Step 2: Queue to auto mode (don't execute immediately)
        task_id = await self.auto_executor.queue_task(task)
        await message.remove_reaction('⏳', self.bot.user)
        await message.add_reaction('📋')

        # Send confirmation
        await message.channel.send(f"📋 Task queued: `{task_id}`\nAuto mode will execute when a worker is available")

    async def send_to_channel(self, channel, message: str):
        """Send message to Discord channel"""
        if channel:
            try:
                await channel.send(message)
                logger.info(f"Sent to {channel.name}: {message[:50]}...")
            except Exception as e:
                logger.error(f"Failed to send message: {e}")
        else:
            logger.warning("Channel not found")

    @commands.command()
    async def status(self, ctx):
        """Get system status"""
        status_msg = f"""
🔧 **JICO System Status**
- Discord Bot: ✅ Connected
- Compression Layer: ✅ Ready
- Nacpac Manager: ✅ Ready
- Jico Manager: ✅ Ready
- Oracle VM: Testing...
        """

        # Test Oracle VM connection
        vm_result = await self.oracle_vm.execute_remote_command("echo 'test'")
        vm_status = "✅" if vm_result.get("status") == "success" else "❌"
        status_msg += f"\n- Oracle VM: {vm_status} {vm_result.get('status')}"

        await ctx.send(status_msg)

    @commands.command()
    async def help_jico(self, ctx):
        """Show JICO system help"""
        help_msg = """
📚 **JICO System Commands**

**Natural Language Tasks:**
- Send any message describing your task
- System will compress, route, and execute

**Examples:**
- "Generate SEO tags for nacpac homepage"
- "Schedule a build for tomorrow at 10am"
- "Run dev tests on jico module"
- "Create ad campaign for Q3"

**Scheduled Tasks:**
- Use natural language with time references
- Examples: "Schedule...", "Tomorrow...", "Next week..."

**System Commands:**
- `!status` - Show system status
- `!help_jico` - Show this help

For detailed help, contact @techbot
        """
        await ctx.send(help_msg)

    @commands.command()
    async def auto_mode(self, ctx, action: str = "start"):
        """Control auto mode - start, stop, pause, resume, status"""
        action = action.lower()

        if action == "start":
            if not self.auto_mode_task:
                self.auto_mode_task = asyncio.create_task(self.auto_executor.start_auto_mode())
                await ctx.send("🤖 **AUTO MODE STARTED**\nSystem is now in autonomous mode - processes tasks continuously")
            else:
                await ctx.send("❌ Auto mode is already running")

        elif action == "stop":
            if self.auto_mode_task:
                await self.auto_executor.pause()
                self.auto_mode_task.cancel()
                self.auto_mode_task = None
                await ctx.send("⏹️ **AUTO MODE STOPPED**")
            else:
                await ctx.send("❌ Auto mode is not running")

        elif action == "pause":
            await self.auto_executor.pause()
            await ctx.send("⏸️ **AUTO MODE PAUSED**\nNo new tasks will be accepted")

        elif action == "resume":
            await self.auto_executor.resume()
            await ctx.send("▶️ **AUTO MODE RESUMED**\nContinuous execution resumed")

        elif action == "status":
            status = await self.auto_executor.get_status()
            status_msg = f"""
🤖 **AUTO MODE STATUS**
Enabled: {'✅ Yes' if status['auto_mode'] else '❌ No'}
Pending Tasks: {status['pending']}
Executing: {status['executing']}
Completed: {status['completed']}

📋 Pending: {', '.join(status['tasks']['pending'][:3]) or 'None'}
⚙️  Executing: {', '.join(status['tasks']['executing'][:3]) or 'None'}
✅ Recent: {', '.join(status['tasks']['recent_completed'][-3:]) or 'None'}
            """
            await ctx.send(status_msg)

        elif action == "history":
            history = await self.auto_executor.get_task_history(10)
            history_msg = "📊 **RECENT TASK HISTORY** (last 10)\n"
            for task in history[-10:]:
                history_msg += f"\n{task.get('task_id')}"
                history_msg += f"\n  Status: {task.get('status')}"
                history_msg += f"\n  Action: {task.get('action')}\n"
            await ctx.send(history_msg)

        else:
            help_msg = """
**Auto Mode Commands:**
- `!auto_mode start` - Start autonomous execution
- `!auto_mode stop` - Stop autonomous mode
- `!auto_mode pause` - Pause (don't accept new tasks)
- `!auto_mode resume` - Resume execution
- `!auto_mode status` - Show current status
- `!auto_mode history` - Show task history
            """
            await ctx.send(help_msg)


def create_discord_bot():
    """Create and configure Discord bot"""
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True

    bot = commands.Bot(command_prefix='!', intents=intents)

    @bot.event
    async def on_ready():
        logger.info(f"Bot logged in as {bot.user}")

    return bot


async def run_discord_manager():
    """Run the Discord manager bot"""
    bot = create_discord_bot()
    await bot.add_cog(DiscordManager(bot))

    try:
        await bot.start(Config.DISCORD_TOKEN)
    except Exception as e:
        logger.error(f"Discord bot error: {e}")


if __name__ == "__main__":
    asyncio.run(run_discord_manager())
