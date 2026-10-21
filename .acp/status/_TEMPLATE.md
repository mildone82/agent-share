---
agent: implementer
timestamp: 2026-10-21T10:00:00+08:00
task_id: template-plan-001
status: in_progress
source: agent-share
target: verifier
plan_path: .acp/plan/_TEMPLATE.md
evidence_path: .acp/evidence/YYYY-MM-DD-task-name.md
---

# Status: task name

- **Status**: 🔵 IN_PROGRESS
- **Plan**: `.acp/plan/YYYY-MM-DD-task-name.md`
- **Evidence**: `.acp/evidence/YYYY-MM-DD-task-name.md`

Frontmatter `status` uses the machine vocabulary. Emoji labels above are display aliases only.

Do not set `complete` or `verified` until `evidence_path` exists and includes `command`, `expect`, `artifact_path`, and `last_run`.
