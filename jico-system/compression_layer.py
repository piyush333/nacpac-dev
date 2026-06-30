import json
import logging
from anthropic import Anthropic
from config import Config

logger = logging.getLogger(__name__)

class CompressionLayer:
    def __init__(self):
        self.client = Anthropic(api_key=Config.ANTHROPIC_API_KEY)
        self.model = "claude-3-5-haiku-20241022"

    def compress_message(self, user_message: str) -> dict:
        """Convert natural language message to optimized task JSON using Claude Haiku"""
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                system="""You are a task compression engine. Convert user messages into structured JSON tasks.

Output JSON with these fields:
{
  "task_type": "nacpac|jico|schedule",
  "action": "string describing the action",
  "target": "dev|seo|ads|build",
  "parameters": {"key": "value"},
  "priority": "high|normal|low",
  "schedule_time": "ISO8601 or null for immediate"
}

Be concise. Extract only essential data.""",
                messages=[
                    {"role": "user", "content": user_message}
                ]
            )

            content = response.content[0].text
            # Try to extract JSON from response
            try:
                task_json = json.loads(content)
            except json.JSONDecodeError:
                # If response isn't pure JSON, create a default task
                task_json = {
                    "task_type": "jico",
                    "action": user_message,
                    "target": "dev",
                    "parameters": {},
                    "priority": "normal",
                    "schedule_time": None
                }

            logger.info(f"Compressed message: {task_json}")
            return task_json

        except Exception as e:
            logger.error(f"Compression error: {e}")
            return {
                "task_type": "jico",
                "action": user_message,
                "target": "dev",
                "parameters": {},
                "priority": "normal",
                "schedule_time": None,
                "error": str(e)
            }

    def decompress_results(self, results: dict, user_id: int) -> str:
        """Convert task results to a human-readable message for Discord"""
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=512,
                system="Convert task results to a concise Discord message (2-3 sentences max). Include status, key findings, and any actions taken.",
                messages=[
                    {"role": "user", "content": f"Convert to message:\n{json.dumps(results)}"}
                ]
            )

            message = response.content[0].text
            logger.info(f"Decompressed results: {message}")
            return message

        except Exception as e:
            logger.error(f"Decompression error: {e}")
            return f"Task completed with results. Check logs for details."
