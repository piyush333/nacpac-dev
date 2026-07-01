import logging
import asyncio
import discord
import json
from discord.ext import commands
from discord.ui import Button, View
from typing import Dict, Any
from anthropic import Anthropic
from compression_layer import CompressionLayer
from task_router import TaskRouter
from nacpac_manager import NacpacManager
from jico_manager import JicoManager
from utils import OracleVMConnector, TaskScheduler
from auto_mode import AutoTaskExecutor
from config import Config
from cost_tracker import CostTracker
from model_selector import ModelSelector
from session_manager import SessionManager

logger = logging.getLogger(__name__)

class ConfirmationView(View):
    """Yes/No confirmation buttons"""
    def __init__(self):
        super().__init__()
        self.result = None

    @discord.ui.button(label="✅ Yes", style=discord.ButtonStyle.green)
    async def yes_button(self, interaction: discord.Interaction, button: Button):
        self.result = "yes"
        await interaction.response.defer()
        self.stop()

    @discord.ui.button(label="❌ No", style=discord.ButtonStyle.red)
    async def no_button(self, interaction: discord.Interaction, button: Button):
        self.result = "no"
        await interaction.response.defer()
        self.stop()

class BuildTypeView(View):
    """Build type selection buttons"""
    def __init__(self):
        super().__init__()
        self.result = None

    @discord.ui.button(label="📱 APK", style=discord.ButtonStyle.blurple)
    async def apk_button(self, interaction: discord.Interaction, button: Button):
        self.result = "apk"
        await interaction.response.defer()
        self.stop()

    @discord.ui.button(label="🖥️ EXE", style=discord.ButtonStyle.blurple)
    async def exe_button(self, interaction: discord.Interaction, button: Button):
        self.result = "exe"
        await interaction.response.defer()
        self.stop()

    @discord.ui.button(label="📦 BOTH", style=discord.ButtonStyle.green)
    async def both_button(self, interaction: discord.Interaction, button: Button):
        self.result = "both"
        await interaction.response.defer()
        self.stop()

class DeployView(View):
    """Deploy to Firebase buttons"""
    def __init__(self):
        super().__init__()
        self.result = None

    @discord.ui.button(label="🚀 Deploy", style=discord.ButtonStyle.green)
    async def deploy_button(self, interaction: discord.Interaction, button: Button):
        self.result = "deploy"
        await interaction.response.defer()
        self.stop()

    @discord.ui.button(label="❌ Cancel", style=discord.ButtonStyle.red)
    async def cancel_button(self, interaction: discord.Interaction, button: Button):
        self.result = "cancel"
        await interaction.response.defer()
        self.stop()

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

        # Cost & Session Management
        self.cost_tracker = CostTracker(monthly_limit=50.0, daily_limit=10.0)
        self.session_manager = SessionManager()
        self.model_selector = ModelSelector()

        # API Client for preview generation
        self.anthropic_client = Anthropic(api_key=Config.ANTHROPIC_API_KEY)

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
        Manager workflow in #general:
        1. Check if greeting → respond directly
        2. If task → screen it (no API calls)
        3. Summarize → ask approval in #general
        4. Wait for yes/no → only then execute
        """
        user_input = message.content.strip()
        if not user_input or user_input.startswith("!"):
            return

        logger.info(f"Manager processing: {user_input}")

        # Step 1: Check for greeting
        if self.is_greeting(user_input):
            await message.channel.send("Hi piyush, what is the agenda today!")
            return

        await message.add_reaction("⏳")

        # Step 2: Screen task (keyword-based, no API)
        brand = self.detect_brand(user_input)
        task = self.compression.compress_message(user_input)

        if brand == "nacpac":
            task["task_type"] = "nacpac"
        elif brand == "jico":
            task["task_type"] = "jico"

        logger.info(f"Screened: {brand}/{task['target']} - {task['action']}")

        # Step 3: Build summary
        summary = f"I understood:\n• **Brand:** {brand.upper()}\n• **Target:** {task['target']}\n• **Action:** {task['action'][:80]}"

        await message.remove_reaction("⏳", self.bot.user)

        # Step 4: Wait for approval with buttons
        confirm_view = ConfirmationView()
        await message.channel.send(
            f"{summary}\n\n**Proceed with build?**",
            view=confirm_view
        )

        try:
            await asyncio.wait_for(confirm_view.wait(), timeout=300)
            if confirm_view.result == "no":
                await message.channel.send("❌ Build cancelled. What would you like instead?")
                return
        except asyncio.TimeoutError:
            await message.channel.send("⏱️ Approval timeout. Please resend your request.")
            return

        # Step 5: If Nacpac → ask what to build with buttons
        if brand == "nacpac":
            build_view = BuildTypeView()
            await message.channel.send(
                "**What to build?**",
                view=build_view
            )

            try:
                await asyncio.wait_for(build_view.wait(), timeout=300)
                task["build_type"] = build_view.result or "both"
            except asyncio.TimeoutError:
                await message.channel.send("⏱️ Build choice timeout.")
                return

        # Step 6: Generate HTML preview of changes (uses Haiku)
        await message.channel.send("📋 Generating UI preview with Haiku...")
        preview_html = await self._generate_preview(task, brand)

        if preview_html:
            # Post preview (split if too long for Discord)
            preview_msg = f"**Preview of changes:**\n```html\n{preview_html[:400]}\n```"
            await message.channel.send(preview_msg)
        else:
            await message.channel.send("⚠️ Preview generation skipped (cost limit or API issue). Proceeding with build...")

        # Step 7: Ask for deployment confirmation with buttons
        deploy_view = DeployView()
        await message.channel.send(
            "**Deploy to Firebase?**",
            view=deploy_view
        )

        try:
            await asyncio.wait_for(deploy_view.wait(), timeout=300)
            if deploy_view.result == "cancel":
                await message.channel.send("❌ Deployment cancelled.")
                return
        except asyncio.TimeoutError:
            await message.channel.send("⏱️ Deploy confirmation timeout.")
            return

        # Step 7: Approved → queue task
        await message.add_reaction("✅")
        task_id = await self.auto_executor.queue_task(task)

        brand_emoji = "📱" if brand == "nacpac" else "🎨"
        await message.channel.send(
            f"{brand_emoji} **{brand.upper()}** task queued\n"
            f"ID: `{task_id}`\n"
            f"Updates → #{brand}-dev"
        )

    def is_greeting(self, user_input: str) -> bool:
        """Check if message is a casual greeting"""
        greetings = ["hi", "hey", "hello", "yo", "sup", "what's up", "howdy", "greetings"]
        return user_input.lower().strip() in greetings

    async def _generate_preview(self, task: dict, brand: str) -> str:
        """Generate HTML preview using Haiku - shows actual UI mockup of changes"""
        action = task.get("action", "Unknown action")
        target = task.get("target", "Unknown target")
        build_type = task.get("build_type", "both")

        # Check cost before calling Haiku (estimated 300 tokens for HTML generation)
        if not self.cost_tracker.check_can_call("haiku", estimated_tokens=300):
            logger.warning("Cost limit exceeded - skipping HTML preview")
            return None

        try:
            loop = asyncio.get_event_loop()
            html = await loop.run_in_executor(None, self._call_haiku_for_preview, action, target)
            return html

        except Exception as e:
            logger.error(f"Failed to generate preview: {e}")
            return None

    def _call_haiku_for_preview(self, action: str, target: str) -> str:
        """Synchronous Haiku API call (runs in executor thread)"""
        try:
            prompt = f"""Generate a minimal HTML mockup (under 200 chars) showing the UI change for this task:

