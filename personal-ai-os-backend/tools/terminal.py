"""Terminal/command execution tools."""

import subprocess
from tool_registry import ToolRegistry


def run_command(command: str, cwd: str = None, timeout: int = 30) -> dict:
    """Run a terminal command."""
    try:
        # Safety checks
        dangerous_commands = ["rm -rf", "sudo", "chmod 777", "dd if="]
        for dangerous in dangerous_commands:
            if dangerous in command.lower():
                return {
                    "success": False,
                    "error": f"Command blocked for safety: {dangerous}"
                }

        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout
        )

        return {
            "success": result.returncode == 0,
            "command": command,
            "return_code": result.returncode,
            "stdout": result.stdout[:2000],  # Limit output
            "stderr": result.stderr[:2000]
        }

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": f"Command timed out after {timeout}s"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


# Register tool
ToolRegistry.register(
    "terminal.run",
    run_command,
    "Run a terminal command",
    {
        "type": "object",
        "properties": {
            "command": {"type": "string", "description": "Command to run"},
            "cwd": {"type": "string", "description": "Working directory (optional)"},
            "timeout": {"type": "integer", "description": "Timeout in seconds (default: 30)"}
        },
        "required": ["command"]
    }
)
