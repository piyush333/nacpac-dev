# JICO System - Agent Orchestration Platform

Multi-agent system that takes natural language input from Discord, compresses it using Claude Haiku, routes tasks to specialized managers (Nacpac & Jico), and executes them with dedicated workers.

## Architecture

```
Discord (Natural Language)
    ↓
Discord Manager Bot
    ↓
Compression Layer (Haiku) → Optimized JSON Task
    ↓
Task Router
    ├─→ Nacpac Manager (dev, seo, ads, build workers)
    ├─→ Jico Manager (dev, seo, ads, build workers)
    └─→ Task Scheduler (Oracle VM cron)
    ↓
Results → Discord #logs/#reports + Telegram summary
```

## Components

### 1. Discord Manager (`discord_manager.py`)
- Main entry point listening to Discord messages
- Routes user input through the system
- Posts results to Discord channels

### 2. Compression Layer (`compression_layer.py`)
- Uses Claude Haiku to convert natural language → JSON tasks
- Decompresses results back to human-readable messages
- Minimizes token usage with Haiku

### 3. Task Router (`task_router.py`)
- Decides: execute now or schedule for later?
- Routes to appropriate manager (Nacpac, Jico, or Scheduler)

### 4. Nacpac Manager (`nacpac_manager.py`)
- Handles sticker printing & packaging tasks
- Workers: dev, seo, ads, build
- Integrates with Cloudflare R2 (nacpac-workspace bucket)

### 5. Jico Manager (`jico_manager.py`)
- Handles general agent orchestration tasks
- Workers: dev, seo, ads, build
- Integrates with Cloudflare R2 (jico-workspace bucket)

### 6. Utils (`utils.py`)
- R2Storage: Cloudflare R2 file operations
- OracleVMConnector: SSH to Oracle VM for remote execution
- TaskScheduler: Manage scheduled tasks

## Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your credentials

# Run the system
python main.py
```

## Configuration

Edit `.env` with:
- Discord token
- Anthropic API key
- Telegram bot token
- Cloudflare R2 credentials
- Oracle VM SSH details

## Usage

Send messages to Discord:
- "Build the nacpac homepage"
- "Schedule SEO optimization for tomorrow 10am"
- "Run dev tests on jico module"
- "Create Q3 ad campaign"

## System Status

```
!status    - Show system health
!help_jico - Show help commands
```

## Logging

Logs are written to `/tmp/jico-system.log` and stdout.

## Workers

Each manager has 4 worker types:
- **dev**: Development tasks (coding, testing, debugging)
- **seo**: SEO tasks (optimization, metadata, keywords)
- **ads**: Advertising tasks (campaigns, targeting, analytics)
- **build**: Build tasks (packaging, deployment, CI/CD)

## Scheduled Tasks

Tasks can be scheduled by including time references:
- "Tomorrow at 10am: ..."
- "Next week: ..."
- "Every day: ..."

Tasks are stored in memory or pushed to Oracle VM cron for persistence.
