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

## Phase 0 Deliverables (This Session)

- [ ] MEMORY.md (this file) — current state
- [ ] DECISIONS.md — append-only decision log
- [ ] SESSION_PROTOCOL.md — session rules
- [ ] Supabase schema created + seeded (new project: jico-agentic)
- [ ] Commit + push to `claude/agentic-system-org-j9gvae`

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

## Next Phase (Phase 1) — Automation-First Build

**Goal:** Dev agents for NacPac & Jico Life, fully automated with manual gates only for production/cost/security.

**Automation Scope:**
- ✅ Auto-detect code changes
- ✅ Auto-build (APK/EXE/GLB)
- ✅ Auto-deploy to staging
- ✅ Auto-backup (R2 + GDrive + GitHub)
- ✅ Auto-retry on failures
- ✅ Auto-update memory + logs
- ✅ Auto-heal from crashes
- 🟡 Manual approval ONLY: production deploys, cost exceeds limit, security-sensitive changes

**Steps:**
1. Create `agentic/` package (config, memory client, auto-executing tools)
2. Build NacPac Dev Agent (git, auto-build APK/EXE, auto-deploy to staging, manual gate for prod)
3. Build Jico Life Dev Agent (git, auto-build GLB, auto-push to staging branch, manual gate for main)
4. Build Orchestrator (intent parsing, routing, auto-execution, memory management, token tracking)
5. Discord gateway (thin bot, slash commands, approval buttons for manual gates only)
6. Failsafe layer (auto dead letter queue, auto-retry with backoff, auto-health monitor, auto-alerts)
7. Backup automation (auto-upload to R2 + GDrive + GitHub on every successful build)
8. Systemd service (auto-start on boot, auto-restart on crash, auto-log rotation)
9. Test end-to-end: request → auto-build → auto-deploy-to-staging → manual-approve-for-prod → auto-deploy → auto-backup → auto-report

**Clarifications resolved:**
- ✅ Jico Life repo: same workspace (nacpac-workspace-main/)
- ✅ AR app build: Static site + Netlify deploy (no build step; git push triggers deploy)
- ✅ Approval flow: Discord buttons (Y/N)
- ✅ Model choice: Haiku for screening/routing, Sonnet for dev reasoning (smart default)

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

1. **Before each session**: Read this file top-to-bottom. Know the org structure, locked decisions, and next steps.
2. **After each session**: Update MEMORY.md + DECISIONS.md with new decisions + progress. Commit + push.
3. **Before builds/deploys**: Ask user for explicit approval (via Discord buttons).
4. **Use git branches**: All work on `claude/agentic-system-org-j9gvae`; commit frequently.
5. **Keep Supabase in sync**: Every task creation, run completion, or decision goes to Supabase. MEMORY.md mirrors for humans.
6. **Track tokens**: Every Anthropic API call logged to Supabase with model + token count + cost. Alert if approaching cap.

---

## Files in This System

| File | Purpose |
|------|---------|
| MEMORY.md | This file; current state (updated end of session) |
| DECISIONS.md | Append-only log of decisions + rationale |
| SESSION_PROTOCOL.md | Rules for how sessions operate |
| agentic/ | Main agent system (Python, Claude Agent SDK) |
| jico-system/ | Old system (reference only; kept for rollback) |

