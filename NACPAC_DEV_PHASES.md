# NacPac Dev Agent — Phases 1-8 Detailed Roadmap

**Status**: Phase 1 complete ✅ | Phase 2 in progress ⏳

---

## **Phase 1: Skillsets** ✅ COMPLETE

**Goal**: Agent possesses technical knowledge of its domain

**Deliverables:**
- ✅ Defined 7 core skillsets (nacpac_codebase, python, nodejs, react, expo_dev, npm, exe_windows)
- ✅ Created SKILLSETS.md with full documentation per skillset
- ✅ Seeded all 7 skillsets to `agent_skillsets` table in Supabase
- ✅ Implemented `_load_skillsets()` in NacPacDevAgent
- ✅ Implemented `get_skillsets_context()` for Claude injection
- ✅ Implemented `get_system_prompt_with_skillsets()` that pre-feeds skillsets
- ✅ Created test_skillsets.py to verify all 7 load correctly
- ✅ Verified skillsets are injected into `build_apk()`, `build_exe()`, `deploy_to_staging()`

**Outcome**: When agent executes tasks, it knows React Native, Express.js, Expo, npm, Windows packaging, etc.

**Commits**: 9b9734a, a3e321d, 4e548bb

---

## **Phase 2: Learning** ⏳ IN PROGRESS (nacpac agent session)

**Goal**: Agent learns from task outcomes and improves over time

⚠️ **CRITICAL BEFORE STARTING: Read SUPABASE_SCHEMA.md**
- Confirm table name: `nacpac_learned_patterns` (NOT `learned_patterns`)
- Confirm agent_id column uses: `nacpac_dev`
- This ensures data doesn't get polluted with wrong naming

**Deliverables:**
1. [ ] Create `nacpac_learned_patterns` table in Supabase (named correctly per SUPABASE_SCHEMA.md)
   - Columns: id, agent_id, pattern_type, pattern_description, successful_examples[], failure_cases[], success_rate, last_used, created_at

2. [ ] Implement feedback loop in agent
   - After each task completion: capture what worked (pattern)
   - After each task failure: capture what failed (anti-pattern)
   - Store in `learned_patterns` table

3. [ ] Implement pattern injection before task execution
   - Query `learned_patterns` for similar past tasks
   - Pre-populate agent context with "Here are 3 similar tasks that succeeded..."
   - Agent uses learned patterns to avoid mistakes

4. [ ] Create `agentic/learn_from_task.py`
   - Function: `capture_pattern(task_id, outcome, pattern_description)`
   - Updates `learned_patterns` table after task completes

5. [ ] Update `agentic/agents/nacpac_dev.py`
   - Add method: `get_learned_patterns_for_task(task_description) -> list`
   - Inject learned patterns into system prompt before decision-making

6. [ ] Test pattern learning
   - Run 5 sample tasks (build APK, build EXE, feature, deploy, etc.)
   - Verify patterns captured in Supabase
   - Verify next similar task uses learned patterns

**Example Pattern (after Phase 2):**
```
Pattern: "APK Build Requires SDK Setup"
Type: pre-build-check
Triggered by: Task mentions "build APK" or "EAS build"
Success rate: 85%
Example: "Before running EAS, verify Android SDK is installed"
```

**Outcome**: Agent remembers common pitfalls and reuses proven approaches

**Files to create/modify:**
- `migrations/002_create_learned_patterns.sql` (new)
- `agentic/learn_from_task.py` (new)
- `agentic/agents/nacpac_dev.py` (modify: add pattern querying)
- `agentic/test_learning.py` (new: verify learning works)

---

## **Phase 3: Memory** ⏳ PENDING Phase 2

**Goal**: Persistent task history and artifact tracking

**Deliverables:**
1. [ ] Implement task logging in memory layer
   - Log every task: input, status, result, cost, duration
   - Use existing `tasks` table (already exists)

2. [ ] Implement build logging
   - Log every build attempt: type (APK/EXE), commit, output_path, status, error (if failed)
   - Use existing `builds` table

3. [ ] Implement deployment logging
   - Log every deployment: environment, commit, timestamp, status
   - Use existing `deployments` table

4. [ ] Create task summary function
   - After task completes: generate summary (what was done, cost, result)
   - Store in `tasks` table under `result_summary`

5. [ ] Update agent to log decisions
   - Log why agent chose certain actions (skillset used, pattern matched, etc.)
   - Track in `runs` table

6. [ ] Test memory persistence
   - Run task, verify logged in `tasks` table
   - Query history, verify data structure

**Outcome**: Agent has complete history of what it has done. Central session can audit/review.

