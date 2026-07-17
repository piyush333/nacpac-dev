#!/usr/bin/env python3
"""Check for new phase assignments from central governance.

This script is run by agent sessions on startup to detect if they've been
assigned a new phase. It reads GOVERNANCE.md, checks current phase, and
automatically transitions to next phase if assigned.

Usage:
    python agentic/check_phase_assignment.py <agent_id>

Example:
    python agentic/check_phase_assignment.py nacpac_dev
"""

import re
import sys
from pathlib import Path
from typing import Optional, Tuple

def read_governance() -> dict:
    """Read GOVERNANCE.md and parse phase assignments."""
    gov_path = Path(__file__).parent.parent / "GOVERNANCE.md"

    if not gov_path.exists():
        return {}

    with open(gov_path) as f:
        content = f.read()

    assignments = {}

    # Parse NacPac Dev Agent section
    nacpac_match = re.search(
        r"### \*\*NacPac Dev Agent\*\*\s*\n(.*?)(?=###|\Z)",
        content,
        re.DOTALL
    )
    if nacpac_match:
        section = nacpac_match.group(1)
        current = extract_phase(section, "Current Phase")
        assigned = extract_phase(section, "Assigned Phase")
        assignments["nacpac_dev"] = {
            "current_phase": current,
            "assigned_phase": assigned,
            "name": "NacPac Dev Agent"
        }

    # Parse Jico Life Agent section
    jico_match = re.search(
        r"### \*\*Jico Life Dev Agent\*\*\s*\n(.*?)(?=###|\Z)",
        content,
        re.DOTALL
    )
    if jico_match:
        section = jico_match.group(1)
        current = extract_phase(section, "Current Phase")
        assigned = extract_phase(section, "Assigned Phase")
        assignments["jico_life_dev"] = {
            "current_phase": current,
            "assigned_phase": assigned,
            "name": "Jico Life Dev Agent"
        }

    return assignments


def extract_phase(section: str, label: str) -> Optional[int]:
    """Extract phase number from section text.

    Looks for patterns like:
    - Current Phase: 2 (✅ COMPLETE)
    - Assigned Phase: 3 (Memory Integration)
    """
    pattern = rf"- \*\*{label}\*\*:\s*(\d+)"
    match = re.search(pattern, section)
    return int(match.group(1)) if match else None


def check_assignment(agent_id: str) -> Tuple[Optional[int], Optional[int], str]:
    """Check if agent has new phase assignment.

    Returns:
        (current_phase, assigned_phase, status_message)
    """
    assignments = read_governance()

    if agent_id not in assignments:
        return None, None, f"❌ Agent {agent_id} not found in GOVERNANCE.md"

    info = assignments[agent_id]
    current = info["current_phase"]
    assigned = info["assigned_phase"]
    name = info["name"]

    if current is None or assigned is None:
        return current, assigned, f"⚠️  Could not parse phases for {name}"

    if assigned > current:
        return current, assigned, f"🟢 New assignment: Phase {assigned} (current: {current})"
    elif assigned == current:
        return current, assigned, f"⏳ Still on Phase {current}"
    else:
        return current, assigned, f"❌ Error: assigned phase ({assigned}) < current ({current})"


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python check_phase_assignment.py <agent_id>")
        print("Example: python check_phase_assignment.py nacpac_dev")
        sys.exit(1)

    agent_id = sys.argv[1]
    current, assigned, message = check_assignment(agent_id)

    print(message)

    if assigned and current and assigned > current:
        print(f"\n✅ Agent {agent_id} should start Phase {assigned}")
        print(f"   See NACPAC_DEV_PHASES.md (Phase {assigned} section) for details")
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
