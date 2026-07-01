import logging
from datetime import datetime, timedelta
from typing import Dict, Any

logger = logging.getLogger(__name__)

class CostTracker:
    """Track API costs with hard limits to prevent overspending"""

    def __init__(self, monthly_limit: float = 50.0, daily_limit: float = 10.0):
        self.monthly_limit = monthly_limit  # $50/month hard cap
        self.daily_limit = daily_limit      # $10/day hard cap
        self.monthly_cost = 0.0
        self.daily_cost = 0.0
        self.daily_start = datetime.now()
        self.call_count = 0
        self.model_usage = {}  # Track usage per model

    def check_can_call(self, model: str = "haiku", estimated_tokens: int = 100) -> bool:
        """Check if we can afford to make an API call"""
        cost = self.estimate_cost(model, estimated_tokens)

        if self.monthly_cost + cost > self.monthly_limit:
            logger.warning(f"❌ MONTHLY LIMIT EXCEEDED: ${self.monthly_cost:.2f} + ${cost:.2f} > ${self.monthly_limit:.2f}")
            return False

        if self.daily_cost + cost > self.daily_limit:
            logger.warning(f"❌ DAILY LIMIT EXCEEDED: ${self.daily_cost:.2f} + ${cost:.2f} > ${self.daily_limit:.2f}")
            return False

        return True

    def log_call(self, model: str, input_tokens: int, output_tokens: int):
        """Log an API call and update costs"""
        cost = self.calculate_cost(model, input_tokens, output_tokens)
        self.monthly_cost += cost
        self.daily_cost += cost
        self.call_count += 1

        if model not in self.model_usage:
            self.model_usage[model] = {"calls": 0, "tokens": 0, "cost": 0}

        self.model_usage[model]["calls"] += 1
        self.model_usage[model]["tokens"] += input_tokens + output_tokens
        self.model_usage[model]["cost"] += cost

        logger.info(f"API call: {model} | Tokens: {input_tokens + output_tokens} | Cost: ${cost:.4f} | Monthly: ${self.monthly_cost:.2f}/{self.monthly_limit:.2f}")

    def estimate_cost(self, model: str, tokens: int) -> float:
        """Estimate cost of API call"""
        rates = {
            "haiku": 0.00008 / 1000,      # $0.80 per 1M input, using avg
            "sonnet": 0.003 / 1000,       # $3 per 1M input
            "opus": 0.015 / 1000          # $15 per 1M input
        }
        return tokens * rates.get(model, rates["haiku"])

    def calculate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Calculate actual cost (input and output rates differ)"""
        costs = {
            "haiku": {"input": 0.80, "output": 4.00},      # per 1M tokens
            "sonnet": {"input": 3.00, "output": 15.00},    # per 1M tokens
            "opus": {"input": 15.00, "output": 75.00}      # per 1M tokens
        }
        rate = costs.get(model, costs["haiku"])
        input_cost = (input_tokens / 1_000_000) * rate["input"]
        output_cost = (output_tokens / 1_000_000) * rate["output"]
        return input_cost + output_cost

    def get_status(self) -> Dict[str, Any]:
        """Get current cost status"""
        return {
            "monthly_used": f"${self.monthly_cost:.2f}",
            "monthly_limit": f"${self.monthly_limit:.2f}",
            "monthly_remaining": f"${self.monthly_limit - self.monthly_cost:.2f}",
            "daily_used": f"${self.daily_cost:.2f}",
            "daily_limit": f"${self.daily_limit:.2f}",
            "daily_remaining": f"${self.daily_limit - self.daily_cost:.2f}",
            "total_calls": self.call_count,
            "model_usage": self.model_usage
        }

    def reset_daily(self):
        """Reset daily counter at midnight"""
        now = datetime.now()
        if (now - self.daily_start).days > 0:
            self.daily_cost = 0.0
            self.daily_start = now
            logger.info("Daily cost counter reset")
