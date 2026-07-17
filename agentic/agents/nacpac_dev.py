"""NacPac Dev Agent - handles code, builds (APK/EXE), deployments."""

import logging
import os
import subprocess
import time
from datetime import datetime
from agentic.config import NACPAC_REPO_PATH, EAS_BUILD_PROFILE, SONNET_MODEL
from agentic.tools.git_tools import git_tools
from agentic.tools.build_tools import build_tools
from agentic.tools.deploy_tools import deploy_tools
from agentic.tools.backup_tools import backup_tools
from agentic.memory import memory
from agentic.cost_tracker import cost_tracker
from agentic.learn_from_task import get_patterns_for_task, capture_pattern
from agentic.agents.feature_agent import get_nacpac_feature_agent

logger = logging.getLogger(__name__)


class NacPacDevAgent:
    """Dev agent for NacPac brand."""

    def __init__(self):
        self.brand = "nacpac"
        self.agent_id = "nacpac_dev"
        self.repo_path = NACPAC_REPO_PATH
        self.model = SONNET_MODEL
        self.skillsets = {}
        self._load_skillsets()
        self._ensure_repo_cloned()
        logger.info(f"NacPac Dev Agent initialized (repo: {self.repo_path}, skillsets: {list(self.skillsets.keys())})")

    def _load_skillsets(self):
        """Load agent skillsets from Supabase."""
        self.skillsets = memory.get_agent_skillsets(self.agent_id)
        if self.skillsets:
            logger.info(f"Loaded skillsets: {', '.join(self.skillsets.keys())}")
        else:
            logger.warning(f"No skillsets found for {self.agent_id} in Supabase")

    def get_skillsets_context(self) -> str:
        """Format skillsets as context string for Claude."""
        if not self.skillsets:
            return "No skillsets loaded."

        context_lines = ["Your technical skillsets:", ""]
        for name, details in self.skillsets.items():
            context_lines.append(f"• {name.upper()}")
            if details.get("description"):
                context_lines.append(f"  Description: {details['description']}")
            if details.get("documentation"):
                context_lines.append(f"  Knowledge: {details['documentation'][:200]}...")  # Truncate for context
            context_lines.append("")

        return "\n".join(context_lines)

    def get_learned_patterns_context(self, task_description: str) -> str:
        """Get learned patterns relevant to this task."""
        patterns = get_patterns_for_task(task_description, self.agent_id)

        if not patterns:
            return "No learned patterns available for this task type."

        # Show top 3 patterns with highest success rates
        context_lines = ["Learned patterns from past tasks:", ""]
        for pattern in patterns[:3]:
            success_rate = pattern.get("success_rate", 0) or 0
            ptype = pattern.get("pattern_type", "unknown")
            desc = pattern.get("pattern_description", "")

            context_lines.append(f"• [{ptype}] {desc}")
            context_lines.append(f"  Success rate: {success_rate:.0%}")

            # Show examples if available
            examples = pattern.get("examples", []) or []
            if examples:
                context_lines.append(f"  Example: {examples[0].get('description', '')}")

            context_lines.append("")

        return "\n".join(context_lines)

    def get_system_prompt_with_skillsets(self) -> str:
        """Get system prompt with skillsets injected for Claude decision-making."""
        prompt = f"""You are the {self.brand.upper()} Dev Agent (agent_id: {self.agent_id}).

Your role is to handle code development, building (APK/EXE), and deployments for the {self.brand.upper()} application.

{self.get_skillsets_context()}

When executing tasks:
1. Use your skillset knowledge to make informed decisions
2. Refer to the NacPac codebase skillset for architecture understanding
3. Use Python/Node.js/React knowledge for implementation
4. Follow Expo/npm/Windows-specific tooling best practices
5. Document your decisions in task logs"""

        return prompt

    def _ensure_repo_cloned(self):
        """If repo_path is a GitHub URL, clone it to local /tmp path."""
        if self.repo_path.startswith("http://") or self.repo_path.startswith("https://"):
            logger.info(f"Repo path is URL: {self.repo_path}, cloning to local...")
            local_path = "/tmp/nacpac-workspace"

            # Check if we need to clone
            if not os.path.exists(local_path):
                clone_url = self.repo_path
                github_token = os.getenv("GITHUB_TOKEN")

                logger.info(f"GitHub token present: {bool(github_token)}")

                if github_token and "github.com" in clone_url:
                    clone_url = clone_url.replace("https://", f"https://{github_token}@")
                    logger.info("Using GitHub token for private repo auth")

                logger.info(f"Attempting to clone from: {clone_url}")
                result = subprocess.run(
                    ["git", "clone", clone_url, local_path],
                    capture_output=True,
                    text=True,
                    timeout=300
                )

                if result.returncode != 0:
                    logger.error(f"Git clone failed with exit code {result.returncode}")
                    logger.error(f"Git stderr: {result.stderr}")
                    logger.error(f"Git stdout: {result.stdout}")
                    logger.warning(f"Clone failed, but continuing with local_path: {local_path}")
                else:
                    logger.info(f"✅ Cloned to {local_path}")
            else:
                logger.info(f"Directory {local_path} already exists, skipping clone")

            # Always update to local path, whether clone succeeded or not
            self.repo_path = local_path
            logger.info(f"Updated repo_path to local: {self.repo_path}")

    def get_current_state(self) -> dict:
        """Get current branch, commit, etc."""
        branch = git_tools.get_current_branch(self.repo_path)
        commit = git_tools.get_last_commit(self.repo_path)
        status = git_tools.status(self.repo_path)

        brand_state = memory.get_brand_state(self.brand)

        return {
            "branch": branch,
            "commit": commit,
            "status": status,
            "memory": brand_state
        }

    def build_apk(self, task_id: str, profile: str = None) -> dict:
        """Build APK via EAS.

        Requires manual approval before proceeding (handled by Discord bot).
        """
        if not profile:
            profile = EAS_BUILD_PROFILE

        logger.info(f"Task {task_id}: Building APK (profile={profile})")

        # Inject learned patterns before execution
        patterns_context = self.get_learned_patterns_context("build APK")
        if patterns_context:
            logger.info(f"Learned patterns:\n{patterns_context}")

        memory.update_nacpac_task(task_id, "in_progress", "Building APK...")

        git_tools.pull(self.repo_path)

        success, output = build_tools.build_apk(self.repo_path, profile)

        if not success:
            logger.error(f"APK build failed: {output}")
            memory.update_nacpac_task(task_id, "failed", f"APK build failed: {output[:200]}")

            # Capture failure pattern
            capture_pattern(
                task_id=task_id,
                outcome="failure",
                pattern_type="failure",
                pattern_description=f"APK build failed: {output[:100]}",
                failure_reason=output[:200],
                agent_id=self.agent_id
            )

            return {"status": "failed", "message": f"APK build failed: {output[:200]}"}

        commit = git_tools.get_last_commit(self.repo_path) or "unknown-commit"
        memory.log_build(self.brand, "apk", commit, output, status="success")

        backup_results = backup_tools.backup_all_platforms(
            output,
            "apk",
            self.brand
        )

        branch = git_tools.get_current_branch(self.repo_path)
        memory.update_brand_state(self.brand, current_branch=branch, last_commit=commit)

        result_msg = f"APK built (commit: {commit[:8]}). Backups: R2={backup_results['r2']}, GDrive={backup_results['gdrive']}"
        memory.update_nacpac_task(task_id, "completed", result_msg)

        # Log run execution (Phase 3 memory tracking)
        memory.log_nacpac_run(task_id, self.model, tokens_in=0, tokens_out=0, cost_usd=0.0)

        # Capture success pattern
        capture_pattern(
            task_id=task_id,
            outcome="success",
            pattern_type="success",
            pattern_description="APK build succeeded with valid package.json and profile configuration",
            example=f"Built APK successfully with profile={profile}, commit={commit[:8]}",
            agent_id=self.agent_id
        )

        return {
            "status": "success",
            "message": result_msg,
            "build_type": "apk",
            "commit": commit,
            "link": output,
            "backups": backup_results
        }

    def build_exe(self, task_id: str) -> dict:
        """Build EXE for Windows (Desktop app)."""
        logger.info(f"Task {task_id}: Building EXE")

        # Inject learned patterns before execution
        patterns_context = self.get_learned_patterns_context("build EXE")
        if patterns_context:
            logger.info(f"Learned patterns:\n{patterns_context}")

        memory.update_nacpac_task(task_id, "in_progress", "Building EXE...")

        git_tools.pull(self.repo_path)

        success, output = build_tools.build_exe(self.repo_path)

        if not success:
            logger.error(f"EXE build failed: {output}")
            memory.update_nacpac_task(task_id, "failed", f"EXE build failed: {output[:200]}")

            # Capture failure pattern
            capture_pattern(
                task_id=task_id,
                outcome="failure",
                pattern_type="failure",
                pattern_description=f"EXE build failed: {output[:100]}",
                failure_reason=output[:200],
                agent_id=self.agent_id
            )

            return {"status": "failed", "message": f"EXE build failed: {output[:200]}"}

        commit = git_tools.get_last_commit(self.repo_path) or "unknown-commit"
        memory.log_build(self.brand, "exe", commit, output, status="success")

        backup_results = backup_tools.backup_all_platforms(
            output,
            "exe",
            self.brand
        )

        branch = git_tools.get_current_branch(self.repo_path)
        memory.update_brand_state(self.brand, current_branch=branch, last_commit=commit)

        result_msg = f"EXE built (commit: {commit[:8]}). Backups: R2={backup_results['r2']}, GDrive={backup_results['gdrive']}"
        memory.update_nacpac_task(task_id, "completed", result_msg)

        # Log run execution (Phase 3 memory tracking)
        memory.log_nacpac_run(task_id, self.model, tokens_in=0, tokens_out=0, cost_usd=0.0)

        # Capture success pattern
        capture_pattern(
            task_id=task_id,
            outcome="success",
            pattern_type="success",
            pattern_description="EXE build succeeded with valid npm build configuration",
            example=f"Built EXE successfully, commit={commit[:8]}",
            agent_id=self.agent_id
        )

        return {
            "status": "success",
            "message": result_msg,
            "build_type": "exe",
            "commit": commit,
            "link": output,
            "backups": backup_results
        }

    def deploy_to_staging(self, task_id: str, artifact: str = "apk") -> dict:
        """Deploy to staging environment."""
        logger.info(f"Task {task_id}: Deploying {artifact} to staging")

        # Inject learned patterns before execution
        patterns_context = self.get_learned_patterns_context(f"deploy {artifact}")
        if patterns_context:
            logger.info(f"Learned patterns:\n{patterns_context}")

        memory.update_nacpac_task(task_id, "in_progress", f"Deploying {artifact} to staging...")

        result = deploy_tools.deploy_to_env(self.repo_path, "staging", artifact)

        if not result.get("success"):
            memory.update_nacpac_task(task_id, "failed", result.get("message", "Deploy failed"))

            # Capture failure pattern
            capture_pattern(
                task_id=task_id,
                outcome="failure",
                pattern_type="failure",
                pattern_description=f"Deployment failed: {result.get('message', 'Unknown error')[:80]}",
                failure_reason=result.get("message", "Deploy failed"),
                agent_id=self.agent_id
            )

            return {"status": "failed", "message": result.get("message", "Deploy failed")}

        commit = git_tools.get_last_commit(self.repo_path)
        memory.log_deployment(self.brand, "staging", commit)
        memory.update_brand_state(self.brand, last_deploy_env="staging")
        memory.update_nacpac_task(task_id, "completed", f"Deployed to staging")

        # Log run execution (Phase 3 memory tracking)
        memory.log_nacpac_run(task_id, self.model, tokens_in=0, tokens_out=0, cost_usd=0.0)

        # Capture success pattern
        capture_pattern(
            task_id=task_id,
            outcome="success",
            pattern_type="success",
            pattern_description=f"Deployment to staging succeeded for {artifact}",
            example=f"Deployed {artifact} to staging successfully",
            agent_id=self.agent_id
        )

        return {
            "status": "success",
            "message": f"Deployed {artifact} to staging",
            "environment": "staging"
        }

    def propose_feature_changes(self, task_id: str, feature_request: str) -> dict:
        """Propose code changes for a feature request (Phase 4).

        Uses feature_agent to analyze codebase and propose changes via Claude.
        Returns proposal JSON for Discord approval flow.
        """
        logger.info(f"Task {task_id}: Proposing changes for: {feature_request}")

        # Inject agent skillsets into context
        skillsets_context = self.get_skillsets_context()
        request_with_context = f"""Feature Request: {feature_request}

Agent Skillsets Available:
{skillsets_context}

Learned Patterns:
{self.get_learned_patterns_context(feature_request)}"""

        try:
            # Get feature agent and propose changes
            feature_agent = get_nacpac_feature_agent()
            proposal = feature_agent.propose_changes(request_with_context)

            # Log proposal in task history
            memory.update_nacpac_task(
                task_id,
                "in_progress",
                f"Proposal ready: {len(proposal.get('files_to_modify', []))} files to modify"
            )

            logger.info(f"✅ Proposal generated for task {task_id}: {len(proposal.get('files_to_modify', []))} files")

            return {
                "status": "proposal_ready",
                "task_id": task_id,
                "feature_request": feature_request,
                "proposal": proposal
            }

        except Exception as e:
            logger.error(f"Failed to propose changes: {e}")
            memory.update_nacpac_task(task_id, "failed", f"Proposal generation failed: {str(e)[:200]}")

            # Capture failure pattern
            capture_pattern(
                task_id=task_id,
                outcome="failure",
                pattern_type="failure",
                pattern_description=f"Feature proposal failed: {str(e)[:100]}",
                failure_reason=str(e)[:200],
                agent_id=self.agent_id
            )

            return {
                "status": "failed",
                "message": f"Failed to generate proposal: {str(e)[:200]}"
            }

    def apply_feature_changes(self, task_id: str, proposal: dict) -> dict:
        """Apply proposed code changes to codebase (Phase 4).

        Applies changes from proposal, commits to feature branch, and logs the update.
        """
        logger.info(f"Task {task_id}: Applying feature changes")

        memory.update_nacpac_task(task_id, "in_progress", "Applying code changes...")

        try:
            # Get feature agent and apply changes
            feature_agent = get_nacpac_feature_agent()
            apply_result = feature_agent.apply_changes(proposal, task_id)

            if apply_result.get("status") != "success":
                logger.error(f"Failed to apply changes: {apply_result.get('message')}")
                memory.update_nacpac_task(
                    task_id,
                    "failed",
                    f"Failed to apply changes: {apply_result.get('message', 'Unknown error')[:200]}"
                )

                # Capture failure pattern
                capture_pattern(
                    task_id=task_id,
                    outcome="failure",
                    pattern_type="failure",
                    pattern_description="Failed to apply feature changes to codebase",
                    failure_reason=apply_result.get("message", "Unknown error")[:200],
                    agent_id=self.agent_id
                )

                return {
                    "status": "failed",
                    "message": apply_result.get("message", "Failed to apply changes")
                }

            # Success: log the applied changes
            branch = apply_result.get("branch", "unknown-branch")
            files_modified = apply_result.get("files_modified", 0)

            result_msg = f"Applied {files_modified} file changes on branch {branch}"
            memory.update_nacpac_task(task_id, "completed", result_msg)

            # Log run execution (Phase 3 memory tracking)
            memory.log_nacpac_run(task_id, self.model, tokens_in=0, tokens_out=0, cost_usd=0.0)

            # Capture success pattern
            capture_pattern(
                task_id=task_id,
                outcome="success",
                pattern_type="success",
                pattern_description=f"Successfully applied feature changes ({files_modified} files)",
                example=f"Feature changes applied on branch {branch}",
                agent_id=self.agent_id
            )

            logger.info(f"✅ Changes applied: {result_msg}")

            return {
                "status": "success",
                "message": result_msg,
                "branch": branch,
                "files_modified": files_modified
            }

        except Exception as e:
            logger.error(f"Exception applying changes: {e}")
            memory.update_nacpac_task(task_id, "failed", f"Error: {str(e)[:200]}")

            # Capture failure pattern
            capture_pattern(
                task_id=task_id,
                outcome="failure",
                pattern_type="failure",
                pattern_description=f"Exception while applying feature: {str(e)[:100]}",
                failure_reason=str(e)[:200],
                agent_id=self.agent_id
            )

            return {
                "status": "failed",
                "message": f"Exception: {str(e)[:200]}"
            }

    def build_with_progress_tracking(self, task_id: str, build_type: str, profile: str = None) -> dict:
        """Build APK or EXE with progress tracking (Phase 5).

        Tracks build start/end times, logs progress updates, handles retries on failure.
        """
        logger.info(f"Task {task_id}: Building {build_type.upper()} with progress tracking")

        start_time = datetime.utcnow()
        memory.update_nacpac_task(task_id, "in_progress", f"Starting {build_type} build...")

        try:
            if build_type.lower() == "apk":
                result = self.build_apk(task_id, profile)
            elif build_type.lower() == "exe":
                result = self.build_exe(task_id)
            else:
                logger.error(f"Unknown build type: {build_type}")
                memory.update_nacpac_task(task_id, "failed", f"Unknown build type: {build_type}")
                return {"status": "failed", "message": f"Unknown build type: {build_type}"}

            # Calculate build duration and cost
            build_duration = (datetime.utcnow() - start_time).total_seconds()
            estimated_cost = self._estimate_build_cost(build_type, build_duration)

            if result.get("status") == "success":
                logger.info(f"✅ {build_type.upper()} build completed in {build_duration:.0f}s (estimated cost: ${estimated_cost:.4f})")

                # Update task with cost tracking
                memory.update_nacpac_task(
                    task_id,
                    "completed",
                    result.get("message"),
                    cost_usd=estimated_cost
                )

                # Log run with cost
                memory.log_nacpac_run(
                    task_id,
                    self.model,
                    tokens_in=0,
                    tokens_out=0,
                    cost_usd=estimated_cost
                )

                return {
                    "status": "success",
                    "build_type": build_type,
                    "duration_seconds": build_duration,
                    "cost_usd": estimated_cost,
                    "message": result.get("message"),
                    "link": result.get("link"),
                    "commit": result.get("commit"),
                    "backups": result.get("backups")
                }
            else:
                logger.error(f"❌ {build_type.upper()} build failed after {build_duration:.0f}s")
                memory.update_nacpac_task(
                    task_id,
                    "failed",
                    f"Build failed: {result.get('message', 'Unknown error')[:200]}"
                )

                return {
                    "status": "failed",
                    "build_type": build_type,
                    "duration_seconds": build_duration,
                    "message": result.get("message", "Build failed")
                }

        except Exception as e:
            logger.error(f"Exception during build: {e}")
            build_duration = (datetime.utcnow() - start_time).total_seconds()
            memory.update_nacpac_task(task_id, "failed", f"Build exception: {str(e)[:200]}")

            return {
                "status": "failed",
                "build_type": build_type,
                "duration_seconds": build_duration,
                "message": f"Build exception: {str(e)[:200]}"
            }

    def _estimate_build_cost(self, build_type: str, duration_seconds: float) -> float:
        """Estimate build cost based on type and duration (Phase 5).

        Estimates cost for EAS builds (pay per minute) and local builds (compute cost).
        """
        if build_type.lower() == "apk":
            # EAS charges approximately $0.10 per build
            # Additional estimate for tokens/compute: ~$0.01 per minute
            base_cost = 0.10
            duration_minutes = duration_seconds / 60
            compute_cost = min(duration_minutes * 0.01, 0.50)  # Cap at $0.50
            return base_cost + compute_cost

        elif build_type.lower() == "exe":
            # Local build on runner, compute cost only
            # Estimate ~$0.001 per second of build time
            return max(duration_seconds * 0.001, 0.05)  # Minimum $0.05

        return 0.0

    def retry_failed_build(self, task_id: str, build_type: str, profile: str = None, max_retries: int = 2) -> dict:
        """Retry a failed build with exponential backoff (Phase 5).

        Retries failed builds with increasing wait times between attempts.
        Logs each retry attempt.
        """
        logger.info(f"Task {task_id}: Retrying {build_type} build (max {max_retries} attempts)")

        for attempt in range(1, max_retries + 1):
            logger.info(f"Build attempt {attempt}/{max_retries}")

            result = self.build_with_progress_tracking(task_id, build_type, profile)

            if result.get("status") == "success":
                logger.info(f"✅ Build succeeded on attempt {attempt}")
                return result

            # Exponential backoff: 2s, 4s, 8s...
            if attempt < max_retries:
                wait_time = 2 ** attempt
                logger.warning(f"Attempt {attempt} failed, waiting {wait_time}s before retry...")
                time.sleep(wait_time)

        logger.error(f"❌ All {max_retries} build attempts failed")
        memory.update_nacpac_task(
            task_id,
            "failed",
            f"Build failed after {max_retries} retry attempts"
        )

        return {
            "status": "failed",
            "build_type": build_type,
            "message": f"Build failed after {max_retries} attempts"
        }

    def get_build_status(self, task_id: str) -> dict:
        """Get current build status for a task (Phase 5).

        Queries nacpac_tasks table for task status and completion info.
        """
        if not memory.client:
            logger.warning("Memory unavailable; cannot get build status")
            return {"status": "unknown"}

        try:
            result = memory.client.table("nacpac_tasks").select("*").eq("id", task_id).execute()
            if result.data:
                task = result.data[0]
                return {
                    "status": task.get("status"),
                    "result_summary": task.get("result_summary", ""),
                    "cost_usd": task.get("cost_usd", 0.0),
                    "created_at": task.get("created_at"),
                    "completed_at": task.get("completed_at"),
                    "is_complete": task.get("status") in ["completed", "failed"]
                }
            return {"status": "not_found"}
        except Exception as e:
            logger.error(f"Failed to get build status: {e}")
            return {"status": "error", "message": str(e)[:200]}


nacpac_dev_agent = NacPacDevAgent()
