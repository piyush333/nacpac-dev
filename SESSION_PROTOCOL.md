# Session Protocol

**Rules all sessions (nacpac agent, jico agent, etc.) must follow for cohesion.**

---

## **Core Rules**

### **1. Read on Startup & Check Phase Assignment**
Every session reads these in this order on startup:
1. `ARCHITECTURE.md` (understand the system)
2. `GOVERNANCE.md` (check if you have a new phase assignment)
3. `AGENT_{AGENT_ID}_CONTEXT.md` (your agent's current status)
4. Run: `python agentic/check_phase_assignment.py {agent_id}` (check for phase change)
5. Run: `python agentic/session_sync.py` (fetch latest from central coordination)

**Example for nacpac agent:**
```bash
# On startup, run:
python agentic/check_phase_assignment.py nacpac_dev

# If output says "🟢 New assignment: Phase 3", then:
# - You should start Phase 3 work
# - Update AGENT_NACPAC_CONTEXT.md to reflect new phase
# - Follow NACPAC_DEV_PHASES.md (Phase 3 section)
```

### **2. One Agent Per Session**
- **nacpac agent** session → only works on nacpac_dev agent
- **jico agent** session → only works on jico_life_dev agent
- No cross-agent work in a single session (prevents context bloat)

### **3. Follow Phase Sequence**
Build in this order; **never skip ahead**:
1. Phase 1: Skillsets (define, seed, test)
2. Phase 2: Learning (learned_patterns, feedback loop)
3. Phase 3: Memory (task tracking, logs)
4. Phase 4: Feature Generation (proposals, approval flow)
5. Phase 5: Build Pipeline (APK/EXE/Web builds)
6. Phase 6: Dashboard UI (status, monitoring)
7. Phase 7: Testing (smoke tests, E2E)
8. Phase 8: Go Live (production deployment)

**Why?** Later phases depend on earlier phases. Phase 4 needs Phase 1 skillsets. Phase 5 needs Phase 3 memory.

### **4. Update Context File Continuously**
Keep `AGENT_{AGENT_ID}_CONTEXT.md` updated:

**On startup:**
```markdown
## Status
- Phase: [Current Phase]
- Status: [waiting | building | testing | live]
- Last Sync: [Timestamp from session_sync.py]
```

**When starting a phase:**
```markdown
## Current Phase
- Phase 2: Learning
- Started: 2026-07-17 15:00
- Tasks:
  - [ ] Create learned_patterns table
  - [ ] Implement feedback loop
  - [ ] Test pattern queries
```

**When completing tasks:**
```markdown
✅ Create learned_patterns table (committed: abc1234)
⏳ Implement feedback loop
❌ Test pattern queries (blocked: missing data)
```

### **5. Commit Messages Format**

**Always use this format:**
```
feat: {agent_id} phase {N} - {feature}

Completed:
- [x] Task 1
- [x] Task 2

Related tables:
- learned_patterns (new)
- tasks (updated)

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01F4vyraqa2XqBszd4aUXvLW
```

### **6. Push Only to Main Branch**
- All work goes to: `claude/agentic-system-org-j9gvae`
- No side branches per agent
- This keeps history linear and simple

### **7. Sync Before & After Each Phase**
```bash
# Before starting phase:
git fetch origin
git pull origin claude/agentic-system-org-j9gvae
python agentic/session_sync.py

# After completing phase:
git push origin claude/agentic-system-org-j9gvae
```

### **8. Test Before Committing**
Before pushing:
```bash
python -m pytest agentic/test_*.py
python agentic/agents/{agent_id}.py
```

---

## **How Central Governance Works**

### **Phase Assignment Flow**
```
Central Session (nacpac-dev):
1. Updates GOVERNANCE.md with new phase assignment
2. Commits & pushes to git
3. (Done — no need to message agent directly)

Agent Session (nacpac_dev):
1. On startup, runs: python agentic/check_phase_assignment.py nacpac_dev
2. Sees: "🟢 New assignment: Phase 3"
3. Updates AGENT_NACPAC_CONTEXT.md phase indicator
4. Starts Phase 3 work per NACPAC_DEV_PHASES.md
5. Commits work regularly
6. When complete, pushes to git

Central Session:
1. Fetches latest commits
2. Reads PHASE{N}_COMPLETION_CHECKLIST.md
3. Updates GOVERNANCE.md with new status
4. Assigns Phase {N+1}
5. (Cycle repeats)
```

### **Key Points**
- **No manual messages needed** — agents auto-detect assignments via git
- **Git is source of truth** — GOVERNANCE.md is the single assignment record
- **Async by design** — agent doesn't wait for central; reads file, acts independently
- **Scalable** — add new agents by adding sections to GOVERNANCE.md

---

## **File Ownership**
| File | Owner | Edit Rules |
|------|-------|-----------|
| `ARCHITECTURE.md` | Central | Only central session |
| `AGENT_{AGENT_ID}_CONTEXT.md` | That session | Update continuously |
| `agentic/agents/{agent_id}.py` | That session | Free to modify |

---

## **Supabase Tables**

| Table | Read | Write | Notes |
|------|------|-------|-------|
| `agent_skillsets` | ✅ | (central only) | Read on startup |
| `learned_patterns` | ✅ | ✅ | Read patterns, write results |
| `session_coordination` | ✅ | (central only) | Check phase/status |
| `agent_tasks` | ✅ | (central only) | See assigned tasks |
| `tasks` | ✅ | ✅ | Read requests, update results |
| `runs` | ✅ | ✅ | Log executions |
| `builds` | - | ✅ | Log artifacts |
| `deployments` | - | ✅ | Log deployments |

---

## **Escalation Path**

If stuck:
1. Check `ARCHITECTURE.md`
2. Check `AGENT_ONBOARDING.md`
3. Update `session_coordination` status='blocked'
4. Central session responds in next meeting

---

**This protocol ensures all sessions work cohesively without context bloat.**
