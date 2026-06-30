#!/usr/bin/env python3
"""
CIRCUIT BREAKER - Prevent cascade failures through graceful degradation
Stop requests to failing services and allow recovery time
"""

import logging
import time
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, Any, Callable

logger = logging.getLogger(__name__)

class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"        # Normal operation
    OPEN = "open"            # Failing - reject requests
    HALF_OPEN = "half_open"  # Testing - allow limited requests

class CircuitBreaker:
    """Prevents cascading failures by stopping requests to failing services"""

    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        success_threshold: int = 2
    ):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.success_threshold = success_threshold

        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.last_state_change = datetime.now()

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection"""
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                self.success_count = 0
                logger.warning(f"🔄 {self.name} circuit breaker entering HALF_OPEN state")
            else:
                raise CircuitBreakerOpen(f"{self.name} circuit is OPEN. Service unavailable.")

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result

        except Exception as e:
            self._on_failure()
            raise

    async def call_async(self, func: Callable, *args, **kwargs) -> Any:
        """Execute async function with circuit breaker protection"""
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                self.success_count = 0
                logger.warning(f"🔄 {self.name} circuit breaker entering HALF_OPEN state")
            else:
                raise CircuitBreakerOpen(f"{self.name} circuit is OPEN. Service unavailable.")

        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result

        except Exception as e:
            self._on_failure()
            raise

    def _on_success(self):
        """Handle successful call"""
        self.failure_count = 0

        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.success_threshold:
                self._reset()
        elif self.state == CircuitState.CLOSED:
            self.success_count = 0

    def _on_failure(self):
        """Handle failed call"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        self.success_count = 0

        logger.error(f"❌ {self.name} failure #{self.failure_count}/{self.failure_threshold}")

        if self.failure_count >= self.failure_threshold:
            self._trip()

    def _trip(self):
        """Trip the circuit breaker"""
        if self.state != CircuitState.OPEN:
            self.state = CircuitState.OPEN
            self.last_state_change = datetime.now()
            logger.error(f"🔴 {self.name} circuit breaker TRIPPED. Service disabled.")

    def _reset(self):
        """Reset the circuit breaker"""
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_state_change = datetime.now()
        logger.info(f"🟢 {self.name} circuit breaker RESET. Service restored.")

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset"""
        if not self.last_failure_time:
            return False

        elapsed = (datetime.now() - self.last_failure_time).total_seconds()
        return elapsed >= self.recovery_timeout

    def get_status(self) -> Dict[str, Any]:
        """Get circuit breaker status"""
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "last_failure": self.last_failure_time.isoformat() if self.last_failure_time else None,
            "recovery_ready": self._should_attempt_reset()
        }


class CircuitBreakerOpen(Exception):
    """Circuit breaker is open - service unavailable"""
    pass


class CircuitBreakerManager:
    """Manage multiple circuit breakers"""

    def __init__(self):
        self.breakers: Dict[str, CircuitBreaker] = {}

    def register(self, name: str, **kwargs) -> CircuitBreaker:
        """Register a new circuit breaker"""
        breaker = CircuitBreaker(name, **kwargs)
        self.breakers[name] = breaker
        logger.info(f"Registered circuit breaker: {name}")
        return breaker

    def get(self, name: str) -> CircuitBreaker:
        """Get a circuit breaker by name"""
        if name not in self.breakers:
            raise KeyError(f"Circuit breaker not found: {name}")
        return self.breakers[name]

    def get_all_status(self) -> Dict[str, Any]:
        """Get status of all circuit breakers"""
        return {
            name: breaker.get_status()
            for name, breaker in self.breakers.items()
        }

    def reset_all(self):
        """Reset all circuit breakers"""
        for breaker in self.breakers.values():
            breaker._reset()
        logger.info("All circuit breakers reset")


# Global circuit breaker manager
circuit_breaker_manager = CircuitBreakerManager()

# Initialize standard circuit breakers
discord_breaker = circuit_breaker_manager.register("discord_bot", failure_threshold=3, recovery_timeout=30)
anthropic_breaker = circuit_breaker_manager.register("anthropic_api", failure_threshold=5, recovery_timeout=60)
cloudflare_breaker = circuit_breaker_manager.register("cloudflare_r2", failure_threshold=5, recovery_timeout=60)
oracle_breaker = circuit_breaker_manager.register("oracle_vm", failure_threshold=3, recovery_timeout=120)
