#!/usr/bin/env python3
"""
AUTO MODE - Continuous autonomous task execution
Monitors Discord, processes tasks continuously, executes in background
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List
import json

logger = logging.getLogger(__name__)

class AutoTaskExecutor:
    """Autonomous task execution engine - runs continuously"""

    def __init__(self, compression_layer, router, discord_manager):
        self.compression = compression_layer
        self.router = router
        self.discord_mgr = discord_manager

        # Task queue
        self.pending_tasks: List[Dict[str, Any]] = []
        self.executing_tasks: Dict[str, Dict[str, Any]] = {}
        self.completed_tasks: List[Dict[str, Any]] = []

        # Configuration
        self.auto_mode_enabled = True
        self.check_interval = 5  # seconds
        self.max_concurrent = 5

    async def start_auto_mode(self):
        """Start autonomous execution loop"""
        logger.info("🤖 AUTO MODE ENABLED - Continuous task execution started")

        while self.auto_mode_enabled:
            try:
                # Check for due scheduled tasks
                due_tasks = await self.router.scheduler.check_due_tasks()
                for task_id, task in due_tasks:
                    await self.queue_task(task)

                # Process pending tasks
                await self.process_pending_tasks()

                # Monitor executing tasks
                await self.monitor_executing_tasks()

                # Wait before next check
                await asyncio.sleep(self.check_interval)

            except Exception as e:
                logger.error(f"Auto mode error: {e}")
                await asyncio.sleep(self.check_interval)

    async def queue_task(self, task: Dict[str, Any]) -> str:
        """Add task to execution queue"""
        task_id = f"{task.get('task_type')}_{datetime.now().timestamp()}"
        task['task_id'] = task_id
        task['queued_at'] = datetime.now().isoformat()
        task['status'] = 'pending'

        self.pending_tasks.append(task)
        logger.info(f"📋 Task queued: {task_id} - {task.get('action')}")

        return task_id

    async def process_pending_tasks(self):
        """Execute pending tasks (up to max_concurrent)"""
        available_slots = self.max_concurrent - len(self.executing_tasks)

        for _ in range(available_slots):
            if not self.pending_tasks:
                break

            task = self.pending_tasks.pop(0)
            task_id = task.get('task_id')

            self.executing_tasks[task_id] = task
            task['status'] = 'executing'
            task['started_at'] = datetime.now().isoformat()

            # Execute in background
            asyncio.create_task(self._execute_task_background(task))

    async def _execute_task_background(self, task: Dict[str, Any]):
        """Execute a single task in the background"""
        task_id = task.get('task_id')

        try:
            logger.info(f"⚙️  Executing task: {task_id}")

            # Route and execute
            result = await self.router.route_task(task)

            task['result'] = result
            task['status'] = 'completed'
            task['completed_at'] = datetime.now().isoformat()

            logger.info(f"✅ Task completed: {task_id}")

            # Post result to Discord
            await self._post_result_to_discord(task, result)

        except Exception as e:
            logger.error(f"❌ Task failed: {task_id} - {e}")
            task['status'] = 'failed'
            task['error'] = str(e)
            task['completed_at'] = datetime.now().isoformat()
            await self._post_error_to_discord(task, str(e))

        finally:
            # Move to completed
            self.completed_tasks.append(task)
            if task_id in self.executing_tasks:
                del self.executing_tasks[task_id]

    async def _post_result_to_discord(self, task: Dict[str, Any], result: Dict[str, Any]):
        """Post task result to appropriate channel (nacpac-dev or jico-dev)"""
        try:
            result['status'] = 'success'
            await self.discord_mgr.post_task_result(task, result)
        except Exception as e:
            logger.error(f"Failed to post result: {e}")

    async def _post_error_to_discord(self, task: Dict[str, Any], error: str):
        """Post task error to #logs channel"""
        try:
            result = {'status': 'error', 'error': error}
            await self.discord_mgr.post_task_result(task, result)
        except Exception as e:
            logger.error(f"Failed to post error: {e}")

    async def monitor_executing_tasks(self):
        """Monitor executing tasks for timeout"""
        now = datetime.now()
        timeout_duration = timedelta(minutes=30)

        for task_id, task in list(self.executing_tasks.items()):
            started = datetime.fromisoformat(task['started_at'])
            if now - started > timeout_duration:
                logger.warning(f"Task timeout: {task_id}")
                task['status'] = 'timeout'
                task['error'] = 'Task execution timeout (30 minutes)'
                self.completed_tasks.append(task)
                del self.executing_tasks[task_id]

    async def get_status(self) -> Dict[str, Any]:
        """Get current auto mode status"""
        return {
            "auto_mode": self.auto_mode_enabled,
            "pending": len(self.pending_tasks),
            "executing": len(self.executing_tasks),
            "completed": len(self.completed_tasks),
            "tasks": {
                "pending": [t.get('task_id') for t in self.pending_tasks],
                "executing": list(self.executing_tasks.keys()),
                "recent_completed": [t.get('task_id') for t in self.completed_tasks[-10:]]
            }
        }

    async def pause(self):
        """Pause auto mode (stop accepting new tasks)"""
        self.auto_mode_enabled = False
        logger.info("⏸️  AUTO MODE PAUSED")

    async def resume(self):
        """Resume auto mode"""
        self.auto_mode_enabled = True
        logger.info("▶️  AUTO MODE RESUMED")

    async def get_task_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent task execution history"""
        return self.completed_tasks[-limit:]
