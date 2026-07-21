"""Tests for tool functionality."""

import pytest
import os
import tempfile
from tools.filesystem import read_file, write_file, list_files
from tools.terminal import run_command
from tools.documentation import read_markdown, summarize_directory
from tools.email import send_email


class TestFilesystemTools:
    """Test filesystem operations."""

    def test_write_and_read_file(self):
        """Test writing and reading a file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "test.txt")
            content = "Test content"

            # Write
            result = write_file(filepath, content)
            assert result["success"] is True
            assert "Wrote" in result["message"]

            # Read
            result = read_file(filepath)
            assert result["success"] is True
            assert result["content"] == content

    def test_read_nonexistent_file(self):
        """Test reading a non-existent file."""
        result = read_file("/nonexistent/file.txt")
        assert result["success"] is False
        assert "not found" in result["error"].lower()

    def test_list_files(self):
        """Test listing directory contents."""
        result = list_files("/tmp")
        assert result["success"] is True
        assert "items" in result
        assert result["count"] >= 0


class TestTerminalTools:
    """Test terminal command execution."""

    def test_simple_command(self):
        """Test running a simple command."""
        result = run_command("echo 'hello world'")
        assert result["success"] is True
        assert "hello world" in result["stdout"]

    def test_blocked_dangerous_command(self):
        """Test that dangerous commands are blocked."""
        result = run_command("rm -rf /tmp/*")
        assert result["success"] is False
        assert "blocked" in result["error"].lower()

    def test_command_with_timeout(self):
        """Test command execution with timeout."""
        result = run_command("sleep 1", timeout=5)
        assert result["success"] is True

    def test_failed_command(self):
        """Test that failed commands are reported."""
        result = run_command("false")
        assert result["success"] is False


class TestDocumentationTools:
    """Test documentation reading."""

    def test_read_markdown(self):
        """Test reading markdown files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "test.md")
            content = "# Heading 1\n\nSome content.\n\n## Heading 2\n\nMore content."

            with open(filepath, 'w') as f:
                f.write(content)

            result = read_markdown(filepath)
            assert result["success"] is True
            assert "Heading 1" in result["headings"][0]
            assert result["word_count"] > 0

    def test_read_nonmarkdown(self):
        """Test reading non-markdown file."""
        result = read_markdown("/etc/hosts")
        assert result["success"] is False


class TestEmailTools:
    """Test email sending."""

    def test_mock_email(self):
        """Test mock email sending."""
        result = send_email(
            to="test@example.com",
            subject="Test",
            body="Test body",
            mock=True
        )
        assert result["success"] is True
        assert result["mock"] is True


class TestToolRegistry:
    """Test tool registry."""

    def test_registry_import(self):
        """Test that tool registry can be imported."""
        from tool_registry import ToolRegistry

        # Get all tools
        tools = ToolRegistry.get_all_tools()
        assert len(tools) > 0

        # Check that core tools are registered
        tool_names = [t["name"] for t in tools]
        assert "filesystem.read" in tool_names
        assert "terminal.run" in tool_names

    def test_tool_schemas(self):
        """Test that tool schemas are properly formatted."""
        from tool_registry import ToolRegistry

        schemas = ToolRegistry.get_tools_for_claude()
        assert len(schemas) > 0

        for schema in schemas:
            assert "name" in schema
            assert "description" in schema
            assert "input_schema" in schema


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
