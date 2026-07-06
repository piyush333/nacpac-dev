# Session Protocol — How We Work

Rules for every session building the Jico agentic system.

---

## Before Session Starts

1. **Read MEMORY.md** (top to bottom) — know org structure, current status, locked decisions
2. **Read last few DECISIONS.md entries** — context on what was decided and why
3. **Check current branch**: `git status` — must be on `claude/agentic-system-org-j9gvae`

---

## During Session

### Communication Style
- **Summarized**: One-liners for status, two sentences max for explanations
- **Ask before action**: "Ready to build the APK now?" rather than just doing it
- **One decision per question**: Don't batch multiple choices

### Git
- **Work on feature branch only**: `claude/agentic-system-org-j9gvae`
- **Commit frequently**: Each logical chunk (e.g., "Add MEMORY.md", "Create Supabase schema", "Build NacPac Dev Agent")
- **Push often**: Push after each commit; no rebasing on main until explicitly asked
- **Branch naming**: Session branches are already allocated; don't create new ones

### Approvals & Gates
- **Before building/deploying**: Always ask user ("Ready to build NacPac APK?")
- **Before accessing production**: Double-check the environment. Ask for confirmation.
- **Cost gates**: Check Supabase before any model call > $0.10. If approaching daily/monthly cap, escalate.

### Memory & Logging
- **Every task**: Create a task row in Supabase (`tasks` table)
- **Every agent run**: Log to Supabase (`runs` table) with model, tokens, cost
- **Every decision**: Log to DECISIONS.md (append-only)
- **End of session**: Update MEMORY.md with progress, commit + push

---

## After Session Ends

1. **Update MEMORY.md**: Current system status, what was built, blockers, next steps
2. **Update DECISIONS.md** (if any new decisions): Append with date, decision, rationale
3. **Commit**: `git commit -m "Phase 0: Create MEMORY/DECISIONS/SESSION_PROTOCOL"`
4. **Push**: `git push -u origin claude/agentic-system-org-j9gvae`
5. **Verify**: Check GitHub that commit landed on the branch

---

## Escalation Path

**If blockers arise:**
- 🟢 Small blocker (e.g., missing env var): Try reasonable default, document in DECISIONS.md
- 🟡 Medium blocker (e.g., unclear Jico Life repo location): Ask user for clarification via AskUserQuestion
- 🔴 Large blocker (e.g., Supabase project inaccessible): Stop, report the blocker, wait for user

---

## Safety Checks

- ❌ Never commit `.env` files (actual secrets)
- ❌ Never force-push or rebase (risk losing work)
- ❌ Never delete old files (archive to `legacy-docs/` if retired)
- ✅ Always use git branches, never work directly on main
- ✅ Ask before builds/deploys/cost-heavy operations

---

## Current Phase Status (as of 2026-07-06)

- ✅ **Phase 0 COMPLETE**: MEMORY.md, DECISIONS.md, SESSION_PROTOCOL.md created
- ✅ **Phase 1 COMPLETE**: Agentic system built, tested, deployed to DigitalOcean
- 🟡 **Phase 1.5**: Switch BUILD_TEST_MODE=false and test real builds (pending user approval)
- ⏳ **Phase 2+**: MCPO agents, enhanced monitoring, Supabase persistence (future)

## Files Modified Each Session

| File | Update Frequency | Why |
|------|-----------------|-----|
| MEMORY.md | End of session | Track progress, deployments, blockers |
| DECISIONS.md | When decisions made | Append-only log |
| agentic/ | Per-feature | Code changes, bug fixes, new agents |
| Dockerfile | When deps change | Cache-busting, health checks |
| requirements.txt | When adding packages | Keep runtime reproducible |

**Files to NEVER modify:**
- .env (secrets, keep local only)
- jico-system/ (legacy reference only)
- Previous DECISIONS.md entries (immutable)

