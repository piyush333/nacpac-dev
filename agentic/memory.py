"""Memory layer - Supabase client for persistent state."""

import json
from datetime import datetime
from typing import Any, Dict, Optional
import logging

from agentic.config import SUPABASE_URL, SUPABASE_KEY

logger = logging.getLogger(__name__)

create_client = None
try:
    from supabase import create_client as _create_client
    create_client = _create_client
except Exception as e:
    logger.warning(f"Supabase unavailable: {type(e).__name__}. Using in-memory storage.")


class MemoryClient:
    """Interface to Supabase for task/run/cost/decision storage."""

    def __init__(self):
        if not create_client:
            logger.warning("Supabase client not installed. Memory operations will be no-ops.")
            self.client = None
            return

        if not SUPABASE_URL or not SUPABASE_KEY:
            logger.error("SUPABASE_URL or SUPABASE_KEY not set")
            self.client = None
            return

        try:
            self.client = create_client(SUPABASE_URL, SUPABASE_KEY)
            logger.info("✅ Supabase client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}")
            self.client = None

    def create_task(self, brand: str, task_type: str, input_text: str, created_by: str = "agentic-system") -> Optional[str]:
        """Create a task record. Returns task_id."""
        if not self.client:
            logger.warning("Memory unavailable; skipping task creation")
            return None

        try:
            result = self.client.table("tasks").insert({
                "brand": brand,
                "task_type": task_type,
                "input_text": input_text,
                "status": "pending",
                "created_by": created_by,
                "created_at": datetime.utcnow().isoformat(),
            }).execute()

            if result.data:
                return result.data[0]["id"]
            return None
        except Exception as e:
            logger.error(f"Failed to create task: {e}")
            return None

    def update_task(self, task_id: str, status: str, result_summary: str = ""):
        """Update task status and result."""
        if not self.client:
            return

        try:
            self.client.table("tasks").update({
                "status": status,
                "result_summary": result_summary,
                "completed_at": datetime.utcnow().isoformat() if status in ["completed", "failed"] else None,
            }).eq("id", task_id).execute()
        except Exception as e:
            logger.error(f"Failed to update task: {e}")

    def get_brand_state(self, brand: str) -> Optional[Dict]:
        """Get current state of a brand."""
        if not self.client:
            return None

        try:
            result = self.client.table("brand_state").select("*").eq("brand", brand).execute()
            if result.data:
                return result.data[0]
            return None
        except Exception as e:
            logger.error(f"Failed to get brand state: {e}")
            return None

    def update_brand_state(self, brand: str, **kwargs):
        """Update brand state."""
        if not self.client:
            return

        try:
            kwargs["updated_at"] = datetime.utcnow().isoformat()
            self.client.table("brand_state").update(kwargs).eq("brand", brand).execute()
        except Exception as e:
            logger.error(f"Failed to update brand state: {e}")

    def log_build(self, brand: str, build_type: str, commit: str, output_path: str, status: str = "success"):
        """Log a build."""
        if not self.client:
            return

        try:
            self.client.table("builds").insert({
                "brand": brand,
                "type": build_type,
                "commit": commit,
                "output_path": output_path,
                "status": status,
                "created_at": datetime.utcnow().isoformat(),
            }).execute()
        except Exception as e:
            logger.error(f"Failed to log build: {e}")

    def log_deployment(self, brand: str, environment: str, commit: str):
        """Log a deployment."""
        if not self.client:
            return

        try:
            self.client.table("deployments").insert({
                "brand": brand,
                "environment": environment,
                "commit": commit,
                "deployed_at": datetime.utcnow().isoformat(),
            }).execute()
        except Exception as e:
            logger.error(f"Failed to log deployment: {e}")

    def log_cost(self, agent: str, model: str, tokens: int, cost_usd: float):
        """Log API call cost."""
        if not self.client:
            return

        try:
            self.client.table("costs").insert({
                "agent": agent,
                "model": model,
                "tokens": tokens,
                "cost_usd": cost_usd,
                "date": datetime.utcnow().isoformat(),
            }).execute()
        except Exception as e:
            logger.error(f"Failed to log cost: {e}")

    def get_daily_cost_usd(self) -> float:
        """Get total cost for today."""
        if not self.client:
            return 0.0

        try:
            from datetime import date
            today = str(date.today())
            result = self.client.rpc("get_daily_cost", {"date": today}).execute()
            return result.data or 0.0
        except Exception as e:
            logger.error(f"Failed to get daily cost: {e}")
            return 0.0

    def get_monthly_cost_usd(self) -> float:
        """Get total cost for this month."""
        if not self.client:
            return 0.0

        try:
            from datetime import date
            today = date.today()
            month_start = today.replace(day=1)
            result = self.client.rpc("get_monthly_cost", {"date_from": str(month_start)}).execute()
            return result.data or 0.0
        except Exception as e:
            logger.error(f"Failed to get monthly cost: {e}")
            return 0.0

    def get_agent_skillsets(self, agent_id: str) -> Dict[str, Dict]:
        """Get all skillsets for an agent. Returns dict: {skillset_name: {description, documentation, version}}."""
        if not self.client:
            logger.warning("Memory unavailable; returning empty skillsets")
            return {}

        try:
            result = self.client.table("agent_skillsets").select("*").eq("agent_id", agent_id).execute()
            if not result.data:
                logger.warning(f"No skillsets found for agent: {agent_id}")
                return {}

            skillsets = {}
            for row in result.data:
                skillsets[row["skillset_name"]] = {
                    "description": row.get("description", ""),
                    "documentation": row.get("documentation", ""),
                    "version": row.get("version", "1.0")
                }

            logger.info(f"✅ Loaded {len(skillsets)} skillsets for {agent_id}")
            return skillsets
        except Exception as e:
            logger.error(f"Failed to get agent skillsets: {e}")
            return {}

    def record_learned_pattern(self, agent_id: str, skillset_name: str, pattern_type: str,
                             pattern_description: str, context: str = None,
                             source_model: str = None, task_id: str = None) -> Optional[str]:
        """Record a learned pattern (success, failure, optimization, best_practice).

        Returns pattern_id if successful, None otherwise.
        """
        if not self.client:
            logger.warning("Memory unavailable; skipping pattern recording")
            return None

        try:
            result = self.client.table("learned_patterns").insert({
                "agent_id": agent_id,
                "skillset_name": skillset_name,
                "pattern_type": pattern_type,
                "pattern_description": pattern_description,
                "context": context,
                "source_model": source_model,
                "related_task_id": task_id,
                "confidence": 0.7,  # Start with moderate confidence
            }).execute()

            if result.data:
                pattern_id = result.data[0]["id"]
                logger.info(f"✅ Recorded {pattern_type} pattern for {agent_id}/{skillset_name}: {pattern_id[:8]}")
                return pattern_id
            return None
        except Exception as e:
            logger.error(f"Failed to record learned pattern: {e}")
            return None

    def get_learned_patterns(self, agent_id: str, skillset_name: str = None, pattern_type: str = None) -> list:
        """Get learned patterns for an agent/skillset. Sorted by confidence (highest first)."""
        if not self.client:
            logger.warning("Memory unavailable; returning empty patterns")
            return []

        try:
            query = self.client.table("learned_patterns").select("*").eq("agent_id", agent_id)

            if skillset_name:
                query = query.eq("skillset_name", skillset_name)
            if pattern_type:
                query = query.eq("pattern_type", pattern_type)

            # Sort by confidence descending
            result = query.order("confidence", desc=True).execute()

            logger.info(f"✅ Loaded {len(result.data)} patterns for {agent_id}")
            return result.data or []
        except Exception as e:
            logger.error(f"Failed to get learned patterns: {e}")
            return []

    def update_pattern_usage(self, pattern_id: str, success: bool):
        """Update pattern usage count and success rate."""
        if not self.client:
            return

        try:
            # Get current pattern
            result = self.client.table("learned_patterns").select("usage_count,success_rate").eq("id", pattern_id).execute()
            if not result.data:
                return

            current = result.data[0]
            usage_count = (current.get("usage_count") or 0) + 1
            success_rate = current.get("success_rate") or 0.0

            # Update success rate: (old_rate * old_count + success) / new_count
            new_success_rate = (success_rate * (usage_count - 1) + (1 if success else 0)) / usage_count

            # Increase confidence based on success rate
            new_confidence = min(0.99, success_rate * 1.2)  # Cap at 0.99

            self.client.table("learned_patterns").update({
                "usage_count": usage_count,
                "success_rate": new_success_rate,
                "confidence": new_confidence,
                "last_applied_at": datetime.utcnow().isoformat(),
            }).eq("id", pattern_id).execute()

            logger.info(f"Updated pattern {pattern_id[:8]}: usage={usage_count}, success_rate={new_success_rate:.2%}")
        except Exception as e:
            logger.error(f"Failed to update pattern usage: {e}")

    def record_learning_feedback(self, agent_id: str, skillset_name: str, feedback_type: str,
                                feedback_text: str, improvement_suggested: str = None,
                                task_id: str = None) -> Optional[str]:
        """Record feedback about agent learning/performance.

        feedback_type: "positive", "negative", "edge_case", "optimization"
        """
        if not self.client:
            logger.warning("Memory unavailable; skipping feedback recording")
            return None

        try:
            result = self.client.table("learning_feedback").insert({
                "agent_id": agent_id,
                "skillset_name": skillset_name,
                "task_id": task_id,
                "feedback_type": feedback_type,
                "feedback_text": feedback_text,
                "improvement_suggested": improvement_suggested,
            }).execute()

            if result.data:
                feedback_id = result.data[0]["id"]
                logger.info(f"✅ Recorded {feedback_type} feedback for {agent_id}/{skillset_name}")
                return feedback_id
            return None
        except Exception as e:
            logger.error(f"Failed to record learning feedback: {e}")
            return None

    def get_learning_insights(self, agent_id: str, skillset_name: str) -> Dict[str, Any]:
        """Get learning insights: most reliable patterns, common failures, improvement opportunities."""
        if not self.client:
            return {}

        try:
            # Get top patterns
            patterns = self.get_learned_patterns(agent_id, skillset_name)

            # Get pending feedback
            feedback_result = self.client.table("learning_feedback").select("*").eq("agent_id", agent_id).eq("skillset_name", skillset_name).eq("applied", False).execute()
            pending_feedback = feedback_result.data or []

            insights = {
                "top_patterns": [p for p in patterns if p.get("confidence", 0) > 0.7][:5],
                "failure_patterns": [p for p in patterns if p.get("pattern_type") == "failure"][:3],
                "optimizations": [p for p in patterns if p.get("pattern_type") == "optimization"][:3],
                "pending_improvements": len(pending_feedback),
                "success_feedback_count": len([f for f in pending_feedback if f.get("feedback_type") == "positive"]),
            }

            logger.info(f"Generated insights for {agent_id}/{skillset_name}")
            return insights
        except Exception as e:
            logger.error(f"Failed to get learning insights: {e}")
            return {}


memory = MemoryClient()
