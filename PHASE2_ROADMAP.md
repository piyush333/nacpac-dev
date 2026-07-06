# Phase 2: Feature Implementation Roadmap

**Status**: In Progress (Option A - Active)

---

## Current Phase: Option A ✅ (ACTIVE NOW)

**Goal**: Wire Discord proposal UI for code change approval

**What's Done:**
- ✅ Feature Agent created (`agentic/agents/feature_agent.py`)
- ✅ Codebase analysis working
- ✅ Claude proposes code changes
- ✅ Test command responds positively

**What's Needed:**
- ⏳ Discord ProposalView (show proposed changes)
- ⏳ Approval/Rejection buttons
- ⏳ Apply execution flow
- ⏳ End-to-end testing

**Workflow (Option A Complete):**
```
User: "Add OAuth to mobile"
  ↓
Manager: "I understand: Add OAuth..."
User: ✅ Approve
  ↓
Feature Agent Proposes:
  "I propose these changes:
   ✨ Create: src/context/AuthContext.tsx
   ✏️  Modify: App.tsx (lines 10-25)
   ✏️  Update: package.json (dependencies)
   
   Review & Apply? [✅ Apply | ❌ Cancel]"
User: ✅ Apply
  ↓
Agent applies → builds → returns R2 links
```

---

## Next Phase: Option B (DO NOT START YET)

**Goal**: Enable real EAS/npm builds

**Tasks:**
- Set BUILD_TEST_MODE=false in DigitalOcean
- Test real APK build via EAS
- Test real EXE build via npm
- Verify artifacts upload to R2

**Why later**: Want proposal approval working first for safety

---

## Final Phase: Option C (DO NOT START YET)

**Goal**: Firebase state tracking

**Tasks:**
- Track deployed features by branch
- Version management
- Feature rollback capability
- State sync between mobile/desktop

---

## Remember

When Phase 2-A is complete:
1. Run full end-to-end test in Discord
2. Then move to Option B (real builds)
3. Then move to Option C (Firebase)

Do NOT skip ahead!

---

**Last Updated**: 2026-07-06
**Current Owner**: You (piyush)
**Current Task**: Wire Discord ProposalView for Option A
