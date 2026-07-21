"""Main FastAPI application for Personal AI OS."""

from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from db import get_db, init_db
from orchestrator import orchestrator

load_dotenv()

app = FastAPI(
    title="Personal AI OS",
    description="Single-user AI executive assistant",
    version="0.1.0"
)

# CORS for local frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple API key authentication
def verify_api_key(authorization: str = Header(None)):
    """Verify API key from Authorization header."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")

    # Expect: "Bearer <token>"
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid authorization format")

    token = parts[1]
    expected_key = os.getenv("API_KEY", "test-key-123")

    if token != expected_key:
        raise HTTPException(status_code=401, detail="Invalid API key")

    return token


# Request/Response models
class RequestInput(BaseModel):
    """User request to the system."""
    project_id: str
    user_input: str


class RequestResponse(BaseModel):
    """Response from the system."""
    request_id: int
    project_id: str
    status: str
    response: str
    tokens_used: int = 0
    estimated_cost: float = 0.0


# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


# Initialize database on startup
@app.on_event("startup")
async def startup():
    """Initialize database on startup."""
    init_db()
    print("✓ Database initialized")


# Main request handler
@app.post("/request", response_model=RequestResponse)
async def handle_request(
    request: RequestInput,
    api_key: str = Depends(verify_api_key),
    db = Depends(get_db)
):
    """
    Handle user request:
    1. Store request in DB
    2. Route to orchestrator
    3. Execute agent + tools
    4. Store response in DB
    5. Return result
    """
    try:
        # Execute orchestrator
        result = await orchestrator.execute(
            user_input=request.user_input,
            project_id=request.project_id,
            db=db
        )

        return RequestResponse(
            request_id=result.get("request_id", 0),
            project_id=request.project_id,
            status=result.get("status", "completed"),
            response=result.get("response", ""),
            tokens_used=result.get("tokens_used", 0),
            estimated_cost=result.get("estimated_cost", 0.0)
        )

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# History endpoint
@app.get("/history/{project_id}")
async def get_history(
    project_id: str,
    api_key: str = Depends(verify_api_key),
    db = Depends(get_db)
):
    """Get request history for a project."""
    try:
        from sqlalchemy import text

        result = db.execute(
            text("""
                SELECT id, user_input, response, status, created_at
                FROM requests
                WHERE project_id = :project_id
                ORDER BY created_at DESC
                LIMIT 50
            """),
            {"project_id": project_id}
        )

        requests = [
            {
                "id": row[0],
                "user_input": row[1],
                "response": row[2],
                "status": row[3],
                "created_at": str(row[4])
            }
            for row in result
        ]

        return {"project_id": project_id, "requests": requests}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
