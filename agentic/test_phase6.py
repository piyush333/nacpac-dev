"""Test Phase 6: Dashboard UI - verify Next.js dashboard structure and scaffolding."""

import sys
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def test_dashboard_directory_structure():
    """Test that dashboard directory structure is properly created."""
    try:
        required_dirs = [
            'dashboard',
            'dashboard/app',
            'dashboard/components',
            'dashboard/hooks',
            'dashboard/lib',
            'dashboard/styles',
        ]

        all_exist = True
        for dir_path in required_dirs:
            full_path = f'/home/user/nacpac-dev/{dir_path}'
            if os.path.isdir(full_path):
                logger.info(f"  ✅ {dir_path}/")
            else:
                logger.error(f"  ❌ {dir_path}/ MISSING")
                all_exist = False

        if all_exist:
            logger.info(f"✅ Test 1 PASS: Dashboard directory structure complete")
            return True
        else:
            logger.error(f"❌ Test 1 FAIL: Missing dashboard directories")
            return False
    except Exception as e:
        logger.error(f"❌ Test 1 FAIL: {e}")
        return False


def test_dashboard_core_files():
    """Test that all critical dashboard files are created."""
    try:
        required_files = {
            'dashboard/package.json': 'npm configuration',
            'dashboard/tsconfig.json': 'TypeScript config',
            'dashboard/next.config.js': 'Next.js config',
            'dashboard/.env.example': 'Environment template',
            'dashboard/README.md': 'Dashboard documentation',
            'dashboard/lib/supabase.ts': 'Supabase client',
            'dashboard/app/layout.tsx': 'Root layout',
            'dashboard/app/page.tsx': 'Main dashboard page',
            'dashboard/components/AgentStatus.tsx': 'Agent status component',
            'dashboard/components/TaskHistory.tsx': 'Task history component',
            'dashboard/components/CostMonitor.tsx': 'Cost monitor component',
            'dashboard/styles/globals.css': 'Global CSS',
        }

        all_exist = True
        for file_path, description in required_files.items():
            full_path = f'/home/user/nacpac-dev/{file_path}'
            if os.path.isfile(full_path):
                logger.info(f"  ✅ {file_path}")
            else:
                logger.error(f"  ❌ {file_path} MISSING")
                all_exist = False

        if all_exist:
            logger.info(f"✅ Test 2 PASS: All {len(required_files)} core files created")
            return True
        else:
            logger.error(f"❌ Test 2 FAIL: Missing dashboard files")
            return False
    except Exception as e:
        logger.error(f"❌ Test 2 FAIL: {e}")
        return False


def test_phase6_planning_document():
    """Test that Phase 6 planning document exists."""
    try:
        plan_file = '/home/user/nacpac-dev/PHASE6_DASHBOARD_PLAN.md'
        if os.path.isfile(plan_file):
            with open(plan_file, 'r') as f:
                content = f.read()

            # Check for key sections
            checks = {
                'Architecture': 'Architecture Overview' in content,
                'Components': '## Component Specifications' in content,
                'Supabase': 'Supabase Realtime Subscriptions' in content,
                'API': 'API Endpoints' in content,
                'Checklist': 'Implementation Checklist' in content,
            }

            if all(checks.values()):
                logger.info(f"✅ Test 3 PASS: Phase 6 planning document complete")
                for section, present in checks.items():
                    status = "✅" if present else "❌"
                    logger.info(f"   {status} {section}")
                return True
            else:
                logger.error(f"❌ Test 3 FAIL: Missing sections in planning document")
                for section, present in checks.items():
                    if not present:
                        logger.error(f"   ❌ {section}")
                return False
        else:
            logger.error(f"❌ Test 3 FAIL: PHASE6_DASHBOARD_PLAN.md not found")
            return False
    except Exception as e:
        logger.error(f"❌ Test 3 FAIL: {e}")
        return False


