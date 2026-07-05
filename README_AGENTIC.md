# Jico Agentic System

Multi-agent orchestration for Jico Org: Discord natural language → AI agents → build APK/EXE/AR → Discord.

## Quick Start (Local)

### 1. Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your credentials
```

### 2. Run locally

```bash
export BUILD_TEST_MODE=true
python -m agentic.main
```

### 3. Test with Discord

In #general: "Build the NacPac APK"

Bot will parse, ask for approval, execute, post results.

## Deploy to DigitalOcean

### Option 1: DigitalOcean App Platform (Recommended)

1. Go to DigitalOcean Apps
2. Create new app
3. Connect GitHub repo: piyush333/nacpac-dev
4. Branch: claude/agentic-system-org-j9gvae
5. Upload .do/app.yaml configuration
6. Set environment variables from .env.example
7. Deploy

Auto-deploys on each push to the branch.

### Option 2: GitHub Actions + doctl

Push to branch triggers workflow:
1. Installs dependencies
2. Runs linting
3. Calls doctl to trigger deployment

Requires GitHub secrets:
- DIGITALOCEAN_TOKEN (from DO)
- DO_APP_ID (from DO)

## Architecture

```
Discord message
   ↓
Orchestrator Agent (intent parsing)
   ↓
├─ NacPac Dev Agent (APK/EXE builds)
├─ Jico Life Dev Agent (AR builds)
└─ Cost gating, memory logging
   ↓
Memory (Supabase: tasks, costs, state)
   ↓
Discord notifications (#logs, #reports)
```

## Files

- `agentic/main.py` - Entry point, starts Discord bot
- `agentic/config.py` - Environment loading
- `agentic/discord_bot.py` - Discord listener + approval UI
- `agentic/agents/orchestrator.py` - Intent parsing + routing
- `agentic/agents/nacpac_dev.py` - NacPac build agent
- `agentic/agents/jico_life_dev.py` - Jico Life build agent
- `agentic/tools/` - Git, build, deploy, backup tools
- `agentic/memory.py` - Supabase client
- `agentic/cost_tracker.py` - Token usage + cost gating

## Cost Tracking

- Daily cap: $10 USD
- Monthly cap: $50 USD
- Every API call logged to Supabase
- Blocked if over budget

## Known Issues

1. npm install may hang on react-native dependency resolution
   - Solution: Use versions in package.json (0.74.1, 18.2.0)
2. EAS builds require EXPO_TOKEN env var or manual auth
3. Network policies in Claude Code environment block Expo API
   - Solution: Run on DigitalOcean or local servers

## Next Steps

- Phase 1 ✅: Dev agents + Orchestrator + Discord
- Phase 2: MCPO agents (Marketing, Customer Success, Product, Operations)
- Phase 3: Vector database for task history search
