"""Generic Agent Engine."""

from pydantic import BaseModel
from typing import List, Optional
import os
from anthropic import Anthropic
from tool_registry import ToolRegistry
import tools  # Import tools to trigger registration


class AgentConfig(BaseModel):
    """Agent configuration."""
    name: str
    system_prompt: str
    tools: List[str]  # Tool names from registry
    memory_namespace: str
    model: str = "claude-opus-4-8"


class Agent:
    """Generic agent that uses configured tools."""

    def __init__(self, config: AgentConfig):
        self.config = config
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.model = config.model
        self.tools = config.tools
        self.system_prompt = config.system_prompt

    def get_claude_tools(self) -> list:
        """Get tools in Claude API format."""
        all_tools = ToolRegistry.get_tools_for_claude()
        return [t for t in all_tools if t["name"] in self.tools]

    def execute(self, user_input: str, context: dict = None) -> dict:
        """
        Execute agent with tool use.

        1. Send request to Claude with tools
        2. Claude decides which tools to use
        3. Execute tools
        4. Send results back to Claude
        5. Return final response
        """
        messages = [
            {"role": "user", "content": user_input}
        ]

        context_str = ""
        if context:
            context_str = f"\n\nContext:\n{context}"

        # System prompt with context
        full_system_prompt = self.system_prompt + context_str

        # Get tools
        tools = self.get_claude_tools()

        if not tools:
            return {
                "success": False,
                "error": "No tools available for this agent",
                "response": "Agent is not configured with any tools"
            }

        # Initial request to Claude
        response = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            system=full_system_prompt,
            tools=tools,
            messages=messages
        )

        # Handle tool use
        while response.stop_reason == "tool_use":
            # Find tool use blocks
            tool_calls = [block for block in response.content if block.type == "tool_use"]
            tool_results = []

            for tool_call in tool_calls:
                tool_name = tool_call.name
                tool_input = tool_call.input

                # Execute tool
                result = ToolRegistry.call_tool(tool_name, **tool_input)

                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tool_call.id,
                    "content": str(result)
                })

            # Add assistant response and tool results to messages
            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user", "content": tool_results})

            # Get next response
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                system=full_system_prompt,
                tools=tools,
                messages=messages
            )

        # Extract final text response
        final_text = ""
        for block in response.content:
            if hasattr(block, "text"):
                final_text += block.text

        # Count tokens (approximation)
        tokens_used = response.usage.input_tokens + response.usage.output_tokens

        return {
            "success": True,
            "response": final_text,
            "tokens_used": tokens_used,
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens
        }


def create_developer_agent() -> Agent:
    """Create the Developer Agent."""
    config = AgentConfig(
        name="developer",
        system_prompt="""You are a Developer Assistant. You help with:
- Cloning and managing GitHub repositories
- Reading and writing code files
- Running terminal commands (npm, git, python, etc)
- Reading and understanding documentation
- Sending emails about development work

Always be cautious with destructive commands.
Explain what you're doing before executing commands.
If a tool call fails, try an alternative approach.""",
        tools=[
            "github.clone",
            "github.commit_and_push",
            "filesystem.read",
            "filesystem.write",
            "filesystem.list",
            "terminal.run",
            "documentation.read",
            "documentation.summarize",
            "email.send"
        ],
        memory_namespace="developer",
        model="claude-opus-4-8"
    )
    return Agent(config)
