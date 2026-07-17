# Agent Onboarding Checklist

**Use this checklist every time a new agent/session is added to Jico Org.**

---

## **Pre-Onboarding (in nacpac-dev session)**

### **1. Define Agent Identity**

Fill in these details:
- **Agent Name**: e.g., "Jico Life Dev Agent", "Jico Amazon Bot"
- **Agent ID**: e.g., "jico_life_dev", "jico_amazon_bot" (snake_case, no spaces)
- **Session Name**: e.g., "jico agent", "jico amazon" (what the Claude Desktop session will be named)
- **Tech Stack**: e.g., "TypeScript, Three.js, AR SDK, React"
- **Repo Path**: e.g., "https://github.com/jico-org/jico-life"
- **Primary Task**: e.g., "Build AR acoustic felt decor app"

### **2. Define Skillsets (7-10 per agent)**

List the core technical skillsets this agent needs:

**Example (Jico Life Dev Agent):**
1. jico_life_codebase — AR app architecture, Three.js, React
2. typescript — Type-safe development
3. threejs — 3D graphics + AR rendering
4. ar_sdk — AR framework (ARKit/ARCore)
5. react — UI components
6. mobile_dev — iOS/Android testing
7. webgl — WebGL shader programming
8. node_backend — Backend services (if needed)
9. firebase — Real-time database (if using)
10. deployment — App store submission (if needed)

### **3. Prepare Supabase Schema**

**Create these SQL entries manually in Supabase:**

#### **A. session_coordination entry**
```sql
INSERT INTO session_coordination (session_name, agent_id, status, current_phase, context_file, cron_interval, notes)
VALUES (
  'jico agent',
  'jico_life_dev',
  'waiting',
  'skillsets',
  'AGENT_JICO_CONTEXT.md',
  30,
  'Jico Life AR app development agent - Phase 0 MVP'
);
```

#### **B. agent_tasks entries (Phase 1-8)**

For each phase, create tasks:

```sql
-- Phase 1: Skillsets
INSERT INTO agent_tasks (agent_id, phase, task_name, description, status, assigned_to)
VALUES
('jico_life_dev', 'skillsets', 'Define skillsets', 'List 7-10 core skillsets', 'pending', 'jico agent'),
('jico_life_dev', 'skillsets', 'Create SKILLSETS.md', 'Document all skillsets with details', 'pending', 'jico agent'),
('jico_life_dev', 'skillsets', 'Seed to Supabase', 'Insert skillsets into agent_skillsets table', 'pending', 'jico agent'),
('jico_life_dev', 'skillsets', 'Test skillset loading', 'Verify agent loads skillsets on init', 'pending', 'jico agent');

-- Phase 2: Learning
INSERT INTO agent_tasks (agent_id, phase, task_name, description, status, assigned_to)
VALUES
('jico_life_dev', 'learning', 'Create learned_patterns table', 'Schema for storing successful patterns', 'pending', 'jico agent'),
('jico_life_dev', 'learning', 'Implement feedback loop', 'Capture patterns from successful tasks', 'pending', 'jico agent'),
('jico_life_dev', 'learning', 'Query & inject patterns', 'Agent queries learned patterns before decisions', 'pending', 'jico agent'),
('jico_life_dev', 'learning', 'Test pattern matching', 'Verify patterns help with similar tasks', 'pending', 'jico agent');

-- Phase 3-8 follow similar pattern
```

#### **C. agent_skillsets entries**

```sql
-- For each skillset, insert:
INSERT INTO agent_skillsets (agent_id, skillset_name, description, documentation, version)
VALUES
('jico_life_dev', 'jico_life_codebase', 'AR app architecture...', 'Full documentation...', '1.0'),
('jico_life_dev', 'typescript', 'TypeScript 4.9+...', 'Full documentation...', '1.0'),
-- ... repeat for all 7-10 skillsets
```

---

## **Onboarding (in new agent session)**

### **4. Create Agent Context File**

Create `AGENT_{AGENT_ID}_CONTEXT.md` in the session repo (copy from AGENT_NACPAC_CONTEXT.md and customize):

