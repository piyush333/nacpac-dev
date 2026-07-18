# Phase 9: Jico Life Dev Agent Onboarding

**Status**: 🟡 PENDING (auto-assigned after Phase 8 production monitoring)  
**Target Start**: 2026-07-25 (after 1 week of Phase 8 stability)  
**Target Completion**: 2026-08-01  
**Owner**: Central Session  

---

## Overview

Phase 9 mirrors Phase 1-8 but for **Jico Life** (the acoustic felt decor brand). The goal is to bring Jico Life's development under the same orchestrator system used for NacPac.

**Success Criteria**: Jico Life Dev Agent can build, test, and deploy AR app features autonomously, just like NacPac.

---

## Prerequisites for Phase 9 Start

✅ **Phase 8 must be stable:**
- [ ] Production monitoring complete (1 week)
- [ ] 99%+ uptime confirmed
- [ ] At least 3 successful test tasks run (build APK, EXE, deploy)
- [ ] Cost tracking verified within 5% accuracy
- [ ] Zero security incidents
- [ ] Artifacts properly backed up to R2 + Google Drive

**Check status:**
```bash
python agentic/check_phase_assignment.py central
```

Should show: `✅ Agent central should start Phase 9`

---

## Phase 9 Scope

### What's in Phase 9

1. **Jico Life Repo Integration**
   - Clone Jico Life repo (if separate) or integrate into workspace
   - Confirm AR app tech stack (current: React Native + Expo AR)
   - Set up Jico Life build tools (EAS, npm, AR SDK)

2. **Supabase Tables for Jico Life**
   - Create `jico_life_tasks` table (parallel to `nacpac_tasks`)
   - Create `jico_life_runs` table
   - Create `jico_life_builds` table (for AR app builds)
   - Create `jico_life_learned_patterns` table (Phase 2+ learning)
   - Ensure schema matches NacPac but with jico_ prefix

3. **Jico Life Dev Agent Setup**
   - Create `agentic/agents/jico_life_dev.py`
   - Mirror NacPacDevAgent structure
   - Implement build methods:
     * `build_ar_app()` — compile AR app for iOS/Android
     * `build_web_app()` — build web preview
   - Implement deploy methods:
     * `deploy_to_staging()` — staging environment
     * `deploy_to_production()` — App Store/Play Store

4. **Orchestrator Updates**
   - Update `orchestrator.py` to route Jico Life tasks to Jico Life agent
   - Intent parsing: detect "jico_life" brand from user input
   - Add Jico Life channels to Discord (if not already)

5. **Jico Life Skillsets** (Phase 1 equiv for Jico)
   - Create `JICO_LIFE_SKILLSETS.md`
   - Define 6-8 core skillsets:
     * jico_codebase
     * ar_development (React Native AR, Expo AR)
     * react_native
     * expo_development
     * npm_tooling
     * ios_android_deployment
     * ar_testing

6. **Testing & Verification**
   - Test: `send_task("jico_life", "Build AR app for staging")`
   - Confirm task routes to Jico Life agent
   - Verify artifact builds and uploads to R2
   - Verify cost tracked in Supabase `costs` table

7. **Documentation**
   - `JICO_LIFE_PHASES.md` — Phase 1-8 roadmap for Jico agent
   - `JICO_LIFE_DEPLOYMENT.md` — Build/deploy procedures
   - Update `GOVERNANCE.md` with Jico assignment

### What's NOT in Phase 9

❌ **No new infrastructure**:
- Discord bot already running
- DigitalOcean already deployed
- Supabase already configured
- R2 + backup already working

❌ **No new CI/CD**:
- Use existing GitHub Actions workflows
- Just add Jico Life repo as source

❌ **No Phase 2+ work yet**:
- Phase 9 is just skillsets + basic build/deploy
- Learning system (Phase 2) starts in Phase 9's nacpac session equivalent

---

## Step-by-Step Plan

### Step 1: Verify Phase 8 Production Stability (5 days)

**Timeline**: 2026-07-18 to 2026-07-22

Daily checks:
```bash
# Check uptime
curl https://jico-oh6t5.ondigitalocean.app/health

# Check logs
# DigitalOcean: Apps → jico → Logs tab

# Check costs
# Supabase: SELECT * FROM costs WHERE DATE(created_at) = CURRENT_DATE;

# Check task history
# Supabase: SELECT * FROM nacpac_tasks ORDER BY created_at DESC LIMIT 5;
```

**Approval gates**:
- [ ] 5 days have passed (2026-07-22)
- [ ] Uptime >= 99%
- [ ] Costs <= $10/day average
- [ ] No error spikes in logs
- [ ] At least 5 successful tasks logged

Once approved, proceed to Step 2.

---

### Step 2: Prepare Jico Life Repository (1 day)

**Timeline**: 2026-07-23

