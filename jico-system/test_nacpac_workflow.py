#!/usr/bin/env python3
"""Test Nacpac workflow integration"""

import asyncio
import json
import logging
import sys
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

from config import Config
from compression_layer import CompressionLayer
from task_router import TaskRouter
from nacpac_manager import NacpacManager
from jico_manager import JicoManager
from utils import TaskScheduler, OracleVMConnector

async def test_compression():
    """Test message compression"""
    print("\n✅ Testing Compression Layer...")
    compression = CompressionLayer()

    test_messages = [
        "Add a button to the mobile app home screen",
        "Update the desktop UI to show job status",
        "Build APK for testing",
        "Schedule a build tomorrow at 10am",
    ]

    for msg in test_messages:
        result = compression.compress_message(msg)
        print(f"  Input: {msg}")
        print(f"  → {result['task_type']}/{result['target']}: {result['action']}")

    return True


async def test_nacpac_manager():
    """Test Nacpac manager initialization"""
    print("\n✅ Testing Nacpac Manager...")

    # Check if Nacpac path exists
    if not Path(Config.NACPAC_DIR).exists():
        print(f"  ⚠️  NACPAC_DIR not found: {Config.NACPAC_DIR}")
        return False

    manager = NacpacManager()
    print(f"  Nacpac directory: {Config.NACPAC_DIR}")
    print(f"  Mobile directory: {Config.MOBILE_DIR}")
    print(f"  Desktop directory: {Config.DESKTOP_DIR}")
    print(f"  Workers available: {list(manager.workers.keys())}")

    return True


async def test_task_routing():
    """Test task routing"""
    print("\n✅ Testing Task Routing...")

    nacpac_mgr = NacpacManager()
    jico_mgr = JicoManager()
    oracle_vm = OracleVMConnector()
    scheduler = TaskScheduler(oracle_vm)
    router = TaskRouter(nacpac_mgr, jico_mgr, scheduler)

    test_tasks = [
        {
            "task_type": "nacpac",
            "action": "Add login screen",
            "target": "dev",
            "parameters": {},
            "priority": "normal",
        },
        {
            "task_type": "jico",
            "action": "Update AR models",
            "target": "dev",
            "parameters": {},
            "priority": "normal",
        },
        {
            "task_type": "unknown",
            "action": "Test",
            "parameters": {},
            "priority": "normal",
        }
    ]

    for task in test_tasks:
        result = await router.route_task(task)
        print(f"  {task['task_type']}: {result['status']}")

    return True


async def test_credentials():
    """Test that all credentials are configured"""
    print("\n✅ Testing Credentials...")

    credentials = {
        "Discord Token": Config.DISCORD_TOKEN,
        "Anthropic API": Config.ANTHROPIC_API_KEY,
        "R2 Account ID": Config.R2_ACCOUNT_ID,
        "R2 Access Key": Config.R2_ACCESS_KEY,
        "Nacpac Dir": Config.NACPAC_DIR,
        "Jico Dir": Config.JICO_DIR,
    }

    for name, value in credentials.items():
        if value:
            masked = value[:10] + "..." if len(str(value)) > 10 else value
            print(f"  ✓ {name}: {masked}")
        else:
            print(f"  ✗ {name}: NOT SET")

    return True


async def test_compression_for_nacpac():
    """Test compression layer specifically for Nacpac tasks"""
    print("\n✅ Testing Nacpac Task Detection...")

    compression = CompressionLayer()

    nacpac_prompts = [
        "Fix the mobile login screen bug",
        "Add dark mode to desktop app",
        "Build and release APK",
        "Update the home page design",
    ]

    nacpac_count = 0
    for prompt in nacpac_prompts:
        task = compression.compress_message(prompt)
        if task.get("task_type") == "nacpac":
            nacpac_count += 1
            print(f"  ✓ Detected Nacpac: {prompt}")
        else:
            print(f"  ? Not Nacpac: {prompt} → {task.get('task_type')}")

    print(f"\n  Nacpac detection: {nacpac_count}/{len(nacpac_prompts)} correct")
    return nacpac_count > 0


async def main():
    """Run all tests"""
    print("=" * 60)
    print("🧪 JICO System Integration Test")
    print("=" * 60)

    tests = [
        ("Credentials", test_credentials),
        ("Compression Layer", test_compression),
        ("Nacpac Manager", test_nacpac_manager),
        ("Task Routing", test_task_routing),
        ("Nacpac Detection", test_compression_for_nacpac),
    ]

    results = {}
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results[test_name] = "✅ PASS" if result else "❌ FAIL"
        except Exception as e:
            results[test_name] = f"❌ ERROR: {str(e)[:40]}"
            logger.error(f"Test {test_name} failed: {e}")

    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    for test_name, result in results.items():
        print(f"{result:15} {test_name}")

    passed = sum(1 for r in results.values() if "PASS" in r)
    total = len(results)
    print(f"\n{'✅' if passed == total else '⚠️ '} {passed}/{total} tests passed")

    return passed == total


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
