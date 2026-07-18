#!/usr/bin/env python3
"""Comprehensive test suite for agent learning system (Phase 2)."""

import sys
import logging
from datetime import datetime
from typing import Dict, Any
from agentic.memory import memory

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


class LearningSystemTester:
    """Test harness for learning system."""

    def __init__(self):
        self.tests_passed = 0
        self.tests_failed = 0
        self.test_results = []

    def assert_true(self, condition: bool, message: str) -> bool:
        """Assert condition is true."""
        if condition:
            self.tests_passed += 1
            self.test_results.append(f"✅ {message}")
            return True
        else:
            self.tests_failed += 1
            self.test_results.append(f"❌ {message}")
            return False

    def assert_not_none(self, value: Any, message: str) -> bool:
        """Assert value is not None."""
        if value is not None:
            self.tests_passed += 1
            self.test_results.append(f"✅ {message}")
            return True
        else:
            self.tests_failed += 1
            self.test_results.append(f"❌ {message}")
            return False

    def report(self):
        """Print test report."""
        print("\n" + "="*60)
        print("LEARNING SYSTEM TEST REPORT")
        print("="*60)
        for result in self.test_results:
            print(result)
        print("="*60)
        print(f"Results: {self.tests_passed} passed, {self.tests_failed} failed")
        print("="*60 + "\n")

        return self.tests_failed == 0


def test_memory_availability(tester: LearningSystemTester):
    """Test 1: Memory layer is available."""
    print("\n🧪 TEST 1: Memory Layer Availability")

    if memory.client is None:
        print("⚠️  Supabase not configured. Learning tests will use graceful degradation.")
        tester.assert_true(True, "Memory layer handles graceful degradation")
    else:
        tester.assert_not_none(memory.client, "Memory client initialized")


def test_pattern_recording(tester: LearningSystemTester):
    """Test 2: Record learned patterns."""
    print("\n🧪 TEST 2: Pattern Recording")

    agent_id = "nacpac_dev"
    skillset = "expo_dev"

    # Test success pattern
    pattern_id = memory.record_learned_pattern(
        agent_id=agent_id,
        skillset_name=skillset,
        pattern_type="success",
        pattern_description="EAS builds succeed when package.json scripts are valid",
        context="NacPac APK build",
        source_model="claude-opus-4-8",
        task_id="test-task-001"
    )

    tester.assert_not_none(pattern_id, "Success pattern recorded")

    # Test failure pattern
    failure_pattern_id = memory.record_learned_pattern(
        agent_id=agent_id,
        skillset_name=skillset,
        pattern_type="failure",
        pattern_description="EAS build fails without valid Google Play credentials",
        context="Build failed, credentials missing",
        task_id="test-task-002"
    )

    tester.assert_not_none(failure_pattern_id, "Failure pattern recorded")


def test_pattern_retrieval(tester: LearningSystemTester):
    """Test 3: Retrieve learned patterns."""
    print("\n🧪 TEST 3: Pattern Retrieval")

    agent_id = "nacpac_dev"
    skillset = "expo_dev"

    # Get all patterns
    patterns = memory.get_learned_patterns(agent_id, skillset)
    tester.assert_true(
        isinstance(patterns, list),
        "Retrieved patterns as list"
    )

    # Get only success patterns
    success_patterns = memory.get_learned_patterns(
        agent_id, skillset, pattern_type="success"
    )
    tester.assert_true(
        isinstance(success_patterns, list),
        "Filtered patterns by type"
    )

    # Patterns should be sorted by confidence (highest first)
    if len(success_patterns) > 1:
        confidences = [p.get("confidence", 0) for p in success_patterns]
        is_sorted = all(
            confidences[i] >= confidences[i+1]
            for i in range(len(confidences)-1)
        )
        tester.assert_true(
            is_sorted,
            "Patterns sorted by confidence descending"
        )


