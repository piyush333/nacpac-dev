# Jico Org — Decision Log

Append-only log of decisions made during agentic system build.

---

## Session 1 (2026-07-02)

### Decision 1: Build fresh vs patch
**Date:** 2026-07-02  
**Decision:** Build fresh `agentic/` directory; keep `jico-system/` as read-only reference  
**Rationale:** jico-system has untested fail-safe modules (git_sync, health_monitor, circuit_breaker) that are never imported. Cleaner to start fresh with proven architecture (Claude Agent SDK).  
**Owner:** Piyush

### Decision 2: Phase 1 scope
**Date:** 2026-07-02  
**Decision:** Phase 1 focus: Dev agents (NacPac, Jico Life) + Orchestrator only. MCPO agents (marketing, customer success, product, operations) deferred to Phase 2.  
**Rationale:** Dev agents unblock code features and deployments immediately. MCPO agents (ads, campaigns) can follow once foundation is stable.  
**Owner:** Piyush

### Decision 3: Memory system (hybrid)
**Date:** 2026-07-02  
**Decision:** Supabase for machine-readable state (source of truth) + git markdown mirror (MEMORY.md, DECISIONS.md) for human readability  
**Rationale:** Supabase provides durable, queryable state + cost tracking; markdown files serve as session recovery + readable audit trail. Avoid single point of failure.  
**Owner:** Piyush

### Decision 4: Runtime (Claude Agent SDK)
**Date:** 2026-07-02  
**Decision:** Use Claude Agent SDK (Python) for orchestrator + subagents. Not discord.py-only, not CLI-shelling as core pattern.  
**Rationale:** Agent SDK gives us orchestration, subagents, tool calling, memory management, and cost tracking out-of-the-box. Better than hand-coding with anthropic SDK.  
**Owner:** Piyush

### Decision 5: Interface (Discord)
**Date:** 2026-07-02  
**Decision:** Discord bot for user interaction (slash commands, approval buttons, result posting)  
**Rationale:** User is familiar with Discord bot flow; existing jico-system has proven button-based UX; async communication suits agent execution.  
**Owner:** Piyush

### Decision 6: Deployment (Remote, always-on)
**Date:** 2026-07-02  
**Decision:** Agentic system runs on Oracle Cloud VM (systemd service), not on dev machine. Always-on, independent.  
**Rationale:** Agents can work while user is offline. No single machine dependency. Failsafe recovery built-in.  
**Owner:** Piyush

### Decision 7: Approval gates (Discord buttons)
**Date:** 2026-07-02  
**Decision:** Before any build/deploy, agent shows Discord approval buttons (Y/N). No auto-execution.  
**Rationale:** Safety gate. Audit trail. Prevents accidental builds. Clear UX.  
**Owner:** Piyush

### Decision 8: Failsafe mechanisms
**Date:** 2026-07-02  
**Decision:** Dead letter queue (failed tasks saved) + auto-retry (exponential backoff) + health monitor (5-min checks, auto-restart) + Discord alerts.  
**Rationale:** System resilient to crashes. No task loss. Auto-recovery. User stays informed.  
**Owner:** Piyush

### Decision 9: Multi-platform backup (3 targets)
**Date:** 2026-07-02  
**Decision:** Every build artifact backed up to R2 + Google Drive + GitHub Releases.  
**Rationale:** No single point of failure. Each platform accessible from different contexts (R2 = fast, GDrive = familiar, GitHub = versioned).  
**Owner:** Piyush

### Decision 10: Token optimization
**Date:** 2026-07-02  
**Decision:** Haiku for cheap ops (screening, formatting), Sonnet for reasoning (dev agent). Track every token. Enforce $10/day + $50/month caps.  
**Rationale:** Cost control. Use smarter model only when needed. Stay within budget.  
**Owner:** Piyush

### Decision 11: Brand repos (same workspace)
**Date:** 2026-07-02  
**Decision:** Both NacPac and Jico Life code in `nacpac-workspace-main/` (same git repo).  
**Rationale:** Simplified tooling. Shared utils/config. Easier monorepo management.  
**Owner:** Piyush

### Decision 12: Jico Life AR build
**Date:** 2026-07-02  
**Decision:** Jico Life AR is a static site hosted on Netlify. No build step. Deploy via git push → GitHub webhook → Netlify auto-deploys.  
**Rationale:** Simpler than EAS. Faster deploys. Netlify handles infrastructure.  
**Owner:** Piyush

---

## Pending Clarifications (before Phase 1 start)

Before Phase 1 starts, confirm with user:
- **Jico Life repo location**: Same workspace (nacpac-workspace-main/) or separate repo?
- **AR app build toolchain**: What tool/command builds the AR app?
- **Approval flow preference**: Discord buttons (Y/N) or text confirmation?
- **Model choice**: Haiku (fast, cheap, ~$0.80/M tokens) vs Sonnet (smarter, ~$3/M tokens) for dev agent reasoning?

---

## Notes

- Decisions are immutable once logged. If a decision needs revision, add a new entry with "Revises: [previous decision ID]".
- Every session should review locked decisions before continuing.
- Cost tracking ($50/mo, $10/day) is a standing constraint carried from previous work.

