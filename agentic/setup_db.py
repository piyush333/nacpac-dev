"""Initialize PostgreSQL database schema."""

import psycopg2
import os
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get database URL from .env
database_url = os.getenv("DATABASE_URL")

if not database_url:
    logger.error("❌ DATABASE_URL not set in .env")
    sys.exit(1)

# Schema SQL
SCHEMA_SQL = """
-- Organizations
CREATE TABLE IF NOT EXISTS organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    owner_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Brands
CREATE TABLE IF NOT EXISTS brands (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID REFERENCES organizations(id),
    name VARCHAR(255) NOT NULL,
    repo_url VARCHAR(255),
    tech_stack VARCHAR(255),
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tasks
CREATE TABLE IF NOT EXISTS tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID REFERENCES organizations(id),
    brand_id UUID REFERENCES brands(id),
    created_by VARCHAR(255),
    input_text TEXT,
    intent JSONB,
    agent VARCHAR(255),
    status VARCHAR(50) DEFAULT 'pending',
    result TEXT,
    error TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP
);

-- Agent Runs
CREATE TABLE IF NOT EXISTS runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID REFERENCES tasks(id),
    agent VARCHAR(255),
    model VARCHAR(255),
    tokens_in INT,
    tokens_out INT,
    cost_usd DECIMAL(10,4),
    duration_seconds INT,
    status VARCHAR(50),
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    finished_at TIMESTAMP,
    logs TEXT
);

-- Brand State
CREATE TABLE IF NOT EXISTS brand_state (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    brand_id UUID REFERENCES brands(id),
    current_branch VARCHAR(255),
    last_commit VARCHAR(255),
    last_deploy_env VARCHAR(50),
    last_deploy_time TIMESTAMP,
    last_build_artifact_path VARCHAR(255),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Builds
CREATE TABLE IF NOT EXISTS builds (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    brand_id UUID REFERENCES brands(id),
    build_type VARCHAR(50),
    branch VARCHAR(255),
    commit_hash VARCHAR(255),
    output_path VARCHAR(255),
    artifact_url VARCHAR(255),
    status VARCHAR(50),
    error_log TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Deployments
CREATE TABLE IF NOT EXISTS deployments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    brand_id UUID REFERENCES brands(id),
    build_id UUID REFERENCES builds(id),
    environment VARCHAR(50),
    status VARCHAR(50),
    deployed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deployed_by VARCHAR(255),
    rollback_available BOOLEAN DEFAULT FALSE
);

-- Costs
CREATE TABLE IF NOT EXISTS costs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID REFERENCES organizations(id),
    date DATE,
    agent VARCHAR(255),
    model VARCHAR(255),
    tokens_in INT,
    tokens_out INT,
    cost_usd DECIMAL(10,4),
    cumulative_day DECIMAL(10,4),
    cumulative_month DECIMAL(10,4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Decisions
CREATE TABLE IF NOT EXISTS decisions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID REFERENCES organizations(id),
    decision_date DATE,
    decision TEXT,
    rationale TEXT,
    decision_owner VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Knowledge
CREATE TABLE IF NOT EXISTS knowledge (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID REFERENCES organizations(id),
    topic VARCHAR(255),
    content TEXT,
    source VARCHAR(255),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Agents Registry
CREATE TABLE IF NOT EXISTS agents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) UNIQUE NOT NULL,
    capabilities TEXT[],
    version VARCHAR(50),
    status VARCHAR(50) DEFAULT 'active',
    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for common queries
CREATE INDEX IF NOT EXISTS idx_tasks_org_id ON tasks(org_id);
CREATE INDEX IF NOT EXISTS idx_tasks_brand_id ON tasks(brand_id);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_runs_task_id ON runs(task_id);
CREATE INDEX IF NOT EXISTS idx_costs_org_id ON costs(org_id);
CREATE INDEX IF NOT EXISTS idx_costs_date ON costs(date);
CREATE INDEX IF NOT EXISTS idx_brands_org_id ON brands(org_id);
"""

def setup_database():
    """Create database schema."""
    try:
        logger.info(f"Connecting to PostgreSQL...")
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()

        logger.info("Creating schema...")
        cursor.execute(SCHEMA_SQL)
        conn.commit()

        logger.info("✅ Database schema created successfully")

        # Verify tables
        cursor.execute("""
            SELECT table_name FROM information_schema.tables
            WHERE table_schema = 'public'
        """)
        tables = cursor.fetchall()
        logger.info(f"✅ Tables created: {len(tables)}")
        for table in tables:
            logger.info(f"   - {table[0]}")

        cursor.close()
        conn.close()
        return True

    except Exception as e:
        logger.error(f"❌ Database setup failed: {e}")
        return False

if __name__ == "__main__":
    success = setup_database()
    sys.exit(0 if success else 1)