**Actions**:
1. Determine Jico Life repo location:
   - Is it a separate repo? (jico/jico-life)
   - Or part of nacpac-workspace-main?
   - **Decision needed from user**

2. Clone/integrate repo:
   ```bash
   # If separate repo:
   git clone https://github.com/jico/jico-life.git
   cd jico-life && git checkout production  # or main branch
   
   # If part of workspace:
   cd nacpac-workspace-main && git checkout jico-life-branch
   ```

3. Confirm tech stack:
   - React Native version
   - Expo version (AR plugin)
   - Build tools (EAS, npm)
   - Current app version (e.g., 1.0.0)

4. Test local build:
   ```bash
   npm install
   npm run build:ar  # or equivalent
   ```

5. Verify EAS access for Jico app:
   - Confirm EAS_TOKEN has access to Jico app
   - Test: `eas build --status`

**Deliverable**: Jico Life repo ready, local build verified.

---

### Step 3: Set Up Jico Life Supabase Schema (1 day)

**Timeline**: 2026-07-24

**Actions**:
1. Create Jico Life tables in Supabase:
   ```sql
   -- Tasks (parallel to nacpac_tasks)
   CREATE TABLE jico_life_tasks (
     id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
     created_by TEXT,
     input_text TEXT,
     status TEXT,
     result_summary TEXT,
     created_at TIMESTAMP DEFAULT now(),
     completed_at TIMESTAMP
   );
   
   -- Runs (execution logs)
   CREATE TABLE jico_life_runs (
     id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
     task_id UUID REFERENCES jico_life_tasks(id),
     agent TEXT,
     model TEXT,
     tokens_in INT,
     tokens_out INT,
     cost_usd FLOAT,
     started_at TIMESTAMP,
     finished_at TIMESTAMP,
     status TEXT
   );
   
   -- Builds (AR app builds)
   CREATE TABLE jico_life_builds (
     id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
     type TEXT,
     commit TEXT,
     platform TEXT,  -- ios, android, web
     output_path TEXT,
     created_at TIMESTAMP DEFAULT now(),
     status TEXT
   );
   
   -- Learned patterns (Phase 2+)
   CREATE TABLE jico_life_learned_patterns (
     id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
     agent_id TEXT,
     pattern_type TEXT,
     pattern_description TEXT,
     successful_examples JSONB,
     failure_cases JSONB,
     success_rate FLOAT,
     last_used TIMESTAMP,
     created_at TIMESTAMP DEFAULT now()
   );
   ```

2. Seed initial data:
   ```sql
   INSERT INTO secrets (key, value) VALUES
     ('JICO_LIFE_BUILD_TEST_MODE', 'false'),
     ('JICO_LIFE_APP_ID', 'com.jico.life.ar');
   ```

3. Grant permissions to Jico app:
   - Ensure `SUPABASE_KEY` (anon) can read/write these tables

**Deliverable**: Jico Life tables created + seeded.

---

### Step 4: Create Jico Life Dev Agent (2 days)

**Timeline**: 2026-07-24 to 2026-07-25

**File**: `agentic/agents/jico_life_dev.py`

**Template** (based on `nacpac_dev.py`):
```python
"""Jico Life Dev Agent — builds and deploys AR app."""

from agentic.base_agent import BaseAgent
from agentic.tools import git, build_tools, deploy_tools
from agentic.memory import log_task

class JicoLifeDevAgent(BaseAgent):
    """Jico Life development automation."""
    
    def __init__(self):
        super().__init__(agent_id="jico_life_dev", brand="jico_life")
        self.repo_path = "/home/jico-life"  # or workspace path
        self.app_id = "com.jico.life.ar"
    
    def build_ar_app(self, target="both"):
        """Build AR app for iOS, Android, or both."""
        # Implementation: EAS build + push to R2
        pass
    
    def build_web_app(self):
        """Build web preview of AR app."""
        # Implementation: npm build for web
        pass
    
    def deploy_to_staging(self):
        """Deploy to staging environment."""
        pass
    
    def deploy_to_production(self):
        """Deploy to App Store/Play Store."""
        pass
```

**Actions**:
1. Create `agentic/agents/jico_life_dev.py` (mirror NacPac structure)
2. Implement core build/deploy methods
3. Wire up to Supabase tables (`jico_life_tasks`, etc.)
4. Test: `python -c "from agentic.agents.jico_life_dev import JicoLifeDevAgent; agent = JicoLifeDevAgent(); print('OK')"`

**Deliverable**: Jico Life agent created and importable.

---

### Step 5: Update Orchestrator for Jico Life (1 day)

**Timeline**: 2026-07-25

**File**: `agentic/agents/orchestrator.py`

**Changes**:
```python
# Add to imports
from agentic.agents.jico_life_dev import JicoLifeDevAgent

# Add to agent registry
AGENTS = {
    "nacpac_dev": NacPacDevAgent(),
    "jico_life_dev": JicoLifeDevAgent(),  # NEW
}

# Update intent parser
def parse_intent(user_input):
    # Check if input mentions "jico" or "jico life"
    if "jico" in user_input.lower():
        return {"brand": "jico_life", "agent": "jico_life_dev", ...}
    # ... rest of parsing
```

