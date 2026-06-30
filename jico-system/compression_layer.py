import logging
import json
from typing import Dict, Any
from anthropic import Anthropic
from config import Config

logger = logging.getLogger(__name__)

class CompressionLayer:
    """Optimized: Keyword-first, Claude-fallback only for ambiguous cases"""

    def __init__(self):
        self.client = Anthropic(api_key=Config.ANTHROPIC_API_KEY)
        self.model = "claude-3-5-haiku-20241022"

    def compress_message(self, user_message: str) -> dict:
        """
        Convert natural language to task JSON.

        OPTIMIZATION: Uses keyword matching first (FREE).
        Only calls Claude for truly ambiguous inputs (RARE).
        """
        try:
            # Step 1: Try keyword-based classification (FREE)
            task = self._classify_by_keywords(user_message)

            if task:
                logger.info(f"Classified via keywords (NO API CALL): {task['task_type']}")
                return task

            # Step 2: Only call Claude if classification was ambiguous (RARE)
            logger.info("Ambiguous input - calling Claude for classification")
            task = self._classify_with_claude(user_message)
            return task

        except Exception as e:
            logger.error(f"Compression error: {e}")
            return self._default_task(user_message)

    def _classify_by_keywords(self, user_input: str) -> Dict[str, Any]:
        """Keyword-based classification (ZERO API calls)"""
        user_lower = user_input.lower()

        # Detect brand
        nacpac_score = sum(1 for kw in [
            "mobile", "desktop", "apk", "exe", "expo", "electron",
            "home screen", "ui", "button", "build", "sticker", "wallpaper",
            "react native", "typescript", "firebase", "screen", "feature",
            "ios", "android", "app", "code", "dark mode", "logout"
        ] if kw in user_lower)

        jico_score = sum(1 for kw in [
            "ar", "panel", "shopify", "3d", "model", "asset", "netlify",
            "glb", "wall", "render", "variant", "color", "acoustic",
            "web", "html", "css", "javascript"
        ] if kw in user_lower)

        # Only classify if confident (2+ keyword matches)
        if nacpac_score >= 2:
            brand = "nacpac"
        elif jico_score >= 2:
            brand = "jico"
        else:
            return None  # Ambiguous - need Claude

        # Detect action type (fast pattern matching)
        action_type = "build" if any(w in user_lower for w in ["build", "compile", "apk", "exe"]) else "dev"

        # Check for scheduling
        schedule_time = None
        if any(w in user_lower for w in ["tomorrow", "next week", "schedule", "at ", "tomorrow at"]):
            schedule_time = self._extract_schedule_time(user_input)

        return {
            "task_type": brand,
            "action": user_input,
            "target": action_type,
            "parameters": {},
            "priority": "high" if "urgent" in user_lower or "asap" in user_lower else "normal",
            "schedule_time": schedule_time,
            "classification_method": "keywords"
        }

    def _classify_with_claude(self, user_message: str) -> Dict[str, Any]:
        """
        Fall back to Claude only for ambiguous cases.
        Used rarely to keep API calls minimal.
        """
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=200,  # Minimal tokens
                system="Classify task concisely. Return JSON only.\n{\"task_type\":\"nacpac|jico\",\"action\":\"...\",\"target\":\"dev|build\",\"priority\":\"high|normal\"}",
                messages=[{"role": "user", "content": user_message}]
            )

            content = response.content[0].text
            try:
                task = json.loads(content)
                task["classification_method"] = "claude"
                return task
            except:
                return self._default_task(user_message)

        except Exception as e:
            logger.error(f"Claude classification failed: {e}")
            return self._default_task(user_message)

    def _extract_schedule_time(self, text: str) -> str:
        """Extract schedule time from text (pattern matching, no API)"""
        # Very basic extraction - in production, use dateparser library
        if "tomorrow" in text.lower():
            return "tomorrow"
        if "next week" in text.lower():
            return "next_week"
        return None

    def _default_task(self, user_message: str) -> Dict[str, Any]:
        """Default classification (no API calls)"""
        return {
            "task_type": "nacpac",  # Default to Nacpac
            "action": user_message,
            "target": "dev",
            "parameters": {},
            "priority": "normal",
            "schedule_time": None,
            "classification_method": "default"
        }

    def decompress_results(self, results: dict, user_id: int = 0) -> str:
        """
        OPTIMIZATION: Format results directly WITHOUT calling Claude.
        Haiku decompress was expensive and unnecessary.
        """
        status = results.get("status", "unknown")

        if status == "success":
            msg_parts = ["✅ **Success**"]

            # Format builds
            if "builds" in results:
                for build in results.get("builds", []):
                    if build.get("status") == "success":
                        url = build.get("url", "built")
                        msg_parts.append(f"📦 {build['type'].upper()}: {url}")

            # Format summary
            if "summary" in results:
                msg_parts.append(f"📝 {results['summary'][:200]}")

            return "\n".join(msg_parts)

        elif status == "error":
            return f"❌ Error: {results.get('error', 'Unknown error')}"

        else:
            return f"⏳ Status: {status}"
