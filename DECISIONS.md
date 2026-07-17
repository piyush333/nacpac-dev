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

### Decision 13: Maximum automation, minimal manual intervention
**Date:** 2026-07-02  
**Decision:** Agent system auto-executes as much as possible. Manual deployments/script uploads only if technically impossible. Approval gates only for: production deploys, cost overruns, security decisions.  
**Rationale:** User wants "set it and forget it". System should be intelligent enough to handle most tasks without escalation. Only interrupt for truly exceptional cases.  
**Owner:** Piyush

**Implementation:**
- Auto-deploy to staging ✅
- Auto-retry on transient failures ✅
- Auto-backup after every build ✅
- Auto-heal on crashes ✅
- Auto-update memory/logs ✅
- Manual approval ONLY for: production deploys, exceeding daily/monthly cap, security-sensitive changes
- Zero manual script uploads — everything runs in the agent

---

## Session 2 (2026-07-06) — Phase 1 Deployment

### Decision 14: DigitalOcean deployment (vs Oracle VM)
**Date:** 2026-07-06  
**Decision:** Deploy to DigitalOcean App Platform instead of Oracle VM. Auto-deploy from GitHub, managed infrastructure.  
**Rationale:** User said "why are we complicating this... we need code which is scalable and can be debugged at times when needed." DO provides simpler setup, auto-scaling, and built-in monitoring. Moved away from Oracle VM complexity.  
**Owner:** Piyush

### Decision 15: Health check server (aiohttp)
**Date:** 2026-07-06  
**Decision:** Add HTTP health server (aiohttp on port 8080) running in parallel with Discord bot.  
**Rationale:** DigitalOcean health probes expect HTTP responses. Discord bot is websocket-only. Needed aiohttp to respond to probes without changing bot architecture.  
**Owner:** Piyush

### Decision 16: Deferred imports for agent loading
**Date:** 2026-07-06  
**Decision:** Use lazy/deferred imports in discord_bot.py via _load_agents() function. No __init__.py magic imports.  
**Rationale:** Avoids circular imports and __init__.py complexity. Agents loaded on first use, preventing import-time failures.  
**Owner:** Piyush

### Decision 17: Docker caching strategy
**Date:** 2026-07-06  
**Decision:** Add cache-bust comments with timestamps in Dockerfile and requirements.txt to force fresh builds.  
**Rationale:** DigitalOcean caches Docker layers. Without cache-busting, old code is served even after push.  
**Owner:** Piyush

### Decision 18: Supabase as optional (graceful degradation)
**Date:** 2026-07-06  
**Decision:** Supabase is optional. System works without it. Memory layer degrades gracefully if SUPABASE_URL/KEY not set.  
**Rationale:** User may not need persistent DB initially. System should be deployable without Supabase setup. Can add later.  
**Owner:** Piyush

### Decision 19: BUILD_TEST_MODE for safe testing
**Date:** 2026-07-06  
**Decision:** Keep BUILD_TEST_MODE=true by default in DigitalOcean. Switch to false only after confirming workflow.  
**Rationale:** Real builds (EAS, npm) take time and cost money. Test mode simulates execution, allowing workflow validation without wasting resources. User can enable real builds after confirming intent parsing + approval flow works.  
**Owner:** Piyush

### Decision 20: Persistent memory backup to Google Drive
**Date:** 2026-07-06  
**Decision:** Create MEMORY.md, DECISIONS.md, SESSION_PROTOCOL.md files. Back up to Google Drive after each session.  
**Rationale:** Previous sessions have failed due to lost context. These files serve as human-readable recovery points. Google Drive ensures backup is accessible across sessions and machines.  
**Owner:** Piyush

---

## Session 3 (2026-07-17) — Phase 2a: Agent Learning System

### Decision 21: Skillsets as agent capability foundation
**Date:** 2026-07-17  
**Decision:** Build agent learning on top of skillsets infrastructure. Skillsets define WHAT agents know; learned_patterns track HOW they improve.  
**Rationale:** Skillsets provide the knowledge foundation; learning system tracks improvements based on that foundation. Decoupled: skillsets are curated knowledge, patterns are discovered knowledge.  
**Owner:** Claude Agent (autonomous Phase 2 work)

### Decision 22: Pattern confidence and success rate tracking
**Date:** 2026-07-17  
**Decision:** Confidence (0.0-1.0) initialized at 0.7, increased based on success_rate with formula: `new_confidence = min(0.99, success_rate * 1.2)`. Success rate updated via Bayesian averaging: `(old_rate * old_count + success) / new_count`.  
**Rationale:** Moderate initial confidence allows patterns to prove themselves. Never reaches 1.0 (always room to learn). Bayesian averaging converges on true rate as usage increases.  
**Owner:** Claude Agent

### Decision 23: Pattern types for different learning scenarios
**Date:** 2026-07-17  
**Decision:** Four pattern types: "success" (what works), "failure" (what doesn't), "optimization" (faster/cheaper), "best_practice" (recommended approach).  
**Rationale:** Different patterns serve different purposes. Agents prioritize success patterns early in execution, apply optimizations for efficiency, avoid failure patterns, follow best practices as guardrails.  
**Owner:** Claude Agent

### Decision 24: Learning feedback loop from agents and humans
**Date:** 2026-07-17  
**Decision:** learning_feedback table accepts feedback from agents (auto-generated) and humans (Discord commands). Tracks feedback_type, suggested improvements, and applied status.  
**Rationale:** Hybrid approach: agents learn from their own outcomes; humans provide additional guidance and validation. Creates feedback loop without manual intervention.  
**Owner:** Claude Agent

---

## Pending Clarifications (before Phase 2b start)

- **Real builds**: When to switch BUILD_TEST_MODE=false?
- **Supabase persistence**: Enable full task/cost history tracking?
- **Monitoring**: What alerts/dashboards needed?
- **MCPO agents**: Timeline for adding marketing/customer success/product/ops agents?
- **Learning integration**: When to integrate pattern recording into agent task execution?
- **Jico Life agent**: Add learning for AR/web deployment workflows?

---

## Notes

- Decisions are immutable once logged. If a decision needs revision, add a new entry with "Revises: [previous decision ID]".
- Every session should review locked decisions before continuing.
- Cost tracking ($50/mo, $10/day) is a standing constraint carried from previous work.

