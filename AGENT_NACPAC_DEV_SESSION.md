# NacPac Dev Agent — Session Handoff

## Context
Building agents one at a time in separate Claude Code sessions to keep context focused and prevent bloat.

**Previous Session Progress:**
- ✅ Created `agent_skillsets` table migration (Supabase)
- ✅ Added `get_agent_skillsets()` to memory layer
- ✅ Updated NacPacDevAgent to load skillsets on init
- ✅ Added skillset context formatting for Claude

**Commit:** `147fd7a` — "feat: add agent skillsets infrastructure"

---

## This Session's Tasks

### **Task 1: Define NacPac Dev Skillsets**
**File:** `agentic/agents/nacpac_dev.py`

NacPac Dev Agent should possess these 7 skillsets:

1. **nacpac_codebase**
   - Custom sticker printing app (mobile + desktop)
   - Tech stack: React Native, Express.js, PostgreSQL
   - Key files: App.js, backend/server.js, package.json
   
2. **python**
   - Version: 3.9+
   - For scripting, automation, agent tooling
   
3. **nodejs**
   - Version: 18+
   - Express.js backend, npm ecosystem
   
4. **react**
   - Component structure, hooks, state management
   - Used in React Native mobile + potential web
   
5. **expo_dev**
   - APK builds via EAS
   - Development workflow, device testing
   
6. **npm**
   - Dependency management, build scripts
   - EXE packaging for Windows
   
7. **exe_windows**
   - Electron or npm build tools
   - Windows installer creation

**Deliverable:** Create `SKILLSETS.md` with full documentation for each skillset.

---

### **Task 2: Seed Skillsets in Supabase**
**Files:** 
- Create seed script or SQL insert statements
- Run migration and populate `agent_skillsets` table

**Steps:**
1. Run the migration: `migrations/001_create_agent_skillsets.sql`
2. Insert the 7 skillsets for agent_id="nacpac_dev"
3. Verify they load on agent init

---

### **Task 3: Test Skillset Injection**
**File:** `agentic/agents/nacpac_dev.py`

Verify that:
1. Agent loads skillsets from Supabase on `__init__`
2. Skillsets appear in log: `Loaded skillsets: nacpac_codebase, python, nodejs, react, expo_dev, npm, exe_windows`
3. `get_skillsets_context()` formats skillsets nicely
4. Skillsets are injected into task execution (next step)

---

### **Task 4: Inject Skillsets into Task Execution**
**File:** `agentic/agents/nacpac_dev.py`

Add skillset context to agent decision-making:
- When agent receives a task, prepend skillset context to the prompt
- Example: `"You are NacPac Dev Agent with these skillsets: [...]"`
- This pre-feeds the agent's technical knowledge before solving tasks

---

### **Task 5: Document & Commit**
- Update `SKILLSETS.md` if needed
- Run smoke tests (verify agent initializes with skillsets)
- Commit with message: `"feat: seed nacpac dev agent skillsets and inject into task execution"`
- Push to `claude/agentic-system-org-j9gvae`

---

## Success Criteria

✅ Agent loads 7 skillsets from Supabase on init
✅ Skillsets are formatted as human-readable context
✅ Skillsets are injected into Claude prompts before task execution
✅ Log shows: `Loaded skillsets: nacpac_codebase, python, nodejs, react, expo_dev, npm, exe_windows`
✅ No breaking changes to existing build/deploy methods

---

## Quick Reference

**Key Files:**
- `agentic/agents/nacpac_dev.py` — Agent class
- `agentic/memory.py` — Already has `get_agent_skillsets()`
- `migrations/001_create_agent_skillsets.sql` — Already created
- `SKILLSETS.md` — To be created (documentation)

**Supabase Table:** `agent_skillsets`
- Columns: id, agent_id, skillset_name, description, documentation, version, created_at, updated_at

**Agent ID:** `"nacpac_dev"`

---

## Next Session (Phase 2)
- Add Jico Life Dev Agent in separate session
- Add learned_patterns table (agent learning)
- Implement skill improvement feedback loop
