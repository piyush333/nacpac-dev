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

    def create_nacpac_task(self, task_input: str) -> Optional[str]:
        """Create a task record in nacpac_tasks. Returns task_id."""
        if not self.client:
            logger.warning("Memory unavailable; skipping task creation")
            return None

        try:
            result = self.client.table("nacpac_tasks").insert({
                "agent_id": "nacpac_dev",
                "task_input": task_input,
                "status": "pending",
                "created_at": datetime.utcnow().isoformat(),
            }).execute()

            if result.data:
                task_id = result.data[0]["id"]
                logger.info(f"✅ Created task: {task_id[:8]}")
                return task_id
            return None
        except Exception as e:
            logger.error(f"Failed to create nacpac task: {e}")
            return None

    def update_nacpac_task(self, task_id: str, status: str, result_summary: str = "", cost_usd: float = 0.0):
        """Update task status, result, and cost in nacpac_tasks."""
        if not self.client:
            return

        try:
            update_data = {
                "status": status,
                "result_summary": result_summary,
                "cost_usd": cost_usd,
            }
            if status in ["completed", "failed"]:
                update_data["completed_at"] = datetime.utcnow().isoformat()

            self.client.table("nacpac_tasks").update(update_data).eq("id", task_id).execute()
            logger.info(f"✅ Updated task {task_id[:8]}: status={status}")
        except Exception as e:
            logger.error(f"Failed to update nacpac task: {e}")

    def log_nacpac_run(self, task_id: str, model: str, tokens_in: int, tokens_out: int, cost_usd: float):
        """Log an execution run to nacpac_runs."""
        if not self.client:
            return

        try:
            self.client.table("nacpac_runs").insert({
                "agent_id": "nacpac_dev",
                "task_id": task_id,
                "model": model,
                "tokens_in": tokens_in,
                "tokens_out": tokens_out,
                "cost_usd": cost_usd,
                "status": "completed",
                "started_at": datetime.utcnow().isoformat(),
                "finished_at": datetime.utcnow().isoformat(),
            }).execute()
            logger.info(f"✅ Logged run for task {task_id[:8]}: {tokens_in+tokens_out} tokens, ${cost_usd:.4f}")
        except Exception as e:
            logger.error(f"Failed to log nacpac run: {e}")

    def get_nacpac_task_history(self, limit: int = 10) -> list:
        """Get recent task history for nacpac_dev."""
        if not self.client:
            return []

        try:
            result = self.client.table("nacpac_tasks").select("*").eq(
                "agent_id", "nacpac_dev"
            ).order("created_at", desc=True).limit(limit).execute()
            logger.info(f"✅ Retrieved {len(result.data or [])} recent tasks")
            return result.data or []
        except Exception as e:
            logger.error(f"Failed to get task history: {e}")
            return []

    def get_nacpac_task_stats(self) -> Dict[str, Any]:
        """Get task statistics for nacpac_dev (total, by status, avg cost)."""
        if not self.client:
            return {}

        try:
            result = self.client.table("nacpac_tasks").select("*").eq(
                "agent_id", "nacpac_dev"
            ).execute()
            tasks = result.data or []

            if not tasks:
                return {
                    "total_tasks": 0,
                    "by_status": {},
                    "total_cost_usd": 0.0,
                    "avg_cost_usd": 0.0
                }

            # Count by status
            by_status = {}
            total_cost = 0.0
            for task in tasks:
                status = task.get("status", "unknown")
                by_status[status] = by_status.get(status, 0) + 1
                total_cost += task.get("cost_usd", 0.0) or 0.0

            avg_cost = total_cost / len(tasks) if tasks else 0.0

            return {
                "total_tasks": len(tasks),
                "by_status": by_status,
                "total_cost_usd": total_cost,
                "avg_cost_usd": avg_cost
            }
        except Exception as e:
            logger.error(f"Failed to get task stats: {e}")
            return {}


memory = MemoryClient()
