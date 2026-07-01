import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class SessionManager:
    """Manage session time and decide when to schedule vs execute"""

    SESSION_LIMIT_MINUTES = 300  # 5 hours in minutes
    SCHEDULE_THRESHOLD_MINUTES = 30  # If <30 min left, schedule cron instead

    def __init__(self):
        self.session_start = datetime.now()
        self.last_activity = datetime.now()

    def get_remaining_time(self) -> int:
        """Get remaining session time in minutes"""
        elapsed = (datetime.now() - self.session_start).total_seconds() / 60
        remaining = self.SESSION_LIMIT_MINUTES - elapsed
        return max(0, int(remaining))

    def should_schedule_cron(self, task_duration_estimate: int = 10) -> bool:
        """
        Check if task should be scheduled as cron instead of executed now

        Args:
            task_duration_estimate: Estimated minutes to complete task

        Returns:
            True if task should be scheduled for later, False if can execute now
        """
        remaining = self.get_remaining_time()

        if remaining < self.SCHEDULE_THRESHOLD_MINUTES:
            logger.warning(f"⏰ Only {remaining}min left. Scheduling task as cron.")
            return True

        if remaining < task_duration_estimate:
            logger.warning(f"⏰ Task needs {task_duration_estimate}min but only {remaining}min left. Scheduling.")
            return True

        logger.info(f"✅ {remaining}min available. Executing task now.")
        return False

    def get_session_status(self) -> dict:
        """Get current session status"""
        remaining = self.get_remaining_time()
        return {
            "elapsed_minutes": self.SESSION_LIMIT_MINUTES - remaining,
            "remaining_minutes": remaining,
            "percent_used": int((self.SESSION_LIMIT_MINUTES - remaining) / self.SESSION_LIMIT_MINUTES * 100),
            "can_execute": remaining >= self.SCHEDULE_THRESHOLD_MINUTES,
            "session_start": self.session_start.isoformat()
        }

    def log_activity(self):
        """Update last activity timestamp"""
        self.last_activity = datetime.now()

    def get_cron_time(self) -> str:
        """Get recommended cron execution time (2 hours from now)"""
        execution_time = datetime.now() + timedelta(hours=2)
        return execution_time.strftime("%H:%M")
