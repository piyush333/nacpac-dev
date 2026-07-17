#!/usr/bin/env python3
"""Test script to verify skillset loading and injection."""

import sys
import logging
from agentic.agents.nacpac_dev import nacpac_dev_agent

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def test_skillset_loading():
    """Test that skillsets load correctly on agent init."""
    print("\n=== TEST 1: Skillset Loading ===")

    skillsets = nacpac_dev_agent.skillsets
    print(f"Loaded {len(skillsets)} skillsets: {list(skillsets.keys())}")

    expected_skillsets = [
        "nacpac_codebase",
        "python",
        "nodejs",
        "react",
        "expo_dev",
        "npm",
        "exe_windows"
    ]

    missing = [s for s in expected_skillsets if s not in skillsets]
    if missing:
        print(f"❌ Missing skillsets: {missing}")
        return False

    print("✅ All expected skillsets loaded")
    return True


def test_skillset_context():
    """Test that skillsets are formatted correctly for Claude."""
    print("\n=== TEST 2: Skillset Context Formatting ===")

    context = nacpac_dev_agent.get_skillsets_context()

    if not context or context == "No skillsets loaded.":
        print("❌ Skillsets not formatted")
        return False

    # Check that context contains key elements
    checks = [
        ("NACPAC_CODEBASE" in context, "NacPac codebase skillset"),
        ("Description:" in context, "Description field"),
        ("Knowledge:" in context, "Knowledge field"),
    ]

    for check, desc in checks:
        if not check:
            print(f"❌ Missing {desc}")
            return False

    print(f"✅ Context formatted correctly ({len(context)} chars)")
    return True


def test_system_prompt():
    """Test that system prompt includes skillsets."""
    print("\n=== TEST 3: System Prompt with Skillsets ===")

    prompt = nacpac_dev_agent.get_system_prompt_with_skillsets()

    checks = [
        ("NACPAC Dev Agent" in prompt, "Agent role statement"),
        ("nacpac_dev" in prompt, "Agent ID"),
        ("skillsets" in prompt.lower(), "Skillsets mentioned"),
        ("NACPAC_CODEBASE" in prompt, "Skillset names"),
    ]

    for check, desc in checks:
        if not check:
            print(f"❌ Missing {desc}")
            return False

    print(f"✅ System prompt generated correctly ({len(prompt)} chars)")
    print(f"\nSample prompt:\n{prompt[:300]}...\n")
    return True


def test_skillset_details():
    """Test that skillset details are complete."""
    print("\n=== TEST 4: Skillset Details ===")

    skillsets = nacpac_dev_agent.skillsets

    for name, details in skillsets.items():
        required_keys = ["description", "documentation", "version"]
        missing_keys = [k for k in required_keys if k not in details]

        if missing_keys:
            print(f"❌ Skillset '{name}' missing keys: {missing_keys}")
            return False

        if not details.get("description"):
            print(f"❌ Skillset '{name}' has empty description")
            return False

    print(f"✅ All {len(skillsets)} skillsets have complete details")
    return True


def main():
    """Run all tests."""
    print("\n" + "="*50)
    print("SKILLSET VERIFICATION TESTS")
    print("="*50)

    tests = [
        test_skillset_loading,
        test_skillset_context,
        test_system_prompt,
        test_skillset_details,
    ]

    results = [test() for test in tests]

    print("\n" + "="*50)
    print(f"Results: {sum(results)}/{len(results)} tests passed")
    print("="*50 + "\n")

    return all(results)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
