"""Database connection and schema management."""

import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/personal_ai"
)

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database schema."""
    with engine.begin() as conn:
        # Projects table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS projects (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) UNIQUE NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            )
        """))

        # Requests table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS requests (
                id SERIAL PRIMARY KEY,
                project_id VARCHAR(255) NOT NULL,
                user_input TEXT NOT NULL,
                response TEXT,
                status VARCHAR(20) DEFAULT 'pending',
                tokens_used INT DEFAULT 0,
                estimated_cost FLOAT DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT NOW(),
                completed_at TIMESTAMP,
                FOREIGN KEY(project_id) REFERENCES projects(name)
            )
        """))

        # Tasks table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS tasks (
                id SERIAL PRIMARY KEY,
                request_id INT NOT NULL,
                title VARCHAR(255),
                description TEXT,
                status VARCHAR(20),
                created_at TIMESTAMP DEFAULT NOW(),
                FOREIGN KEY(request_id) REFERENCES requests(id)
            )
        """))

        # Decisions table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS decisions (
                id SERIAL PRIMARY KEY,
                request_id INT NOT NULL,
                decision TEXT,
                reasoning TEXT,
                created_at TIMESTAMP DEFAULT NOW(),
                FOREIGN KEY(request_id) REFERENCES requests(id)
            )
        """))

        # Observability table (logs)
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS logs (
                id SERIAL PRIMARY KEY,
                request_id INT,
                level VARCHAR(20),
                message TEXT,
                data JSONB,
                created_at TIMESTAMP DEFAULT NOW(),
                FOREIGN KEY(request_id) REFERENCES requests(id)
            )
        """))

        print("✓ Database schema initialized")


def save_request(
    db: Session,
    project_id: str,
    user_input: str,
    response: str,
    status: str = "completed",
    tokens_used: int = 0,
    estimated_cost: float = 0.0
) -> int:
    """Save request to database and return request_id."""
    from sqlalchemy import text

    result = db.execute(
        text("""
            INSERT INTO requests
            (project_id, user_input, response, status, tokens_used, estimated_cost)
            VALUES (:project_id, :user_input, :response, :status, :tokens_used, :estimated_cost)
            RETURNING id
        """),
        {
            "project_id": project_id,
            "user_input": user_input,
            "response": response,
            "status": status,
            "tokens_used": tokens_used,
            "estimated_cost": estimated_cost
        }
    )
    db.commit()
    return result.scalar()


def log_event(
    db: Session,
    request_id: int,
    level: str,
    message: str,
    data: dict = None
):
    """Log an event to the observability table."""
    from sqlalchemy import text
    import json

    db.execute(
        text("""
            INSERT INTO logs (request_id, level, message, data)
            VALUES (:request_id, :level, :message, :data)
        """),
        {
            "request_id": request_id,
            "level": level,
            "message": message,
            "data": json.dumps(data or {})
        }
    )
    db.commit()