Task: {action}
Target: {target}

Return ONLY HTML code with the update preview. Make it visual and concise. Include styling in <style> tags."""

            response = self.anthropic_client.messages.create(
                model="claude-3-5-haiku-20241022",
                max_tokens=300,
                messages=[{"role": "user", "content": prompt}]
            )

            html = response.content[0].text if response.content else None

            # Log the API call for cost tracking
            input_tokens = len(prompt.split()) * 1.3  # Rough estimate
            output_tokens = len(html.split()) * 1.3 if html else 0
            self.cost_tracker.log_call("haiku", int(input_tokens), int(output_tokens))

            logger.info(f"Generated preview with Haiku ({int(input_tokens)} input, {int(output_tokens)} output tokens)")
            return html

        except Exception as e:
            logger.error(f"Haiku API call failed: {e}")
            return None

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
        - Build results → #nacpac-dev or #jico-dev (with download links)
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

        # Add result details with special formatting for builds
        if status == "success":
            if "builds" in result:
                builds = result.get("builds", [])
                result_msg += "\n**📥 DOWNLOADS:**\n"

                apk_url = None
                exe_url = None

                for build in builds:
                    if build.get("status") == "success":
                        build_type = build.get('type', '').upper()
                        url = build.get('url', '')

                        if build_type == "APK":
                            apk_url = url
                            result_msg += f"📱 **APK:** [{url}]({url})\n"
                        elif build_type == "EXE":
                            exe_url = url
                            result_msg += f"🖥️ **EXE:** [{url}]({url})\n"
                    else:
                        error = build.get('error', 'Unknown error')
                        result_msg += f"❌ {build.get('type', 'Build').upper()} failed: {error}\n"

                # Add summary if available
                if "summary" in result:
                    result_msg += f"\n📝 **Summary:** {result['summary'][:200]}\n"
            else:
                if "summary" in result:
                    result_msg += f"📝 {result['summary'][:200]}\n"
        elif status == "error":
            result_msg += f"\n❌ **Error:** {result.get('error', 'Unknown error')}\n"

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
