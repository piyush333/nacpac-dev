-- Create learned_patterns table for agent skill improvement tracking
CREATE TABLE IF NOT EXISTS learned_patterns (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  agent_id TEXT NOT NULL,           -- "nacpac_dev", "jico_life_dev", etc.
  skillset_name TEXT NOT NULL,      -- "python", "expo_dev", "react", etc.
  pattern_type TEXT NOT NULL,       -- "success", "failure", "optimization", "best_practice"
  pattern_description TEXT NOT NULL, -- What was learned
  context TEXT,                      -- Where/when it was learned
  confidence DECIMAL(3,2) DEFAULT 0.5, -- 0.0-1.0 confidence level
  usage_count INTEGER DEFAULT 0,     -- Times this pattern has been applied
  success_rate DECIMAL(3,2) DEFAULT 0.0, -- Success rate when applied (0.0-1.0)
  related_task_id TEXT,              -- Reference to task that generated this learning
  source_model TEXT,                 -- Which model discovered this ("claude-opus", "claude-sonnet", etc.)
  discovered_at TIMESTAMP DEFAULT NOW(),
  last_applied_at TIMESTAMP,
  updated_at TIMESTAMP DEFAULT NOW(),

  CONSTRAINT unique_pattern UNIQUE(agent_id, skillset_name, pattern_type, pattern_description)
);

-- Index for fast lookup by agent/skillset
CREATE INDEX IF NOT EXISTS idx_learned_patterns_agent_skill
  ON learned_patterns(agent_id, skillset_name);

-- Index for pattern type lookup
CREATE INDEX IF NOT EXISTS idx_learned_patterns_type
  ON learned_patterns(pattern_type);

-- Index for confidence-based sorting (find most reliable patterns)
CREATE INDEX IF NOT EXISTS idx_learned_patterns_confidence
  ON learned_patterns(confidence DESC);

-- Add trigger to auto-update updated_at
CREATE OR REPLACE FUNCTION update_learned_patterns_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER learned_patterns_update_timestamp
BEFORE UPDATE ON learned_patterns
FOR EACH ROW
EXECUTE FUNCTION update_learned_patterns_timestamp();

-- Create learning_feedback table for tracking improvements over time
CREATE TABLE IF NOT EXISTS learning_feedback (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  agent_id TEXT NOT NULL,
  skillset_name TEXT NOT NULL,
  task_id TEXT,
  feedback_type TEXT NOT NULL,  -- "positive", "negative", "edge_case", "optimization"
  feedback_text TEXT NOT NULL,
  improvement_suggested TEXT,   -- Suggested improvement to skillset
  applied BOOLEAN DEFAULT FALSE, -- Whether improvement was applied
  applied_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Index for agent/skillset feedback
CREATE INDEX IF NOT EXISTS idx_feedback_agent_skill
  ON learning_feedback(agent_id, skillset_name);

-- Index for improvement tracking
CREATE INDEX IF NOT EXISTS idx_feedback_applied
  ON learning_feedback(applied);
