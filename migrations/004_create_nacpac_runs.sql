-- Phase 3: Create nacpac_runs table
-- Stores execution logs for nacpac_dev agent
-- Schema locked per SUPABASE_SCHEMA.md

CREATE TABLE IF NOT EXISTS nacpac_runs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  agent_id TEXT NOT NULL DEFAULT 'nacpac_dev',
  task_id UUID NOT NULL,              -- Reference to nacpac_tasks
  model TEXT NOT NULL,                -- Claude model used (e.g., claude-sonnet-5)
  tokens_in INT NOT NULL,             -- Input tokens consumed
  tokens_out INT NOT NULL,            -- Output tokens consumed
  cost_usd FLOAT DEFAULT 0.0,         -- Cost for this specific run
  status TEXT NOT NULL DEFAULT 'completed',  -- started, completed, failed
  started_at TIMESTAMP DEFAULT NOW(),
  finished_at TIMESTAMP,

  -- Constraints
  CONSTRAINT valid_run_status CHECK (status IN ('started', 'completed', 'failed')),
  CONSTRAINT valid_tokens CHECK (tokens_in >= 0 AND tokens_out >= 0),
  CONSTRAINT valid_run_cost CHECK (cost_usd >= 0)
);

-- Index for fast lookup by agent
CREATE INDEX IF NOT EXISTS idx_nacpac_runs_agent
  ON nacpac_runs(agent_id);

-- Index for task_id lookups (find all runs for a task)
CREATE INDEX IF NOT EXISTS idx_nacpac_runs_task_id
  ON nacpac_runs(task_id);

-- Index for run history (most recent first)
CREATE INDEX IF NOT EXISTS idx_nacpac_runs_started
  ON nacpac_runs(started_at DESC);

-- Foreign key constraint to tasks table
ALTER TABLE nacpac_runs ADD CONSTRAINT fk_nacpac_runs_task_id
  FOREIGN KEY (task_id) REFERENCES nacpac_tasks(id) ON DELETE CASCADE;
