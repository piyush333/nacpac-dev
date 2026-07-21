# Personal AI Operating System - Quick Start Guide

Get the Personal AI OS backend running in 5 minutes.

## Prerequisites

- Python 3.10+
- Docker & Docker Compose
- Anthropic API Key (free: https://console.anthropic.com)

## 1️⃣ Clone and Setup

```bash
cd /path/to/nacpac-dev

# Install Python dependencies
pip install -r personal-ai-os-backend/requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env and add your Anthropic API key
nano .env
# Add: ANTHROPIC_API_KEY=sk-ant-...
```

## 2️⃣ Start Database

```bash
# Start PostgreSQL in Docker
docker-compose up -d

# Wait a few seconds for PostgreSQL to initialize
sleep 5

# Verify it's running
docker-compose ps
```

## 3️⃣ Run Backend

```bash
cd personal-ai-os-backend

# Start the FastAPI server
python main.py

# You should see:
# ✓ Database initialized
# INFO:     Application startup complete
# INFO:     Uvicorn running on http://0.0.0.0:8000
```

## 4️⃣ Test with Your First Request

In a new terminal:

```bash
# Simple test
curl http://localhost:8000/health

# Make a request to the AI
curl -X POST http://localhost:8000/request \
  -H "Authorization: Bearer test-key-123" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "test-project",
    "user_input": "What is 2 + 2?"
  }'

# You should get back something like:
# {
#   "request_id": 1,
#   "project_id": "test-project",
#   "status": "completed",
#   "response": "2 + 2 = 4",
#   "tokens_used": 45,
#   "estimated_cost": 0.000225
# }
```

## 5️⃣ Try File Operations

```bash
curl -X POST http://localhost:8000/request \
  -H "Authorization: Bearer test-key-123" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "test-project",
    "user_input": "Read the file personal-ai-os-backend/README.md and tell me the first section"
  }'
```

## 6️⃣ View Request History

```bash
curl -X GET http://localhost:8000/history/test-project \
  -H "Authorization: Bearer test-key-123"

# Returns all requests for this project
```

## Available Tools

Your AI assistant can use these tools:

### 📁 Filesystem
- Read files
- Write files
- List directories

### 🖥️ Terminal
- Run shell commands (with safety checks)
- Blocked: `rm -rf`, `sudo`, `chmod 777`, `dd if=`

### 📚 Documentation
- Read markdown files
- Summarize directory structures

### 💌 Email
- Send emails (mock mode by default)

### 🔗 GitHub
- Clone repositories
- Commit and push changes

## Example Requests

### 1. Read a file
```json
{
  "project_id": "my-project",
  "user_input": "Read the file at personal-ai-os-backend/README.md"
}
```

### 2. Create a file
```json
{
  "project_id": "my-project",
  "user_input": "Create a new file at /tmp/test.txt with the content 'Hello World'"
}
```

### 3. Run a command
```json
{
  "project_id": "my-project",
  "user_input": "Run the command 'ls -la' and tell me what's in the current directory"
}
```

### 4. Clone a repository
```json
{
  "project_id": "my-project",
  "user_input": "Clone the repository https://github.com/anthropics/anthropic-sdk-python.git to /tmp/sdk-python"
}
```

## Stopping Everything

```bash
# Stop the backend (Ctrl+C in the terminal running main.py)
# Then stop the database:
docker-compose down

# Remove volumes (careful - deletes data):
docker-compose down -v
```

## Troubleshooting

### ❌ "Connection refused" when running backend
**Solution:** Make sure PostgreSQL is running:
```bash
docker-compose ps
docker-compose up -d
```

### ❌ "ANTHROPIC_API_KEY not set"
**Solution:** Add your key to `.env`:
```bash
echo "ANTHROPIC_API_KEY=sk-ant-..." >> .env
```

### ❌ "Port 5432 already in use"
**Solution:** Stop existing PostgreSQL or change port in `.env`:
```bash
DB_PORT=5433
```

### ❌ "Authorization header missing"
**Solution:** Always include auth header:
```bash
-H "Authorization: Bearer test-key-123"
```

### ❌ Database migration errors
**Solution:** Drop and recreate tables:
```bash
docker-compose down -v
docker-compose up -d
sleep 5
python personal-ai-os-backend/main.py
```

## Next Steps

1. **Create your own agent** in `personal-ai-os-backend/agent.py`:
   ```python
   config = AgentConfig(
       name="my-custom-agent",
       system_prompt="You are a specialized AI assistant for...",
       tools=["filesystem.read", "terminal.run"],
       memory_namespace="my-agent",
       model="claude-opus-4-8"
   )
   agent = Agent(config)
   ```

2. **Add custom tools** in `personal-ai-os-backend/tools/`:
   ```python
   from tool_registry import ToolRegistry
   
   def my_tool(input_param: str) -> dict:
       return {"success": True, "result": "..."}
   
   ToolRegistry.register("my_namespace.my_tool", my_tool, "...", {...})
   ```

3. **Build the frontend** (Phase 2): Create a Next.js UI for easier interaction

4. **Monitor costs**: Check `requests.estimated_cost` in the database

## API Reference

### POST /request
Execute a request with the AI

**Headers:**
- `Authorization: Bearer <API_KEY>`
- `Content-Type: application/json`

**Body:**
```json
{
  "project_id": "string",
  "user_input": "string"
}
```

**Response:**
```json
{
  "request_id": 1,
  "project_id": "string",
  "status": "completed|failed",
  "response": "string",
  "tokens_used": 123,
  "estimated_cost": 0.00123
}
```

### GET /history/{project_id}
Get all requests for a project

**Headers:**
- `Authorization: Bearer <API_KEY>`

**Response:**
```json
{
  "project_id": "string",
  "requests": [
    {
      "id": 1,
      "user_input": "...",
      "response": "...",
      "status": "completed",
      "created_at": "2025-01-15T10:30:00"
    }
  ]
}
```

### GET /health
Health check

**Response:**
```json
{
  "status": "healthy"
}
```

## Architecture

```
User Request (curl, frontend, etc)
        ↓
FastAPI (/request endpoint)
        ↓
Orchestrator (routes to agent, logs results)
        ↓
Agent (Claude API + Tool Use Loop)
        ↓
Tool Registry (github, filesystem, terminal, docs, email)
        ↓
PostgreSQL (stores requests, responses, decisions, logs)
```

## Performance Notes

- **First request:** ~2-3 seconds (includes model init)
- **Subsequent requests:** ~1-2 seconds
- **Token limit:** Claude 3.5 Sonnet has 8K input context (handles most requests)
- **Timeout:** Commands timeout after 30 seconds by default

## Security Notes

⚠️ **Development Only** - Don't use in production yet:
- API key is hardcoded in .env
- No rate limiting
- No request signing
- No audit logging

Phase 2 will add:
- Proper authentication (JWT tokens)
- Rate limiting per project
- Cost gating ($10/day, $50/month limits)
- Detailed audit logs
- HTTPS-only endpoints

## Getting Help

1. Check logs in the backend terminal
2. Read `personal-ai-os-backend/README.md` for detailed docs
3. Review `PERSONAL_AI_OS_PHASE1.md` for architecture details
4. Check tool documentation in `personal-ai-os-backend/tools/`

## What's Next?

- **Phase 2:** React/Next.js UI, advanced cost tracking
- **Phase 3:** Memory & context management across sessions
- **Phase 4:** Multi-agent coordination
- **Phase 5:** Custom agent templates
- **Phase 6+:** MCPO agents (Marketing, Customer Success, Product, Operations)

---

**Ready?** Run `python personal-ai-os-backend/main.py` and make your first request! 🚀