**Files to modify:**
- `agentic/memory.py` (already has methods, may add task_summary())
- `agentic/agents/nacpac_dev.py` (add logging at key decision points)

---

## **Phase 4: Feature Generation** ⏳ PENDING Phase 3

**Goal**: Agent can propose and apply code changes

**Deliverables:**
1. [ ] Wire feature_agent to nacpac_dev context
   - feature_agent queries nacpac_dev skillsets
   - feature_agent understands NacPac codebase architecture
   - feature_agent uses learned patterns from Phase 2

2. [ ] Implement proposal workflow
   - Task: "add checkout feature"
   - Agent analyzes codebase → proposes changes
   - Returns JSON: {files_to_modify[], diffs, risks, testing_notes}

3. [ ] Implement Discord approval flow
   - Post proposal in Discord with diffs
   - User clicks "Approve" or "Reject"
   - If approved: agent applies changes, creates commit

4. [ ] Implement git integration
   - Create feature branch: `feature/{task-slug}`
   - Commit changes with description
   - Push to remote
   - Return branch URL to Discord

5. [ ] Test end-to-end
   - Submit feature request via Discord
   - Verify proposal shows in Discord
   - Approve proposal
   - Verify branch created + changes committed

**Outcome**: Agent can generate and apply code changes autonomously (with human approval)

**Files to modify/create:**
- `agentic/agents/feature_agent.py` (already exists, integrate with nacpac_dev)
- `agentic/agents/nacpac_dev.py` (add method: propose_feature_changes())
- Discord bot integration (already exists, enhance with proposal UI)

---

## **Phase 5: Build Pipeline** ⏳ PENDING Phase 4

**Goal**: Agent can trigger and track production builds

**Deliverables:**
1. [ ] Implement APK build workflow
   - Trigger: task says "build APK" or feature approved
   - Agent runs EAS build with correct profile
   - Poll for completion (10-20 min typical)
   - Download artifact from EAS
   - Upload to R2 + Google Drive
   - Return download links

2. [ ] Implement EXE build workflow
   - Trigger: task says "build EXE" or "desktop"
   - Agent runs npm build script
   - Generate Windows installer
   - Upload to R2 + Google Drive
   - Return download links

3. [ ] Implement build failure recovery
   - If build fails: capture error message
   - Log in learned_patterns as anti-pattern
   - Suggest fixes to user
   - Optionally retry after fixes

4. [ ] Implement build progress tracking
   - Log build start/end times
   - Track cost per build (EAS credits)
   - Display progress in Discord (updates every 5 min)

5. [ ] Test builds
   - Trigger APK build → verify artifact in R2
   - Trigger EXE build → verify artifact in R2
   - Test failure case → verify error logged

**Outcome**: Agent can autonomously build production-ready APK/EXE from code

**Files to modify:**
- `agentic/agents/nacpac_dev.py` (already has build_apk/build_exe, enhance with full workflow)
- `agentic/tools/build_tools.py` (verify handles test vs real mode)
- `agentic/tools/backup_tools.py` (verify R2 upload works)

---

## **Phase 6: Dashboard UI** ⏳ PENDING Phase 5

**Goal**: Real-time monitoring of agent status and tasks

**Deliverables:**
1. [ ] Build real-time dashboard (Next.js)
   - Agent status card (current task, skillsets loaded, last action)
   - Pending proposals queue (code changes waiting for approval)
   - Build progress (current APK/EXE build status, ETA)
   - Task history (last 10 tasks with results)
   - Cost monitoring (daily/monthly spend, budget remaining)

2. [ ] Implement live updates via Supabase Realtime
   - Dashboard subscribes to `tasks`, `runs`, `builds` tables
   - Auto-refreshes when agent updates data
   - No manual refresh needed

3. [ ] Add interactive controls
   - Approve/Reject buttons for proposals
   - "View Diff" modal for code changes
   - Manual task submission form
   - Cancel build button

4. [ ] Integrate with Discord
   - Dashboard link in Discord messages
   - Show live build progress in Discord
   - Option to approve proposals from Discord OR dashboard

5. [ ] Test dashboard
   - Submit task, watch progress on dashboard
   - Verify real-time updates work
   - Test approval flow from dashboard

**Outcome**: Users have visibility into agent activity. Can monitor builds, approve proposals, check costs.

**Files to create:**
- `dashboard/` (new Next.js app)
- `dashboard/components/AgentStatus.tsx`
- `dashboard/components/ProposalQueue.tsx`
- `dashboard/components/BuildProgress.tsx`
- `dashboard/components/CostMonitor.tsx`

---

## **Phase 7: Testing** ⏳ PENDING Phase 6

