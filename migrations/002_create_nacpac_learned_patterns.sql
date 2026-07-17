-- Phase 2: Create nacpac_learned_patterns table
-- Stores learned patterns from nacpac_dev agent task execution
-- Schema locked per SUPABASE_SCHEMA.md

CREATE TABLE IF NOT EXISTS nacpac_learned_patterns (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  agent_id TEXT NOT NULL DEFAULT 'nacpac_dev',
  pattern_type TEXT NOT NULL,        -- "success", "failure", "optimization", "best_practice"
  pattern_description TEXT NOT NULL, -- What was learned
  examples JSONB DEFAULT '[]',       -- Successful examples array
  failures JSONB DEFAULT '[]',       -- Failure cases array
  success_rate FLOAT DEFAULT 0.0,    -- 0.0-1.0: success percentage
  last_used TIMESTAMP,               -- When pattern was last applied
  created_at TIMESTAMP DEFAULT NOW(),

  CONSTRAINT valid_success_rate CHECK (success_rate >= 0.0 AND success_rate <= 1.0)
);

-- Index for fast lookup by agent
CREATE INDEX IF NOT EXISTS idx_nacpac_patterns_agent
  ON nacpac_learned_patterns(agent_id);

-- Index for pattern type lookup
CREATE INDEX IF NOT EXISTS idx_nacpac_patterns_type
  ON nacpac_learned_patterns(pattern_type);

-- Index for success rate (find most reliable patterns)
CREATE INDEX IF NOT EXISTS idx_nacpac_patterns_success_rate
  ON nacpac_learned_patterns(success_rate DESC);
