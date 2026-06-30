#!/usr/bin/env python3
"""
System connectivity test - verify all components are ready
"""

import asyncio
import logging
from config import Config
from compression_layer import CompressionLayer
from utils import R2Storage, OracleVMConnector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_system():
    """Test all system components"""
    print("\n" + "=" * 60)
    print("JICO System Connectivity Test")
    print("=" * 60 + "\n")

    results = {}

    # 1. Test Anthropic/Haiku
    print("1️⃣  Testing Anthropic API (Claude Haiku)...")
    try:
        compression = CompressionLayer()
        test_task = compression.compress_message("test message")
        if test_task and 'task_type' in test_task:
            print("   ✅ Anthropic API: Connected")
            results['anthropic'] = True
        else:
            print("   ❌ Anthropic API: Failed to compress message")
            results['anthropic'] = False
    except Exception as e:
        print(f"   ❌ Anthropic API: {e}")
        results['anthropic'] = False

    # 2. Test Cloudflare R2 - Nacpac
    print("\n2️⃣  Testing Cloudflare R2 - Nacpac Bucket...")
    try:
        r2_nacpac = R2Storage(Config.NACPAC_R2_BUCKET)
        files = r2_nacpac.list_objects()
        print(f"   ✅ Nacpac R2: Connected ({len(files)} objects)")
        results['r2_nacpac'] = True
    except Exception as e:
        print(f"   ❌ Nacpac R2: {e}")
        results['r2_nacpac'] = False

    # 3. Test Cloudflare R2 - Jico
    print("\n3️⃣  Testing Cloudflare R2 - Jico Bucket...")
    try:
        r2_jico = R2Storage(Config.JICO_R2_BUCKET)
        files = r2_jico.list_objects()
        print(f"   ✅ Jico R2: Connected ({len(files)} objects)")
        results['r2_jico'] = True
    except Exception as e:
        print(f"   ❌ Jico R2: {e}")
        results['r2_jico'] = False

    # 4. Test Oracle VM SSH
    print("\n4️⃣  Testing Oracle VM SSH Connection...")
    try:
        oracle = OracleVMConnector()
        result = await oracle.execute_remote_command("echo 'JICO System Connected' && hostname")
        if result['status'] == 'success':
            print(f"   ✅ Oracle VM: Connected")
            print(f"      Output: {result['output'].strip()}")
            results['oracle_vm'] = True
        else:
            print(f"   ❌ Oracle VM: {result.get('message')}")
            results['oracle_vm'] = False
    except Exception as e:
        print(f"   ❌ Oracle VM: {e}")
        results['oracle_vm'] = False

    # 5. Test Discord Token (format only)
    print("\n5️⃣  Testing Discord Token...")
    if Config.DISCORD_TOKEN and len(Config.DISCORD_TOKEN) > 20:
        print(f"   ✅ Discord Token: Format OK")
        results['discord'] = True
    else:
        print(f"   ❌ Discord Token: Invalid format")
        results['discord'] = False

    # Summary
    print("\n" + "=" * 60)
    print("System Status Summary")
    print("=" * 60)

    total = len(results)
    passed = sum(1 for v in results.values() if v)

    for component, status in results.items():
        symbol = "✅" if status else "❌"
        print(f"{symbol} {component.upper()}")

    print(f"\n{passed}/{total} components ready")

    if passed == total:
        print("\n🚀 System is READY TO START!")
    else:
        print("\n⚠️  Some components need attention")

    return passed == total

if __name__ == "__main__":
    success = asyncio.run(test_system())
    exit(0 if success else 1)
