# Supabase Schema Design & Naming Convention

**LOCKED FOR ALL PHASES.** Do NOT change without central session approval.

---

## **Naming Convention (MANDATORY)**

Every table follows this pattern:

```
{agent_id}_{table_type}

Examples:
- nacpac_skillsets
- nacpac_learned_patterns
- nacpac_tasks
- nacpac_runs

- jico_skillsets
- jico_learned_patterns
- jico_tasks
- jico_runs

- amazon_skillsets
- amazon_learned_patterns
- amazon_tasks
- amazon_runs
```

**Why**: Clear ownership, prevents chaos, scales to 10+ agents

---

## **Table Types (Same for Every Agent)**

Every agent gets exactly these 4 tables:

| Table | Stores | Columns |
|-------|--------|---------|
| `{agent}_skillsets` | Technical capabilities | id, agent_id, skillset_name, description, documentation, version, created_at, updated_at |
| `{agent}_learned_patterns` | Learned patterns from tasks | id, agent_id, pattern_type, pattern_description, examples[], failures[], success_rate, last_used, created_at |
| `{agent}_tasks` | Task history | id, agent_id, task_input, status, result_summary, cost_usd, created_at, completed_at |
| `{agent}_runs` | Execution logs | id, agent_id, task_id, model, tokens_in, tokens_out, cost_usd, status, started_at, finished_at |

---

## **Shared/System Tables (Org-Wide)**

| Table | Purpose | Owner |
|-------|---------|-------|
| `session_coordination` | Track what each session is building | Central (nacpac-dev) |
| `agent_tasks` | Meta-level: phases + tasks per agent | Central |
| `costs` | Unified cost tracking across all agents | Central |
| `decisions` | Org-wide decisions (append-only) | Central |

---

## **Current Agent Tables (Phase 1-2)**

✅ **nacpac_dev**
- nacpac_skillsets (Phase 1: 7 skillsets seeded)
- nacpac_learned_patterns (Phase 2: ready to populate)
- nacpac_tasks (Phase 3+)
- nacpac_runs (Phase 3+)

---

## **Future Agent Tables (DO NOT CREATE YET)**

⏳ **jico_life_dev** (Phase 3, when jico agent session starts)
- jico_skillsets
- jico_learned_patterns
- jico_tasks
- jico_runs

⏳ **jico_amazon_bot** (Phase 4+)
- amazon_skillsets
- amazon_learned_patterns
- amazon_tasks
- amazon_runs

⏳ **jico_meta_bot** (Phase 5+)
- meta_skillsets
- meta_learned_patterns
- meta_tasks
- meta_runs

⏳ **MCPO Agents** (Phase 6+)
- marketing_skillsets, marketing_learned_patterns, marketing_tasks, marketing_runs
- customer_success_skillsets, customer_success_learned_patterns, customer_success_tasks, customer_success_runs
- product_skillsets, product_learned_patterns, product_tasks, product_runs
- operations_skillsets, operations_learned_patterns, operations_tasks, operations_runs

---

## **Total Table Count at Full Scale**

```
8 agents × 4 tables = 32 agent tables
+ 4 shared tables = 36 total tables
```

---

## **CRITICAL: Phase 2 Checklist**

⚠️ **BEFORE nacpac agent creates nacpac_learned_patterns table in Phase 2:**

- [ ] Confirm naming convention is correct: `nacpac_learned_patterns` (NOT `learned_patterns`)
- [ ] Confirm columns match schema above
- [ ] Confirm agent_id column uses value: `nacpac_dev`
- [ ] Create migration: `migrations/002_create_nacpac_learned_patterns.sql`
- [ ] Test table creation in Supabase
- [ ] Verify data can be inserted
- [ ] Only THEN proceed with Phase 2 work

**If table is created with WRONG name, data pollution happens. Cannot fix without migration.**

---

## **How to Add New Agent (Template)**

When adding new agent (e.g., jico_life_dev):

1. **Create migration file:**
   ```sql
   -- migrations/003_create_jico_tables.sql
   
   CREATE TABLE jico_skillsets (
     id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
     agent_id TEXT DEFAULT 'jico_life_dev',
     skillset_name TEXT NOT NULL,
     description TEXT,
     documentation TEXT,
     version TEXT DEFAULT '1.0',
     created_at TIMESTAMP DEFAULT NOW(),
     updated_at TIMESTAMP DEFAULT NOW()
   );
   
   CREATE TABLE jico_learned_patterns (
     id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
     agent_id TEXT DEFAULT 'jico_life_dev',
     pattern_type TEXT NOT NULL,
     pattern_description TEXT,
     examples JSONB DEFAULT '[]',
     failures JSONB DEFAULT '[]',
     success_rate FLOAT DEFAULT 0,
     last_used TIMESTAMP,
     created_at TIMESTAMP DEFAULT NOW()
   );
   
   CREATE TABLE jico_tasks (
     id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
     agent_id TEXT DEFAULT 'jico_life_dev',
     task_input TEXT NOT NULL,
     status TEXT,
     result_summary TEXT,
     cost_usd FLOAT,
     created_at TIMESTAMP DEFAULT NOW(),
     completed_at TIMESTAMP
   );
   
   CREATE TABLE jico_runs (
     id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
     agent_id TEXT DEFAULT 'jico_life_dev',
     task_id UUID,
     model TEXT,
     tokens_in INT,
     tokens_out INT,
     cost_usd FLOAT,
     status TEXT,
     started_at TIMESTAMP,
     finished_at TIMESTAMP
   );
   ```

2. **Add to session_coordination:**
   ```sql
   INSERT INTO session_coordination (session_name, agent_id, status, current_phase, context_file)
   VALUES ('jico_agent', 'jico_life_dev', 'waiting', 'skillsets', 'AGENT_JICO_CONTEXT.md');
   ```

3. **Update SUPABASE_SCHEMA.md** (this file)

4. **Proceed with agent onboarding**

---

## **Version History**

| Date | Change | Owner |
|------|--------|-------|
| 2026-07-17 | Schema locked for nacpac_dev (Phases 1-8) | nacpac-dev |
| TBD | Add jico_life_dev schema (Phase 3) | nacpac-dev |
| TBD | Add amazon schema (Phase 4) | nacpac-dev |
| TBD | Add MCPO schemas (Phase 6) | nacpac-dev |

---

## **DO NOT:**

❌ Create tables without {agent_id} prefix  
❌ Create tables without approval from central session  
❌ Rename/restructure tables after data is populated  
❌ Deviate from the 4 tables per agent pattern  

---

## **IF YOU REALIZE AN ERROR:**

If Phase 2 starts and you realize table name/schema is wrong:

1. **STOP immediately**
2. **Do NOT populate data**
3. **Delete the table**
4. **Update SUPABASE_SCHEMA.md**
5. **Create table with correct name**
6. **Resume Phase 2**

**Fixing before data populates = 5 min  
Fixing after data populates = 1-2 hours of migration**

---

**This schema is locked. Central session (nacpac-dev) ensures consistency.**
