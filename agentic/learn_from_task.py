"""Learn from task execution - capture patterns and outcomes."""

import json
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
from agentic.memory import memory

logger = logging.getLogger(__name__)


def capture_pattern(
    task_id: str,
    outcome: str,  # "success", "failure"
    pattern_type: str,  # "success", "failure", "optimization", "best_practice"
    pattern_description: str,
    example: Optional[str] = None,
    failure_reason: Optional[str] = None,
    agent_id: str = "nacpac_dev"
) -> Optional[str]:
    """
    Capture a learned pattern after task execution.

    Args:
        task_id: Task identifier
        outcome: "success" or "failure"
        pattern_type: Type of pattern learned
        pattern_description: What was learned
        example: Successful execution example (if success)
        failure_reason: Why it failed (if failure)
        agent_id: Which agent learned this

    Returns:
        Pattern ID if saved, None otherwise
    """
    if not memory.client:
        logger.warning("Supabase unavailable; pattern not captured")
        return None

    try:
        # Initialize examples/failures arrays
        examples = []
        failures = []

        if outcome == "success" and example:
            examples.append({
                "description": example,
                "timestamp": datetime.utcnow().isoformat(),
                "task_id": task_id
            })

        if outcome == "failure" and failure_reason:
            failures.append({
                "reason": failure_reason,
                "timestamp": datetime.utcnow().isoformat(),
                "task_id": task_id
            })

        # Insert pattern into nacpac_learned_patterns table
        result = memory.client.table("nacpac_learned_patterns").insert({
            "agent_id": agent_id,
            "pattern_type": pattern_type,
            "pattern_description": pattern_description,
            "examples": examples,
            "failures": failures,
            "success_rate": 1.0 if outcome == "success" else 0.0,
            "last_used": datetime.utcnow().isoformat()
        }).execute()

        if result.data:
            pattern_id = result.data[0]["id"]
            logger.info(f"✅ Captured {pattern_type} pattern for {agent_id}: {pattern_id[:8]}")
            return pattern_id

        return None

    except Exception as e:
        logger.error(f"Failed to capture pattern: {e}")
        return None


def update_pattern_from_task(
    pattern_id: str,
    outcome: str,  # "success" or "failure"
    example: Optional[str] = None,
    failure_reason: Optional[str] = None
) -> bool:
    """
    Update a pattern with new outcome data (success or failure).

    Maintains running examples/failures arrays and updates success_rate.

    Args:
        pattern_id: Pattern to update
        outcome: "success" or "failure"
        example: New success example
        failure_reason: Why it failed

    Returns:
        True if updated, False otherwise
    """
    if not memory.client:
        logger.warning("Supabase unavailable; pattern not updated")
        return False

    try:
        # Get current pattern
        result = memory.client.table("nacpac_learned_patterns").select("*").eq("id", pattern_id).execute()
        if not result.data:
            logger.warning(f"Pattern not found: {pattern_id}")
            return False

        pattern = result.data[0]
        examples = pattern.get("examples", []) or []
        failures = pattern.get("failures", []) or []
        old_success_rate = pattern.get("success_rate", 0.0) or 0.0

        # Add new example or failure
        if outcome == "success" and example:
            examples.append({
                "description": example,
                "timestamp": datetime.utcnow().isoformat()
            })
        elif outcome == "failure" and failure_reason:
            failures.append({
                "reason": failure_reason,
                "timestamp": datetime.utcnow().isoformat()
            })

        # Recalculate success rate: successes / (successes + failures)
        total = len(examples) + len(failures)
        new_success_rate = len(examples) / total if total > 0 else 0.0

        # Update pattern
        update_result = memory.client.table("nacpac_learned_patterns").update({
            "examples": examples,
            "failures": failures,
            "success_rate": new_success_rate,
            "last_used": datetime.utcnow().isoformat()
        }).eq("id", pattern_id).execute()

        logger.info(
            f"Updated pattern {pattern_id[:8]}: "
            f"success_rate={new_success_rate:.1%} "
            f"(examples={len(examples)}, failures={len(failures)})"
        )
        return True

    except Exception as e:
        logger.error(f"Failed to update pattern: {e}")
        return False


def get_patterns_for_task(task_description: str, agent_id: str = "nacpac_dev") -> List[Dict[str, Any]]:
    """
    Retrieve learned patterns similar to a task description.

    Currently returns high-confidence patterns. Future: use semantic similarity.

    Args:
        task_description: Description of task (e.g., "build APK")
        agent_id: Which agent's patterns to retrieve

    Returns:
        List of patterns sorted by success_rate (highest first)
    """
    if not memory.client:
        logger.warning("Supabase unavailable; no patterns available")
        return []

    try:
        # Query patterns for this agent, sorted by success_rate
        result = memory.client.table("nacpac_learned_patterns").select("*").eq(
            "agent_id", agent_id
        ).order("success_rate", desc=True).execute()

        patterns = result.data or []
        logger.info(f"Retrieved {len(patterns)} patterns for {agent_id}")
        return patterns

    except Exception as e:
        logger.error(f"Failed to retrieve patterns: {e}")
        return []


def summarize_patterns(agent_id: str = "nacpac_dev") -> Dict[str, Any]:
    """
    Summarize learned patterns: success rate, pattern count by type, etc.

    Returns:
        Summary dict with pattern statistics
    """
    if not memory.client:
        return {}

    try:
        result = memory.client.table("nacpac_learned_patterns").select("*").eq(
            "agent_id", agent_id
        ).execute()

        patterns = result.data or []

        if not patterns:
            return {
                "total_patterns": 0,
                "by_type": {},
                "avg_success_rate": 0.0
            }

        # Group by type
        by_type = {}
        total_success = 0.0
        for p in patterns:
            ptype = p.get("pattern_type", "unknown")
            by_type[ptype] = by_type.get(ptype, 0) + 1
            total_success += p.get("success_rate", 0) or 0

        avg_success = total_success / len(patterns) if patterns else 0.0

        return {
            "total_patterns": len(patterns),
            "by_type": by_type,
            "avg_success_rate": avg_success,
            "top_pattern": max(patterns, key=lambda p: p.get("success_rate", 0)) if patterns else None
        }

    except Exception as e:
        logger.error(f"Failed to summarize patterns: {e}")
        return {}
