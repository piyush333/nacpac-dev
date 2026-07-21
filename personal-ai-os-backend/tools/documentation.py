"""Documentation and file reading tools."""

from pathlib import Path
from tool_registry import ToolRegistry


def read_markdown(path: str) -> dict:
    """Read and parse a markdown file."""
    try:
        file_path = Path(path)

        if not file_path.exists():
            return {"success": False, "error": f"File not found: {path}"}

        if not file_path.suffix.lower() in ['.md', '.markdown']:
            return {"success": False, "error": "File is not markdown"}

        with open(file_path, 'r') as f:
            content = f.read()

        # Simple heading extraction
        lines = content.split('\n')
        headings = [line for line in lines if line.startswith('#')]

        return {
            "success": True,
            "path": path,
            "headings": headings,
            "word_count": len(content.split()),
            "preview": content[:500] + "..." if len(content) > 500 else content
        }

    except Exception as e:
        return {"success": False, "error": str(e)}


def summarize_directory(path: str) -> dict:
    """Summarize contents of a directory (README, documentation structure)."""
    try:
        dir_path = Path(path)

        if not dir_path.exists():
            return {"success": False, "error": f"Path not found: {path}"}

        if not dir_path.is_dir():
            return {"success": False, "error": f"Not a directory: {path}"}

        # Look for README files
        readme_files = [f for f in dir_path.glob("*") if f.name.upper().startswith("README")]
        docs = [f for f in dir_path.glob("*") if f.is_dir() and f.name.lower() in ["docs", "documentation"]]

        summary = {
            "success": True,
            "path": path,
            "readme_files": [f.name for f in readme_files],
            "doc_directories": [f.name for f in docs],
            "total_files": len([f for f in dir_path.rglob("*") if f.is_file()])
        }

        # Read first README if found
        if readme_files:
            with open(readme_files[0], 'r') as f:
                summary["readme_preview"] = f.read()[:1000]

        return summary

    except Exception as e:
        return {"success": False, "error": str(e)}


# Register tools
ToolRegistry.register(
    "documentation.read",
    read_markdown,
    "Read a markdown documentation file",
    {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Path to markdown file"}
        },
        "required": ["path"]
    }
)

ToolRegistry.register(
    "documentation.summarize",
    summarize_directory,
    "Summarize documentation in a directory",
    {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Directory path"}
        },
        "required": ["path"]
    }
)
