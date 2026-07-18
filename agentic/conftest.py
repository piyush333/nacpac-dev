"""Pytest configuration and fixtures for agentic tests."""

import pytest
from agentic.test_learning_system import LearningSystemTester


@pytest.fixture
def tester():
    """Provide a LearningSystemTester instance for tests."""
    return LearningSystemTester()
