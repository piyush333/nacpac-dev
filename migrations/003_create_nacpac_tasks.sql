-- Phase 3: Create nacpac_tasks table
-- Stores task history for nacpac_dev agent
-- Schema locked per SUPABASE_SCHEMA.md

CREATE TABLE IF NOT EXISTS nacpac_tasks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  agent_id TEXT NOT NULL DEFAULT 'nacpac_dev',
  task_input TEXT NOT NULL,           -- Task description/input from user
  status TEXT NOT NULL DEFAULT 'pending',  -- pending, in_progress, completed, failed
  result_summary TEXT,                -- Final result/outcome after completion
  cost_usd FLOAT DEFAULT 0.0,         -- Total cost for this task
  created_at TIMESTAMP DEFAULT NOW(),
  completed_at TIMESTAMP             -- When task finished

  -- Constraints
  CONSTRAINT valid_status CHECK (status IN ('pending', 'in_progress', 'completed', 'failed')),
  CONSTRAINT valid_cost CHECK (cost_usd >= 0)
);

-- Index for fast lookup by agent
CREATE INDEX IF NOT EXISTS idx_nacpac_tasks_agent
  ON nacpac_tasks(agent_id);

-- Index for status lookups (find pending/in_progress tasks)
CREATE INDEX IF NOT EXISTS idx_nacpac_tasks_status
  ON nacpac_tasks(status);

-- Index for task history (most recent first)
CREATE INDEX IF NOT EXISTS idx_nacpac_tasks_created
  ON nacpac_tasks(created_at DESC);
