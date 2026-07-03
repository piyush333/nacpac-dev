# Integration Checklist — Testing & Deployment Guide

Use this checklist when testing agents and MCP servers before deploying to production.

---

## Pre-Integration Testing (Local)

### Code Quality
- [ ] No syntax errors (`python -m py_compile agentic/agents/my_agent.py`)
- [ ] Passes linting if configured
- [ ] Docstrings added to all methods
- [ ] Type hints on method signatures
- [ ] Follows existing code style

### Functionality Testing
- [ ] Agent initializes without errors
- [ ] `get_current_state()` returns expected dict
- [ ] `execute()` routes to correct methods
- [ ] Each action returns dict with `status` key
- [ ] Error cases handled (return `status: "error"`)
- [ ] Logging works (check log output)

### CLI Testing
```bash
# Test agent existence
python cli.py list-agents | grep my_agent

# Test action execution
python cli.py build my_brand my_action

# Test with parameters
python cli.py build my_brand my_action "param1=value1"

# Check system status
python cli.py status
```

### Database Testing
- [ ] Agent can read from PostgreSQL (if needed)
- [ ] Agent can write to PostgreSQL (if needed)
- [ ] Database schema migrations applied
- [ ] No SQL errors in logs

---

## Integration Testing (Against Other Components)

### Orchestrator Integration
- [ ] Orchestrator can parse intent for this agent
- [ ] Orchestrator routes to correct agent name
- [ ] Agent receives task from orchestrator
- [ ] Agent returns result to orchestrator
- [ ] Result appears in task logging

### Registry Testing
```python
from registry import registry

# Check agent is registered
agent = registry.get_agent("my_agent")
assert agent is not None

# Check capabilities
caps = registry.get_capabilities("my_agent")
assert "my_action" in caps

# Find agent for action
agent_name = registry.find_agent_for_action("my_action")
assert agent_name == "my_agent"
```

### Cost Tracking
- [ ] Token counts logged correctly
- [ ] Cost calculation accurate
- [ ] Cost gate enforced ($10/day limit)
- [ ] Warnings at 80% of budget

### Queue Integration
```python
from queue import queue

# Push task
task_id = queue.push_task("my_agent", "my_action", {"param": "value"})
assert task_id != ""

# Pull task
task = queue.pull_task("my_agent")
assert task["action"] == "my_action"

# Push result
success = queue.push_result(task_id, "my_agent", {"status": "success"})
assert success
```

---

## Deployment Testing (Oracle VM)

### Pre-Deployment
- [ ] All code committed to `claude/agentic-system-org-j9gvae`
- [ ] All tests passing locally
- [ ] No uncommitted changes
- [ ] Branch is up-to-date with main

### Deployment Steps
```bash
# 1. Clone/pull latest code
ssh ubuntu@oracle_ip "cd /home/ubuntu/nacpac-dev && git pull"

# 2. Install/update dependencies
ssh ubuntu@oracle_ip "cd /home/ubuntu/nacpac-dev/agentic && pip install -r requirements.txt"

# 3. Restart service
ssh ubuntu@oracle_ip "sudo systemctl restart jico-agentic"

# 4. Check logs
ssh ubuntu@oracle_ip "sudo journalctl -u jico-agentic -n 50"
```

### Post-Deployment Verification
- [ ] Service is running: `sudo systemctl status jico-agentic`
- [ ] No errors in logs: `journalctl -u jico-agentic`
- [ ] Agent registered (check logs for "Registered agent")
- [ ] Can trigger via Discord command

---

## Production Validation

### Discord Bot Testing
```
Message in #general: "Build nacpac apk"
Expected:
  1. Bot parses intent
  2. Bot routes to correct agent
  3. Agent executes
  4. Bot posts result link
  5. Result logged to #logs channel
```

### Load Testing
- [ ] System handles 5 concurrent tasks
- [ ] Queue processes tasks in order
- [ ] Cost tracking works under load
- [ ] No memory leaks (check RAM usage)

### Error Scenarios
- [ ] Network error → graceful fallback
- [ ] Missing credentials → clear error message
- [ ] Invalid parameter → validation error
- [ ] Agent crash → automatic restart
- [ ] Database down → reconnect with backoff

---

## Monitoring Checklist

### Daily
- [ ] Check system status: `python cli.py status`
- [ ] Review error logs: `grep ERROR /tmp/jico-agentic.log`
- [ ] Check cost tracking: Daily spend < $10
- [ ] Verify agent availability

### Weekly
- [ ] Review task history (successful vs failed)
- [ ] Check database backup status
- [ ] Review agent metrics (tasks completed, avg time)
- [ ] Update MEMORY.md with notes

### Monthly
- [ ] Review total spend ($50 budget)
- [ ] Analyze agent performance trends
- [ ] Identify slow operations
- [ ] Plan optimizations

---

## Rollback Procedure

If something goes wrong:

```bash
# 1. Check latest commits
git log --oneline -5

# 2. Revert to last known good
git revert <commit_hash>
git push origin claude/agentic-system-org-j9gvae

# 3. Redeploy to Oracle
ssh ubuntu@oracle_ip "cd /home/ubuntu/nacpac-dev && git pull"
ssh ubuntu@oracle_ip "sudo systemctl restart jico-agentic"

# 4. Verify
ssh ubuntu@oracle_ip "sudo journalctl -u jico-agentic -n 20"
```

---

## Sign-Off

Agent/Feature: ________________  
Tester: ________________  
Date: ________________  

- [ ] All tests passing
- [ ] Documented in MEMORY.md
- [ ] Ready for production
- [ ] Approved by (user): ________________  

Signature: ________________  Date: ________________
