"""Memory layer - Supabase client for persistent state."""

import json
from datetime import datetime
from typing import Any, Dict, Optional
import logging

from config import SUPABASE_URL, SUPABASE_KEY

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

    def create_task(
        self,
        brand: str,
        task_type: str,
        input_text: str,
        created_by: str = "agentic-system"
    ) -> Optional[str]:
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
            logger.error(f"Failed to update task {task_id}: {e}")

    def log_run(
        self,
        task_id: str,
        agent: str,
        model: str,
        tokens_in: int,
        tokens_out: int,
        cost_usd: float,
        status: str = "completed",
        log_url: str = ""
    ):
        """Log an agent run (execution) with token/cost data."""
        if not self.client:
            return

        try:
            self.client.table("runs").insert({
                "task_id": task_id,
                "agent": agent,
                "model": model,
                "tokens_in": tokens_in,
                "tokens_out": tokens_out,
                "cost_usd": cost_usd,
                "status": status,
                "log_url": log_url,
                "started_at": datetime.utcnow().isoformat(),
                "finished_at": datetime.utcnow().isoformat(),
            }).execute()
        except Exception as e:
            logger.error(f"Failed to log run: {e}")

    def get_brand_state(self, brand: str) -> Optional[Dict[str, Any]]:
        """Get current state of a brand (branch, last commit, deploy env, etc.)."""
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

    def update_brand_state(
        self,
        brand: str,
        current_branch: str = None,
        last_commit: str = None,
        last_deploy_env: str = None,
        last_deploy_time: str = None,
    ):
        """Update brand state (current branch, last commit, etc.)."""
        if not self.client:
            return

        try:
            update_dict = {}
            if current_branch:
                update_dict["current_branch"] = current_branch
            if last_commit:
                update_dict["last_commit"] = last_commit
            if last_deploy_env:
                update_dict["last_deploy_env"] = last_deploy_env
            if last_deploy_time:
                update_dict["last_deploy_time"] = last_deploy_time

            self.client.table("brand_state").update(update_dict).eq("brand", brand).execute()
        except Exception as e:
            logger.error(f"Failed to update brand state: {e}")

    def log_build(
        self,
        brand: str,
        build_type: str,
        commit: str,
        output_path: str,
        status: str = "success"
    ):
        """Log a build (APK/EXE/GLB)."""
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

    def log_deployment(
        self,
        brand: str,
        environment: str,
        commit: str,
        deployed_by: str = "agentic-system"
    ):
        """Log a deployment."""
        if not self.client:
            return

        try:
            self.client.table("deployments").insert({
                "brand": brand,
                "environment": environment,
                "commit": commit,
                "deployed_at": datetime.utcnow().isoformat(),
                "deployed_by": deployed_by,
            }).execute()
        except Exception as e:
            logger.error(f"Failed to log deployment: {e}")

    def get_daily_cost_usd(self) -> float:
        """Get total cost for today (USD)."""
        if not self.client:
            return 0.0

        try:
            today = datetime.utcnow().date().isoformat()
            result = self.client.table("costs").select("cost_usd").eq("date", today).execute()
            return sum(row["cost_usd"] for row in result.data or [])
        except Exception as e:
            logger.error(f"Failed to get daily cost: {e}")
            return 0.0

    def get_monthly_cost_usd(self) -> float:
        """Get total cost for current month (USD)."""
        if not self.client:
            return 0.0

        try:
            today = datetime.utcnow()
            month_start = today.replace(day=1).isoformat()
            result = self.client.table("costs").select("cost_usd").gte("date", month_start).execute()
            return sum(row["cost_usd"] for row in result.data or [])
        except Exception as e:
            logger.error(f"Failed to get monthly cost: {e}")
            return 0.0

    def log_cost(self, agent: str, model: str, tokens: int, cost_usd: float):
        """Log API cost."""
        if not self.client:
            return

        try:
            self.client.table("costs").insert({
                "date": datetime.utcnow().date().isoformat(),
                "agent": agent,
                "model": model,
                "tokens": tokens,
                "cost_usd": cost_usd,
            }).execute()
        except Exception as e:
            logger.error(f"Failed to log cost: {e}")

    def get_failed_tasks(self) -> list:
        """Get tasks in dead letter queue (failed, not yet retried)."""
        if not self.client:
            return []

        try:
            result = self.client.table("tasks").select("*").eq("status", "failed").execute()
            return result.data or []
        except Exception as e:
            logger.error(f"Failed to get failed tasks: {e}")
            return []


# Global instance
memory = MemoryClient()
