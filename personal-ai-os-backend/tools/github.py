"""GitHub tools."""

import subprocess
import os
from pathlib import Path
from tool_registry import ToolRegistry


def clone_repository(url: str, target_path: str) -> dict:
    """Clone a GitHub repository."""
    try:
        # Ensure parent directory exists
        Path(target_path).parent.mkdir(parents=True, exist_ok=True)

        result = subprocess.run(
            ["git", "clone", url, target_path],
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode == 0:
            return {
                "success": True,
                "message": f"Cloned {url} to {target_path}",
                "output": result.stdout
            }
        else:
            return {
                "success": False,
                "error": result.stderr
            }

    except Exception as e:
        return {"success": False, "error": str(e)}


def list_repositories(username: str = None) -> dict:
    """List GitHub repositories (placeholder)."""
    return {
        "success": True,
        "message": "Use 'ls' or 'filesystem' tools to explore local repos"
    }


def commit_and_push(repo_path: str, message: str) -> dict:
    """Commit changes and push to origin."""
    try:
        # Add all changes
        subprocess.run(
            ["git", "add", "."],
            cwd=repo_path,
            capture_output=True,
            check=True
        )

        # Commit
        result = subprocess.run(
            ["git", "commit", "-m", message],
            cwd=repo_path,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            return {"success": False, "error": result.stderr}

        # Push
        push_result = subprocess.run(
            ["git", "push"],
            cwd=repo_path,
            capture_output=True,
            text=True
        )

        if push_result.returncode == 0:
            return {
                "success": True,
                "message": f"Committed and pushed: {message}",
                "output": push_result.stdout
            }
        else:
            return {
                "success": False,
                "error": push_result.stderr
            }

    except Exception as e:
        return {"success": False, "error": str(e)}


# Register tools
ToolRegistry.register(
    "github.clone",
    clone_repository,
    "Clone a GitHub repository",
    {
        "type": "object",
        "properties": {
            "url": {"type": "string", "description": "GitHub repository URL"},
            "target_path": {"type": "string", "description": "Local path to clone to"}
        },
        "required": ["url", "target_path"]
    }
)

ToolRegistry.register(
    "github.commit_and_push",
    commit_and_push,
    "Commit changes and push to GitHub",
    {
        "type": "object",
        "properties": {
            "repo_path": {"type": "string", "description": "Path to the repository"},
            "message": {"type": "string", "description": "Commit message"}
        },
        "required": ["repo_path", "message"]
    }
)
