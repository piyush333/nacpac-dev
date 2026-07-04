"""CLI Interface - command line testing for Phase 1 development."""

import sys
import logging
import json
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

logger = logging.getLogger(__name__)


def print_header(text):
    """Print formatted header."""
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")


def print_section(text):
    """Print formatted section."""
    print(f"\n>>> {text}\n")


def main():
    """CLI entry point for Phase 1 testing."""

    if len(sys.argv) < 2:
        print_header("Jico Agentic System - Phase 1 CLI")
        print("""
Usage:
  python cli.py <command> [args]

Commands:
  build <brand> <target> [feature]   Build artifact
    - build nacpac apk                Build NacPac APK
    - build nacpac exe                Build NacPac EXE
    - build jico ar                   Build Jico AR app
    - build nacpac apk "Add checkout" Build with feature

  preview <brand> [feature]           Preview feature before building
    - preview nacpac "Add checkout"   Preview NacPac with new feature
    - preview jico "Add AR"           Preview Jico with new feature

  list-agents                         List all registered agents
  status                              System status
  help                                Show this help

Examples:
  python cli.py build nacpac apk
  python cli.py preview nacpac "Add checkout feature"
  python cli.py list-agents
        """)
        return

    command = sys.argv[1].lower()

    if command == "build":
        handle_build(sys.argv[2:])
    elif command == "preview":
        handle_preview(sys.argv[2:])
    elif command == "list-agents":
        handle_list_agents()
    elif command == "status":
        handle_status()
    elif command == "help":
        print("See usage above")
    else:
        print(f"❌ Unknown command: {command}")
        print("Run 'python cli.py' for help")


def handle_build(args):
    """Handle build command."""
    if len(args) < 2:
        print("❌ Usage: python cli.py build <brand> <target> [feature]")
        return

    brand = args[0].lower()
    target = args[1].lower()
    feature = " ".join(args[2:]) if len(args) > 2 else None

    print_header(f"Building {brand} {target}")

    try:
        from agents.orchestrator import orchestrator
        from registry import registry

        # Create intent
        intent = {
            "brand": brand,
            "task_type": "build",
            "target": target,
            "feature": feature
        }

        print_section(f"Intent: {json.dumps(intent, indent=2)}")

        # Route to agent
        agent_name = orchestrator.route_to_agent(intent)
        print_section(f"Routed to: {agent_name}")

        agent = registry.get_agent_class(agent_name)
        if not agent:
            print(f"❌ Agent not found: {agent_name}")
            return

        # Execute build
        if target == "apk":
            print_section("Executing: build_apk()")
            result = agent.build_apk(task_id="cli-test-1", profile="preview")
        elif target == "exe":
            print_section("Executing: build_exe()")
            result = agent.build_exe(task_id="cli-test-1")
        else:
            print(f"❌ Unknown target: {target}")
            return

        print_section("Result:")
        print(json.dumps(result, indent=2))

        if result.get("status") == "success":
            print(f"\n✅ Build successful: {result.get('link', result.get('path', 'N/A'))}")
        else:
            print(f"\n❌ Build failed: {result.get('error', 'Unknown error')}")

    except Exception as e:
        logger.error(f"Build command failed: {e}", exc_info=True)
        print(f"❌ Error: {e}")


def handle_preview(args):
    """Handle preview command."""
    if len(args) < 1:
        print("❌ Usage: python cli.py preview <brand> [feature]")
        return

    brand = args[0].lower()
    feature = " ".join(args[1:]) if len(args) > 1 else None

    print_header(f"Previewing {brand}" + (f" - {feature}" if feature else ""))

    try:
        from preview import preview
        from agents.orchestrator import orchestrator
        from registry import registry

        agent_name = orchestrator.route_to_agent({"brand": brand})
        agent = registry.get_agent_class(agent_name)

        if not agent:
            print(f"❌ Agent not found: {agent_name}")
            return

        # For now, just indicate preview capability
        print_section("Preview capability (Phase 1.5)")
        print(f"Agent: {agent_name}")
        print(f"Feature: {feature or 'None specified'}")
        print("\nNote: Preview system ready with Playwright integration")
        print("      Run 'npm install playwright' to enable screenshots")

    except Exception as e:
        logger.error(f"Preview command failed: {e}", exc_info=True)
        print(f"❌ Error: {e}")


def handle_list_agents():
    """Handle list-agents command."""
    print_header("Registered Agents")

    try:
        from registry import registry

        agents = registry.list_agents()
        if not agents:
            print("No agents registered yet")
            return

        for agent in agents:
            print(f"📦 {agent['name']}")
            print(f"   Version: {agent['version']}")
            print(f"   Capabilities: {', '.join(agent['capabilities'])}")
            print(f"   Status: {agent['status']}")
            print()

    except Exception as e:
        logger.error(f"List agents failed: {e}", exc_info=True)
        print(f"❌ Error: {e}")


def handle_status():
    """Handle status command."""
    print_header("System Status")

    try:
        from registry import registry
        from task_queue import queue

        agents = registry.list_agents()
        print(f"✅ Registered agents: {len(agents)}")

        for agent in agents:
            agent_name = agent['name']
            queue_len = queue.queue_length(agent_name)
            print(f"   - {agent_name}: {queue_len} tasks in queue")

        print("\n✅ System ready for Phase 1 testing")

    except Exception as e:
        logger.error(f"Status check failed: {e}", exc_info=True)
        print(f"⚠️  Status check failed: {e}")


if __name__ == "__main__":
    main()