**Goal**: Verify agent works end-to-end before production

**Deliverables:**
1. [ ] Smoke tests
   - Agent initializes without errors
   - All 7 skillsets load
   - Connection to Supabase works
   - Discord bot responds to `/task` command

2. [ ] End-to-end tests (5 sample tasks)
   - Task 1: Feature request → proposal → approve → build APK → R2
   - Task 2: Build EXE without code changes
   - Task 3: Feature with code changes → build → deploy
   - Task 4: Build failure → capture error → retry
   - Task 5: Query learned patterns → verify pattern reused

3. [ ] Error handling tests
   - EAS build timeout → graceful failure + logging
   - Git push conflict → error message to user
   - Supabase unavailable → fallback to in-memory
   - Discord command malformed → helpful error

4. [ ] Load tests
   - 3 concurrent tasks → verify no conflicts
   - Cost tracking accuracy → verify per-task costs

5. [ ] Documentation
   - Create TESTING.md with test cases
   - Runbook for troubleshooting common errors

**Outcome**: Agent is validated, tested, ready for production

**Files to create:**
- `agentic/test_e2e.py` (end-to-end tests)
- `TESTING.md` (test documentation)

---

## **Phase 8: Go Live** ⏳ PENDING Phase 7

**Goal**: Deploy to production and monitor first real tasks

**Deliverables:**
1. [ ] Production deployment checklist
   - [ ] All Phases 1-7 complete and tested
   - [ ] BUILD_TEST_MODE=false (real builds, not pre-builts)
   - [ ] Supabase production credentials configured
   - [ ] Discord bot token configured
   - [ ] Cost tracking enabled
   - [ ] Monitoring + alerts set up

2. [ ] Deploy Discord bot to production
   - Bot runs 24/7 on VPS (Linode/Vultr)
   - Listens to #general channel
   - Responds to `/task` commands

3. [ ] Monitor first 5 real tasks
   - Watch logs for errors
   - Verify builds succeed
   - Check cost tracking accurate
   - Validate Discord reports correct

4. [ ] Create runbook
   - How to restart agent if it crashes
   - How to check logs
   - How to pause agent (stop accepting tasks)
   - Escalation procedure for errors

5. [ ] Document success metrics
   - X% of tasks succeed
   - Average time per task
   - Average cost per task
   - Error types + frequency

**Outcome**: Agent is live, handling real tasks from users

**Files to create:**
- `PRODUCTION_RUNBOOK.md`
- `DEPLOYMENT_CHECKLIST.md`

---

## **Current Status Summary**

| Phase | Status | Deliverables | Next Action |
|-------|--------|--------------|------------|
| 1 | ✅ DONE | Skillsets loaded, injected, tested | - |
| 2 | ⏳ IN PROGRESS | Phase 2 in nacpac agent session | Wait for completion |
| 3 | ⏳ PENDING | Memory + logging | Start after Phase 2 |
| 4 | ⏳ PENDING | Feature generation + proposals | Start after Phase 3 |
| 5 | ⏳ PENDING | Build pipeline (APK/EXE) | Start after Phase 4 |
| 6 | ⏳ PENDING | Real-time dashboard | Start after Phase 5 |
| 7 | ⏳ PENDING | Testing + validation | Start after Phase 6 |
| 8 | ⏳ PENDING | Production deployment | Start after Phase 7 |

---

## **What You Should Work On Next (Phase 3)**

Once nacpac agent completes Phase 2 (Learning), they should immediately start **Phase 3: Memory**.

**Phase 3 task list for nacpac agent:**
1. Verify existing `tasks`, `builds`, `deployments` tables in Supabase
2. Add task logging to agent (log every task to `tasks` table)
3. Add build logging (log every APK/EXE build to `builds` table)
4. Add deployment logging (log every deploy to `deployments` table)
5. Create task_summary function (after task completes, summarize result)
6. Update agent to log key decisions
7. Test: run sample task, verify logged in Supabase
8. Commit and report completion

**Estimated time**: 2-3 days for nacpac agent session

---

## **After All 8 Phases Complete**

NacPac Dev Agent will be **LIVE** and able to:
- ✅ Load technical skillsets
- ✅ Learn from task patterns
- ✅ Track all task history
- ✅ Generate code proposals
- ✅ Build APK/EXE automatically
- ✅ Deploy to staging/production
- ✅ Report status via Dashboard + Discord
- ✅ Improve continuously from experience

Then we add **Jico Life Dev Agent** using the same 8-phase template.

---

**Keep nacpac_dev focused. Stay on Phases 1-8. No Jico, no distractions.**
