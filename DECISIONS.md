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

---

## Pending Clarifications (Phase 1)

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

