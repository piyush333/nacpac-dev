# How to Build an MCP Server — Phase 2+ Integration Guide

This guide helps you build MCP (Model Context Protocol) servers that integrate with the Jico Agentic System.

MCP servers provide external capabilities (Amazon Ads, Google Ads, Shopify, GitHub, etc.) that agents can use as tools.

---

## What is an MCP Server?

MCP is Anthropic's standard for connecting Claude to external tools and APIs. Instead of hardcoding API calls in agents, you:
1. Create an MCP server that wraps your external API
2. Register it with Claude
3. Claude can discover and use the tools automatically

---

## Quick Start

1. **Install MCP CLI**: `pip install mcp`
2. **Create server file**: `agentic/mcp_servers/my_service.py`
3. **Implement tools** (see template below)
4. **Register in main.py**
5. **Test with CLI**: `python cli.py mcp-test amazon_ads`

---

## MCP Server Template

Save this as `agentic/mcp_servers/amazon_ads.py`:

```python
"""Amazon Ads MCP Server."""

import json
import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


class AmazonAdsMCP:
    """MCP server for Amazon Ads API."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://advertising-api.amazon.com"
        logger.info("✅ Amazon Ads MCP server initialized")

    def list_campaigns(self) -> Dict[str, Any]:
        """List all active campaigns.

        Returns:
            {
                "status": "success",
                "campaigns": [
                    {"id": "...", "name": "...", "budget": 100}
                ]
            }
        """
        logger.info("Fetching campaigns from Amazon Ads")
        try:
            # Call Amazon Ads API here
            # This is a stub - replace with actual API call

            return {
                "status": "success",
                "campaigns": [
                    {"id": "camp_1", "name": "Q3 Campaign", "budget": 500}
                ]
            }
        except Exception as e:
            logger.error(f"Failed to list campaigns: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    def create_campaign(self, name: str, budget: float) -> Dict[str, Any]:
        """Create a new campaign.

        Args:
            name: Campaign name
            budget: Budget in USD

        Returns:
            {
                "status": "success",
                "campaign_id": "new_camp_id"
            }
        """
        logger.info(f"Creating campaign: {name} (budget: ${budget})")
        try:
            # Call Amazon Ads API
            campaign_id = "camp_new_123"

            return {
                "status": "success",
                "campaign_id": campaign_id,
                "message": f"Campaign '{name}' created"
            }
        except Exception as e:
            logger.error(f"Failed to create campaign: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    def get_campaign_metrics(self, campaign_id: str) -> Dict[str, Any]:
        """Get metrics for a campaign.

        Returns:
            {
                "status": "success",
                "metrics": {
                    "impressions": 1000,
                    "clicks": 50,
                    "spend": 125.50,
                    "ctr": 5.0
                }
            }
        """
        logger.info(f"Fetching metrics for campaign: {campaign_id}")
        try:
            # Call Amazon Ads API
            return {
                "status": "success",
                "metrics": {
                    "impressions": 5000,
                    "clicks": 250,
                    "spend": 500,
                    "ctr": 5.0,
                    "cpc": 2.00
                }
            }
        except Exception as e:
            logger.error(f"Failed to get metrics: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    def get_tools(self) -> list:
        """Return list of tools this MCP server provides."""
        return [
            {
                "name": "list_campaigns",
                "description": "List all Amazon Ads campaigns",
                "parameters": {}
            },
            {
                "name": "create_campaign",
                "description": "Create a new campaign",
                "parameters": {
                    "name": "str (campaign name)",
                    "budget": "float (budget in USD)"
                }
            },
            {
                "name": "get_campaign_metrics",
                "description": "Get performance metrics for a campaign",
                "parameters": {
                    "campaign_id": "str (campaign ID)"
                }
            }
        ]


amazon_ads_mcp = AmazonAdsMCP(api_key="your_api_key_here")
```

---

## How Agents Use MCP Servers

In an agent:

