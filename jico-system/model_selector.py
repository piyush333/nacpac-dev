import logging

logger = logging.getLogger(__name__)

class ModelSelector:
    """Select optimal model based on task complexity and cost"""

    @staticmethod
    def choose_model(task: dict) -> str:
        """
        Choose cheapest model that can handle the task:
        - Haiku: Simple screening, routing, summaries
        - Sonnet: Medium complexity, moderate reasoning
        - Opus: Complex builds, creative work, multi-step reasoning
        """
        action = task.get("action", "").lower()
        target = task.get("target", "").lower()
        priority = task.get("priority", "normal")

        # Check complexity indicators
        is_simple = ModelSelector._is_simple_task(action, target)
        is_complex = ModelSelector._is_complex_task(action, target)

        if is_complex or priority == "critical":
            logger.info("📊 Selected: OPUS (complex task)")
            return "opus"
        elif is_simple:
            logger.info("📊 Selected: HAIKU (simple task)")
            return "haiku"
        else:
            logger.info("📊 Selected: SONNET (medium complexity)")
            return "sonnet"

    @staticmethod
    def _is_simple_task(action: str, target: str) -> bool:
        """Detect simple tasks that Haiku can handle"""
        simple_keywords = [
            "summarize", "extract", "list", "count", "find",
            "format", "parse", "classify", "tag", "screen",
            "check", "validate", "verify", "review summary"
        ]
        return any(kw in action for kw in simple_keywords)

    @staticmethod
    def _is_complex_task(action: str, target: str) -> bool:
        """Detect complex tasks that need Opus"""
        complex_keywords = [
            "build", "create", "design", "architect", "generate code",
            "refactor", "optimize", "integrate", "develop app",
            "implement feature", "full stack", "build from scratch"
        ]
        return any(kw in action for kw in complex_keywords)

    @staticmethod
    def estimate_tokens(task: dict, model: str) -> dict:
        """Estimate input/output tokens for task"""
        action_length = len(task.get("action", ""))
        target_length = len(task.get("target", ""))

        # Very rough estimation
        input_tokens = min(action_length + target_length, 2000)

        if model == "haiku":
            output_tokens = 500  # Small responses
        elif model == "sonnet":
            output_tokens = 1500  # Medium responses
        else:  # opus
            output_tokens = 3000  # Larger responses

        return {"input": input_tokens, "output": output_tokens, "total": input_tokens + output_tokens}

    @staticmethod
    def estimate_cost(task: dict) -> dict:
        """Estimate cost for different models"""
        haiku = ModelSelector.estimate_tokens(task, "haiku")
        sonnet = ModelSelector.estimate_tokens(task, "sonnet")
        opus = ModelSelector.estimate_tokens(task, "opus")

        costs = {
            "haiku": (haiku["input"] / 1_000_000 * 0.80) + (haiku["output"] / 1_000_000 * 4.00),
            "sonnet": (sonnet["input"] / 1_000_000 * 3.00) + (sonnet["output"] / 1_000_000 * 15.00),
            "opus": (opus["input"] / 1_000_000 * 15.00) + (opus["output"] / 1_000_000 * 75.00)
        }

        return {
            "haiku": f"${costs['haiku']:.4f}",
            "sonnet": f"${costs['sonnet']:.4f}",
            "opus": f"${costs['opus']:.4f}",
            "recommended": min(costs, key=costs.get)
        }
