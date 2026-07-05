"""Agent registry for dynamic discovery."""

import logging
from typing import Optional, List

logger = logging.getLogger(__name__)


class AgentRegistry:
    """Manage agent discovery and lifecycle."""

    def __init__(self):
        self.agents = {}
        self._ensure_agents_loaded()

    def _ensure_agents_loaded(self):
        """Load all agents."""
        try:
            from agentic.agents import nacpac_dev_agent, jico_life_dev_agent

            self.agents = {
                "nacpac_dev": {
                    "name": "NacPac Dev Agent",
                    "version": "1.0.0",
                    "capabilities": ["build_apk", "build_exe", "deploy"],
                    "status": "ready",
                    "instance": nacpac_dev_agent
                },
                "jico_life_dev": {
                    "name": "Jico Life Dev Agent",
                    "version": "1.0.0",
                    "capabilities": ["build_glb", "deploy"],
                    "status": "ready",
                    "instance": jico_life_dev_agent
                },
            }
            logger.info(f"✅ Loaded {len(self.agents)} agents")
        except Exception as e:
            logger.error(f"Failed to load agents: {e}")

    def get_agent_class(self, agent_name: str) -> Optional[object]:
        """Get agent instance by name."""
        agent = self.agents.get(agent_name)
        return agent["instance"] if agent else None

    def list_agents(self) -> List[dict]:
        """List all registered agents."""
        return [
            {"name": k, **v} for k, v in self.agents.items()
        ]


registry = AgentRegistry()
