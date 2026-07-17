# Jico Org Memory — System State & Decisions

**Last updated:** 2026-07-06  
**Status:** ✅ Phase 1 COMPLETE — LIVE on DigitalOcean

---

## Org Structure

| Brand | Purpose | Repo | Tech Stack | Current Status |
|-------|---------|------|-----------|-----------------|
| **NacPac** | Sticker printing & packaging (India) | `nacpac-workspace-main/` | Mobile: Expo/React Native, Desktop: Electron, Web: HTML/CSS/JS | ✅ APK + EXE in production |
| **Jico Life** | Acoustic felt decor + AR try-on | `nacpac-workspace-main/` (same workspace) | AR: Static HTML + model-viewer (Google), hosted on Netlify, 3D models (GLB) from Google Drive renders | ✅ AR web app in production (Netlify) |

---

## System Status

### DEPLOYMENT STATUS (2026-07-06)
✅ **APP LIVE** — DigitalOcean dolhin-app running in production
- **Discord Bot**: Connected, listening to #general
- **Health Server**: aiohttp on port 8080, responding to probes
- **Orchestrator**: Parsing natural language commands
- **Tested**: Message parsing → intent routing → task logging ✅
- **Build Mode**: Currently TEST_MODE (simulated builds)

### Current Architecture
- **Deployment**: DigitalOcean App Platform (auto-deploy from jico-org/agentic-system repo)
- **Database**: Supabase (optional, configured but not required for operation)
- **Runtime**: Python 3.11 + aiohttp + discord.py
- **Docker**: python:3.11-slim, health checks enabled
- **Cost**: ~$5/month DO base app

