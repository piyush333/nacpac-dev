# Discord Manager Architecture - Channel-Based Routing

## Overview

The JICO system uses Discord as the interface. The **Manager** intelligently routes tasks based on user input in **#general**, while specialized channels handle bot-to-bot communication and logging.

## Channel Roles

### 🗣️ #general - User Interaction
**Purpose:** Where you talk to the Manager

```
You: "Add dark mode to the mobile app"
Manager: "📱 NACPAC task queued. Updates → #nacpac-dev"
```

**Flow:**
1. You type a natural language message
2. Manager reads the message
3. Manager detects brand from keywords (Nacpac vs Jico)
4. Manager compresses message to task JSON
5. Manager queues task to Auto Mode
6. Manager posts confirmation in #general

### 📱 #nacpac-dev - Nacpac Development
**Purpose:** Nacpac task updates and worker communication

**What appears here:**
- Task started: `📋 Task {id} started - Action: ...`
- Build progress: `Building APK... ETA 10-20 min`
- Build complete: `✅ Task {id} success - APK: [URL] EXE: [URL]`
- Errors: `❌ Task {id} error - Error: ...`

**Audience:** Internal bot-to-bot communication (you don't need to monitor this)

### 🎨 #jico-dev - Jico Development
**Purpose:** Jico task updates and AR worker communication

**What appears here:**
- AR model updates
- Shopify integration tasks
- Netlify deployment status
- 3D asset processing

**Audience:** Internal bot-to-bot communication (you don't need to monitor this)

### 📋 #logs - Worker Output
**Purpose:** Raw worker output, errors, and debugging

**What appears here:**
- Compilation errors
- Git errors
- Build failures
- Command output for debugging

**Audience:** If something goes wrong, check here for details

### 📊 #reports - Scheduled Reports
**Purpose:** Periodic reports and analytics

**What appears here:**
- Build reports (APK/EXE versions, sizes, timing)
- SEO analysis results
- Ad campaign metrics
- Task statistics

**Audience:** For monitoring trends and performance

## How the Manager Works

### 1. Brand Detection
When you send a message in #general, the Manager detects which brand it's for:

**Nacpac Keywords:**
- mobile, desktop, APK, EXE, expo, electron
- home screen, UI, button, build, sticker, wallpaper
- react native, typescript, firebase, screen, feature

**Jico Keywords:**
- AR, panel, Shopify, 3D, model, asset, Netlify
- GLB, wall, render, variant, color, acoustic

**Example:**
```
You: "Add a logout button"
Manager thinks: "Contains 'button', 'logout'... probably Nacpac"
Tasks routed to: Nacpac Manager
```

### 2. Natural Language Compression
Once brand is detected, the message is compressed into structured JSON:

```json
{
  "task_type": "nacpac",
  "action": "Add a logout button to the home screen",
  "target": "dev",
  "parameters": {},
  "priority": "normal",
  "schedule_time": null
}
```

### 3. Task Routing
The task is routed to the appropriate manager:
- **Nacpac:** Code changes → builds → upload
- **Jico:** AR/3D content management
- **Scheduler:** If time-based, stored for future execution

### 4. Background Execution
Auto Mode executes the task in the background (up to 5 concurrent):
- Dev worker: generates code, makes changes
- Build worker: compiles APK/EXE, uploads to R2
- Other workers: SEO, ads, content management

### 5. Results Posting
When the task completes, results are posted to the appropriate channel:
- Task success → **#nacpac-dev** or **#jico-dev**
- Build URL → Shown in the dev channel
- Errors → **#logs**
- Reports → **#reports** (periodic)

## Workflow Examples

### Example 1: Code Change → Build → Upload

```
#general
You: "Add dark mode toggle to home screen"

Manager (internal routing)
1. Detects: Nacpac (keywords: home screen, UI)
2. Creates task: type=nacpac, target=dev, action="Add dark mode..."
3. Queues to Auto Mode

#general
Manager responds: "📱 NACPAC task queued. Updates → #nacpac-dev"

Auto Mode executes in background:
- Dev worker: Runs Claude against codebase
- Modifies: mobile/app/index.tsx
- Git push: commits changes to GitHub

#nacpac-dev
Manager posts: "📋 Task started - Adding dark mode toggle"
Manager posts: "⚙️ Building APK..."
Manager posts: "✅ APK ready: [EAS URL]"
Manager posts: "✅ EXE ready: [R2 URL]"

#general
You see the notification and get the links from #nacpac-dev
```

### Example 2: Scheduled Build

```
#general
You: "Schedule a build for tomorrow at 10am"

Manager (internal)
1. Detects: Nacpac (keyword: build)
2. Creates task: type=nacpac, target=build, schedule_time="2026-07-01T10:00:00Z"
3. Stores in scheduler

#general
Manager: "📅 Build scheduled for tomorrow at 10am. ID: task_123"

Next day at 10am:
- Scheduler wakes up task
- Auto Mode executes build
- Results posted to #nacpac-dev

#general
You don't see anything until you check the scheduler or #nacpac-dev
```

### Example 3: Jico AR Task

```
#general
You: "Update the panel colors for summer collection"

Manager
1. Detects: Jico (keywords: panel, colors)
2. Routes to: Jico Manager
3. Posts: "🎨 JICO task queued. Updates → #jico-dev"

#jico-dev
Internal: "Processing AR asset updates..."
Internal: "Uploading to Netlify..."
Internal: "✅ Assets deployed"

#general
You see the ack, check #jico-dev later for results
```

## Command Reference

### In #general (can use anywhere)

```
!status                 - Show system health
!help_jico              - Show this architecture
!auto_mode status       - Show pending tasks
!auto_mode history      - Show recent completions
!auto_mode pause        - Stop accepting new tasks
!auto_mode resume       - Resume task acceptance
```

### Workflow

You never send commands to #nacpac-dev, #jico-dev, #logs, or #reports.

**Your workflow:**
1. Type in #general
2. Manager routes
3. Check #nacpac-dev or #jico-dev for results (if you want)
4. Or just wait for the confirmation emoji in #general

## Channel Setup

To use this system, create these Discord channels:

```
#general              (already exists)
#nacpac-dev           (new - for Nacpac worker updates)
#jico-dev             (new - for Jico worker updates)
#logs                 (new - for error logs)
#reports              (new - for periodic reports)
```

Give the bot permissions:
- Read messages
- Write messages
- Add reactions

## Key Principles

1. **#general is where you talk** - Natural language, any task
2. **Manager decides the brand** - Based on keywords
3. **Worker channels are internal** - Bot-to-bot communication
4. **You stay in #general** - Everything important comes back there
5. **No manual routing needed** - Manager figures it out

## Ambiguous Input

If the Manager can't decide (equal keywords for both brands):

```
You: "Update the system"

Manager: "Is this for Nacpac (mobile/desktop) or Jico (AR/Shopify)?"

You: "Nacpac mobile app"

Manager: "📱 NACPAC task queued..."
```

To avoid this, include a brand hint:
- "In the mobile app..." → Nacpac
- "For the AR experience..." → Jico
- "Build the APK" → Nacpac
- "Update the panel model" → Jico

## Advantages of This Architecture

| Benefit | How It Works |
|---------|--------------|
| **Simple UX** | Type in #general, let Manager route |
| **Clean logs** | Worker output stays in dedicated channels |
| **Bot talk** | Internal communication (#nacpac-dev, #jico-dev) isolated |
| **No noise** | You only see task confirmations in #general |
| **Scalable** | Easy to add more managers/workers |
| **Debuggable** | Errors go to #logs, sorted by worker |

## Troubleshooting

### Message not processed?
- Check you're in #general
- Check the bot has permissions
- Check you're the authorized user (Config.ALLOWED_USER_ID)

### Task went to wrong channel?
- Check the brand keywords in your message
- Be explicit: "In Nacpac mobile app..." or "For Jico AR..."

### Where are my results?
- Check #nacpac-dev or #jico-dev for that task type
- Check #logs if there was an error
- Check #reports for periodic summaries

### How do I see what's running?
- `!auto_mode status` - Shows pending and executing
- `!auto_mode history` - Shows recent completions
- Check #nacpac-dev for in-flight Nacpac tasks
- Check #jico-dev for in-flight Jico tasks

---

**This is the primary interface. Everything else (config, logging, deployment) supports this Discord workflow.**
