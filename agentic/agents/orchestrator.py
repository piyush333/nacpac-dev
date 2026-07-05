"""Orchestrator Agent - routes tasks to dev agents, manages memory, enforces cost gates."""

import logging
import json
from anthropic import Anthropic

from agentic.config import HAIKU_MODEL, SONNET_MODEL
from agentic.cost_tracker import cost_tracker
from agentic.memory import memory

logger = logging.getLogger(__name__)


class OrchestratorAgent:
    """Main orchestrator: intent parsing, routing, cost gating."""

    def __init__(self):
        try:
            self.client = Anthropic()
        except Exception as e:
            logger.warning(f"Failed to init Anthropic client: {e}")
            self.client = None
        self.model = HAIKU_MODEL  # Use cheap model for orchestration
        self.max_tokens = 1024

    def parse_intent(self, user_message: str) -> dict:
        """Parse natural language to extract: brand, task_type, details.

        Returns: {"brand": "nacpac"|"jico_life", "task_type": "code"|"build"|"deploy", ...}
        """
        logger.info(f"Parsing intent: {user_message[:100]}")

        system_prompt = """You are an intent parser for a CI/CD orchestration system.

Given a user request, extract:
1. brand: "nacpac" or "jico_life"
2. task_type: "code" (feature/fix), "build" (APK/EXE/GLB), or "deploy" (to staging or production)
3. details: brief description of what to do

Respond ONLY with valid JSON, no other text.

Example: User says "Build the nacpac APK for v2.1"
Response: {"brand": "nacpac", "task_type": "build", "build_target": "apk", "details": "Build APK for v2.1"}"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_message}
                ]
            )

            # Log tokens
            cost_tracker.log_call(
                "orchestrator",
                self.model,
                response.usage.input_tokens,
                response.usage.output_tokens
            )

            intent_text = response.content[0].text
            logger.info(f"Intent parsed: {intent_text}")

            # Try to parse as JSON
            intent = json.loads(intent_text)
            return intent
        except Exception as e:
            logger.error(f"Intent parsing failed: {e}")
            # Fallback: assume nacpac build
            return {
                "brand": "nacpac",
                "task_type": "build",
                "details": user_message,
                "error": str(e)
            }

    def check_cost_gate(self, tokens_estimate: int = 5000) -> tuple[bool, str]:
        """Check if we can afford this operation."""
        can_afford, reason = cost_tracker.can_afford_call(tokens_estimate, self.model)

        if not can_afford:
            logger.warning(f"Cost gate blocked: {reason}")
            return False, reason

        return True, ""

    def route_to_agent(self, intent: dict) -> str:
        """Route to appropriate agent based on intent.

        Returns: agent name ("nacpac_dev" or "jico_life_dev")
        """
        brand = intent.get("brand", "nacpac").lower()

        if "jico" in brand:
            return "jico_life_dev"
        else:
            return "nacpac_dev"

    def format_response(self, result: dict) -> str:
        """Format agent result into natural language."""
        if result.get("status") == "success":
            return f"✅ {result.get('message', 'Task completed successfully')}"
        else:
            return f"❌ {result.get('message', 'Task failed')}"


orchestrator = OrchestratorAgent()
