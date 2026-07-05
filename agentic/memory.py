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


memory = MemoryClient()
