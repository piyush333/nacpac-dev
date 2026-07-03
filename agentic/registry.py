"""Agent Registry - dynamically discover and manage agents."""

import logging
import json
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class AgentRegistry:
    """Central registry for all agents in the system."""

    def __init__(self):
        self.agents: Dict[str, dict] = {}
        self.logger = logging.getLogger(__name__)

    def register(self, agent_name: str, agent_class, capabilities: List[str], version: str = "1.0.0"):
        """Register a new agent.

        Args:
            agent_name: Unique agent identifier (e.g., "nacpac_dev", "jico_life_dev")
            agent_class: The agent class/instance
            capabilities: List of actions this agent can perform (e.g., ["build_apk", "build_exe"])
            version: Agent version
        """
        self.agents[agent_name] = {
            "name": agent_name,
            "class": agent_class,
            "capabilities": capabilities,
            "version": version,
            "registered_at": datetime.now().isoformat(),
            "status": "active"
        }
        self.logger.info(f"✅ Registered agent: {agent_name} (v{version}) with capabilities: {capabilities}")

    def get_agent(self, agent_name: str) -> Optional[dict]:
        """Get agent by name."""
        return self.agents.get(agent_name)

    def find_agent_for_action(self, action: str) -> Optional[str]:
        """Find which agent can handle this action.

        Args:
            action: Action name (e.g., "build_apk", "build_exe")

        Returns:
            Agent name that can handle this action, or None
        """
        for agent_name, agent_info in self.agents.items():
            if action in agent_info.get("capabilities", []):
                return agent_name
        return None

    def list_agents(self) -> List[dict]:
        """List all registered agents."""
        return list(self.agents.values())

    def get_capabilities(self, agent_name: str) -> List[str]:
        """Get list of capabilities for an agent."""
        agent = self.get_agent(agent_name)
        return agent.get("capabilities", []) if agent else []

    def get_agent_class(self, agent_name: str):
        """Get the agent class/instance."""
        agent = self.get_agent(agent_name)
        return agent.get("class") if agent else None

    def deregister(self, agent_name: str):
        """Deregister an agent."""
        if agent_name in self.agents:
            del self.agents[agent_name]
            self.logger.info(f"Deregistered agent: {agent_name}")


registry = AgentRegistry()
