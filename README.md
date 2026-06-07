# 🤖 Agent Share

Multi-agent context exchange hub — shared workspace for AI agent collaboration via GitHub.

## Purpose

This repository serves as a **centralized context exchange medium** for multiple AI agents (Claude Code, Codex, Hermes, etc.) working on shared tasks.

## Directory Structure

```
agent-share/
├── README.md           # This file
├── .acp/               # Agent Collaboration Protocol
│   ├── plan/           # Implementation plans from Planner agents
│   ├── status/         # Current execution status
│   ├── deliverables/   # Final outputs
│   └── logs/           # Execution logs and traces
├── contexts/           # Shared context files (JSON/Markdown)
├── snippets/           # Reusable code snippets
└── archives/           # Completed / archived tasks
```

## Agent Collaboration Protocol (ACP)

### Workflow

```
Planner Agent          Implementer Agent         Delivery Agent
     │                        │                        │
     ▼                        ▼                        ▼
  Create Plan            Read Plan               Read Status
  in .acp/plan/          Execute Tasks           Verify Output
     │                        │                        │
     ▼                        ▼                        ▼
  Push & Notify          Update Status           Archive Task
                       in .acp/status/         in .acp/deliverables/
```

### File Naming Convention

| Directory | Filename Pattern | Example |
|-----------|-----------------|---------|
| `plan/` | `YYYY-MM-DD-task-name.md` | `2026-06-07-aws-cost-analyzer.md` |
| `status/` | `YYYY-MM-DD-task-name-progress.md` | `2026-06-07-aws-cost-analyzer-progress.md` |
| `deliverables/` | `YYYY-MM-DD-task-name-complete.md` | `2026-06-07-aws-cost-analyzer-complete.md` |
| `logs/` | `YYYY-MM-DD-task-name-log.md` | `2026-06-07-aws-cost-analyzer-log.md` |

### Status Values

- `🟡 PLANNED` — Plan created, awaiting execution
- `🔵 IN_PROGRESS` — Implementation ongoing
- `🟠 BLOCKED` — Blocked, needs intervention
- `🟢 COMPLETE` — Finished, awaiting verification
- `✅ VERIFIED` — Verified and archived

## Quick Start

```bash
# Clone this repo
gh repo clone mildone82/agent-share

# Create a new task plan
cat > .acp/plan/2026-06-07-my-task.md << 'EOF'
# Task: My Task

## Objective
...

## Requirements
- [ ] Requirement 1
- [ ] Requirement 2

## Acceptance Criteria
...
EOF

# Commit and push
git add . && git commit -m "[Planner] Add my-task plan" && git push
```

## Rules

1. **One task per directory entry** — keep plans focused and atomic
2. **Update status promptly** — status files should reflect reality
3. **Clean up after completion** — move completed tasks to `archives/`
4. **Use Markdown** — all context files should be human and agent readable
5. **Link related PRs/Issues** — reference GitHub PRs and Issues in status files

---

*Managed by Hermes Agent for mildone82*
