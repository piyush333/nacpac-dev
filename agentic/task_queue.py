"""Redis task queue for distributed execution."""

import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)

try:
    import redis
except ImportError:
    logger.warning("redis not installed; task queue will use fallback")
    redis = None


class TaskQueue:
    """Redis-based task queue."""

    def __init__(self):
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        self.client = None

        if redis:
            try:
                self.client = redis.from_url(self.redis_url, decode_responses=True)
                self.client.ping()
                logger.info("✅ Redis task queue connected")
            except Exception as e:
                logger.warning(f"Failed to connect to Redis: {e}")
                self.client = None

    def push_task(self, queue_name: str, task: dict) -> bool:
        """Push task to queue."""
        if not self.client:
            logger.warning("Task queue unavailable")
            return False

        try:
            import json
            self.client.rpush(queue_name, json.dumps(task))
            return True
        except Exception as e:
            logger.error(f"Failed to push task: {e}")
            return False

    def pull_task(self, queue_name: str, timeout: int = 0) -> Optional[dict]:
        """Pull task from queue."""
        if not self.client:
            return None

        try:
            import json
            result = self.client.blpop(queue_name, timeout=timeout)
            if result:
                return json.loads(result[1])
            return None
        except Exception as e:
            logger.error(f"Failed to pull task: {e}")
            return None

    def queue_length(self, queue_name: str) -> int:
        """Get queue length."""
        if not self.client:
            return 0

        try:
            return self.client.llen(queue_name)
        except Exception as e:
            logger.error(f"Failed to get queue length: {e}")
            return 0


queue = TaskQueue()
