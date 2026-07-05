"""Discord bot for Jico agentic system - natural language conversation with manager agent."""

import discord
from discord.ext import commands
import logging
from datetime import datetime

from agentic.config import (
    DISCORD_TOKEN, DISCORD_GUILD_ID, ALLOWED_USER_ID,
    DISCORD_GENERAL_CHANNEL_ID, DISCORD_NACPAC_DEV_CHANNEL_ID,
    DISCORD_JICO_DEV_CHANNEL_ID, DISCORD_LOGS_CHANNEL_ID, DISCORD_REPORTS_CHANNEL_ID
)
from agentic.agents import orchestrator, nacpac_dev_agent, jico_life_dev_agent
from agentic.memory import memory

logger = logging.getLogger(__name__)

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    logger.info(f"✅ Bot logged in as {bot.user}")


@bot.event
async def on_message(message: discord.Message):
    """Listen to messages in #general and route to orchestrator."""
    if message.author == bot.user:
        await bot.process_commands(message)
        return

    if message.content.startswith("!"):
        await bot.process_commands(message)
        return

    if message.channel.id != DISCORD_GENERAL_CHANNEL_ID:
        await bot.process_commands(message)
        return

    if message.author.id != ALLOWED_USER_ID:
        return

    logger.info(f"Message from {message.author}: {message.content}")

    intent = orchestrator.parse_intent(message.content)
    logger.info(f"Parsed intent: {intent}")

    can_afford, reason = orchestrator.check_cost_gate()
    if not can_afford:
        await message.reply(f"❌ Cost gate: {reason}")
        return

    task_id = memory.create_task(
        intent.get("brand", "nacpac"),
        intent.get("task_type", "general"),
        message.content,
        created_by=str(message.author)
    )

    agent_name = orchestrator.route_to_agent(intent)

    view = TaskApprovalView(task_id, agent_name, intent, message)
    embed = discord.Embed(
        title="📋 Task Approval",
        description=f"**Message:** {message.content}\n**Agent:** {agent_name}",
        color=discord.Color.blue()
    )
    embed.add_field(name="Brand", value=intent.get("brand", "unknown"))
    embed.add_field(name="Task Type", value=intent.get("task_type", "unknown"))
    embed.set_footer(text="Parsed by manager agent")

    await message.reply(embed=embed, view=view)


