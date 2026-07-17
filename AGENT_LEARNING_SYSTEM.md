# Agent Learning System — Phase 2

**Status:** ✅ Implemented  
**Date:** 2026-07-17  
**Purpose:** Enable agents to learn from experience and improve skill execution over time.

---

## Overview

The Agent Learning System tracks what agents learn from executing tasks, capturing:
- **Learned Patterns** — Success/failure patterns, optimizations, best practices
- **Learning Feedback** — Human or system feedback on agent performance
- **Usage Metrics** — How often patterns are used and their success rates

This enables agents to improve incrementally across sessions through:
1. Pattern discovery (from tasks)
2. Pattern validation (usage tracking)
3. Confidence scoring (success rates)
4. Feedback incorporation (human input)

---

## Architecture

### Tables

#### `learned_patterns`
Persistent storage of patterns agents discover while working.

```sql
id UUID                    -- Unique pattern ID
agent_id TEXT              -- "nacpac_dev", "jico_life_dev"
skillset_name TEXT         -- "python", "react", "expo_dev"
pattern_type TEXT          -- "success", "failure", "optimization", "best_practice"
pattern_description TEXT   -- What was learned (e.g., "Always update package-lock.json before builds")
context TEXT               -- Where learned (task_id, branch, error message)
confidence DECIMAL(0-1)    -- 0.5-0.99: How confident we are in this pattern
usage_count INTEGER        -- How many times pattern has been applied
success_rate DECIMAL(0-1)  -- Percentage of successful applications
related_task_id TEXT       -- Original task that discovered this
source_model TEXT          -- Which Claude model discovered it
discovered_at TIMESTAMP    -- When first discovered
last_applied_at TIMESTAMP  -- Most recent usage
updated_at TIMESTAMP       -- Last modification
```

#### `learning_feedback`
Human or system feedback on agent learning and performance.

```sql
id UUID                      -- Unique feedback ID
agent_id TEXT                -- Agent receiving feedback
skillset_name TEXT           -- Which skillset the feedback applies to
task_id TEXT                 -- Related task (if any)
feedback_type TEXT           -- "positive", "negative", "edge_case", "optimization"
feedback_text TEXT           -- Human-written feedback
improvement_suggested TEXT   -- Suggested change to skillset/pattern
applied BOOLEAN              -- Whether improvement was implemented
applied_at TIMESTAMP         -- When improvement was applied
created_at TIMESTAMP         -- When feedback was recorded
```

---

## How Agents Learn

### 1. **Pattern Discovery** (During Task Execution)

When an agent completes a task, it can record learned patterns:

```python
# After a successful build
memory.record_learned_pattern(
    agent_id="nacpac_dev",
    skillset_name="expo_dev",
    pattern_type="success",
    pattern_description="EAS build succeeds when package.json has valid scripts",
    context="NacPac APK build task #123",
    source_model="claude-opus-4-8",
    task_id="task-123"
)

# Or a failure that was resolved
memory.record_learned_pattern(
    agent_id="nacpac_dev",
    skillset_name="python",
    pattern_type="failure",
    pattern_description="Credential loading fails if GOOGLE_DRIVE_CREDENTIALS_JSON path is relative",
    context="Build failed, then succeeded with absolute path",
    task_id="task-124"
)

# Or an optimization discovered
memory.record_learned_pattern(
    agent_id="nacpac_dev",
    skillset_name="npm",
    pattern_type="optimization",
    pattern_description="npm ci is 30% faster than npm install for CI environments",
    context="Measured during EXE build task #125",
    task_id="task-125"
)
```

### 2. **Pattern Usage & Validation**

Agents retrieve learned patterns when working on similar tasks and track success:

```python
# Get reliable patterns for this skillset
patterns = memory.get_learned_patterns(
    agent_id="nacpac_dev",
    skillset_name="expo_dev",
    pattern_type="success"
)

# Use highest-confidence patterns first
for pattern in sorted(patterns, key=lambda p: p["confidence"], reverse=True):
    if pattern["confidence"] > 0.8:
        # Apply this pattern
        apply_pattern(pattern)
        
        # Track whether it worked
        if succeeded:
            memory.update_pattern_usage(pattern["id"], success=True)
        else:
            memory.update_pattern_usage(pattern["id"], success=False)
```

### 3. **Feedback Integration**

Humans (or systems) can provide feedback on agent learning:

