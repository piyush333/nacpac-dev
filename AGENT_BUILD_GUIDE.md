# How to Build a New Agent — Phase 1 Extension Guide

This guide helps you build new agents that integrate seamlessly with the Jico Agentic System.

## Quick Start

1. **Create agent file**: `agentic/agents/my_agent.py`
2. **Implement standard interface** (see template below)
3. **Register with orchestrator**: Add to `agentic/main.py`
4. **Test via CLI**: `python cli.py build my_brand my_action`
5. **Commit and deploy**

---

## Agent Interface Standard

Every agent must implement this interface:

```python
class MyAgent:
    """My custom agent."""

    def __init__(self):
        self.brand = "my_brand"  # Unique brand identifier
        self.model = SONNET_MODEL  # Claude model to use

    def get_current_state(self) -> dict:
        """Return current state (branch, commit, status, etc.)"""
        return {
            "status": "active",
            "version": "1.0.0"
        }

    def execute(self, action: str, params: dict) -> dict:
        """Execute an action. Route to specific methods below."""
        if action == "build":
            return self.build(**params)
        elif action == "deploy":
            return self.deploy(**params)
        else:
            return {"status": "error", "error": f"Unknown action: {action}"}

    def build(self, **params) -> dict:
        """Build artifact.

        Returns:
            {
                "status": "success" | "error",
                "link": "download_url" (if success),
                "error": "error_message" (if failed)
            }
        """
        # Your implementation
        pass

    def deploy(self, **params) -> dict:
        """Deploy artifact.

        Returns:
            {
                "status": "success" | "error",
                "deployed_at": "timestamp",
                "error": "error_message" (if failed)
            }
        """
        # Your implementation
        pass
```

---

## Complete Agent Template

Save this as `agentic/agents/my_agent.py`:

```python
"""My custom agent."""

import logging
from anthropic import Anthropic
from config import SONNET_MODEL
from cost_tracker import cost_tracker
from registry import registry

logger = logging.getLogger(__name__)


class MyAgent:
    """Custom agent for my_brand."""

    def __init__(self):
        self.brand = "my_brand"
        self.client = Anthropic()
        self.model = SONNET_MODEL
        logger.info(f"✅ {self.__class__.__name__} initialized")

    def get_current_state(self) -> dict:
        """Get current state."""
        return {
            "brand": self.brand,
            "status": "active",
            "version": "1.0.0"
        }

    def execute(self, action: str, params: dict) -> dict:
        """Route action to specific method."""
        if action == "my_action":
            return self.my_action(**params)
        else:
            return {
                "status": "error",
                "error": f"Unknown action: {action}"
            }

    def my_action(self, **params) -> dict:
        """Perform my custom action."""
        logger.info(f"Executing my_action with params: {params}")

        try:
            # Your logic here
            result = "Success"

            # Log tokens if using Claude
            # cost_tracker.log_call("my_agent", self.model, tokens_in, tokens_out)

            return {
                "status": "success",
                "result": result,
                "agent": self.brand
            }

        except Exception as e:
            logger.error(f"❌ my_action failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "agent": self.brand
            }


# Instantiate
my_agent = MyAgent()
```

---

## Registration Process

### 1. Import your agent in `agentic/main.py`:

```python
from agents.my_agent import my_agent
```

### 2. Register in the registry:

```python
registry.register(
    agent_name="my_agent",
    agent_class=my_agent,
    capabilities=["my_action", "other_action"],
    version="1.0.0"
)
```

### 3. Update orchestrator routing in `agentic/agents/orchestrator.py`:

```python
def route_to_agent(self, intent: dict) -> str:
    brand = intent.get("brand", "").lower()

    if "my_brand" in brand:
        return "my_agent"
    # ... other routes ...
```

---

## Testing Your Agent

### Via CLI:

```bash
# Test basic execution
python cli.py build my_brand my_action

# Test with parameters
python cli.py build my_brand my_action "param1=value1"
```

### Via Python:

```python
from agents.my_agent import my_agent
from registry import registry

# Register
registry.register("my_agent", my_agent, ["my_action"], "1.0.0")

# Execute
result = my_agent.execute("my_action", {"param": "value"})
print(result)
```

---

## Agent Capabilities Matrix

| Agent | Brand | Capabilities | Status |
|-------|-------|--------------|--------|
| NacPac Dev | nacpac | build_apk, build_exe, deploy | ✅ Active |
| Jico Life Dev | jico_life | build_ar, deploy | ✅ Active |
| Amazon Ads (Phase 2) | amazon | create_campaign, set_budget, get_metrics | 🚧 Planned |
| GitHub (Phase 2) | github | create_pr, merge_pr, get_commits | 🚧 Planned |
| Shopify (Phase 3) | shopify | add_product, update_product, sync_ar | 🚧 Planned |

---

## Integration Checklist

When building a new agent:

- [ ] Agent class created with standard interface
- [ ] `__init__()` method implemented
- [ ] `get_current_state()` method implemented
- [ ] `execute()` method routes to actions
- [ ] All action methods return dict with `status` key
- [ ] Logging added with logger
- [ ] Agent registered in `main.py`
- [ ] Orchestrator routing updated
- [ ] CLI tests passing
- [ ] Docstrings added
- [ ] Committed to `claude/agentic-system-org-j9gvae` branch

---

## Error Handling

All agents should return consistent error responses:

```python
{
    "status": "error",
    "error": "Human-readable error message",
    "agent": "agent_name",
    "details": {...}  # Optional additional context
}
```

---

## Token Tracking

If your agent uses Claude API:

```python
from cost_tracker import cost_tracker

response = self.client.messages.create(...)

cost_tracker.log_call(
    "my_agent",
    self.model,
    response.usage.input_tokens,
    response.usage.output_tokens
)
```

---

## Next Steps

1. Create your agent file
2. Implement the standard interface
3. Register in `main.py`
4. Test via CLI
5. Create PR with tests
6. Get review and merge

Questions? Check `agentic/agents/nacpac_dev.py` or `jico_life_dev.py` for real examples.
