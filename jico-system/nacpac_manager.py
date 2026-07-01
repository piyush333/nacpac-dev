import logging
import asyncio
import subprocess
import json
from pathlib import Path
from typing import Dict, Any
import boto3
from utils import R2Storage
from config import Config
from build_backup import BuildBackup
from google_drive_backup import GoogleDriveBackup

logger = logging.getLogger(__name__)

def run_command(cmd: str, cwd: str = None, timeout: int = 1800) -> tuple:
    """Execute shell command and return (returncode, stdout, stderr)"""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True,
            cwd=cwd, timeout=timeout, text=True
        )
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    except subprocess.TimeoutExpired:
        return 1, "", "Command timed out"
    except Exception as e:
        return 1, "", str(e)


def upload_to_r2(local_path: str, r2_key: str) -> str:
    """Upload file to Cloudflare R2 and return public URL"""
    s3 = boto3.client(
        "s3",
        endpoint_url=Config.R2_ENDPOINT,
        aws_access_key_id=Config.R2_ACCESS_KEY,
        aws_secret_access_key=Config.R2_SECRET_KEY,
        region_name="auto",
    )
    s3.upload_file(local_path, Config.NACPAC_R2_BUCKET, r2_key)
    from urllib.parse import quote
    return f"{Config.NACPAC_R2_URL}/{quote(r2_key)}"


