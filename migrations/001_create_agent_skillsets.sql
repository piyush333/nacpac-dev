-- Create agent_skillsets table for persistent agent capabilities
CREATE TABLE IF NOT EXISTS agent_skillsets (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  agent_id TEXT NOT NULL,  -- "nacpac_dev", "jico_life_dev", etc.
  skillset_name TEXT NOT NULL,  -- "python", "react", "expo_dev", etc.
  description TEXT,  -- Human-readable skill description
  documentation TEXT,  -- Full documentation/knowledge for this skill
  version TEXT DEFAULT '1.0',  -- Version of this skill
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),

  CONSTRAINT unique_agent_skill UNIQUE(agent_id, skillset_name)
);

-- Create index for fast lookup by agent_id
CREATE INDEX IF NOT EXISTS idx_agent_skillsets_agent_id ON agent_skillsets(agent_id);

-- Add trigger to auto-update updated_at
CREATE OR REPLACE FUNCTION update_agent_skillsets_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER agent_skillsets_update_timestamp
BEFORE UPDATE ON agent_skillsets
FOR EACH ROW
EXECUTE FUNCTION update_agent_skillsets_timestamp();