```python
from mcp_servers.amazon_ads import amazon_ads_mcp

class MarketingAgent:
    def analyze_campaign(self, campaign_name: str) -> dict:
        """Use MCP server to analyze campaign."""

        # Get campaigns
        campaigns_result = amazon_ads_mcp.list_campaigns()

        if campaigns_result["status"] != "success":
            return {"status": "error", "error": "Failed to fetch campaigns"}

        campaigns = campaigns_result["campaigns"]

        # Find campaign by name
        target_campaign = next(
            (c for c in campaigns if c["name"] == campaign_name),
            None
        )

        if not target_campaign:
            return {"status": "error", "error": f"Campaign not found: {campaign_name}"}

        # Get metrics
        metrics_result = amazon_ads_mcp.get_campaign_metrics(target_campaign["id"])

        return {
            "status": "success",
            "campaign": target_campaign,
            "metrics": metrics_result.get("metrics", {})
        }
```

---

## Registration Process

### 1. Create your MCP server (as shown above)

### 2. Register in `agentic/main.py`:

```python
from mcp_servers.amazon_ads import amazon_ads_mcp
from registry import registry

# Register MCP server as "tool" that agents can use
registry.register(
    agent_name="amazon_ads_mcp",
    agent_class=amazon_ads_mcp,
    capabilities=["list_campaigns", "create_campaign", "get_campaign_metrics"],
    version="1.0.0"
)
```

### 3. Update orchestrator to route to MCP servers:

```python
def route_to_agent(self, intent: dict) -> str:
    task_type = intent.get("task_type", "").lower()

    if "ads" in task_type:
        return "amazon_ads_mcp"
    # ... other routes ...
```

---

## Testing Your MCP Server

### Via CLI:

```bash
python cli.py mcp-test amazon_ads list_campaigns
python cli.py mcp-test amazon_ads create_campaign "Q4 Campaign" 1000
```

### Via Python:

```python
from mcp_servers.amazon_ads import amazon_ads_mcp

# Test list_campaigns
result = amazon_ads_mcp.list_campaigns()
print(result)

# Test create_campaign
result = amazon_ads_mcp.create_campaign("Q4 Campaign", 1000)
print(result)
```

---

## MCP Server Capabilities

| Server | Capabilities | Status |
|--------|--------------|--------|
| Amazon Ads | list_campaigns, create_campaign, get_metrics | 🚧 Phase 2 |
| Google Ads | list_campaigns, create_campaign, get_metrics | 🚧 Phase 2 |
| GitHub | list_repos, create_pr, merge_pr, get_commits | 🚧 Phase 2 |
| Shopify | list_products, add_ar_to_product, get_analytics | 🚧 Phase 3 |
| Slack | post_message, create_thread, react_to_message | 🚧 Phase 2 |

---

## Integration Checklist

When building an MCP server:

- [ ] MCP class created with clear method names
- [ ] `__init__()` method with API credentials
- [ ] All methods return `{"status": "success"/"error", ...}`
- [ ] `get_tools()` returns list of available tools
- [ ] Error handling for API failures
- [ ] Logging added
- [ ] Registered in `main.py`
- [ ] Orchestrator routing updated
- [ ] CLI tests passing
- [ ] Docstrings added
- [ ] Committed to `claude/agentic-system-org-j9gvae`

---

## Best Practices

1. **Error Handling**: Always catch exceptions and return `{"status": "error", "error": "..."}`
2. **Logging**: Log all API calls for debugging
3. **Timeouts**: Set reasonable timeouts for API calls
4. **Rate Limiting**: Implement rate limiting if needed
5. **Credentials**: Use environment variables, never hardcode API keys
6. **Caching**: Cache results when appropriate to save API calls
7. **Documentation**: Document all parameters and return values

---

## Example: Real Amazon Ads Integration

```python
import requests

class AmazonAdsMCP:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def list_campaigns(self):
        try:
            response = requests.get(
                "https://advertising-api.amazon.com/v2/campaigns",
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()

            return {
                "status": "success",
                "campaigns": response.json().get("campaigns", [])
            }
        except requests.exceptions.RequestException as e:
            return {
                "status": "error",
                "error": f"API call failed: {str(e)}"
            }
```

---

## Next Steps

1. Build your MCP server (follow template above)
2. Register in `main.py`
3. Update orchestrator routing
4. Test via CLI
5. Create PR with tests
6. Merge to main

Questions? Check `agentic/mcp_servers/` for examples.