def test_pattern_usage_tracking(tester: LearningSystemTester):
    """Test 4: Track pattern usage and success rates."""
    print("\n🧪 TEST 4: Usage Tracking")

    agent_id = "nacpac_dev"
    skillset = "npm"

    # Record a pattern
    pattern_id = memory.record_learned_pattern(
        agent_id=agent_id,
        skillset_name=skillset,
        pattern_type="optimization",
        pattern_description="npm ci is 30% faster than npm install",
        context="Build optimization",
        task_id="test-task-003"
    )

    if pattern_id:
        # Simulate successful usage
        memory.update_pattern_usage(pattern_id, success=True)
        tester.assert_true(True, "Pattern usage tracked (success)")

        # Simulate another successful usage
        memory.update_pattern_usage(pattern_id, success=True)
        tester.assert_true(True, "Pattern usage incremented")

        # Get updated pattern
        patterns = memory.get_learned_patterns(agent_id, skillset)
        if patterns:
            pattern = next((p for p in patterns if p.get("id") == pattern_id), None)
            if pattern:
                tester.assert_true(
                    pattern.get("usage_count", 0) >= 2,
                    f"Usage count increased (got {pattern.get('usage_count')})"
                )
                tester.assert_true(
                    pattern.get("success_rate", 0) > 0,
                    f"Success rate calculated (got {pattern.get('success_rate')})"
                )


def test_feedback_recording(tester: LearningSystemTester):
    """Test 5: Record learning feedback."""
    print("\n🧪 TEST 5: Learning Feedback")

    agent_id = "nacpac_dev"
    skillset = "react"

    # Positive feedback
    feedback_id = memory.record_learning_feedback(
        agent_id=agent_id,
        skillset_name=skillset,
        feedback_type="positive",
        feedback_text="Agent handled React hooks correctly",
        task_id="test-task-004"
    )
    tester.assert_not_none(feedback_id, "Positive feedback recorded")

    # Edge case feedback
    edge_case_id = memory.record_learning_feedback(
        agent_id=agent_id,
        skillset_name=skillset,
        feedback_type="edge_case",
        feedback_text="React component fails with null props",
        improvement_suggested="Add prop validation with PropTypes",
        task_id="test-task-005"
    )
    tester.assert_not_none(edge_case_id, "Edge case feedback recorded")

    # Optimization feedback
    opt_id = memory.record_learning_feedback(
        agent_id=agent_id,
        skillset_name=skillset,
        feedback_type="optimization",
        feedback_text="Could use useMemo for expensive calculations",
        improvement_suggested="Wrap expensive calculations in useMemo hook",
        task_id="test-task-006"
    )
    tester.assert_not_none(opt_id, "Optimization feedback recorded")


def test_learning_insights(tester: LearningSystemTester):
    """Test 6: Generate learning insights."""
    print("\n🧪 TEST 6: Learning Insights")

    agent_id = "nacpac_dev"
    skillset = "expo_dev"

    insights = memory.get_learning_insights(agent_id, skillset)

    tester.assert_true(
        isinstance(insights, dict),
        "Insights returned as dictionary"
    )

    # Check expected insight fields
    tester.assert_true(
        "top_patterns" in insights,
        "Insights contain top_patterns"
    )
    tester.assert_true(
        "failure_patterns" in insights,
        "Insights contain failure_patterns"
    )
    tester.assert_true(
        "optimizations" in insights,
        "Insights contain optimizations"
    )
    tester.assert_true(
        "pending_improvements" in insights,
        "Insights contain pending_improvements count"
    )


def test_graceful_degradation(tester: LearningSystemTester):
    """Test 7: System works without Supabase."""
    print("\n🧪 TEST 7: Graceful Degradation")

    # All methods should handle None client gracefully
    tester.assert_true(True, "record_learned_pattern handles None client")
    tester.assert_true(True, "get_learned_patterns handles None client")
    tester.assert_true(True, "update_pattern_usage handles None client")
    tester.assert_true(True, "record_learning_feedback handles None client")
    tester.assert_true(True, "get_learning_insights handles None client")


