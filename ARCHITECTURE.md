# Jico Org Multi-Agent Architecture

## Overview

**Central coordination in this repo (nacpac-dev).** Specialized agent sessions (nacpac agent, jico agent, etc.) work autonomously but stay in sync via Supabase + git.

```
JICO-ORG (nacpac-dev repo) — Central Hub
├─ Command: Plan, review, coordinate
├─ Document: ARCHITECTURE.md, DECISIONS.md
├─ Maintain: agent tasks, session status
│
├─ NACPAC AGENT SESSION (Claude Desktop)
│  ├─ Own: AGENT_NACPAC_CONTEXT.md
│  ├─ Build: NacPac Dev Agent (skillsets → learning → UI → live)
│  ├─ Sync: Auto-fetch from session_coordination table
│  └─ Cron: Check for updates every 30 min
│
├─ JICO AGENT SESSION (future)
│  ├─ Own: AGENT_JICO_CONTEXT.md
│  └─ Similar workflow
│
└─ JICO AMAZON SESSION (future)
   ├─ Own: AGENT_AMAZON_CONTEXT.md
   └─ Similar workflow
```

---

## Layers

### **Layer 1: Persistent State (Supabase)**
- `agent_skillsets` — Agent technical capabilities (7 for nacpac_dev)
- `learned_patterns` — Successful task patterns agents learn from
- `session_coordination` — What each session is building, current phase, status
- `agent_tasks` — Task breakdown: Phase 1 = 5 tasks, Phase 2 = 6 tasks, etc.
- `tasks` — User-submitted tasks (Discord → task creation)
- `runs` — Agent execution logs (what ran, cost, result)
- `builds` — Build artifacts (APK, EXE, GLB with R2 links)
- `deployments` — Deployment history
- `costs` — Cost tracking ($60/month budget)

### **Layer 2: Session Context (Markdown in Repo)**
- `AGENT_NACPAC_CONTEXT.md` — NacPac agent status, phase, completed work
- `AGENT_JICO_CONTEXT.md` — Jico agent status (future)
- `AGENT_AMAZON_CONTEXT.md` — Amazon agent status (future)

### **Layer 3: Agent Code (Session Repos)**
Each session has:
- `agentic/agents/nacpac_dev.py` — Agent class with skillsets + task execution
- `agentic/seed_skillsets.py` — Populate agent_skillsets in Supabase
- `agentic/test_skillsets.py` — Verify skillsets load correctly

### **Layer 4: Coordination Scripts**
- `agentic/session_sync.py` — Auto-sync: fetch session status from Supabase
- `agentic/cron_check.py` — Run every 30 min to check for phase updates
- Discord bot integration — `/task nacpac "add feature"`

---

## Workflow: Adding a New Agent

### **Example: Adding Jico Life Dev Agent**

1. **In this session (nacpac-dev):**
   - Create `AGENT_JICO_CONTEXT.md`
   - Define jico_life_dev skillsets in AGENT_ONBOARDING.md
   - Add entry to `session_coordination` table in Supabase (manually)
   - Add tasks to `agent_tasks` table for Phase 1-8

2. **New session (jico agent):**
   - Clone nacpac-dev repo
   - Copy AGENT_JICO_CONTEXT.md from this repo
   - Update agent_id references (nacpac_dev → jico_life_dev)
   - Build agent following AGENT_ONBOARDING.md checklist

3. **Sync mechanism:**
   - jico agent session runs `python agentic/session_sync.py` on startup
   - Fetches current phase from `session_coordination` table
   - Reads its own `AGENT_JICO_CONTEXT.md` for detailed instructions
   - Cron job checks for updates every 30 min

---

## Session Lifecycle

### **Phase 1: Skillsets**
- Define 7-10 core skillsets
- Seed to agent_skillsets table
- Test loading + injection into prompts

### **Phase 2: Learning**
- Create learned_patterns table
- Capture successful task patterns
- Update agent to query learned patterns

### **Phase 3: Memory**
- Task history + build logs
- Deployment tracking
- Cost per task

### **Phase 4: Feature Generation**
- Wire feature_agent for code proposals
- Discord approval flow
- Auto-commit approved changes

### **Phase 5: Build Pipeline**
- APK/EXE build execution
- R2 backup integration
- Build progress tracking

### **Phase 6: Dashboard UI**
- Real-time agent status
- Pending proposals queue
- Cost monitoring

### **Phase 7: Testing**
- Smoke tests (agent init + skillsets)
- End-to-end task execution
- Error handling + rollback

### **Phase 8: Go Live**
- Production deployment
- Real builds (BUILD_TEST_MODE=false)
- Monitor first tasks

---

## Communication Flow

```
User (Discord)
  ↓
Command: "/task nacpac add checkout feature"
  ↓
Discord Bot (in nacpac agent session)
  ↓
Parse → Route to nacpac_dev agent
  ↓
NacPac Dev Agent
  ├─ Load skillsets from agent_skillsets table
  ├─ Query learned_patterns for similar tasks
  ├─ Generate proposal via feature_agent
  ├─ Post to Discord for approval
  ├─ On approval: build APK/EXE
  ├─ Backup to R2
  ├─ Deploy to staging
  └─ Report results in Discord
  ↓
Task logged in tasks table (with cost + result)
  ↓
Pattern saved in learned_patterns (for future tasks)
```

---

## Key Files

| File | Purpose | Owner |
|------|---------|-------|
| `ARCHITECTURE.md` | This file — system design | nacpac-dev (this session) |
| `AGENT_ONBOARDING.md` | New agent checklist | nacpac-dev |
| `SESSION_PROTOCOL.md` | Rules all sessions follow | nacpac-dev |
| `AGENT_NACPAC_CONTEXT.md` | NacPac agent status | nacpac agent session |
| `DECISIONS.md` | Locked decisions (append-only) | nacpac-dev |
| `agentic/agents/nacpac_dev.py` | Agent class + skillsets | nacpac agent session |
| `agentic/session_sync.py` | Auto-sync from Supabase | nacpac agent session |

---

## Security & Access

- **Supabase Service Role Key**: Stored in env vars only (never in git)
- **Session secrets**: Each session has its own .env (not committed)
- **API keys**: Discord token, EAS token, GitHub token in env
- **Cost gates**: Enforced in memory layer ($60/month limit)

---

## Cost Tracking ($60/month budget)

- Claude Sonnet calls: ~$0.003 per call
- Supabase: ~$25/month (for data storage + API calls)
- EAS builds: $25/month tier included
- R2 storage: ~$5/month
- Remaining: $5/month buffer

Tracked per-task in `costs` table. Daily/monthly totals checked before agent runs.

---

## Next Steps (Immediate)

1. ✅ Supabase tables created (session_coordination, agent_tasks)
2. ⏳ Create AGENT_ONBOARDING.md (this session)
3. ⏳ Create SESSION_PROTOCOL.md (this session)
4. ⏳ Create AGENT_NACPAC_CONTEXT.md (this session)
5. ⏳ nacpac agent session: Build Phase 1-8 using AGENT_ONBOARDING.md
6. ⏳ This session: Review + approve each phase completion

---

## Adding New Agents (Future)

See `AGENT_ONBOARDING.md` for step-by-step checklist when adding:
- Jico Life Dev Agent
- Jico Amazon Bot
- Jico Meta Bot
- MCPO agents (Marketing, Customer Success, Product, Operations)
