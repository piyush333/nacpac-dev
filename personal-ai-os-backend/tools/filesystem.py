"""Filesystem tools."""

from pathlib import Path
from tool_registry import ToolRegistry


def read_file(path: str) -> dict:
    """Read a file."""
    try:
        file_path = Path(path)

        if not file_path.exists():
            return {"success": False, "error": f"File not found: {path}"}

        if not file_path.is_file():
            return {"success": False, "error": f"Not a file: {path}"}

        with open(file_path, 'r') as f:
            content = f.read()

        return {
            "success": True,
            "path": path,
            "size": len(content),
            "content": content
        }

    except Exception as e:
        return {"success": False, "error": str(e)}


def write_file(path: str, content: str) -> dict:
    """Write to a file."""
    try:
        file_path = Path(path)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, 'w') as f:
            f.write(content)

        return {
            "success": True,
            "path": path,
            "message": f"Wrote {len(content)} bytes"
        }

    except Exception as e:
        return {"success": False, "error": str(e)}


def list_files(path: str = ".") -> dict:
    """List files in a directory."""
    try:
        dir_path = Path(path)

        if not dir_path.exists():
            return {"success": False, "error": f"Path not found: {path}"}

        if not dir_path.is_dir():
            return {"success": False, "error": f"Not a directory: {path}"}

        items = []
        for item in sorted(dir_path.iterdir()):
            if item.is_dir():
                items.append(f"[DIR]  {item.name}/")
            else:
                size = item.stat().st_size
                items.append(f"[FILE] {item.name} ({size} bytes)")

        return {
            "success": True,
            "path": path,
            "items": items,
            "count": len(items)
        }

    except Exception as e:
        return {"success": False, "error": str(e)}


# Register tools
ToolRegistry.register(
    "filesystem.read",
    read_file,
    "Read a file from the filesystem",
    {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "File path to read"}
        },
        "required": ["path"]
    }
)

ToolRegistry.register(
    "filesystem.write",
    write_file,
    "Write to a file",
    {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "File path to write to"},
            "content": {"type": "string", "description": "Content to write"}
        },
        "required": ["path", "content"]
    }
)

ToolRegistry.register(
    "filesystem.list",
    list_files,
    "List files in a directory",
    {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Directory path (default: current)"}
        },
        "required": []
    }
)
