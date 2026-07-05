"""Database setup for PostgreSQL on DigitalOcean."""

import os
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

try:
    import psycopg2
    from psycopg2.extras import DictCursor
except ImportError:
    logger.error("psycopg2 not installed")
    psycopg2 = None


def init_database():
    """Initialize database schema."""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        logger.error("DATABASE_URL not set")
        return False

    if not psycopg2:
        logger.error("psycopg2 not available")
        return False

    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()

        # Create tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id SERIAL PRIMARY KEY,
                brand VARCHAR(50),
                task_type VARCHAR(50),
                input_text TEXT,
                status VARCHAR(50),
                created_by VARCHAR(100),
                created_at TIMESTAMP,
                completed_at TIMESTAMP,
                result_summary TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS builds (
                id SERIAL PRIMARY KEY,
                brand VARCHAR(50),
                type VARCHAR(50),
                commit VARCHAR(100),
                output_path TEXT,
                status VARCHAR(50),
                created_at TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS deployments (
                id SERIAL PRIMARY KEY,
                brand VARCHAR(50),
                environment VARCHAR(50),
                commit VARCHAR(100),
                deployed_at TIMESTAMP
            )
        """)

        conn.commit()
        cursor.close()
        conn.close()

        logger.info("✅ Database initialized")
        return True

    except Exception as e:
        logger.error(f"Database init failed: {e}")
        return False


if __name__ == "__main__":
    init_database()
