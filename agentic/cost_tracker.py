"""Cost tracking and budget enforcement."""

import logging
from datetime import datetime
from config import DAILY_CAP_USD, MONTHLY_CAP_USD, HAIKU_MODEL, SONNET_MODEL
from memory import memory

logger = logging.getLogger(__name__)

# Token pricing (as of 2026-07)
PRICING = {
    "claude-3-5-haiku-20241022": {
        "input": 0.80 / 1_000_000,      # $0.80 per 1M input tokens
        "output": 4.00 / 1_000_000,     # $4.00 per 1M output tokens
    },
    "claude-3-5-sonnet-20241022": {
        "input": 3.0 / 1_000_000,       # $3.00 per 1M input tokens
        "output": 15.0 / 1_000_000,     # $15.00 per 1M output tokens
    },
}


class CostTracker:
    """Track and enforce API costs."""

    def calculate_cost(self, model: str, tokens_in: int, tokens_out: int) -> float:
        """Calculate cost for a model call."""
        if model not in PRICING:
            logger.warning(f"Unknown model {model}; assuming $0")
            return 0.0

        prices = PRICING[model]
        cost = (tokens_in * prices["input"]) + (tokens_out * prices["output"])
        return round(cost, 6)

    def can_afford_call(self, tokens_estimate: int = 5000, model: str = HAIKU_MODEL) -> tuple[bool, str]:
        """Check if we can afford a model call given current budget.

        Returns: (can_call: bool, reason: str)
        """
        # Estimate cost (assume 40% input, 60% output tokens)
        estimated_tokens_in = int(tokens_estimate * 0.4)
        estimated_tokens_out = int(tokens_estimate * 0.6)
        estimated_cost = self.calculate_cost(model, estimated_tokens_in, estimated_tokens_out)

        daily_cost = memory.get_daily_cost_usd()
        monthly_cost = memory.get_monthly_cost_usd()

        if daily_cost + estimated_cost > DAILY_CAP_USD:
            return False, f"Daily cap exceeded: ${daily_cost:.2f} + ${estimated_cost:.2f} > ${DAILY_CAP_USD:.2f}"

        if monthly_cost + estimated_cost > MONTHLY_CAP_USD:
            return False, f"Monthly cap exceeded: ${monthly_cost:.2f} + ${estimated_cost:.2f} > ${MONTHLY_CAP_USD:.2f}"

        if daily_cost + estimated_cost > DAILY_CAP_USD * 0.8:
            logger.warning(f"Daily cost at 80%: ${daily_cost + estimated_cost:.2f} / ${DAILY_CAP_USD:.2f}")

        return True, ""

    def log_call(self, agent: str, model: str, tokens_in: int, tokens_out: int):
        """Log a completed model call."""
        cost = self.calculate_cost(model, tokens_in, tokens_out)
        memory.log_cost(agent, model, tokens_in + tokens_out, cost)
        logger.info(f"{agent} used {model}: {tokens_in}+{tokens_out} tokens (${cost:.4f})")


# Global instance
cost_tracker = CostTracker()


def log_api_call(agent: str, model: str, tokens_in: int, tokens_out: int):
    """Helper function to log API call."""
    cost_tracker.log_call(agent, model, tokens_in, tokens_out)