### Old System (Reference)
- **jico-system/**: Kept as reference; not currently used
  - Partial Discord bot, keyword router, in-memory state (no persistence)
  - Reliable for basic tasks but not scalable

### New System Status
- ✅ `agentic/` directory fully deployed
- ✅ Orchestrator agent with Haiku parsing (fast, cheap)
- ✅ Discord approval workflow (buttons Y/N)
- ✅ NacPac Dev Agent ready (build APK/EXE)
- ✅ Jico Life Dev Agent ready (build AR app)
- ✅ Cost gating ($10/day, $50/month enforced)
- ✅ Health checks passing
- ⚠️ BUILD_TEST_MODE = true (switch to false for real builds)

---

## Locked Decisions (This Session)

| Date | Decision | Rationale | Owner |
|------|----------|-----------|-------|
| 2026-07-02 | Build fresh `agentic/`, not patch jico-system | Cleaner, untested fail-safe code in jico-system | Piyush |
| 2026-07-02 | Scope Phase 1: Dev agents only (NacPac, Jico Life) + Orchestrator | MCPO agents (marketing/ads) deferred to Phase 2 | Piyush |
| 2026-07-02 | Memory: Supabase + git markdown mirror | Hybrid: durable DB + human-readable docs | Piyush |
| 2026-07-02 | Runtime: Claude Agent SDK (Python) | Orchestration, subagents, tool calling, memory built-in | Piyush |
| 2026-07-02 | Interface: Discord | User familiar, existing bot setup, button UX proven | Piyush |
| 2026-07-02 | Deployment: Remote (systemd on Oracle VM, not local machine) | Always-on, recoverable, independent of dev machine | Piyush |
| 2026-07-02 | Approval: Discord buttons (Y/N) before builds/deploys | Clear UX, audit trail, prevents accidental deploys | Piyush |
| 2026-07-02 | Failsafe: Dead letter queue + auto-retry + health monitor | Graceful degradation; system recovers from crashes | Piyush |
| 2026-07-02 | Backup: 3-platform (R2 + Google Drive + GitHub Releases) | No single point of failure; accessible from multiple places | Piyush |
| 2026-07-02 | Token optimization: Haiku for screening/routing, Sonnet for reasoning | Cost control; use smarter model only when needed | Piyush |

---

## Phase 0 Deliverables (Memory Foundation) — ✅ COMPLETE

- [x] MEMORY.md (this file) — current state
- [x] DECISIONS.md — append-only decision log  
- [x] SESSION_PROTOCOL.md — session rules
- [x] All clarifications documented

## Phase 1 Deliverables (Agentic System Architecture) — ✅ COMPLETE

### Core Infrastructure Built
- [x] **Agent Registry System** (`registry.py`)
  - Dynamic agent discovery
  - Capability-based routing
  - Self-registering agents
  
- [x] **Task Queue** (`queue.py`)
  - Redis-based work distribution
  - Dead letter queue for failures
  - Result tracking

- [x] **Preview System** (`preview.py`)
  - Local app rendering (npm start, expo start)
  - Playwright screenshot integration
  - Complete preview workflow

- [x] **CLI Interface** (`cli.py`)
  - Build, preview, status commands
  - Local testing without Discord
  - Agent listing and troubleshooting

### Existing Code (Previously Built)
- [x] Orchestrator Agent (intent parsing + routing)
- [x] NacPac Dev Agent (build_apk, build_exe)
- [x] Jico Life Dev Agent (build_ar)
- [x] Build tools (EAS, npm, GLB)
- [x] Git tools (clone, branch, commit)
- [x] Cost tracker ($10/day, $50/month gating)
- [x] Memory layer (PostgreSQL client)
- [x] Discord bot (natural language interface)

### Documentation Built
- [x] `AGENT_BUILD_GUIDE.md` — How to build new agents
- [x] `MCP_SERVER_GUIDE.md` — How to build MCP servers (Phase 2+)
- [x] `INTEGRATION_CHECKLIST.md` — Testing & deployment procedures
- [x] `.env.template` — Updated with DB credentials

### Status
- ✅ Code committed to `claude/agentic-system-org-j9gvae`
- ✅ Ready for local testing (GitBash)
- ✅ Ready for database setup (credentials pending)
- ✅ Scalable architecture for Phase 2+

---

## Build Commands & Deployment

### NacPac (nacpac-workspace-main/)
| Target | Command | Approval | Backup to |
|--------|---------|----------|-----------|
| **APK** | `eas build --platform android --profile preview --non-interactive` | Manual | R2 + GDrive + GitHub Releases |
| **EXE** | `cd desktop && npm run build` | Manual | R2 + GDrive + GitHub Releases |
| Deploy to staging | SCP to staging server + systemd restart | Manual | Documented in Supabase |
| Deploy to prod | SCP to prod + systemd restart | Manual + double-confirm | Documented in Supabase |

### Jico Life (nacpac-workspace-main/)
| Target | Command | Approval | Backup to |
|--------|---------|----------|-----------|
| **AR Web** | Git push → GitHub → Netlify webhook auto-deploys | Manual (git commit) | Git + Netlify (auto) + GitHub Releases |
| **GLB Models** | `python scripts/build_glb.py [render.png]` → save to `/assets` | Manual | R2 + GDrive + GitHub |
| Deploy to prod | Git merge to main → Netlify deploys automatically | Manual | Same as above |

---

## Phase 2 — Agent Learning System + Real Builds + Enhanced Monitoring

### Phase 2a: Agent Learning ✅ (COMPLETE — 2026-07-17)
- ✅ **Skillsets Infrastructure**: Created agent_skillsets table + 7 NacPac Dev skillsets
- ✅ **Skillset Seeding**: Script to populate and maintain skillsets
- ✅ **Skillset Injection**: Skillsets injected into agent decision-making prompts
- ✅ **Learning System**: 
  - learned_patterns table for tracking agent discoveries
  - learning_feedback table for human/system feedback
  - Memory layer methods: record, retrieve, update, insights
  - Full documentation in AGENT_LEARNING_SYSTEM.md

### Phase 2b: Remaining Actions (when ready)
1. ⚠️ **Enable real builds**: Change `BUILD_TEST_MODE=false` in DigitalOcean
2. **Test real build**: Send "Build NacPac APK" → verify actual EAS build
3. **Monitor costs**: Track Anthropic API usage in DigitalOcean logs
4. **Supabase integration** (optional): Enable persistent task history + cost tracking
5. **Add monitoring**: Dashboard to view task history, costs, build status
6. **MCPO agents** (Phase 3+): Add marketing, customer success, product, ops agents

### Phase 2 Progress
**Deployed:**
- ✅ Code: 18+ files, fully functional
- ✅ Orchestrator: Intent parsing with Haiku
- ✅ Dev agents: NacPac (APK/EXE) + Jico Life (AR app)
- ✅ Discord interface: Natural language + approval buttons
- ✅ Cost gating: $10/day, $50/month enforced
- ✅ Health monitoring: Probes responding
- ✅ Auto-deploy: GitHub → DigitalOcean pipeline working
- ✅ **Skillsets**: 7 core skillsets for NacPac Dev Agent
- ✅ **Learning**: Pattern tracking, feedback loop, insights system

---

## Remote Deployment Architecture

**System runs on:** Oracle Cloud VM (Ubuntu, IP: 68.233.110.235, user: ubuntu)  
**How:** systemd service (`jico-agentic.service`) runs Python agent system 24/7  
**Recovery:** Health check every 5 min; auto-restart if down; Discord alert if unhealthy > 15 min

### Failsafe Strategy
1. **Dead Letter Queue**: Failed tasks go to `failed_tasks` table in Supabase (not lost)
2. **Auto-retry**: Exponential backoff (2s, 4s, 8s, 16s) up to 3 attempts
3. **Health Monitor**: Ping Discord every 5 min; if no response → auto-restart service
4. **Rollback**: Every successful build saved; `!rollback nacpac-apk` restores last good version
5. **Alerts**: System status sent to Discord; critical errors @-mention you

### Multi-Platform Backup
- **R2 (Cloudflare)**: Fast access, build artifacts + metadata
- **Google Drive**: Accessible, human-readable, full backup of builds + logs
- **GitHub Releases**: Versioned, public-accessible, tagged releases for important builds

All three are populated automatically after every successful build.

---

## Token Optimization Strategy

**Model selection:**
- **Haiku** (cheap): Task screening, intent classification, memory reads, result formatting
- **Sonnet** (smart): Dev agent reasoning, complex code understanding, multi-step decisions

**Optimization tactics:**
1. Cache agent system prompts (reuse same prompt for multiple tasks)
2. Compress old task history before storing (summarize completed tasks)
3. Batch API calls (don't call model once per step; batch related steps)
4. Track every token in Supabase (`runs` table); alert if approaching cap
5. Use tool calling instead of generating text when possible (cheaper, more deterministic)

**Cost gates:**
- Daily cap: $10/day (hard stop; no more calls if exceeded)
- Monthly cap: $50/month (soft warning at 80%)
- Per-task budget: Tasks over $0.50 need explicit approval

---

## Session Protocol

### ⚠️ CRITICAL APPROVAL PROTOCOL
**Do NOT plan or act unless explicit approval is given.**
- Before proposing changes, designing systems, or executing work: wait for user's say-so
- When user says "do not plan or act unless you have my say so" — this applies to ALL subsequent work
- Wait for explicit approval on every major decision (design, implementation, deployment)
- Every time: ask if user wants to proceed, review architecture, change approach, etc.

### Standard Protocol
1. **Before each session**: Read this file top-to-bottom. Know the org structure, locked decisions, and next steps.
2. **After each session**: Update MEMORY.md + DECISIONS.md with new decisions + progress. Commit + push.
3. **Before proposing/planning**: Ask user for explicit approval before moving forward
4. **Before builds/deploys**: Ask user for explicit approval (via Discord buttons or direct confirmation).
5. **Use git branches**: All work on `claude/agentic-system-org-j9gvae`; commit frequently.
6. **Keep Supabase in sync**: Every task creation, run completion, or decision goes to Supabase. MEMORY.md mirrors for humans.
7. **Track tokens**: Every Anthropic API call logged to Supabase with model + token count + cost. Alert if approaching cap.

---

## Files in This System

| File | Purpose |
|------|---------|
| MEMORY.md | This file; current state (updated end of session) |
| DECISIONS.md | Append-only log of decisions + rationale |
| SESSION_PROTOCOL.md | Rules for how sessions operate |
| agentic/ | Main agent system (Python, Claude Agent SDK) |
| jico-system/ | Old system (reference only; kept for rollback) |

