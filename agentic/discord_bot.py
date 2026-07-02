"""Discord bot for Jico agentic system."""

import discord
from discord.ext import commands
from discord import app_commands
import logging
from datetime import datetime

from config import (
    DISCORD_TOKEN, DISCORD_GUILD_ID, ALLOWED_USER_ID,
    DISCORD_NACPAC_BUILDS_CHANNEL_ID, DISCORD_NACPAC_DEPLOYS_CHANNEL_ID,
    DISCORD_JICO_BUILDS_CHANNEL_ID, DISCORD_JICO_DEPLOYS_CHANNEL_ID
)
from agents import orchestrator, nacpac_dev_agent, jico_life_dev_agent
from memory import memory

logger = logging.getLogger(__name__)

# Set up bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

def get_channel_id(brand: str, message_type: str) -> int:
    """Get Discord channel ID based on brand and message type.

    message_type: 'builds' or 'deploys'
    """
    if brand.lower() == "jico_life" or "jico" in brand.lower():
        if message_type == "builds":
            return DISCORD_JICO_BUILDS_CHANNEL_ID
        else:  # deploys
            return DISCORD_JICO_DEPLOYS_CHANNEL_ID
    else:  # nacpac
        if message_type == "builds":
            return DISCORD_NACPAC_BUILDS_CHANNEL_ID
        else:  # deploys
            return DISCORD_NACPAC_DEPLOYS_CHANNEL_ID


@bot.event
async def on_ready():
    logger.info(f"✅ Bot logged in as {bot.user}")
    try:
        synced = await bot.tree.sync()
        logger.info(f"Synced {len(synced)} command(s)")
    except Exception as e:
        logger.error(f"Failed to sync commands: {e}")


@bot.tree.command(name="task", description="Submit a task to the agentic system")
@app_commands.describe(brand="nacpac or jico_life", request="What should the agent do?")
async def task_command(interaction: discord.Interaction, brand: str, request: str):
    """Submit a task. Example: /task brand:nacpac request:Build APK for v2.1"""

    # Check permissions
    if interaction.user.id != ALLOWED_USER_ID:
        await interaction.response.send_message("❌ You don't have permission to use this command", ephemeral=True)
        return

    await interaction.response.defer()

    logger.info(f"Task submitted by {interaction.user}: brand={brand}, request={request}")

    # Create task in memory
    task_id = memory.create_task(brand, "general", request, created_by=str(interaction.user))

    # Parse intent
    intent = orchestrator.parse_intent(f"brand={brand}; {request}")

    # Check cost gate
    can_afford, reason = orchestrator.check_cost_gate()
    if not can_afford:
        await interaction.followup.send(f"❌ Cost gate: {reason}")
        memory.update_task(task_id, "failed", reason)
        return

    # Route to agent
    agent_name = orchestrator.route_to_agent(intent)

    # Get approval (show buttons)
    view = TaskApprovalView(task_id, agent_name, intent)
    embed = discord.Embed(
        title="⚠️ Task Approval Required",
        description=f"**Request:** {request}\n**Agent:** {agent_name}",
        color=discord.Color.yellow()
    )
    embed.add_field(name="Brand", value=brand)
    embed.add_field(name="Task Type", value=intent.get("task_type", "unknown"))

    await interaction.followup.send(embed=embed, view=view)


class TaskApprovalView(discord.ui.View):
    """Approval buttons for tasks."""

    def __init__(self, task_id: str, agent_name: str, intent: dict):
        super().__init__(timeout=3600)  # 1 hour timeout
        self.task_id = task_id
        self.agent_name = agent_name
        self.intent = intent

    @discord.ui.button(label="✅ Approve", style=discord.ButtonStyle.success)
    async def approve_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()

        logger.info(f"Task {self.task_id} approved by {interaction.user}")
        memory.update_task(self.task_id, "approved", "User approved task")

        # Route execution
        result = await self.execute_task()

        # Post result
        result_msg = f"✅ **Task Completed**\n{result.get('message', 'Success')}"
        if result.get("status") != "success":
            result_msg = f"❌ **Task Failed**\n{result.get('message', 'Unknown error')}"

        await interaction.followup.send(result_msg)

    @discord.ui.button(label="❌ Reject", style=discord.ButtonStyle.danger)
    async def reject_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()

        logger.info(f"Task {self.task_id} rejected by {interaction.user}")
        memory.update_task(self.task_id, "rejected", "User rejected task")

        await interaction.followup.send("❌ Task rejected")

    async def execute_task(self) -> dict:
        """Execute the approved task."""
        agent_name = self.agent_name
        intent = self.intent
        task_type = intent.get("task_type", "unknown")

        try:
            if agent_name == "nacpac_dev":
                if task_type == "build":
                    build_target = intent.get("build_target", "apk")
                    if build_target == "apk":
                        return nacpac_dev_agent.build_apk(self.task_id)
                    elif build_target == "exe":
                        return nacpac_dev_agent.build_exe(self.task_id)
                elif task_type == "deploy":
                    return nacpac_dev_agent.deploy_to_staging(self.task_id, "apk")

            elif agent_name == "jico_life_dev":
                if task_type == "build":
                    return jico_life_dev_agent.build_glb_model(self.task_id, intent.get("render_path", ""))
                elif task_type == "deploy":
                    return jico_life_dev_agent.deploy_to_staging_branch(self.task_id)

            return {"status": "unknown", "message": "Unknown task type"}
        except Exception as e:
            logger.error(f"Task execution failed: {e}", exc_info=True)
            return {"status": "error", "message": f"Error: {str(e)[:200]}"}


@bot.command(name="status")
async def status_command(ctx):
    """Show system status."""
    state_nacpac = memory.get_brand_state("nacpac")
    state_jico = memory.get_brand_state("jico_life")

    embed = discord.Embed(title="🤖 Agentic System Status", color=discord.Color.green())

    if state_nacpac:
        embed.add_field(
            name="NacPac",
            value=f"Branch: {state_nacpac.get('current_branch', 'unknown')}\nCommit: {state_nacpac.get('last_commit', 'unknown')[:8]}...",
            inline=False
        )

    if state_jico:
        embed.add_field(
            name="Jico Life",
            value=f"Branch: {state_jico.get('current_branch', 'unknown')}\nCommit: {state_jico.get('last_commit', 'unknown')[:8]}...",
            inline=False
        )

    embed.set_footer(text=f"Last updated: {datetime.utcnow().isoformat()}")
    await ctx.send(embed=embed)


@bot.command(name="help_agentic")
async def help_command(ctx):
    """Show help."""
    embed = discord.Embed(title="📖 Agentic System Help", color=discord.Color.blue())
    embed.add_field(
        name="/task",
        value="Submit a task: `/task brand:nacpac request:Build APK for v2.1`",
        inline=False
    )
    embed.add_field(
        name="!status",
        value="Show system status",
        inline=False
    )
    embed.add_field(
        name="Supported brands",
        value="- nacpac\n- jico_life",
        inline=False
    )
    await ctx.send(embed=embed)


async def main():
    """Start the bot."""
    logger.info("Starting Discord bot...")
    async with bot:
        await bot.start(DISCORD_TOKEN)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
