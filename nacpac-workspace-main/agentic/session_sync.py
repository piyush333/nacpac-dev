"""Auto-sync session context from central Supabase coordination.

Run on session startup and via cron every 30 minutes.
Fetches current phase, status, and notes from session_coordination table.
"""

import logging
from datetime import datetime
from agentic.memory import memory

logger = logging.getLogger(__name__)


def sync_session(session_name: str) -> dict:
    """Fetch session status from Supabase and log it.

    Returns:
        dict: Session status {agent_id, status, current_phase, notes, last_update}
        or empty dict if not found
    """
    if not memory.client:
        logger.warning("Supabase unavailable; cannot sync session")
        return {}

    try:
        result = memory.client.table("session_coordination") \
            .select("*") \
            .eq("session_name", session_name) \
            .execute()

        if not result.data:
            logger.warning(f"No session found in coordination table: {session_name}")
            return {}

        status = result.data[0]
        agent_id = status.get("agent_id")
        current_phase = status.get("current_phase")
        current_status = status.get("status")
        notes = status.get("notes", "")

        # Display sync banner
        logger.info(f"""
╔══════════════════════════════════════════════════════════════════╗
║ SESSION SYNC — {session_name.upper()}
╠══════════════════════════════════════════════════════════════════╣
║ Agent ID:        {agent_id}
║ Status:          {current_status.upper()}
║ Current Phase:   {current_phase}
║ Last Update:     {status.get('last_update', 'N/A')}
╚══════════════════════════════════════════════════════════════════╝
        """)

        if notes:
            logger.info(f"📝 Notes from central: {notes}")

        return status

    except Exception as e:
        logger.error(f"Failed to sync session: {e}")
        return {}


def get_assigned_tasks(agent_id: str) -> list:
    """Fetch all tasks assigned to this agent.

    Returns:
        list: Tasks [{phase, task_name, status, description}]
    """
    if not memory.client:
        return []

    try:
        result = memory.client.table("agent_tasks") \
            .select("phase, task_name, status, description") \
            .eq("agent_id", agent_id) \
            .execute()

        if result.data:
            logger.info(f"Found {len(result.data)} assigned tasks:")
            for task in result.data:
                phase = task.get("phase")
                name = task.get("task_name")
                status = task.get("status")
                logger.info(f"  - [{status}] {phase}: {name}")
            return result.data

        return []

    except Exception as e:
        logger.error(f"Failed to fetch assigned tasks: {e}")
        return []


def update_session_status(session_name: str, status: str, notes: str = ""):
    """Update session status in Supabase (use carefully).

    Typically called by agent when phase completes or blocks.

    Args:
        session_name: Name of session (e.g., "nacpac_agent")
        status: New status (building, waiting, live, paused, blocked)
        notes: Optional notes (e.g., "Phase 1 complete, ready for Phase 2")
    """
    if not memory.client:
        logger.warning("Supabase unavailable; cannot update session")
        return

    try:
        update_data = {
            "status": status,
            "notes": notes,
            "last_update": datetime.utcnow().isoformat()
        }

        memory.client.table("session_coordination") \
            .update(update_data) \
            .eq("session_name", session_name) \
            .execute()

        logger.info(f"✅ Updated {session_name} status: {status}")

    except Exception as e:
        logger.error(f"Failed to update session status: {e}")


if __name__ == "__main__":
    import sys

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    # Get session name from command line or environment
    session_name = sys.argv[1] if len(sys.argv) > 1 else "nacpac_agent"

    logger.info(f"🔄 Syncing session: {session_name}")

    # Sync session status
    session_status = sync_session(session_name)

    if session_status:
        agent_id = session_status.get("agent_id")
        current_phase = session_status.get("current_phase")

        logger.info(f"\n📋 Tasks for phase '{current_phase}':")

        # Get assigned tasks
        tasks = get_assigned_tasks(agent_id)

        if tasks:
            for task in tasks:
                if task.get("phase") == current_phase:
                    logger.info(f"  - [{task.get('status')}] {task.get('task_name')}")
        else:
            logger.info("  (No tasks assigned yet)")

        logger.info("\n✅ Sync complete. Ready to work!")
    else:
        logger.error("❌ Sync failed. Check Supabase connection.")
        sys.exit(1)
