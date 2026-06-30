# 🤖 AUTO MODE - Autonomous Task Execution

## What is Auto Mode?

**Auto Mode** makes the JICO system fully autonomous. Instead of executing tasks immediately when you send a message, tasks are:

1. **Queued** automatically
2. **Executed in the background** with up to 5 concurrent workers
3. **Monitored** for completion or failures
4. **Results posted** to Discord automatically

## How It Works

```
Discord Message
    ↓
[Compress to JSON task]
    ↓
[Queue to Auto Mode]
    ↓ (runs in background)
[Execute when worker available]
    ↓
[Monitor execution]
    ↓
[Post results to Discord]
```

## Key Features

### ✅ Autonomous Execution
- Runs 24/7 without manual intervention
- Continuously checks for pending tasks
- Executes up to 5 tasks concurrently
- Monitors task completion/failures

### ✅ Task Queue Management
- Pending tasks stored in queue
- Execute FIFO (First In, First Out)
- Max 5 concurrent executions
- Tracks execution history

### ✅ Smart Task Monitoring
- Tracks execution time
- Timeout protection (30 minutes per task)
- Error handling & recovery
- Status reporting

### ✅ Discord Integration
- Queued confirmation (`📋` reaction)
- Status updates in #logs
- Results in #reports
- Task history available

## Commands

### Start Auto Mode
```
!auto_mode start
```
Starts the autonomous execution engine. Tasks sent via Discord will be queued and executed continuously.

### Stop Auto Mode
```
!auto_mode stop
```
Stops the system completely. No new tasks will be accepted.

### Pause/Resume
```
!auto_mode pause
!auto_mode resume
```
Pause accepts no new tasks (executing tasks finish). Resume restarts accepting new tasks.

### View Status
```
!auto_mode status
```
Shows:
- Enabled/disabled state
- Pending tasks count
- Currently executing tasks
- Recently completed tasks

### View History
```
!auto_mode history
```
Shows last 10 completed tasks with status and details.

## Task Lifecycle

```
1. USER SENDS MESSAGE
   "Build nacpac homepage"
   ↓
2. COMPRESS
   task = {
     "task_type": "nacpac",
     "action": "Build homepage",
     "target": "build"
   }
   ↓
3. QUEUE TO AUTO MODE
   Status: pending
   Reaction: 📋
   Discord: "Task queued: nacpac_1719755400.123"
   ↓
4. WAIT FOR WORKER AVAILABLE
   (Up to 5 concurrent executions)
   ↓
5. EXECUTE
   Status: executing
   Reaction: ⚙️
   Worker: build
   ↓
6. COMPLETE/FAIL
   Status: completed or failed
   Time: ~5-30 minutes (depends on task)
   ↓
7. POST RESULT
   Channel: #reports (success) or #logs (error)
   Message: Auto-decompressed readable summary
```

## Status States

| State | Meaning | Action |
|-------|---------|--------|
| `pending` | In queue, waiting for worker | Wait |
| `executing` | Running on a worker | Monitor |
| `completed` | Finished successfully | Posted result |
| `failed` | Error during execution | Posted error |
| `timeout` | Exceeded 30 minute limit | Posted timeout error |

## Concurrent Execution

Auto Mode can run **up to 5 tasks simultaneously**:

```
Available Workers: 5

Task 1: 🔄 Executing (dev worker)
Task 2: 🔄 Executing (seo worker)
Task 3: 🔄 Executing (ads worker)
Task 4: 🔄 Executing (build worker)
Task 5: 📋 Queued (waiting for worker)
Task 6: 📋 Queued (waiting for worker)
Task 7: 📋 Queued (waiting for worker)

When Task 1 completes → Task 5 starts executing
When Task 2 completes → Task 6 starts executing
...and so on
```

## Example Workflow

**You send:**
```
build nacpac homepage with hero section
```

**System responds immediately:**
```
📋 Task queued: nacpac_1719755400.123
Auto mode will execute when a worker is available
```

**System executes in background:**
```
[Auto mode picks up task]
[Routes to Nacpac Manager]
[Assigns to build worker]
[Worker executes]
[Posts to #reports]
```

**After execution (posted to Discord):**
```
✅ Task Completed
Type: nacpac
Action: build nacpac homepage with hero section
Worker: build

Successfully created homepage with hero section. 
Deployed to R2. Ready for preview.
```

## Scheduling Integration

Auto Mode also handles **scheduled tasks**:

```
User: "Tomorrow at 10am: run SEO optimization"
    ↓
Task scheduled for tomorrow 10am
    ↓
Auto Mode checks every 5 seconds
    ↓
When time arrives: Task moved to pending queue
    ↓
Executed like normal task
    ↓
Result posted to Discord
```

## Fault Tolerance

### Task Failures
- Caught and logged
- Error posted to #logs channel
- System continues accepting new tasks

### Timeout Protection
- Tasks limited to 30 minutes max
- Auto-marked as failed if exceeded
- Worker freed for next task

### Connection Loss
- Auto mode continues running
- Tasks queued while offline
- Executed when connection restored
- No data loss

## Performance Tuning

In `auto_mode.py`:

```python
self.check_interval = 5        # Check for tasks every 5 seconds
self.max_concurrent = 5        # Max concurrent executions
```

Adjust for your needs:
- Lower `check_interval` = faster response (uses more CPU)
- Higher `max_concurrent` = more parallel execution (uses more memory)

## Monitoring

### View Current Status
```
!auto_mode status
```

### View Task History
```
!auto_mode history
```

### Monitor Logs
```
tail -f /tmp/jico-system.log | grep "AUTO"
```

### Real-time Monitoring
Tasks auto-post results to Discord as they complete, so you always see latest status.

## Use Cases

### 24/7 Continuous Operation
- Start auto mode once
- System runs continuously
- Send messages anytime
- All tasks queued and executed

### Batch Processing
- Queue 100 tasks
- Auto mode processes all
- Track progress with status command

### Schedule-based Automation
- "Tomorrow at 10am: optimize SEO"
- "Every day at 9pm: generate reports"
- System executes automatically

### Hands-off Operation
- No manual intervention needed
- Discord-based monitoring only
- Full automation for your team

## Status Indicators

### Discord Reactions
- `📋` = Task queued
- `⚙️` = Task executing
- `✅` = Task completed
- `❌` = Task failed

### Discord Posts
- **#logs** = Scheduled tasks, errors, system events
- **#reports** = Task results, summaries

## Starting Auto Mode

The system **auto-starts** Auto Mode when the bot connects:

```python
# On Discord bot connection:
Auto Mode automatically starts
System is ready to accept tasks
```

Or manually:
```
!auto_mode start
```

## Stopping Auto Mode

To stop gracefully:
```
!auto_mode stop
```

Executing tasks finish before stopping.

---

## 🚀 Your System is Now Truly Autonomous!

With Auto Mode enabled, the JICO system is a complete **autonomous agent orchestration platform**:

- ✅ Takes natural language input
- ✅ Compresses to optimized tasks
- ✅ Routes to appropriate managers
- ✅ Executes with specialized workers
- ✅ Stores results in Cloudflare R2
- ✅ Reports back to Discord
- ✅ Schedules future tasks
- ✅ Monitors everything automatically

**No manual intervention needed. Just send messages and let auto mode handle the rest!** 🤖
