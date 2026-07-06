"""Agents package - with lazy imports to handle old code versions."""

import logging

logger = logging.getLogger(__name__)

# Lazy imports to avoid __init__.py issues
def __getattr__(name):
    """Dynamically import agents when accessed."""
    if name == "orchestrator":
        from agentic.agents.orchestrator import orchestrator
        return orchestrator
    elif name == "nacpac_dev_agent":
        from agentic.agents.nacpac_dev import nacpac_dev_agent
        return nacpac_dev_agent
    elif name == "jico_life_dev_agent":
        from agentic.agents.jico_life_dev import jico_life_dev_agent
        return jico_life_dev_agent
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = ["orchestrator", "nacpac_dev_agent", "jico_life_dev_agent"]