class NacpacWorker:
    """Individual worker for Nacpac tasks"""

    def __init__(self, worker_type: str):
        self.worker_type = worker_type  # dev, seo, ads, build

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a Nacpac task"""
        logger.info(f"Nacpac {self.worker_type} worker executing: {task.get('action')}")

        action = task.get('action', '')
        parameters = task.get('parameters', {})

        if self.worker_type == 'dev':
            return await self.dev_task(action, parameters)
        elif self.worker_type == 'seo':
            return await self.seo_task(action, parameters)
        elif self.worker_type == 'ads':
            return await self.ads_task(action, parameters)
        elif self.worker_type == 'build':
            return await self.build_task(action, parameters)
        else:
            return {"status": "error", "message": f"Unknown worker type: {self.worker_type}"}

    async def dev_task(self, action: str, params: Dict) -> Dict[str, Any]:
        """Development tasks - code changes via Claude"""
        logger.info(f"Dev task: {action}")

        if not Config.NACPAC_DIR:
            return {"status": "error", "message": "NACPAC_DIR not configured"}

        try:
            # Use Claude to make code changes
            prompt = (
                f"You are an AI coding agent for the Nacpac app. "
                f"The app has a mobile folder (Expo React Native) and a desktop folder (Electron). "
                f"Task: {action}\n\n"
                f"Make all necessary code changes. When done, summarise what you changed in 2-3 lines."
            )

            # Run claude command against the codebase
            cmd = f'claude --print --max-turns 5 "{prompt}"'
            code, out, err = await self._run_async(cmd, cwd=Config.NACPAC_DIR, timeout=600)

            if code != 0:
                return {
                    "status": "error",
                    "worker": "dev",
                    "action": action,
                    "error": err or out,
                }

            summary = out[-1500:] if out else "Changes applied"
            return {
                "status": "success",
                "worker": "dev",
                "action": action,
                "summary": summary,
                "changes_made": True,
            }
        except Exception as e:
            logger.error(f"Dev task failed: {e}")
            return {"status": "error", "worker": "dev", "error": str(e)}

    async def seo_task(self, action: str, params: Dict) -> Dict[str, Any]:
        """SEO tasks - metadata, keywords, optimization"""
        logger.info(f"SEO task: {action}")
        return {"status": "success", "worker": "seo", "action": action}

    async def ads_task(self, action: str, params: Dict) -> Dict[str, Any]:
        """Ads tasks - campaigns, targeting, analytics"""
        logger.info(f"Ads task: {action}")
        return {"status": "success", "worker": "ads", "action": action}

    async def build_task(self, action: str, params: Dict) -> Dict[str, Any]:
        """Build tasks - APK, EXE, and upload to Firebase"""
        logger.info(f"Build task: {action}")

        if not Config.NACPAC_DIR:
            return {"status": "error", "message": "NACPAC_DIR not configured"}

        try:
            results = []
            build_type = params.get('build_type', 'both')  # apk, exe, or both
            deploy_to_firebase = params.get('deploy_to_firebase', True)

            # Build APK if requested
            if build_type in ('apk', 'both'):
                # Check if mobile directory exists
                if not Path(Config.MOBILE_DIR).exists():
                    logger.warning(f"Mobile directory not found: {Config.MOBILE_DIR}")
                    results.append({
                        "type": "apk",
                        "status": "skipped",
                        "message": "Mobile app not set up on this instance",
                    })
                else:
                    logger.info("Building APK...")
                    code, out, err = await self._run_async(
                        "eas build --platform android --profile preview --non-interactive",
                        cwd=Config.MOBILE_DIR,
                        timeout=1800,
                    )

                    if code == 0:
                        # Extract download URL from output
                        lines = out.split("\n")
                        url = next((l.strip() for l in lines if l.strip().startswith("https://") and "apk" in l.lower()), None)
                        if not url:
                            url = next((l.strip() for l in reversed(lines) if l.strip().startswith("https://")), None)

                        result_item = {
                            "type": "apk",
                            "status": "success",
                            "url": url or "APK built but URL not found",
                        }
                        results.append(result_item)

                        # Save backup
                        if url:
                            self.backup.save_build("apk", "mobile-app.apk", url)
                    else:
                        results.append({
                            "type": "apk",
                            "status": "error",
                            "error": (err or out)[-400:],
                        })

            # Build EXE if requested
            if build_type in ('exe', 'both'):
                # Check if npm is available
                npm_check, _, _ = await self._run_async("which npm", timeout=5)
                if npm_check != 0:
                    logger.warning("npm not found on this instance")
                    results.append({
                        "type": "exe",
                        "status": "skipped",
                        "message": "npm not installed on this instance. Run: sudo apt-get install -y nodejs npm",
                    })
                else:
                    logger.info("Building EXE...")
                    code, out, err = await self._run_async(
                        "npm run build",
                        cwd=Config.DESKTOP_DIR,
                        timeout=300,
                    )

                    if code == 0:
                        # Find and upload EXE
                        dist_dir = Path(Config.DESKTOP_DIR) / "dist"
                        exe_files = list(dist_dir.glob("*.exe"))

                        if exe_files:
                            exe_path = str(exe_files[0])
                            try:
                                r2_url = upload_to_r2(exe_path, f"desktop/{exe_files[0].name}")
                                result_item = {
                                    "type": "exe",
                                    "status": "success",
                                    "url": r2_url,
                                    "filename": exe_files[0].name,
                                }
                                results.append(result_item)

                                # Save backup
                                self.backup.save_build("exe", exe_files[0].name, r2_url)
                            except Exception as e:
                                results.append({
                                    "type": "exe",
                                    "status": "error",
                                    "error": f"Upload failed: {str(e)}",
                                })
                        else:
                            results.append({
                                "type": "exe",
                                "status": "error",
                                "error": "No .exe found in dist/",
                            })
                    else:
                        results.append({
                            "type": "exe",
                            "status": "error",
                            "error": (err or out)[-300:],
                        })

            # Deploy to Firebase if requested
            if deploy_to_firebase and any(b.get("status") == "success" for b in results):
                logger.info("Deploying to Firebase...")
                firebase_result = await self._deploy_to_firebase(Config.NACPAC_DIR)
                results.append({
                    "type": "firebase",
                    "status": firebase_result.get("status", "error"),
                    "message": firebase_result.get("message", "Deployment unknown"),
                })

            # Backup to Google Drive if builds succeeded
            if any(b.get("status") == "success" for b in results):
                logger.info("Backing up to Google Drive...")
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, self.gdrive_backup.backup_folder, Config.NACPAC_DIR, "nacpac-build")

            return {
                "status": "success",
                "worker": "build",
                "action": action,
                "builds": results,
            }
        except Exception as e:
            logger.error(f"Build task failed: {e}")
            return {"status": "error", "worker": "build", "error": str(e)}

    async def _run_async(self, cmd: str, cwd: str = None, timeout: int = 1800) -> tuple:
        """Run command asynchronously"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, run_command, cmd, cwd, timeout)