```python
# Positive feedback on how agent handled something
memory.record_learning_feedback(
    agent_id="nacpac_dev",
    skillset_name="react",
    feedback_type="positive",
    feedback_text="Great use of React hooks in the new mobile build",
    task_id="task-126"
)

# Report an edge case the agent missed
memory.record_learning_feedback(
    agent_id="nacpac_dev",
    skillset_name="python",
    feedback_type="edge_case",
    feedback_text="Script fails on Windows paths with spaces",
    improvement_suggested="Use pathlib.Path instead of string concatenation",
    task_id="task-127"
)

# Suggest an optimization
memory.record_learning_feedback(
    agent_id="nacpac_dev",
    skillset_name="npm",
    feedback_type="optimization",
    feedback_text="Could use npm workspaces for monorepo management",
    improvement_suggested="Create root package.json with 'workspaces' field",
    task_id="task-128"
)
```

### 4. **Learning Insights**

Get a summary of what an agent has learned:

```python
insights = memory.get_learning_insights("nacpac_dev", "expo_dev")

# Returns:
{
    "top_patterns": [
        {"pattern_description": "...", "confidence": 0.95, "success_rate": 0.92},
        {"pattern_description": "...", "confidence": 0.88, "success_rate": 0.85},
    ],
    "failure_patterns": [
        {"pattern_description": "EAS build fails when...", "usage_count": 3},
    ],
    "optimizations": [
        {"pattern_description": "Use npm ci instead of install", "success_rate": 0.98},
    ],
    "pending_improvements": 2,
    "success_feedback_count": 5
}
```

---

## Confidence & Success Scoring

### Confidence (0.0 - 1.0)

Represents how confident the system is in a pattern.

**Initial:** 0.7 (moderate, needs validation)  
**Growth:** Increases with successful usage  
**Cap:** 0.99 (never 1.0, always room for improvement)  
**Formula:** `new_confidence = min(0.99, success_rate * 1.2)`

### Success Rate (0.0 - 1.0)

Percentage of times a pattern successfully applied.

**Tracked:** Usage count + success/failure results  
**Updated:** Every time pattern is applied  
**Formula:** `new_rate = (old_rate * old_count + success) / new_count`

### Pattern Selection

When multiple patterns available, agents prefer:
1. Patterns with highest confidence (> 0.8)
2. Patterns with highest success rate
3. Patterns used recently (last_applied_at)

---

## Pattern Types

| Type | Purpose | Example |
|------|---------|---------|
| **success** | What worked well | "EAS builds succeed with valid package.json scripts" |
| **failure** | Common failures & workarounds | "Git clone fails on shallow clones; use full clone instead" |
| **optimization** | Performance/cost improvements | "npm ci 30% faster than npm install in CI" |
| **best_practice** | Recommended approaches | "Always validate environment variables before running builds" |

---

## Workflow: From Task to Learning

```
┌─────────────────────────────────────────────────┐
│ Agent Executes Task (build_apk, build_exe, etc) │
└────────────────────┬────────────────────────────┘
                     ↓
         ┌─────────────────────────────┐
         │ Observe outcomes (success/  │
         │ failure, performance metrics)│
         └────────────┬────────────────┘
                      ↓
         ┌──────────────────────────────┐
         │ Discover patterns from       │
         │ results (successes work-     │
         │ arounds, optimizations)      │
         └────────────┬─────────────────┘
                      ↓
    ┌─────────────────────────────────────┐
    │ Record learned_patterns in Supabase │
    │ (pattern_type, confidence, context) │
    └────────────┬────────────────────────┘
                 ↓
    ┌──────────────────────────────────────────┐
    │ Next time similar task runs:             │
    │ Retrieve patterns, apply high-confidence │
    │ ones first                               │
    └────────────┬─────────────────────────────┘
                 ↓
    ┌──────────────────────────────────────────┐
    │ Track usage (success/failure) with       │
    │ update_pattern_usage()                   │
    │ → Updates success_rate, confidence       │
    └────────────┬─────────────────────────────┘
                 ↓
    ┌──────────────────────────────────────────┐
    │ Receive feedback (human or system):      │
    │ Positive, negative, edge case,           │
    │ optimization suggestion                  │
    └────────────┬─────────────────────────────┘
                 ↓
    ┌──────────────────────────────────────────┐
    │ Patterns become more/less reliable;      │
    │ Agent gradually improves                 │
    │ (fewer failures, faster execution)       │
    └──────────────────────────────────────────┘
```

