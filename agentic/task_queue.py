"""Task Queue - Redis-based work distribution."""

import json
import logging
import uuid
import os
from datetime import datetime
from typing import Dict, Optional, Any
from redis import Redis
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class TaskQueue:
    """Redis-based task queue for agent work distribution."""

    def __init__(self, redis_url: str = None):
        """Initialize Redis connection.

        Args:
            redis_url: Redis connection URL (defaults to REDIS_URL from .env)
        """
        if redis_url is None:
            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")

        try:
            self.redis = Redis.from_url(redis_url, decode_responses=True)
            self.redis.ping()
            logger.info(f"✅ Connected to Redis")
        except Exception as e:
            logger.error(f"❌ Redis connection failed: {e}")
            self.redis = None

    def push_task(self, agent_name: str, action: str, params: Dict[str, Any], priority: int = 5) -> str:
        """Push a task to the queue.

        Args:
            agent_name: Target agent (e.g., "nacpac_dev")
            action: Action to perform (e.g., "build_apk")
            params: Action parameters
            priority: Queue priority (1=lowest, 10=highest)

        Returns:
            Task ID (UUID)
        """
        if not self.redis:
            logger.error("Redis not connected")
            return ""

        task_id = str(uuid.uuid4())
        task = {
            "task_id": task_id,
            "agent": agent_name,
            "action": action,
            "params": params,
            "priority": priority,
            "created_at": datetime.now().isoformat(),
            "status": "pending"
        }

        queue_name = f"queue:{agent_name}"
        try:
            self.redis.lpush(queue_name, json.dumps(task))
            logger.info(f"✅ Task {task_id} pushed to {queue_name}")
            return task_id
        except Exception as e:
            logger.error(f"❌ Failed to push task: {e}")
            return ""

    def pull_task(self, agent_name: str) -> Optional[Dict]:
        """Pull a task from the queue.

        Args:
            agent_name: Agent name to pull from

        Returns:
            Task dict or None if queue is empty
        """
        if not self.redis:
            logger.error("Redis not connected")
            return None

        queue_name = f"queue:{agent_name}"
        try:
            task_json = self.redis.rpop(queue_name)
            if task_json:
                task = json.loads(task_json)
                logger.info(f"✅ Task {task.get('task_id')} pulled from {queue_name}")
                return task
            return None
        except Exception as e:
            logger.error(f"❌ Failed to pull task: {e}")
            return None

    def push_result(self, task_id: str, agent_name: str, result: Dict) -> bool:
        """Push task result to result queue.

        Args:
            task_id: Task ID
            agent_name: Agent name
            result: Result dictionary

        Returns:
            True if successful
        """
        if not self.redis:
            logger.error("Redis not connected")
            return False

        result_queue = "queue:results"
        result_with_id = {
            "task_id": task_id,
            "agent": agent_name,
            "result": result,
            "completed_at": datetime.now().isoformat()
        }

        try:
            self.redis.lpush(result_queue, json.dumps(result_with_id))
            logger.info(f"✅ Result for task {task_id} pushed to {result_queue}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to push result: {e}")
            return False

    def pull_result(self) -> Optional[Dict]:
        """Pull a result from the result queue.

        Returns:
            Result dict or None if queue is empty
        """
        if not self.redis:
            logger.error("Redis not connected")
            return None

        try:
            result_json = self.redis.rpop("queue:results")
            if result_json:
                result = json.loads(result_json)
                logger.info(f"✅ Result for task {result.get('task_id')} pulled")
                return result
            return None
        except Exception as e:
            logger.error(f"❌ Failed to pull result: {e}")
            return None

    def queue_length(self, agent_name: str) -> int:
        """Get queue length for an agent.

        Args:
            agent_name: Agent name

        Returns:
            Number of tasks in queue
        """
        if not self.redis:
            return 0

        queue_name = f"queue:{agent_name}"
        try:
            return self.redis.llen(queue_name)
        except Exception as e:
            logger.error(f"❌ Failed to get queue length: {e}")
            return 0

    def push_failed_task(self, task_id: str, agent_name: str, error: str) -> bool:
        """Push failed task to dead letter queue.

        Args:
            task_id: Task ID
            agent_name: Agent name
            error: Error message

        Returns:
            True if successful
        """
        if not self.redis:
            logger.error("Redis not connected")
            return False

        dlq = "queue:dead_letter"
        failed_task = {
            "task_id": task_id,
            "agent": agent_name,
            "error": error,
            "failed_at": datetime.now().isoformat()
        }

        try:
            self.redis.lpush(dlq, json.dumps(failed_task))
            logger.warning(f"⚠️  Task {task_id} moved to dead letter queue")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to push to DLQ: {e}")
            return False


queue = TaskQueue()
