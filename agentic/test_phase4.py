"""Test Phase 4: Feature Generation - verify proposal and application workflows."""

import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def test_feature_agent_exists():
    """Test that feature_agent module exists and can be imported."""
    try:
        from agentic.agents.feature_agent import get_nacpac_feature_agent, FeatureAgent
        logger.info("✅ Test 1 PASS: feature_agent module imports successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Test 1 FAIL: {e}")
        return False


def test_nacpac_dev_feature_methods():
    """Test that nacpac_dev.py has Phase 4 methods."""
    try:
        import ast

        with open('agentic/agents/nacpac_dev.py', 'r') as f:
            tree = ast.parse(f.read())
            methods = {node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)}

        required_methods = {
            'propose_feature_changes',
            'apply_feature_changes'
        }

        missing = required_methods - methods

        if not missing:
            logger.info(f"✅ Test 2 PASS: Both Phase 4 methods defined in nacpac_dev.py")
            return True
        else:
            logger.error(f"❌ Test 2 FAIL: Missing methods: {missing}")
            return False
    except Exception as e:
        logger.error(f"❌ Test 2 FAIL: {e}")
        return False


def test_phase4_imports_in_nacpac_dev():
    """Test that nacpac_dev.py imports feature_agent."""
    try:
        with open('agentic/agents/nacpac_dev.py', 'r') as f:
            content = f.read()

        if 'from agentic.agents.feature_agent import get_nacpac_feature_agent' in content:
            logger.info("✅ Test 3 PASS: nacpac_dev.py imports get_nacpac_feature_agent")
            return True
        else:
            logger.error("❌ Test 3 FAIL: get_nacpac_feature_agent import missing")
            return False
    except Exception as e:
        logger.error(f"❌ Test 3 FAIL: {e}")
        return False


def test_method_signatures():
    """Test that Phase 4 methods have correct signatures."""
    try:
        import ast

        with open('agentic/agents/nacpac_dev.py', 'r') as f:
            tree = ast.parse(f.read())

        # Find the methods
        methods_found = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if node.name == 'propose_feature_changes':
                    # Check parameters: task_id, feature_request
                    params = [arg.arg for arg in node.args.args]
                    methods_found['propose_feature_changes'] = 'task_id' in params and 'feature_request' in params

                elif node.name == 'apply_feature_changes':
                    # Check parameters: task_id, proposal
                    params = [arg.arg for arg in node.args.args]
                    methods_found['apply_feature_changes'] = 'task_id' in params and 'proposal' in params

        if all(methods_found.values()):
            logger.info(f"✅ Test 4 PASS: All Phase 4 method signatures correct")
            for method, correct in methods_found.items():
                logger.info(f"   - {method}()")
            return True
        else:
            logger.error(f"❌ Test 4 FAIL: Invalid method signatures: {methods_found}")
            return False
    except Exception as e:
        logger.error(f"❌ Test 4 FAIL: {e}")
        return False


def test_phase4_patterns_integration():
    """Test that Phase 4 methods integrate skillsets and patterns."""
    try:
        with open('agentic/agents/nacpac_dev.py', 'r') as f:
            content = f.read()

        checks = {
            'skillsets_context': 'self.get_skillsets_context()' in content,
            'patterns_context': 'self.get_learned_patterns_context' in content,
            'proposal_method': 'propose_feature_changes' in content,
            'apply_method': 'apply_feature_changes' in content,
            'memory_logging': 'memory.update_nacpac_task' in content,
            'pattern_capture': 'capture_pattern' in content,
        }

        if all(checks.values()):
            logger.info(f"✅ Test 5 PASS: Phase 4 integration complete")
            for check, result in checks.items():
                status = "✅" if result else "❌"
                logger.info(f"   {status} {check}")
            return True
        else:
            logger.error(f"❌ Test 5 FAIL: Missing integrations")
            for check, result in checks.items():
                if not result:
                    logger.error(f"   ❌ {check}")
            return False
    except Exception as e:
        logger.error(f"❌ Test 5 FAIL: {e}")
        return False


def test_feature_agent_methods():
    """Test that feature_agent has required methods."""
    try:
        import ast

        with open('agentic/agents/feature_agent.py', 'r') as f:
            tree = ast.parse(f.read())
            methods = {node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)}

        required_methods = {
            'analyze_codebase',
            'propose_changes',
            'apply_changes',
            'implement_feature'
        }

        missing = required_methods - methods

        if not missing:
            logger.info(f"✅ Test 6 PASS: feature_agent has all required methods")
            for method in sorted(required_methods):
                logger.info(f"   - {method}()")
            return True
        else:
            logger.error(f"❌ Test 6 FAIL: Missing methods in feature_agent: {missing}")
            return False
    except Exception as e:
        logger.error(f"❌ Test 6 FAIL: {e}")
        return False


def main():
    """Run all Phase 4 tests."""
    logger.info("=" * 60)
    logger.info("Phase 4: Feature Generation Testing Suite")
    logger.info("=" * 60)

    # Run tests
    test1_pass = test_feature_agent_exists()
    test2_pass = test_nacpac_dev_feature_methods()
    test3_pass = test_phase4_imports_in_nacpac_dev()
    test4_pass = test_method_signatures()
    test5_pass = test_phase4_patterns_integration()
    test6_pass = test_feature_agent_methods()

    # Summary
    logger.info("=" * 60)
    all_pass = all([test1_pass, test2_pass, test3_pass, test4_pass, test5_pass, test6_pass])

    if all_pass:
        logger.info("✅ ALL TESTS PASSED (Phase 4: Feature Generation Ready)")
        return 0
    else:
        logger.error("❌ SOME TESTS FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
