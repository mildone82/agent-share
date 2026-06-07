# 🧠 Agent Context Exchange Protocol

## Overview

This repo enables **two Hermes Agent instances** (on different machines) to share working context via git push/pull.

## How It Works

```
Machine A (Mac mini)                    Machine B (MacBook)
     │                                       │
     ├── Write context file                  │
     ├── git add + commit + push             │
     │                                       ├── git pull
     │                                       ├── Read context file
     │                                       ├── Execute task
     │                                       ├── git add + commit + push
     ├── git pull ◄──────────────────────────┤
     ├── Read result                         │
```

## Context File Format

Each context file in `contexts/` follows this convention:

```yaml
---
agent: <agent-name>              # e.g. hermes-mac-mini, hermes-macbook
timestamp: <ISO-8601>            # 2026-06-07T08:00:00+08:00
task_id: <uuid-or-name>          # unique task identifier
status: pending|in_progress|completed|blocked
source: <machine-hostname>       # where this context originated
target: <target-agent>           # optional: intended recipient
---
```

## Directory Roles

| Directory | Purpose |
|-----------|---------|
| `contexts/` | Shared context files — tasks, state, messages between agents |
| `.acp/plan/` | Task plans created by Planner agent |
| `.acp/status/` | Execution status updates |
| `.acp/logs/` | Execution logs and traces |
| `archives/` | Completed tasks moved here |

## Push/Pull Discipline

1. **Always `git pull` before starting work** — avoid conflicts
2. **One file per context unit** — keeps diffs clean
3. **Use `--allow-unrelated-histories` if needed** for first-time merge between two machines
4. **Prefix commit messages** with `[Agent: <name>]` for clear attribution
