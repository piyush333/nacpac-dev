import logging
import asyncio
import json
from typing import Dict, Any, Optional
import boto3
from paramiko import SSHClient, AutoAddPolicy, RSAKey
from config import Config

logger = logging.getLogger(__name__)

# Setup logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class R2Storage:
    """Cloudflare R2 storage handler"""

    def __init__(self, bucket: str):
        self.s3_client = boto3.client(
            's3',
            endpoint_url=Config.R2_ENDPOINT,
            aws_access_key_id=Config.R2_ACCESS_KEY,
            aws_secret_access_key=Config.R2_SECRET_KEY,
            region_name='auto'
        )
        self.bucket = bucket

    def upload_file(self, file_path: str, object_name: str) -> Optional[str]:
        """Upload file to R2"""
        try:
            self.s3_client.upload_file(file_path, self.bucket, object_name)
            logger.info(f"Uploaded {object_name} to {self.bucket}")
            return object_name
        except Exception as e:
            logger.error(f"R2 upload error: {e}")
            return None

    def download_file(self, object_name: str, file_path: str) -> bool:
        """Download file from R2"""
        try:
            self.s3_client.download_file(self.bucket, object_name, file_path)
            logger.info(f"Downloaded {object_name} from {self.bucket}")
            return True
        except Exception as e:
            logger.error(f"R2 download error: {e}")
            return False

    def list_objects(self, prefix: str = "") -> list:
        """List objects in R2 bucket"""
        try:
            response = self.s3_client.list_objects_v2(Bucket=self.bucket, Prefix=prefix)
            return response.get('Contents', [])
        except Exception as e:
            logger.error(f"R2 list error: {e}")
            return []


class OracleVMConnector:
    """Connect to Oracle VM and manage scheduled tasks"""

    def __init__(self):
        self.ip = Config.ORACLE_VM_IP
        self.user = Config.ORACLE_VM_USER
        self.key_path = Config.ORACLE_SSH_KEY_PATH

    async def execute_remote_command(self, command: str) -> Dict[str, Any]:
        """Execute command on Oracle VM via SSH"""
        try:
            ssh = SSHClient()
            ssh.set_missing_host_key_policy(AutoAddPolicy())

            # Load SSH key
            key = RSAKey.from_private_key_file(self.key_path)
            ssh.connect(self.ip, username=self.user, pkey=key, timeout=10)

            stdin, stdout, stderr = ssh.exec_command(command)
            output = stdout.read().decode('utf-8')
            error = stderr.read().decode('utf-8')

            ssh.close()

            logger.info(f"Remote command executed: {command}")
            return {
                "status": "success",
                "output": output,
                "error": error if error else None
            }

        except Exception as e:
            logger.error(f"SSH error: {e}")
            return {
                "status": "error",
                "message": str(e)
            }

    async def schedule_cron_task(self, task_id: str, cron_expression: str, command: str) -> Dict[str, Any]:
        """Schedule a task on Oracle VM cron"""
        cron_entry = f"{cron_expression} {command}"
        cron_command = f"echo '{cron_entry}' | crontab -"

        return await self.execute_remote_command(cron_command)


class TaskScheduler:
    """In-memory task scheduler"""

    def __init__(self, oracle_vm: OracleVMConnector):
        self.oracle_vm = oracle_vm
        self.scheduled_tasks: Dict[str, Any] = {}

    async def schedule_task(self, task: Dict[str, Any], schedule_time: str) -> Dict[str, Any]:
        """Schedule a task for future execution"""
        task_id = f"{task.get('task_type')}_{task.get('action')}_{schedule_time}"

        self.scheduled_tasks[task_id] = {
            "task": task,
            "scheduled_time": schedule_time,
            "status": "pending"
        }

        logger.info(f"Task scheduled: {task_id} for {schedule_time}")

        # Optionally push to Oracle VM cron
        # await self.oracle_vm.schedule_cron_task(task_id, cron_expr, "curl ...")

        return {
            "status": "scheduled",
            "task_id": task_id,
            "scheduled_time": schedule_time
        }

    async def check_due_tasks(self) -> list:
        """Check for tasks that are due to execute"""
        from datetime import datetime

        due_tasks = []
        now = datetime.now()

        for task_id, task_info in self.scheduled_tasks.items():
            scheduled = datetime.fromisoformat(task_info['scheduled_time'])
            if scheduled <= now and task_info['status'] == 'pending':
                due_tasks.append((task_id, task_info['task']))
                task_info['status'] = 'executing'

        return due_tasks
