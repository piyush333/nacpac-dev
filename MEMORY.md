# Jico Org Memory — System State & Decisions

**Last updated:** 2026-07-02  
**Status:** Phase 0 (Memory foundation) — In Progress

---

## Org Structure

| Brand | Purpose | Repo | Tech Stack | Current Status |
|-------|---------|------|-----------|-----------------|
| **NacPac** | Sticker printing & packaging (India) | `nacpac-workspace-main/` | Mobile: Expo/React Native, Desktop: Electron, Web: HTML/CSS/JS | ✅ APK + EXE in production |
| **Jico Life** | Acoustic felt decor | TBD (same workspace or separate?) | AR app (toolchain TBD) | ✅ AR app in production |

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

---

## Phase 0 Deliverables (This Session)

- [ ] MEMORY.md (this file) — current state
- [ ] DECISIONS.md — append-only decision log
- [ ] SESSION_PROTOCOL.md — session rules
- [ ] Supabase schema created + seeded (new project: jico-agentic)
- [ ] Commit + push to `claude/agentic-system-org-j9gvae`

---

## Next Phase (Phase 1)

**Goal:** Dev agents for NacPac & Jico Life, working end-to-end.

**Steps:**
1. Create `agentic/` package (config, memory client, tools)
2. Build NacPac Dev Agent (git, build APK/EXE, deploy)
3. Build Jico Life Dev Agent (git, build AR app, deploy)
4. Build Orchestrator (intent parsing, routing, memory management)
5. Discord gateway (thin bot, slash commands)
6. Test end-to-end: request → agent → build → deploy → report

**Clarifications needed before Phase 1:**
- Jico Life repo: same workspace or separate?
- AR app build toolchain: EAS? custom?
- Approval flow: Discord buttons or text confirmation?
- Model choice: Haiku (cheap) or Sonnet (smarter) for dev tasks?

---

## Session Protocol

1. **Before each session**: Read this file top-to-bottom. Know the org structure, locked decisions, and next steps.
2. **After each session**: Update MEMORY.md + DECISIONS.md with new decisions + progress. Commit + push.
3. **Before builds/deploys**: Ask user for explicit approval.
4. **Use git branches**: All work on `claude/agentic-system-org-j9gvae`; commit frequently.
5. **Keep Supabase in sync**: Every task creation, run completion, or decision goes to Supabase. MEMORY.md mirrors for humans.

---

## Files in This System

| File | Purpose |
|------|---------|
| MEMORY.md | This file; current state (updated end of session) |
| DECISIONS.md | Append-only log of decisions + rationale |
| SESSION_PROTOCOL.md | Rules for how sessions operate |
| agentic/ | Main agent system (Python, Claude Agent SDK) |
| jico-system/ | Old system (reference only; kept for rollback) |

