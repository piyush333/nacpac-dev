import logging
from datetime import datetime
from typing import Dict, Any

logger = logging.getLogger(__name__)

class TaskRouter:
    def __init__(self, nacpac_manager, jico_manager, scheduler):
        self.nacpac_manager = nacpac_manager
        self.jico_manager = jico_manager
        self.scheduler = scheduler

    async def route_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Route task to appropriate manager and decide execution timing"""

        task_type = task.get('task_type', 'jico')
        schedule_time = task.get('schedule_time')

        logger.info(f"Routing task: {task_type} - {task.get('action')}")

        # Decide: schedule or execute immediately
        if schedule_time:
            logger.info(f"Scheduling task for {schedule_time}")
            return await self.scheduler.schedule_task(task, schedule_time)

        # Execute immediately
        if task_type == 'nacpac':
            return await self.nacpac_manager.execute(task)
        elif task_type == 'jico':
            return await self.jico_manager.execute(task)
        else:
            return {
                "status": "error",
                "message": f"Unknown task type: {task_type}"
            }

    async def handle_scheduled_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a task that was scheduled"""
        logger.info(f"Executing scheduled task: {task}")

        task_type = task.get('task_type', 'jico')

        if task_type == 'nacpac':
            return await self.nacpac_manager.execute(task)
        elif task_type == 'jico':
            return await self.jico_manager.execute(task)
        else:
            return {"status": "error", "message": f"Unknown task type: {task_type}"}
