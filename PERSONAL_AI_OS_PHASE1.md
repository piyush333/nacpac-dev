# Personal AI Operating System - Phase 1

## Project Overview

This is a complete architectural pivot from the multi-agent NacPac/Jico system to a **single-user AI executive assistant** (Personal AI OS).

**Key Difference:** Instead of managing multiple brands with separate agents, this system is designed for one user to delegate tasks to a personal AI that acts as an executive assistant.

## Phase 1 Implementation Status

### ✓ Completed

1. **Backend Foundation** (`personal-ai-os-backend/`)
   - FastAPI application with two endpoints (/request, /health, /history)
   - PostgreSQL database schema (projects, requests, tasks, decisions, logs)
   - Generic Agent Engine (configurable by AgentConfig)
   - Tool Registry pattern (self-registering tools)
   - 5 core tools implemented:
     - github (clone, commit_and_push)
     - filesystem (read, write, list)
     - terminal (run with safety checks)
     - documentation (read markdown, summarize dirs)
     - email (send with mock mode)

2. **Infrastructure**
   - `docker-compose.yml` for PostgreSQL
   - `.env.example` with all required variables
   - `requirements.txt` with dependencies
   - Unit tests for tools (`backend/tests/test_tools.py`)

3. **Architecture**
   - **Orchestrator**: Routes requests to agents, manages execution
   - **Agent Engine**: Takes config, executes with Claude API + tool use
   - **Tool Registry**: Centralized tool management and registration
   - **Database**: Persistent storage of requests, responses, costs
   - **Safety**: Dangerous commands blocked in terminal tool

### ⚠ Current Limitations (Phase 2+)

- No frontend yet (Phase 2)
- No memory/context persistence across sessions (Phase 3)
- Single agent only (Developer Agent)
- No advanced cost gating (Phase 2)
- No MCPO agents yet (Phase 2+)

## Quick Start

### Setup

```bash
# Install dependencies
pip install -r personal-ai-os-backend/requirements.txt

# Start PostgreSQL
docker-compose up -d

# Set up environment
cp .env.example .env
# Edit .env and add ANTHROPIC_API_KEY=sk-ant-...
```

### Run Backend

```bash
cd personal-ai-os-backend
python main.py
# Server on http://localhost:8000
```

### Test with curl

```bash
curl -X POST http://localhost:8000/request \
  -H "Authorization: Bearer test-key-123" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "my-project",
    "user_input": "Read the file personal-ai-os-backend/README.md"
  }'
```

## Database Schema

```sql
projects
  - id, name, description, created_at, updated_at

requests
  - id, project_id, user_input, response, status, tokens_used, estimated_cost, created_at, completed_at

tasks
  - id, request_id, title, description, status, created_at

decisions
  - id, request_id, decision, reasoning, created_at

logs
  - id, request_id, level, message, data (JSONB), created_at
```

## File Structure

```
personal-ai-os-backend/
├── main.py              # FastAPI application
├── db.py                # Database schema
├── orchestrator.py       # Request routing
├── agent.py             # Agent engine (generic, configurable)
├── tool_registry.py     # Tool registration system
├── tools/
│   ├── __init__.py
│   ├── github.py        # GitHub tools
│   ├── filesystem.py    # File operations
│   ├── terminal.py      # Shell commands (with safety)
│   ├── documentation.py # Markdown reader
│   └── email.py         # Email sending
├── tests/
│   ├── __init__.py
│   └── test_tools.py    # Unit tests
└── requirements.txt     # Python dependencies

docker-compose.yml      # PostgreSQL service definition
.env.example            # Environment template
PERSONAL_AI_OS_PHASE1.md # This file
```

## API Endpoints

### POST /request
Execute a request

**Request:**
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
  "project_id": "my-project",
  "status": "completed",
  "response": "...",
  "tokens_used": 1234,
  "estimated_cost": 0.025
}
```

### GET /history/{project_id}
Get request history

### GET /health
Health check

## Debugging

### Database connection error
```bash
# Make sure PostgreSQL is running
docker-compose ps
docker-compose logs postgres
```

### Tool not found error
Make sure all tool modules are imported in `agent.py` before creating agents.

### Token limit issues
Claude 3.5 Sonnet has 8K input and 16K output context limits. Truncate large responses in tools.

## Cost Tracking

Estimated costs based on Claude 3.5 Sonnet pricing:
- Input: $3 per 1M tokens
- Output: $15 per 1M tokens

All costs tracked in `requests.estimated_cost` column.

## Next Phases

- **Phase 2**: Next.js frontend UI + advanced cost gating
- **Phase 3**: Memory system & context management
- **Phase 4**: Multi-agent coordination
- **Phase 5**: Custom agent templates
- **Phase 6+**: MCPO agents (Marketing, Customer Success, Product, Operations)

## Key Design Decisions

1. **Native Anthropic SDK** (not LangChain): Direct tool-use loop for control
2. **Tool Registry pattern**: Self-registering tools for modularity
3. **Generic Agent class**: Configurable, not hardcoded agent types
4. **PostgreSQL**: Structured data for observability
5. **Deterministic tools**: Functions with clear inputs/outputs, no abstractions

## Troubleshooting

See `personal-ai-os-backend/README.md` for detailed troubleshooting guide.