def test_component_structure():
    """Test that React components have proper structure."""
    try:
        components = {
            'dashboard/components/AgentStatus.tsx': 'AgentStatus',
            'dashboard/components/TaskHistory.tsx': 'TaskHistory',
            'dashboard/components/CostMonitor.tsx': 'CostMonitor',
        }

        all_valid = True
        for file_path, component_name in components.items():
            full_path = f'/home/user/nacpac-dev/{file_path}'
            with open(full_path, 'r') as f:
                content = f.read()

            # Check for key patterns
            checks = [
                f'export function {component_name}' in content or f'export const {component_name}' in content,
                'interface' in content or 'type' in content,  # TypeScript
                'react' in content.lower() or 'React' in content,  # React import
            ]

            if all(checks):
                logger.info(f"  ✅ {component_name}")
            else:
                logger.error(f"  ❌ {component_name} - invalid structure")
                all_valid = False

        if all_valid:
            logger.info(f"✅ Test 4 PASS: All React components properly structured")
            return True
        else:
            logger.error(f"❌ Test 4 FAIL: Some components have invalid structure")
            return False
    except Exception as e:
        logger.error(f"❌ Test 4 FAIL: {e}")
        return False


def test_configuration_files():
    """Test that Next.js configuration is valid."""
    try:
        checks_passed = 0

        # Check package.json
        with open('/home/user/nacpac-dev/dashboard/package.json', 'r') as f:
            pkg = f.read()
            if '"name": "nacpac-dashboard"' in pkg and '"next"' in pkg:
                logger.info("  ✅ package.json - valid")
                checks_passed += 1
            else:
                logger.error("  ❌ package.json - invalid")

        # Check tsconfig.json
        with open('/home/user/nacpac-dev/dashboard/tsconfig.json', 'r') as f:
            ts_config = f.read()
            if '"strict": true' in ts_config and '"jsx"' in ts_config:
                logger.info("  ✅ tsconfig.json - valid")
                checks_passed += 1
            else:
                logger.error("  ❌ tsconfig.json - invalid")

        # Check next.config.js
        with open('/home/user/nacpac-dev/dashboard/next.config.js', 'r') as f:
            next_config = f.read()
            if 'nextConfig' in next_config and 'module.exports' in next_config:
                logger.info("  ✅ next.config.js - valid")
                checks_passed += 1
            else:
                logger.error("  ❌ next.config.js - invalid")

        if checks_passed == 3:
            logger.info(f"✅ Test 5 PASS: All configuration files valid")
            return True
        else:
            logger.error(f"❌ Test 5 FAIL: {checks_passed}/3 config files valid")
            return False
    except Exception as e:
        logger.error(f"❌ Test 5 FAIL: {e}")
        return False


def test_realtime_integration_scaffolding():
    """Test that Supabase realtime integration is scaffolded."""
    try:
        with open('/home/user/nacpac-dev/dashboard/app/page.tsx', 'r') as f:
            content = f.read()

        checks = {
            'supabase_import': "from '@/lib/supabase'" in content,
            'realtime_subscribe': '.subscribe()' in content,
            'useEffect': 'useEffect' in content,
            'useState': 'useState' in content,
            'fetchTasks': 'fetchTasks()' in content,
        }

        if all(checks.values()):
            logger.info(f"✅ Test 6 PASS: Realtime integration scaffolded")
            for check, result in checks.items():
                status = "✅" if result else "❌"
                logger.info(f"   {status} {check}")
            return True
        else:
            logger.error(f"❌ Test 6 FAIL: Missing realtime scaffolding")
            for check, result in checks.items():
                if not result:
                    logger.error(f"   ❌ {check}")
            return False
    except Exception as e:
        logger.error(f"❌ Test 6 FAIL: {e}")
        return False


def main():
    """Run all Phase 6 tests."""
    logger.info("=" * 60)
    logger.info("Phase 6: Dashboard UI Testing Suite")
    logger.info("=" * 60)

    # Run tests
    test1_pass = test_dashboard_directory_structure()
    test2_pass = test_dashboard_core_files()
    test3_pass = test_phase6_planning_document()
    test4_pass = test_component_structure()
    test5_pass = test_configuration_files()
    test6_pass = test_realtime_integration_scaffolding()

    # Summary
    logger.info("=" * 60)
    all_pass = all([test1_pass, test2_pass, test3_pass, test4_pass, test5_pass, test6_pass])

    if all_pass:
        logger.info("✅ ALL TESTS PASSED (Phase 6: Dashboard UI Scaffolding Ready)")
        logger.info("\nNext Steps:")
        logger.info("1. cd dashboard")
        logger.info("2. npm install")
        logger.info("3. cp .env.example .env.local")
        logger.info("4. Fill in Supabase credentials")
        logger.info("5. npm run dev")
        return 0
    else:
        logger.error("❌ SOME TESTS FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