```markdown
# {Agent Name} — Session Context

## Identity
- Agent ID: {agent_id}
- Session Name: {session_name}
- Tech Stack: {stack}
- Primary Repo: {repo_url}

## Current Status
- Phase: Skillsets (Building)
- Status: Building
- Last Sync: [auto-filled]

## Phase Breakdown
- Phase 1: Skillsets ⏳
- Phase 2: Learning ⏳
- Phase 3: Memory ⏳
- Phase 4: Feature Generation ⏳
- Phase 5: Build Pipeline ⏳
- Phase 6: Dashboard UI ⏳
- Phase 7: Testing ⏳
- Phase 8: Go Live ⏳

## Skillsets (7-10)
1. {skillset_name} — {description}
2. {skillset_name} — {description}
[...]

## How to Use This File
- Update "Phase:" when starting a new phase
- Check "Last Sync:" to see when you last synced with central session
- Run `python agentic/session_sync.py` to auto-update this file
```

### **5. Copy Core Infrastructure**

Copy these from nacpac-dev into the new session repo:

```
agentic/
├─ __init__.py
├─ config.py
├─ memory.py
├─ cost_tracker.py
├─ session_sync.py (NEW — see below)
├─ agents/
│  ├─ __init__.py
│  └─ {agent_id}.py (e.g., jico_life_dev.py — customize from nacpac_dev.py)
├─ tools/
│  ├─ git_tools.py
│  ├─ build_tools.py
│  ├─ deploy_tools.py
│  └─ backup_tools.py
└─ migrations/
   └─ 001_create_agent_skillsets.sql (already done globally)
```

### **6. Create session_sync.py**

Create `agentic/session_sync.py` for auto-sync:

```python
"""Auto-sync session context from central Supabase coordination."""

import logging
from agentic.memory import memory

logger = logging.getLogger(__name__)

def sync_session(session_name: str):
    """Fetch session status from Supabase and log it."""
    if not memory.client:
        logger.warning("Supabase unavailable; skipping sync")
        return
    
    try:
        result = memory.client.table("session_coordination") \
            .select("*") \
            .eq("session_name", session_name) \
            .execute()
        
        if result.data:
            status = result.data[0]
            logger.info(f"""
╔════════════════════════════════════════╗
║ SESSION SYNC - {session_name.upper()}
╠════════════════════════════════════════╣
║ Agent ID: {status['agent_id']}
║ Status: {status['status']}
║ Current Phase: {status['current_phase']}
║ Last Update: {status['last_update']}
║ Notes: {status['notes']}
╚════════════════════════════════════════╝
            """)
            return status
        else:
            logger.warning(f"No session found: {session_name}")
            return None
    except Exception as e:
        logger.error(f"Failed to sync session: {e}")
        return None

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    sync_session("nacpac_agent")  # or "jico_agent", etc.
```

### **7. Customize Agent Class**

Update `agentic/agents/{agent_id}.py`:

```python
"""Replace nacpac_dev references with your agent_id."""

# In __init__:
self.brand = "{brand_name}"  # e.g., "jico_life"
self.agent_id = "{agent_id}"  # e.g., "jico_life_dev"

# In _load_skillsets:
self.skillsets = memory.get_agent_skillsets("{agent_id}")

# Customize build methods based on agent's tech stack
# (APK/EXE for nacpac_dev → ARB/Web for jico_life_dev, etc.)
```

### **8. Create Cron Job**

Set up a cron to auto-sync every 30 minutes:

**On Linux/Mac:**
```bash
# Add to crontab -e:
*/30 * * * * cd /path/to/repo && python -m agentic.session_sync
```

**On Windows (Task Scheduler):**
```
Trigger: Every 30 minutes
Action: Run C:\python\python.exe C:\path\to\repo\agentic\session_sync.py
```

---

## **Phase Execution (in new agent session)**

### **9. Execute Phase 1: Skillsets**

Follow the AGENT_NACPAC_SESSION.md pattern:

1. Create `SKILLSETS.md` with all 7-10 skillsets documented
2. Run: `python -m agentic.seed_skillsets`
3. Verify: `python -m agentic.test_skillsets`
4. Commit: `feat: seed {agent_id} skillsets`
5. Push to branch `claude/agentic-system-org-j9gvae`

