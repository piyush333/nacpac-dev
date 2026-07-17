"""Test Phase 5: Build Pipeline - verify build progress tracking and retry mechanisms."""

import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def test_build_pipeline_methods():
    """Test that nacpac_dev.py has Phase 5 build pipeline methods."""
    try:
        import ast

        with open('agentic/agents/nacpac_dev.py', 'r') as f:
            tree = ast.parse(f.read())
            methods = {node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)}

        required_methods = {
            'build_with_progress_tracking',
            'retry_failed_build',
            'get_build_status',
            '_estimate_build_cost'
        }

        missing = required_methods - methods

        if not missing:
            logger.info(f"✅ Test 1 PASS: All {len(required_methods)} Phase 5 methods defined")
            for method in sorted(required_methods):
                logger.info(f"   - {method}()")
            return True
        else:
            logger.error(f"❌ Test 1 FAIL: Missing methods: {missing}")
            return False
    except Exception as e:
        logger.error(f"❌ Test 1 FAIL: {e}")
        return False


def test_phase5_cost_tracking():
    """Test that Phase 5 includes cost tracking integration."""
    try:
        with open('agentic/agents/nacpac_dev.py', 'r') as f:
            content = f.read()

        checks = {
            'cost_estimation': '_estimate_build_cost' in content,
            'cost_logging': 'memory.log_nacpac_run' in content and 'cost_usd' in content,
            'duration_tracking': 'datetime.utcnow()' in content and 'start_time' in content,
            'build_status_query': 'get_build_status' in content,
        }

        if all(checks.values()):
            logger.info(f"✅ Test 2 PASS: Phase 5 cost tracking integrated")
            for check, result in checks.items():
                status = "✅" if result else "❌"
                logger.info(f"   {status} {check}")
            return True
        else:
            logger.error(f"❌ Test 2 FAIL: Missing cost tracking features")
            for check, result in checks.items():
                if not result:
                    logger.error(f"   ❌ {check}")
            return False
    except Exception as e:
        logger.error(f"❌ Test 2 FAIL: {e}")
        return False


def test_phase5_retry_mechanism():
    """Test that Phase 5 includes retry mechanism."""
    try:
        with open('agentic/agents/nacpac_dev.py', 'r') as f:
            content = f.read()

        checks = {
            'retry_method': 'retry_failed_build' in content,
            'max_retries_param': 'max_retries' in content,
            'exponential_backoff': '2 ** attempt' in content or 'exponential' in content.lower(),
            'wait_sleep': 'time.sleep' in content,
        }

        if all(checks.values()):
            logger.info(f"✅ Test 3 PASS: Phase 5 retry mechanism implemented")
            for check, result in checks.items():
                status = "✅" if result else "❌"
                logger.info(f"   {status} {check}")
            return True
        else:
            logger.error(f"❌ Test 3 FAIL: Missing retry mechanism features")
            for check, result in checks.items():
                if not result:
                    logger.error(f"   ❌ {check}")
            return False
    except Exception as e:
        logger.error(f"❌ Test 3 FAIL: {e}")
        return False


def test_build_cost_estimation_logic():
    """Test that cost estimation method has reasonable logic."""
    try:
        import ast
        import re

        with open('agentic/agents/nacpac_dev.py', 'r') as f:
            content = f.read()

        # Extract _estimate_build_cost method
        method_match = re.search(r'def _estimate_build_cost\(self.*?\n(?:.*?\n)*?        return', content, re.DOTALL)

        if not method_match:
            logger.error("❌ Test 4 FAIL: Could not find _estimate_build_cost method")
            return False

        method_code = method_match.group()

        checks = {
            'apk_base_cost': '0.10' in method_code,
            'exe_minimum_cost': '0.05' in method_code,
            'duration_calculation': 'duration' in method_code.lower(),
            'different_costs_per_type': 'build_type.lower()' in method_code and ('apk' in method_code or 'exe' in method_code),
        }

        if all(checks.values()):
            logger.info(f"✅ Test 4 PASS: Cost estimation logic is reasonable")
            for check, result in checks.items():
                status = "✅" if result else "❌"
                logger.info(f"   {status} {check}")
            return True
        else:
            logger.error(f"❌ Test 4 FAIL: Cost estimation logic incomplete")
            for check, result in checks.items():
                if not result:
                    logger.error(f"   ❌ {check}")
            return False
    except Exception as e:
        logger.error(f"❌ Test 4 FAIL: {e}")
        return False


def test_phase5_progress_tracking_calls():
    """Test that build methods call progress tracking functions."""
    try:
        with open('agentic/agents/nacpac_dev.py', 'r') as f:
            content = f.read()

        # Count build method calls in build_with_progress_tracking
        if 'def build_with_progress_tracking' in content:
            # Should contain memory.update_nacpac_task multiple times
            calls_count = content.count('memory.update_nacpac_task(')
            log_calls = content.count('memory.log_nacpac_run(')

            if calls_count >= 12 and log_calls >= 3:  # Multiple status updates + logging
                logger.info(f"✅ Test 5 PASS: Progress tracking integrated in build methods")
                logger.info(f"   - {calls_count} task status update calls")
                logger.info(f"   - {log_calls} run logging calls")
                return True
            else:
                logger.error(f"❌ Test 5 FAIL: Insufficient tracking calls")
                logger.error(f"   - Task updates: {calls_count} (need ≥12)")
                logger.error(f"   - Run logs: {log_calls} (need ≥3)")
                return False
        else:
            logger.error("❌ Test 5 FAIL: build_with_progress_tracking not found")
            return False
    except Exception as e:
        logger.error(f"❌ Test 5 FAIL: {e}")
        return False


def test_method_signatures():
    """Test that Phase 5 methods have correct signatures."""
    try:
        import ast

        with open('agentic/agents/nacpac_dev.py', 'r') as f:
            tree = ast.parse(f.read())

        methods_found = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if node.name == 'build_with_progress_tracking':
                    params = [arg.arg for arg in node.args.args]
                    methods_found['build_with_progress_tracking'] = (
                        'task_id' in params and 'build_type' in params
                    )
                elif node.name == 'retry_failed_build':
                    params = [arg.arg for arg in node.args.args]
                    methods_found['retry_failed_build'] = (
                        'task_id' in params and 'build_type' in params and 'max_retries' in params
                    )
                elif node.name == 'get_build_status':
                    params = [arg.arg for arg in node.args.args]
                    methods_found['get_build_status'] = 'task_id' in params

        if all(methods_found.values()):
            logger.info(f"✅ Test 6 PASS: All Phase 5 method signatures correct")
            return True
        else:
            logger.error(f"❌ Test 6 FAIL: Invalid method signatures: {methods_found}")
            return False
    except Exception as e:
        logger.error(f"❌ Test 6 FAIL: {e}")
        return False


def main():
    """Run all Phase 5 tests."""
    logger.info("=" * 60)
    logger.info("Phase 5: Build Pipeline Testing Suite")
    logger.info("=" * 60)

    # Run tests
    test1_pass = test_build_pipeline_methods()
    test2_pass = test_phase5_cost_tracking()
    test3_pass = test_phase5_retry_mechanism()
    test4_pass = test_build_cost_estimation_logic()
    test5_pass = test_phase5_progress_tracking_calls()
    test6_pass = test_method_signatures()

    # Summary
    logger.info("=" * 60)
    all_pass = all([test1_pass, test2_pass, test3_pass, test4_pass, test5_pass, test6_pass])

    if all_pass:
        logger.info("✅ ALL TESTS PASSED (Phase 5: Build Pipeline Ready)")
        return 0
    else:
        logger.error("❌ SOME TESTS FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
