# Jico Org Memory — System State & Decisions

**Last updated:** 2026-07-02  
**Status:** Phase 0 (Memory foundation) — In Progress

---

## Org Structure

| Brand | Purpose | Repo | Tech Stack | Current Status |
|-------|---------|------|-----------|-----------------|
| **NacPac** | Sticker printing & packaging (India) | `nacpac-workspace-main/` | Mobile: Expo/React Native, Desktop: Electron, Web: HTML/CSS/JS | ✅ APK + EXE in production |
| **Jico Life** | Acoustic felt decor + AR try-on | `nacpac-workspace-main/` (same workspace) | AR: Static HTML + model-viewer (Google), hosted on Netlify, 3D models (GLB) from Google Drive renders | ✅ AR web app in production (Netlify) |

---

## System Status

### Current State
- **Old system** (`jico-system/`): Discord bot (partial) → keyword router → managers → CLI shelling
  - ✅ Working: discord_manager.py, compression_layer.py, task_router.py, nacpac_manager.py (for APK/EXE)
  - ❌ Not wired: git_sync.py, health_monitor.py, circuit_breaker.py (code exists, never imported)
  - ❌ Stubs: jico_manager.py (all workers), nacpac_manager seo/ads tasks
  - ❌ In-memory only: task queue, cost tracker, scheduler (lost on restart)
  - ❌ Latent bugs: scheduler stores "tomorrow" strings instead of ISO timestamps

### New System (This Session)
- Creating: `agentic/` directory (Claude Agent SDK–based)
- Memory: Supabase (machine truth) + MEMORY.md / DECISIONS.md (human readable)
- Runtime: Orchestrator agent + subagents (NacPac Dev, Jico Life Dev) + Discord gateway
- Status: Phase 0 (memory files + Supabase schema)

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

## Next Phase (Phase 2) — Supabase Setup + Oracle Deployment

**Goal:** Set up persistent memory layer + deploy system to Oracle VM as 24/7 service.

**Phase 2 Steps:**
1. Create Supabase project (`jico-agentic`) — OR use existing if available
2. Create schema + tables (brands, tasks, runs, brand_state, builds, deployments, decisions, costs)
3. Seed initial data (NacPac, Jico Life brands)
4. Test memory client (insert/read operations)
5. Copy `.env.template` → `.env`, fill in all credentials
6. Deploy to Oracle VM:
   - Install Python 3.11+ + systemd
   - Clone repo to `/home/ubuntu/nacpac-dev/`
   - Install pip dependencies
   - Copy `.env` to `/home/ubuntu/nacpac-dev/agentic/.env`
   - Copy systemd service: `sudo cp systemd/jico-agentic.service /etc/systemd/system/`
   - Enable + start service: `sudo systemctl enable jico-agentic && sudo systemctl start jico-agentic`
7. Verify deployment:
   - Check logs: `journalctl -u jico-agentic -f`
   - Test Discord command: `/task brand:nacpac request:Show status`
8. Set up monitoring + alerts

**What's ready:**
- ✅ Code complete (18 files, fully documented)
- ✅ Orchestrator with intent parsing
- ✅ Dev agents for both brands (auto-build + auto-deploy + auto-backup)
- ✅ Discord bot with approval buttons
- ✅ Cost tracking + gates
- ✅ Failsafe mechanisms (auto-retry, dead letter queue, health monitor)
- ✅ Systemd service file

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