### **10. Execute Phases 2-8**

For each phase:
1. Update `AGENT_{AGENT_ID}_CONTEXT.md` (set current phase)
2. Complete phase tasks (see agent_tasks table)
3. Commit with message: `feat: {agent_id} phase {N} - {feature}`
4. Push to `claude/agentic-system-org-j9gvae`
5. Report back to central session (nacpac-dev)

### **11. Central Session Reviews**

Back in nacpac-dev session:
1. Review commits from agent session
2. Update `session_coordination` table:
   ```sql
   UPDATE session_coordination
   SET status = 'live', current_phase = 'live'
   WHERE agent_id = 'jico_life_dev';
   ```
3. Update this agent's entry in ARCHITECTURE.md

---

## **Post-Onboarding**

### **12. Documentation**

Create in the agent's session repo:
- `AGENT_{AGENT_ID}_CONTEXT.md` ✅ (done in step 4)
- `README_AGENT.md` (how to run this agent)
- `SKILLSETS.md` ✅ (done in Phase 1)
- `ERRORS_AND_FIXES.md` (troubleshooting)

### **13. Testing**

Before going live:
- [ ] Agent loads all skillsets without errors
- [ ] Agent can receive a sample task from Discord
- [ ] Agent processes task end-to-end (build, deploy, report)
- [ ] Logs appear in correct Discord channels
- [ ] Cost tracking works ($X per task)

### **14. Deployment**

- [ ] Set `BUILD_TEST_MODE=false` (real builds)
- [ ] Deploy Discord bot to production
- [ ] Monitor first 5 real tasks
- [ ] Set up alerts for failures
- [ ] Document runbook for agent maintenance

---

## **Quick Reference: File Checklist**

**Create in new agent session:**
- [ ] `AGENT_{AGENT_ID}_CONTEXT.md`
- [ ] `agentic/agents/{agent_id}.py` (customize from nacpac_dev.py)
- [ ] `agentic/session_sync.py` (copy template above)
- [ ] `SKILLSETS.md` (Phase 1 deliverable)
- [ ] Cron job configured

**Create in nacpac-dev (central) session:**
- [ ] Entry in `session_coordination` table (Supabase)
- [ ] Phase 1-8 entries in `agent_tasks` table (Supabase)
- [ ] Agent skillsets in `agent_skillsets` table (Supabase)
- [ ] Update `ARCHITECTURE.md` with agent reference

---

## **Template SQL for New Agent**

Copy-paste this template and customize:

```sql
-- 1. Add session_coordination entry
INSERT INTO session_coordination (session_name, agent_id, status, current_phase, context_file, cron_interval, notes)
VALUES ('[SESSION_NAME]', '[AGENT_ID]', 'waiting', 'skillsets', 'AGENT_[AGENT_ID]_CONTEXT.md', 30, '[DESCRIPTION]');

-- 2. Add skillset entries (repeat for each skillset)
INSERT INTO agent_skillsets (agent_id, skillset_name, description, documentation, version)
VALUES ('[AGENT_ID]', '[SKILLSET_NAME]', '[DESCRIPTION]', '[FULL_DOCUMENTATION]', '1.0');

-- 3. Add Phase 1 tasks (repeat for each phase)
INSERT INTO agent_tasks (agent_id, phase, task_name, description, status, assigned_to)
VALUES
('[AGENT_ID]', 'skillsets', 'Define skillsets', 'List all core skillsets', 'pending', '[SESSION_NAME]'),
('[AGENT_ID]', 'skillsets', 'Create SKILLSETS.md', 'Full documentation', 'pending', '[SESSION_NAME]'),
-- ... add more tasks
```

---

## **Support**

**Questions about:**
- **Architecture**: See `ARCHITECTURE.md`
- **Session protocol**: See `SESSION_PROTOCOL.md`
- **Phase details**: See `AGENT_NACPAC_SESSION.md` (reference implementation)
- **New agent setup**: You're reading it! 📖

**Need help?** Update `session_coordination` table with status='blocked' and notes, then ask in nacpac-dev session.