**Discord Setup**:
1. Create `#jico-dev` channel (if not existing)
2. Update bot permissions to read/write in Jico channels
3. Test: Send message to `#jico-dev`: `"Build AR app for staging"`

**Deliverable**: Orchestrator routes Jico Life tasks correctly.

---

### Step 6: Create Jico Life Skillsets (1 day)

**Timeline**: 2026-07-25 to 2026-07-26

**File**: `JICO_LIFE_SKILLSETS.md`

**Content** (template):
```markdown
# Jico Life Dev Agent — Core Skillsets

## 1. Jico Codebase
- Repo structure
- Build configuration
- AR setup

## 2. AR Development
- React Native AR
- Expo AR plugin
- iOS/Android AR APIs

## 3. React Native
- Component structure
- Navigation
- State management

## 4. Expo Development
- EAS build system
- Preview builds
- OTA updates

## 5. iOS/Android Deployment
- App Store submission
- Play Store submission
- Certificate management

## 6. AR Testing
- Device testing
- AR debugging
- Performance profiling
```

**Actions**:
1. Create `JICO_LIFE_SKILLSETS.md`
2. Insert into Supabase `agent_skillsets` table (agent_id: "jico_life_dev")
3. Update `orchestrator.py` to load Jico skillsets

**Deliverable**: Jico skillsets defined + seeded to Supabase.

---

### Step 7: Test End-to-End (1 day)

**Timeline**: 2026-07-26

**Test Script**:
```bash
# 1. Send task via Discord
# Go to #general: "Build Jico Life AR app for staging"

# 2. Verify task created
psql $SUPABASE_URL -c "SELECT * FROM jico_life_tasks ORDER BY created_at DESC LIMIT 1;"

# 3. Verify build executed
psql $SUPABASE_URL -c "SELECT * FROM jico_life_runs ORDER BY created_at DESC LIMIT 1;"

# 4. Verify artifact in R2
# Check: https://jico-workspace.r2.cloudflarestorage.com/jico-life/build-*.zip

# 5. Verify cost tracked
psql $SUPABASE_URL -c "SELECT * FROM costs WHERE DATE(created_at) = CURRENT_DATE AND agent = 'jico_life_dev';"
```

**Success Criteria**:
- [ ] Task created in Supabase
- [ ] Build completed without errors
- [ ] Artifact uploaded to R2
- [ ] Cost tracked correctly
- [ ] Discord shows completion message

**Deliverable**: Jico Life agent fully operational.

---

### Step 8: Update GOVERNANCE.md (1 day)

**Timeline**: 2026-07-26

**Changes**:
1. Update Central Infrastructure:
   ```
   - **Current Phase**: 9 (✅ COMPLETE)
   - **Assigned Phase**: 10 (MCPO Agent Onboarding) — or pause
   ```

2. Add Jico Life Agent section:
   ```
   ### **Jico Life Dev Agent**
   - **Status**: 🟢 ACTIVE
   - **Current Phase**: 1 (✅ COMPLETE)
   - **Assigned Phase**: 2 (Learning Integration)
   - ...
   ```

3. Update tracking table to show Jico Life active

**Deliverable**: GOVERNANCE.md reflects Jico Life onboarding complete.

---

## Rollback Plan (If Needed)

If Jico Life agent integration fails:

1. **Scale down Jico agent**: Don't activate jico_life_dev in orchestrator
2. **Keep tables**: Leave Supabase tables for Jico (no data loss)
3. **Re-attempt**: Next session can retry Phase 9 with more debugging

---

## Success Metrics

✅ **By end of Phase 9:**
- [ ] Jico Life Dev Agent created and tested
- [ ] Supabase tables for Jico ready
- [ ] Orchestrator routes Jico tasks correctly
- [ ] At least 1 successful Jico build completed
- [ ] Skillsets documented + loaded
- [ ] GOVERNANCE.md updated with Jico assignment
- [ ] Discord channels for Jico operational

**Timeline**: 7 days (2026-07-18 to 2026-07-26)

**Effort**: ~40 hours (mirroring Phase 1-8 work from NacPac)

---

## Next Phase (Phase 10+)

After Phase 9 stable, start **MCPO Agent Onboarding**:
- Marketing Agent (ad campaigns, analytics)
- Customer Success Agent (support, feedback)
- Product Agent (roadmap, prioritization)
- Operations Agent (infrastructure, monitoring)

Each follows same 1-9 phase roadmap.

---

**Status**: 🟡 PENDING START  
**Auto-assigned by**: `check_phase_assignment.py central` (after Phase 8 verified stable)  
**Last updated**: 2026-07-18 14:45 UTC
