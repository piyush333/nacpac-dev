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
        _ensure_agents_loaded()
        agent = self.get_agent(agent_name)
        return agent.get("class") if agent else None

    def deregister(self, agent_name: str):
        """Deregister an agent."""
        if agent_name in self.agents:
            del self.agents[agent_name]
            self.logger.info(f"Deregistered agent: {agent_name}")


registry = AgentRegistry()


# Lazy-load agents on first access
_agents_loaded = False

def _ensure_agents_loaded():
    """Lazy-load and register agents on first access."""
    global _agents_loaded
    if _agents_loaded:
        return
    _agents_loaded = True

    try:
        from agents.nacpac_dev import nacpac_dev_agent
        from agents.jico_life_dev import jico_life_dev_agent

        registry.register(
            "nacpac_dev",
            nacpac_dev_agent,
            capabilities=["build_apk", "build_exe", "deploy_staging", "run_tests", "get_state"],
            version="1.0.0"
        )

        registry.register(
            "jico_life_dev",
            jico_life_dev_agent,
            capabilities=["build_glb", "deploy_staging", "deploy_production", "get_state"],
            version="1.0.0"
        )

        logger.info(f"✅ Auto-registered {len(registry.list_agents())} agents")
    except Exception as e:
        logger.warning(f"⚠️  Failed to auto-register agents: {e}")


# Wrap list_agents to ensure agents are loaded
_original_list_agents = registry.list_agents
def list_agents_with_lazy_load():
    _ensure_agents_loaded()
    return _original_list_agents()

registry.list_agents = list_agents_with_lazy_load