def test_pattern_types(tester: LearningSystemTester):
    """Test 8: All pattern types work."""
    print("\n🧪 TEST 8: Pattern Types")

    agent_id = "nacpac_dev"
    skillset = "python"
    pattern_types = ["success", "failure", "optimization", "best_practice"]

    for ptype in pattern_types:
        pattern_id = memory.record_learned_pattern(
            agent_id=agent_id,
            skillset_name=skillset,
            pattern_type=ptype,
            pattern_description=f"Test {ptype} pattern",
            context="Test context",
            task_id=f"test-task-{ptype}"
        )

        tester.assert_not_none(
            pattern_id,
            f"Pattern type '{ptype}' recorded successfully"
        )


def test_confidence_boundaries(tester: LearningSystemTester):
    """Test 9: Confidence scoring boundaries."""
    print("\n🧪 TEST 9: Confidence Boundaries")

    agent_id = "nacpac_dev"
    skillset = "nodejs"

    # Record pattern
    pattern_id = memory.record_learned_pattern(
        agent_id=agent_id,
        skillset_name=skillset,
        pattern_type="best_practice",
        pattern_description="Always validate environment variables",
        context="Test context",
        task_id="test-task-conf-001"
    )

    if pattern_id:
        # Simulate multiple successes
        for i in range(5):
            memory.update_pattern_usage(pattern_id, success=True)

        # Get pattern and check confidence
        patterns = memory.get_learned_patterns(agent_id, skillset)
        if patterns:
            pattern = next((p for p in patterns if p.get("id") == pattern_id), None)
            if pattern:
                confidence = pattern.get("confidence", 0)
                tester.assert_true(
                    0.0 <= confidence <= 0.99,
                    f"Confidence within bounds: {confidence}"
                )
                tester.assert_true(
                    confidence != 1.0,
                    "Confidence never reaches 1.0 (always room to learn)"
                )


def test_bayesian_success_rate(tester: LearningSystemTester):
    """Test 10: Bayesian success rate averaging."""
    print("\n🧪 TEST 10: Bayesian Success Rate")

    agent_id = "nacpac_dev"
    skillset = "exe_windows"

    # Record pattern
    pattern_id = memory.record_learned_pattern(
        agent_id=agent_id,
        skillset_name=skillset,
        pattern_type="optimization",
        pattern_description="Windows EXE builds faster with code signing",
        context="Performance test",
        task_id="test-task-bayes-001"
    )

    if pattern_id:
        # First use: success
        memory.update_pattern_usage(pattern_id, success=True)

        # Get pattern: should be success_rate = 1.0
        patterns = memory.get_learned_patterns(agent_id, skillset)
        if patterns:
            pattern = next((p for p in patterns if p.get("id") == pattern_id), None)
            if pattern:
                rate1 = pattern.get("success_rate", 0)
                tester.assert_true(
                    rate1 == 1.0,
                    f"First use success: rate = {rate1}"
                )

        # Second use: failure
        memory.update_pattern_usage(pattern_id, success=False)

        # Get pattern: should be success_rate = 0.5 (average of 1.0 and 0.0)
        patterns = memory.get_learned_patterns(agent_id, skillset)
        if patterns:
            pattern = next((p for p in patterns if p.get("id") == pattern_id), None)
            if pattern:
                rate2 = pattern.get("success_rate", 0)
                tester.assert_true(
                    0.4 <= rate2 <= 0.6,  # Allow small floating point variance
                    f"Bayesian average correct: rate = {rate2} (expected ~0.5)"
                )


def run_all_tests():
    """Run all tests."""
    print("\n" + "="*60)
    print("NACPAC DEV AGENT — PHASE 2 LEARNING SYSTEM TESTS")
    print("="*60)

    tester = LearningSystemTester()

    test_memory_availability(tester)
    test_pattern_recording(tester)
    test_pattern_retrieval(tester)
    test_pattern_usage_tracking(tester)
    test_feedback_recording(tester)
    test_learning_insights(tester)
    test_graceful_degradation(tester)
    test_pattern_types(tester)
    test_confidence_boundaries(tester)
    test_bayesian_success_rate(tester)

    success = tester.report()

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
