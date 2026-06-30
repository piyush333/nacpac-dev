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
    """Discord Bot Manager for JICO System - Manager routing from #general"""

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

        # Channel references
        self.general_channel = None
        self.nacpac_dev_channel = None
        self.jico_dev_channel = None
        self.logs_channel = None
        self.reports_channel = None

    @commands.Cog.listener()
    async def on_ready(self):
        """Bot is ready - initialize channel references"""
        logger.info(f"🤖 Discord Manager online as {self.bot.user}")

        if Config.DISCORD_GUILD_ID:
            guild = self.bot.get_guild(int(Config.DISCORD_GUILD_ID))
            if guild:
                # Set up channel references
                self.general_channel = discord.utils.get(guild.channels, name="general")
                self.nacpac_dev_channel = discord.utils.get(guild.channels, name="nacpac-dev")
                self.jico_dev_channel = discord.utils.get(guild.channels, name="jico-dev")
                self.logs_channel = discord.utils.get(guild.channels, name="logs")
                self.reports_channel = discord.utils.get(guild.channels, name="reports")

                logger.info(f"✅ Channels initialized: general={self.general_channel is not None}, nacpac-dev={self.nacpac_dev_channel is not None}, jico-dev={self.jico_dev_channel is not None}")

        # Start auto mode
        if not self.auto_mode_task:
            self.auto_mode_task = asyncio.create_task(self.auto_executor.start_auto_mode())
            logger.info("🤖 Auto mode started - listening for tasks in #general")

    @commands.Cog.listener()
    async def on_message(self, message):
        """Handle messages - Manager listens in #general only"""
        # Ignore bot messages
        if message.author == self.bot.user:
            return

        # Only process messages from #general (where user talks to Manager)
        if message.channel.name != "general":
            return

        # Only authorized user can command
        if message.author.id != Config.ALLOWED_USER_ID:
            logger.warning(f"Unauthorized message from {message.author}: {message.content}")
            return

        try:
            await self.process_user_message(message)
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            await message.channel.send(f"❌ Error: {str(e)}")

        await self.bot.process_commands(message)

    async def process_user_message(self, message):
        """
        Manager intelligently reads user input in #general:
        1. Decide: Nacpac or Jico?
        2. Parse: What task?
        3. Route: Queue to auto mode
        4. Update: Post to appropriate channel
        """
        user_input = message.content.strip()
        if not user_input or user_input.startswith("!"):
            return

        logger.info(f"Manager processing: {user_input}")
        await message.add_reaction("⏳")

        # Step 1: Intelligently detect brand (Nacpac vs Jico)
        brand = self.detect_brand(user_input)
        logger.info(f"Detected brand: {brand}")

        # Step 2: Compress message into task JSON
        task = self.compression.compress_message(user_input)

        # Step 3: Override task_type based on brand detection if needed
        if brand == "nacpac":
            task["task_type"] = "nacpac"
        elif brand == "jico":
            task["task_type"] = "jico"

        logger.info(f"Task: {task['task_type']}/{task['target']} - {task['action']}")

        # Step 4: Queue to auto mode
        task_id = await self.auto_executor.queue_task(task)

        await message.remove_reaction("⏳", self.bot.user)
        await message.add_reaction("✅")

        # Step 5: Acknowledge in #general
        brand_emoji = "📱" if brand == "nacpac" else "🎨"
        await message.channel.send(
            f"{brand_emoji} **{brand.upper()}** task queued\n"
            f"ID: `{task_id}`\n"
            f"Action: {task['action'][:100]}...\n"
            f"Updates → #{brand}-dev"
        )

        # Step 6: Post to brand channel (nacpac-dev or jico-dev)
        brand_channel = self.nacpac_dev_channel if brand == "nacpac" else self.jico_dev_channel
        if brand_channel:
            await brand_channel.send(
                f"📋 Task {task_id} started\n"
                f"**Action:** {task['action']}\n"
                f"**Target:** {task['target']}\n"
                f"**Priority:** {task['priority']}"
            )

    def detect_brand(self, user_input: str) -> str:
        """
        Intelligently detect brand from user input:
        - Nacpac keywords: mobile, desktop, APK, EXE, expo, electron, home screen, UI, button, build, sticker, wallpaper
        - Jico keywords: AR, panel, Shopify, 3D, model, asset, Netlify, glb, wall
        - Default: Nacpac (more common)
        """
        nacpac_keywords = [
            "mobile", "desktop", "apk", "exe", "expo", "electron",
            "home screen", "ui", "button", "build", "sticker", "wallpaper",
            "react native", "typescript", "firebase", "screen", "feature"
        ]
        jico_keywords = [
            "ar", "panel", "shopify", "3d", "model", "asset", "netlify",
            "glb", "wall", "render", "variant", "color", "acoustic"
        ]

        user_lower = user_input.lower()

        # Count keyword matches
        nacpac_score = sum(1 for kw in nacpac_keywords if kw in user_lower)
        jico_score = sum(1 for kw in jico_keywords if kw in user_lower)

        if jico_score > nacpac_score:
            return "jico"
        return "nacpac"  # Default to Nacpac

    async def post_task_result(self, task: Dict[str, Any], result: Dict[str, Any]):
        """
        Post task result to appropriate channel:
        - Task updates → #nacpac-dev or #jico-dev
        - Logs → #logs
        - Reports → #reports
        """
        task_type = task.get("task_type", "unknown")
        task_id = task.get("task_id", "unknown")
        action = task.get("action", "")
        status = result.get("status", "unknown")

        # Determine which dev channel
        if task_type == "nacpac":
            channel = self.nacpac_dev_channel
        elif task_type == "jico":
            channel = self.jico_dev_channel
        else:
            channel = self.logs_channel

        if not channel:
            logger.warning(f"No channel found for task type: {task_type}")
            return

        # Format result message
        status_emoji = "✅" if status == "success" else "❌" if status == "error" else "⏳"
        result_msg = (
            f"{status_emoji} **Task {task_id} {status.upper()}**\n"
            f"Action: {action}\n"
            f"Target: {task.get('target', 'unknown')}\n"
        )

        # Add result details
        if status == "success":
            if "builds" in result:
                for build in result.get("builds", []):
                    if build.get("status") == "success":
                        result_msg += f"📦 {build['type'].upper()}: {build.get('url', 'built')}\n"
            if "summary" in result:
                result_msg += f"📝 {result['summary'][:200]}\n"
        elif status == "error":
            result_msg += f"❌ Error: {result.get('error', 'Unknown error')}\n"

        try:
            await channel.send(result_msg)
            logger.info(f"Posted result to #{channel.name}")
        except Exception as e:
            logger.error(f"Failed to post result: {e}")

    async def send_to_channel(self, channel, message: str):
        """Send message to specific Discord channel"""
        if channel:
            try:
                await channel.send(message)
                logger.info(f"Sent to #{channel.name}: {message[:50]}...")
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
📚 **JICO Manager Architecture**

**How it works:**
1️⃣ You talk in **#general** (plain language, any task)
2️⃣ Manager reads → decides brand (Nacpac/Jico) → routes task
3️⃣ Workers execute in background
4️⃣ Results appear in **#nacpac-dev** or **#jico-dev**

**You stay in #general. Manager handles the routing.**

**Channels:**
- **#general** — You talk here, Manager listens and routes
- **#nacpac-dev** — Nacpac task updates and results (bot-to-bot)
- **#jico-dev** — Jico task updates and results (bot-to-bot)
- **#logs** — Raw worker output and errors
- **#reports** — Scheduled reports (builds, analytics)

**Example in #general:**
You: "Add dark mode to mobile app"
Manager: "📱 NACPAC task queued. Updates → #nacpac-dev"
[Manager routes to dev worker, which generates code and builds]

**Commands (anywhere):**
- `!status` — System health
- `!auto_mode status` — Pending tasks
- `!auto_mode history` — Recent work

Stay in #general. The bots handle the rest.
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