---

## Integration with Agents

### NacPac Dev Agent

**Skillsets to learn:**
- expo_dev — APK build patterns (EAS configuration, signing, dependencies)
- npm — Build optimization (caching, parallel builds)
- exe_windows — EXE packaging (Electron, signing, installer creation)

**Learn from:** Build success/failure, performance metrics, error recovery

### Jico Life Dev Agent

**Skillsets to learn:**
- React — Component patterns, state management
- nodejs — Server operations, API handling
- expo_dev — AR app deployment via Netlify

**Learn from:** Feature implementations, edge cases, optimization opportunities

---

## Memory Layer API

### Recording Patterns

```python
pattern_id = memory.record_learned_pattern(
    agent_id: str,
    skillset_name: str,
    pattern_type: str,            # "success", "failure", "optimization", "best_practice"
    pattern_description: str,
    context: str = None,          # Optional context (task_id, error message, etc)
    source_model: str = None,     # Which Claude model discovered this
    task_id: str = None           # Related task
) -> Optional[str]
```

### Retrieving Patterns

```python
patterns = memory.get_learned_patterns(
    agent_id: str,
    skillset_name: str = None,    # Optional filter
    pattern_type: str = None      # Optional filter
) -> list                          # Sorted by confidence DESC
```

### Updating Usage

```python
memory.update_pattern_usage(
    pattern_id: str,
    success: bool                 # Track success/failure
) -> None
```

### Recording Feedback

```python
feedback_id = memory.record_learning_feedback(
    agent_id: str,
    skillset_name: str,
    feedback_type: str,           # "positive", "negative", "edge_case", "optimization"
    feedback_text: str,
    improvement_suggested: str = None,
    task_id: str = None
) -> Optional[str]
```

### Getting Insights

```python
insights = memory.get_learning_insights(
    agent_id: str,
    skillset_name: str
) -> Dict[str, Any]
```

---

## Success Metrics

An agent's learning is successful when:

✅ **Pattern Usage Increases** — Patterns discovered early reused in later tasks  
✅ **Success Rate Climbs** — Patterns become more reliable (higher success_rate)  
✅ **Confidence Stabilizes** — High-confidence patterns (> 0.9) stay reliable  
✅ **Task Efficiency** — Tasks complete faster as optimizations are learned  
✅ **Failure Recovery** — Failure patterns prevent repeated mistakes  
✅ **Positive Feedback** — Humans/systems provide positive feedback on improvements

---

## Phase 2 Implementation

### Completed ✅
- [x] learned_patterns migration
- [x] learning_feedback migration
- [x] Memory layer methods (record, retrieve, update, insights)
- [x] Documentation

### Next Steps
1. Integrate pattern recording into agent task execution
2. Add pattern retrieval to task decision-making
3. Create feedback command for Discord bot
4. Build insights dashboard for monitoring learning
5. Test learning feedback loop with real tasks

---

## Files

| File | Purpose |
|------|---------|
| `migrations/002_create_learned_patterns.sql` | Schema for learning tables |
| `agentic/memory.py` | Memory layer + learning methods |
| `AGENT_LEARNING_SYSTEM.md` | This documentation |

---

## Example: End-to-End Learning Scenario

**Task:** Build NacPac APK  
**Agent:** NacPac Dev Agent  
**Skillset:** expo_dev

**Execution:**
1. Agent starts APK build
2. Encounters credential validation: "Always verify GOOGLE_DRIVE_CREDENTIALS_JSON is absolute path"
3. Build succeeds
4. Agent records: success pattern "Validate credentials before build"
5. Stores: `learned_patterns.insert({pattern_type: 'best_practice', confidence: 0.8})`

**Next Build (same task type, different user):**
1. Agent retrieves patterns for expo_dev skillset
2. Finds success pattern with 0.8 confidence: "Validate credentials..."
3. Applies pattern upfront → build succeeds faster
4. Updates: `usage_count: 2, success_rate: 1.0, confidence: 0.95`

**Feedback from User:**
1. User: "Great! APK built fast and without errors"
2. System records: positive feedback
3. Confidence increases: `confidence: 0.98`

**Result:** Agent gradually becomes more reliable at APK builds by learning what works.

---

**System Status:** ✅ Ready for integration  
**Next Session:** Integrate with agent task execution
