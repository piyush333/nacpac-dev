"""Feature Implementation Agent - handles codebase modifications based on natural language requests."""

import logging
import os
import subprocess
import json
from datetime import datetime
from pathlib import Path
from anthropic import Anthropic

from agentic.config import SONNET_MODEL, GITHUB_TOKEN
from agentic.tools.git_tools import git_tools
from agentic.memory import memory

logger = logging.getLogger(__name__)

client = Anthropic()


class FeatureAgent:
    """Agent for implementing features via codebase modifications."""

    def __init__(self, brand: str, repo_url: str, repo_path: str):
        self.brand = brand
        self.repo_url = repo_url
        self.repo_path = repo_path
        self.conversation_history = []
        self._ensure_repo_cloned()

    def _ensure_repo_cloned(self):
        """Clone repo if not already cloned."""
        if not os.path.exists(self.repo_path):
            try:
                clone_url = self.repo_url
                if GITHUB_TOKEN and "github.com" in clone_url:
                    clone_url = clone_url.replace("https://", f"https://{GITHUB_TOKEN}@")

                logger.info(f"Cloning {self.brand} repo to {self.repo_path}")
                subprocess.run(
                    ["git", "clone", clone_url, self.repo_path],
                    check=True,
                    capture_output=True,
                    timeout=300
                )
                logger.info(f"✅ Cloned {self.brand} repo")
            except Exception as e:
                logger.error(f"Failed to clone repo: {e}")
                raise

    def analyze_codebase(self) -> str:
        """Analyze codebase structure and return summary."""
        logger.info(f"Analyzing {self.brand} codebase...")

        analysis = {
            "repo_path": self.repo_path,
            "structure": self._get_directory_structure(),
            "key_files": self._get_key_files(),
            "tech_stack": self._detect_tech_stack(),
        }

        return json.dumps(analysis, indent=2)

    def _get_directory_structure(self) -> dict:
        """Get repo directory structure."""
        structure = {}
        for root, dirs, files in os.walk(self.repo_path):
            # Skip hidden and common non-essential dirs
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '.git']]

            level = root.replace(self.repo_path, '').count(os.sep)
            if level < 3:  # Limit depth
                rel_path = os.path.relpath(root, self.repo_path)
                structure[rel_path] = [f for f in files if not f.startswith('.')]

        return structure

    def _get_key_files(self) -> list:
        """Find key files (package.json, app.json, main.js, etc)."""
        key_files = [
            'package.json', 'app.json', 'main.js', 'main.ts',
            'index.js', 'App.tsx', 'App.js', 'tsconfig.json',
            'webpack.config.js', 'eas.json', '.env'
        ]

        found_files = []
        for root, dirs, files in os.walk(self.repo_path):
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != 'node_modules']
            for key_file in key_files:
                if key_file in files:
                    full_path = os.path.join(root, key_file)
                    rel_path = os.path.relpath(full_path, self.repo_path)
                    found_files.append(rel_path)

        return found_files

    def _detect_tech_stack(self) -> dict:
        """Detect tech stack from files."""
        stack = {
            "mobile": None,
            "desktop": None,
            "backend": None
        }

        # Check for mobile
        if os.path.exists(os.path.join(self.repo_path, "mobile", "app.json")):
            stack["mobile"] = "React Native (Expo)"
        elif os.path.exists(os.path.join(self.repo_path, "mobile", "package.json")):
            stack["mobile"] = "React Native"

        # Check for desktop
        if os.path.exists(os.path.join(self.repo_path, "desktop", "main.js")):
            stack["desktop"] = "Electron"
        elif os.path.exists(os.path.join(self.repo_path, "desktop", "package.json")):
            with open(os.path.join(self.repo_path, "desktop", "package.json")) as f:
                pkg = json.load(f)
                if "electron" in pkg.get("dependencies", {}):
                    stack["desktop"] = "Electron"

        return stack

    def propose_changes(self, feature_request: str) -> dict:
        """Use Claude to propose code changes for a feature request."""
        logger.info(f"Proposing changes for: {feature_request}")

        # Analyze codebase
        codebase_analysis = self.analyze_codebase()

        # Get conversation history context
        system_prompt = f"""You are an expert developer helping implement features in a {self.brand} application.

Codebase Analysis:
{codebase_analysis}

Your job is to:
1. Understand the feature request
2. Analyze what files need to be modified
3. Propose specific code changes
4. Explain each change clearly

Format your response as JSON with:
{{
  "summary": "Brief description of changes",
  "files_to_modify": [
    {{
      "path": "path/to/file.tsx",
      "action": "modify|create|delete",
      "reason": "Why this change",
      "current_snippet": "Current code (if modifying)",
      "new_code": "New code to apply"
    }}
  ],
  "risks": ["Any potential issues"],
  "testing_notes": "How to test these changes"
}}"""

        self.conversation_history.append({
            "role": "user",
            "content": f"Feature Request: {feature_request}"
        })

        response = client.messages.create(
            model=SONNET_MODEL,
            max_tokens=4096,
            system=system_prompt,
            messages=self.conversation_history
        )

        assistant_message = response.content[0].text
        self.conversation_history.append({
            "role": "assistant",
            "content": assistant_message
        })

        logger.info(f"Claude proposed changes")

        try:
            # Try to extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', assistant_message, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return {"raw_response": assistant_message}
        except:
            return {"raw_response": assistant_message}

    def apply_changes(self, proposal: dict, task_id: str) -> dict:
        """Apply proposed changes to the codebase."""
        logger.info(f"Applying changes for task {task_id}")

        try:
            # Create feature branch
            branch_name = f"feature/{task_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            git_tools.create_branch(self.repo_path, branch_name)
            logger.info(f"✅ Created branch: {branch_name}")

            # Apply file modifications
            files_modified = 0
            for file_change in proposal.get("files_to_modify", []):
                path = file_change.get("path")
                action = file_change.get("action")
                new_code = file_change.get("new_code")

                full_path = os.path.join(self.repo_path, path)

                if action == "create":
                    os.makedirs(os.path.dirname(full_path), exist_ok=True)
                    with open(full_path, "w") as f:
                        f.write(new_code)
                    logger.info(f"✅ Created: {path}")
                    files_modified += 1

                elif action == "modify":
                    if os.path.exists(full_path):
                        with open(full_path, "w") as f:
                            f.write(new_code)
                        logger.info(f"✅ Modified: {path}")
                        files_modified += 1
                    else:
                        logger.warning(f"File not found: {path}")

            # Commit changes
            commit_msg = f"Implement: {proposal.get('summary', 'Feature update')}"
            git_tools.commit_and_push(
                self.repo_path,
                commit_msg,
                branch_name
            )
            logger.info(f"✅ Committed and pushed to {branch_name}")

            return {
                "status": "success",
                "branch": branch_name,
                "files_modified": files_modified,
                "message": f"Applied {files_modified} file changes to {branch_name}"
            }

        except Exception as e:
            logger.error(f"Failed to apply changes: {e}")
            return {
                "status": "failed",
                "message": str(e)
            }

    def implement_feature(self, feature_request: str, task_id: str) -> dict:
        """Full workflow: propose → user approve → apply → build."""
        logger.info(f"Task {task_id}: Implementing feature: {feature_request}")

        # Step 1: Propose changes
        proposal = self.propose_changes(feature_request)
        logger.info(f"Proposal: {json.dumps(proposal, indent=2)[:500]}")

        # Return proposal for user approval
        return {
            "status": "proposal_ready",
            "task_id": task_id,
            "feature_request": feature_request,
            "proposal": proposal
        }


# Instance creation helpers
nacpac_feature_agent = None
jico_feature_agent = None


def get_nacpac_feature_agent():
    """Get or create NacPac feature agent."""
    global nacpac_feature_agent
    if nacpac_feature_agent is None:
        nacpac_feature_agent = FeatureAgent(
            brand="nacpac",
            repo_url="https://github.com/jico-org/nacpac-workspace.git",
            repo_path="/tmp/nacpac-workspace"
        )
    return nacpac_feature_agent


def get_jico_feature_agent():
    """Get or create Jico Life feature agent."""
    global jico_feature_agent
    if jico_feature_agent is None:
        jico_feature_agent = FeatureAgent(
            brand="jico_life",
            repo_url="https://github.com/jico-org/jico-workspace.git",
            repo_path="/tmp/jico-workspace"
        )
    return jico_feature_agent
