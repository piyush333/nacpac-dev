-- Jico Agentic System Database Schema
-- Execute this in your Supabase project

-- ============ ORG STRUCTURE ============

CREATE TABLE brands (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL UNIQUE,
  repo_url TEXT,
  tech_stack TEXT,
  status TEXT DEFAULT 'active',
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

INSERT INTO brands (name, repo_url, tech_stack, status) VALUES
  ('nacpac', 'https://github.com/piyush333/nacpac-dev/tree/main/nacpac-workspace-main', 'Expo/React Native (mobile), Electron (desktop), Firebase', 'active'),
  ('jico_life', 'https://github.com/piyush333/nacpac-dev/tree/main/nacpac-workspace-main', 'Static HTML/JS (Netlify), model-viewer, GLB 3D models', 'active');

-- ============ AGENT EXECUTION ============

CREATE TABLE tasks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  brand TEXT NOT NULL REFERENCES brands(name),
  task_type TEXT NOT NULL,
  input_text TEXT,
  status TEXT DEFAULT 'pending',
  created_by TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  completed_at TIMESTAMP,
  result_summary TEXT,
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_tasks_brand ON tasks(brand);
CREATE INDEX idx_tasks_status ON tasks(status);

CREATE TABLE runs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  task_id UUID REFERENCES tasks(id),
  agent TEXT NOT NULL,
  model TEXT NOT NULL,
  tokens_in INTEGER DEFAULT 0,
  tokens_out INTEGER DEFAULT 0,
  cost_usd DECIMAL(10, 6) DEFAULT 0,
  status TEXT DEFAULT 'completed',
  log_url TEXT,
  started_at TIMESTAMP DEFAULT NOW(),
  finished_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_runs_task ON runs(task_id);
CREATE INDEX idx_runs_agent ON runs(agent);

-- ============ BRAND STATE ============

CREATE TABLE brand_state (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  brand TEXT NOT NULL UNIQUE REFERENCES brands(name),
  current_branch TEXT,
  last_commit TEXT,
  last_deploy_env TEXT,
  last_deploy_time TIMESTAMP,
  version TEXT,
  updated_at TIMESTAMP DEFAULT NOW()
);

INSERT INTO brand_state (brand, current_branch, last_commit) VALUES
  ('nacpac', 'develop', 'unknown'),
  ('jico_life', 'main', 'unknown');

-- ============ BUILD HISTORY ============

CREATE TABLE builds (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  brand TEXT NOT NULL REFERENCES brands(name),
  type TEXT NOT NULL,
  commit TEXT,
  output_path TEXT,
  size_bytes BIGINT,
  status TEXT DEFAULT 'success',
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_builds_brand ON builds(brand);
CREATE INDEX idx_builds_type ON builds(type);

CREATE TABLE deployments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  brand TEXT NOT NULL REFERENCES brands(name),
  environment TEXT NOT NULL,
  commit TEXT,
  deployed_at TIMESTAMP DEFAULT NOW(),
  deployed_by TEXT DEFAULT 'agentic-system'
);

CREATE INDEX idx_deployments_brand ON deployments(brand);
CREATE INDEX idx_deployments_env ON deployments(environment);

-- ============ ORG KNOWLEDGE ============

CREATE TABLE decisions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  session_date DATE,
  decision TEXT NOT NULL,
  rationale TEXT,
  decision_log_url TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE knowledge (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  topic TEXT NOT NULL,
  content TEXT,
  source TEXT,
  updated_at TIMESTAMP DEFAULT NOW()
);

-- ============ COST TRACKING ============

CREATE TABLE costs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  date DATE DEFAULT CURRENT_DATE,
  agent TEXT,
  model TEXT,
  tokens INTEGER,
  cost_usd DECIMAL(10, 6),
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_costs_date ON costs(date);
CREATE INDEX idx_costs_agent ON costs(agent);

-- ============ SESSION TRACKING ============

CREATE TABLE sessions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  started_at TIMESTAMP DEFAULT NOW(),
  ended_at TIMESTAMP,
  summary TEXT,
  user_email TEXT
);

-- ============ DEAD LETTER QUEUE ============

CREATE TABLE failed_tasks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  task_id UUID REFERENCES tasks(id),
  error_message TEXT,
  retry_count INTEGER DEFAULT 0,
  next_retry_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW()
);

-- ============ ROW-LEVEL SECURITY ============

ALTER TABLE tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE runs ENABLE ROW LEVEL SECURITY;
ALTER TABLE brand_state ENABLE ROW LEVEL SECURITY;

-- Allow all authenticated users to read/write (adjust as needed)
CREATE POLICY "Allow authenticated" ON tasks FOR ALL
  USING (auth.role() = 'authenticated');

CREATE POLICY "Allow authenticated" ON runs FOR ALL
  USING (auth.role() = 'authenticated');

CREATE POLICY "Allow authenticated" ON brand_state FOR ALL
  USING (auth.role() = 'authenticated');

-- ============ VIEWS ============

-- Daily cost aggregation
CREATE VIEW daily_costs AS
SELECT
  date,
  SUM(cost_usd) as total_cost,
  COUNT(*) as call_count
FROM costs
GROUP BY date
ORDER BY date DESC;

-- Monthly cost aggregation
CREATE VIEW monthly_costs AS
SELECT
  DATE_TRUNC('month', date)::DATE as month,
  SUM(cost_usd) as total_cost,
  COUNT(*) as call_count
FROM costs
GROUP BY DATE_TRUNC('month', date)
ORDER BY month DESC;

-- Task completion rate
CREATE VIEW task_stats AS
SELECT
  brand,
  COUNT(*) as total_tasks,
  SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed_tasks,
  SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed_tasks,
  ROUND(100.0 * SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) / COUNT(*), 2) as completion_rate
FROM tasks
GROUP BY brand;

COMMIT;