class TaskApprovalView(discord.ui.View):
    """Approval buttons for tasks."""

    def __init__(self, task_id: str, agent_name: str, intent: dict, message: discord.Message):
        super().__init__(timeout=3600)
        self.task_id = task_id
        self.agent_name = agent_name
        self.intent = intent
        self.message = message

    @discord.ui.button(label="✅ Approve", style=discord.ButtonStyle.success)
    async def approve_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()

        logger.info(f"Task {self.task_id} approved by {interaction.user}")
        memory.update_task(self.task_id, "approved", "User approved task")
        await self.message.add_reaction("✅")

        result = await self.execute_task()

        if result.get("status") == "success":
            result_text = f"✅ **Task Completed**\n{result.get('message', 'Success')}"
            color = discord.Color.green()
        else:
            result_text = f"❌ **Task Failed**\n{result.get('message', 'Unknown error')}"
            color = discord.Color.red()

        logs_channel = bot.get_channel(DISCORD_LOGS_CHANNEL_ID)
        if logs_channel:
            embed = discord.Embed(
                title="📝 Task Log",
                description=result_text,
                color=color
            )
            embed.add_field(name="Task ID", value=self.task_id)
            embed.add_field(name="Agent", value=self.agent_name)
            embed.set_footer(text=f"Executed by: {interaction.user}")
            await logs_channel.send(embed=embed)

        reports_channel = bot.get_channel(DISCORD_REPORTS_CHANNEL_ID)
        if reports_channel:
            embed = discord.Embed(
                title="📊 Task Report",
                description=self.message.content,
                color=color
            )
            embed.add_field(name="Status", value="Completed" if result.get("status") == "success" else "Failed")
            embed.add_field(name="Agent", value=self.agent_name)
            await reports_channel.send(embed=embed)

        await interaction.followup.send(result_text)

    @discord.ui.button(label="❌ Reject", style=discord.ButtonStyle.danger)
    async def reject_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()

        logger.info(f"Task {self.task_id} rejected by {interaction.user}")
        memory.update_task(self.task_id, "rejected", "User rejected task")
        await self.message.add_reaction("❌")

        logs_channel = bot.get_channel(DISCORD_LOGS_CHANNEL_ID)
        if logs_channel:
            embed = discord.Embed(
                title="📝 Task Rejected",
                description=self.message.content,
                color=discord.Color.orange()
            )
            embed.add_field(name="Task ID", value=self.task_id)
            embed.set_footer(text=f"Rejected by: {interaction.user}")
            await logs_channel.send(embed=embed)

        await interaction.followup.send("❌ Task rejected and cancelled")

    async def execute_task(self) -> dict:
        """Execute the approved task."""
        agent_name = self.agent_name
        intent = self.intent
        task_type = intent.get("task_type", "unknown")

        try:
            logger.info(f"Executing {agent_name}::{task_type} for task {self.task_id}")

            if agent_name == "nacpac_dev":
                if task_type == "build":
                    build_target = intent.get("build_target", "apk")
                    if build_target == "apk":
                        result = nacpac_dev_agent.build_apk(self.task_id)
                    elif build_target == "exe":
                        result = nacpac_dev_agent.build_exe(self.task_id)
                    else:
                        result = {"status": "error", "message": f"Unknown build target: {build_target}"}
                elif task_type == "deploy":
                    result = nacpac_dev_agent.deploy_to_staging(self.task_id, "apk")
                else:
                    result = {"status": "error", "message": f"Unknown NacPac task type: {task_type}"}
            elif agent_name == "jico_life_dev":
                if task_type == "build":
                    result = jico_life_dev_agent.build_glb_model(self.task_id, "")
                elif task_type == "deploy":
                    result = jico_life_dev_agent.deploy_to_staging_branch(self.task_id)
                else:
                    result = {"status": "error", "message": f"Unknown Jico Life task type: {task_type}"}
            else:
                result = {"status": "error", "message": f"Unknown agent: {agent_name}"}

            logger.info(f"Task {self.task_id} result: {result.get('status', 'unknown')}")
            return result

        except Exception as e:
            error_msg = f"Task execution failed: {str(e)[:200]}"
            logger.error(error_msg, exc_info=True)
            memory.update_task(self.task_id, "failed", error_msg)
            return {"status": "error", "message": error_msg}


@bot.command(name="status")
async def status_command(ctx):
    """Show system status."""
    if ctx.author.id != ALLOWED_USER_ID:
        await ctx.send("❌ You don't have permission to use this command")
        return

    state_nacpac = memory.get_brand_state("nacpac")
    state_jico = memory.get_brand_state("jico_life")

    embed = discord.Embed(title="🤖 Agentic System Status", color=discord.Color.green())

    if state_nacpac:
        embed.add_field(
            name="NacPac",
            value=f"Branch: {state_nacpac.get('current_branch', 'unknown')}",
            inline=False
        )

    if state_jico:
        embed.add_field(
            name="Jico Life",
            value=f"Branch: {state_jico.get('current_branch', 'unknown')}",
            inline=False
        )

    embed.set_footer(text=f"Last updated: {datetime.utcnow().isoformat()}")
    await ctx.send(embed=embed)


@bot.command(name="help_agentic")
async def help_command(ctx):
    """Show help."""
    if ctx.author.id != ALLOWED_USER_ID:
        return

    embed = discord.Embed(title="📖 Agentic System Help", color=discord.Color.blue())
    embed.add_field(
        name="Natural Language Tasks",
        value="Type in #general. Manager agent will parse and ask for approval.",
        inline=False
    )
    embed.add_field(
        name="Examples",
        value="- 'Build the NacPac APK'\n- 'Deploy Jico Life to staging'",
        inline=False
    )
    embed.add_field(
        name="!status",
        value="Show current branch/deploy status",
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