class NacpacManager:
    """Manage Nacpac workers and coordinate tasks"""

    def __init__(self):
        self.workers = {
            'dev': NacpacWorker('dev'),
            'seo': NacpacWorker('seo'),
            'ads': NacpacWorker('ads'),
            'build': NacpacWorker('build'),
        }
        self.backup = BuildBackup()
        self.gdrive_backup = GoogleDriveBackup()

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a Nacpac task by routing to appropriate worker"""
        target = task.get('target', 'dev')

        if target not in self.workers:
            logger.error(f"Unknown target: {target}")
            return {"status": "error", "message": f"Unknown target: {target}"}

        worker = self.workers[target]
        result = await worker.execute(task)

        logger.info(f"Nacpac {target} completed: {result}")
        return result

    async def execute_full_workflow(self, description: str) -> Dict[str, Any]:
        """Execute complete workflow: code changes -> git push -> build -> upload"""
        results = {
            "status": "in_progress",
            "workflow": [],
        }

        try:
            # Step 1: Code changes
            logger.info(f"Starting workflow for: {description}")
            dev_task = {
                "action": description,
                "target": "dev",
            }
            dev_result = await self.execute(dev_task)
            results["workflow"].append({
                "step": "code_changes",
                "result": dev_result,
            })

            if dev_result.get("status") != "success":
                results["status"] = "error"
                return results

            # Step 2: Git push
            logger.info("Pushing changes to GitHub...")
            push_code, push_out, push_err = await self._run_git_push()
            if push_code != 0:
                results["workflow"].append({
                    "step": "git_push",
                    "status": "error",
                    "error": push_err or push_out,
                })
                results["status"] = "error"
                return results

            results["workflow"].append({
                "step": "git_push",
                "status": "success",
            })

            # Step 3: Build (user typically decides, but can auto-build)
            logger.info("Build step ready")
            results["workflow"].append({
                "step": "build",
                "status": "waiting",
                "message": "Ready to build APK/EXE. Awaiting user confirmation.",
            })

            results["status"] = "success"
            return results

        except Exception as e:
            logger.error(f"Workflow failed: {e}")
            results["status"] = "error"
            results["error"] = str(e)
            return results

    async def _deploy_to_firebase(self, cwd: str) -> Dict[str, Any]:
        """Deploy built app to Firebase Hosting"""
        try:
            logger.info("Starting Firebase deployment...")
            loop = asyncio.get_event_loop()

            # Run firebase deploy
            code, out, err = await loop.run_in_executor(
                None,
                run_command,
                "firebase deploy --only hosting",
                cwd,
                600,
            )

            if code == 0:
                logger.info("Firebase deployment successful")
                return {
                    "status": "success",
                    "message": "Deployed to Firebase Hosting"
                }
            else:
                logger.error(f"Firebase deployment failed: {err}")
                return {
                    "status": "error",
                    "message": f"Firebase deployment failed: {err[:200]}"
                }
        except Exception as e:
            logger.error(f"Firebase deployment error: {e}")
            return {
                "status": "error",
                "message": str(e)
            }

    async def _run_git_push(self) -> tuple:
        """Push changes to GitHub"""
        loop = asyncio.get_event_loop()

        # First push mobile submodule if it exists
        if Path(Config.MOBILE_DIR).exists():
            await loop.run_in_executor(
                None,
                run_command,
                'git add . && git commit -m "auto: code update" && git push origin main',
                Config.MOBILE_DIR,
                300,
            )

        # Then push parent repo
        return await loop.run_in_executor(
            None,
            run_command,
            'git add . && git commit -m "auto: code update" && git push origin main',
            Config.NACPAC_DIR,
            300,
        )
