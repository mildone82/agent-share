# Agent Context Exchange Protocol

## Overview

This repo is the fleet task board for Mildone's agents and still the git push/pull channel between machines. Two Hermes agents can exchange a context file. A larger crew can leave a plan, claim it from `.acp/buffer/`, and attach evidence before anyone calls it done.

**ACP** here is the **Agent Collaboration Protocol** (also described as the Agent Context Exchange Protocol): Markdown plus YAML frontmatter, shared through git. It is not the Zed Agent Client Protocol. CI is `acp-collab-lint` so the name does not collide with Zed or with PyPI `acplint`.

Roles: `.acp/crew/ROSTER.md`. Guardrails: `docs/guardrails/README.md`.

| Role | Seat |
|------|------|
| Lauran | Intel |
| Mildone | Coordinator |
| Anita | Protocol and evidence |
| Juha | Architecture guardrails and lint |
| Linus | Engineer |
| Human | Merge only |

The implementer is the buffer card's `role_owner`. One owner executes. `reviewers` do not.

## How a task moves

```
plan  →  buffer (queued → claimed → in_progress)
              │
              ▼
         status + evidence
              │
              ▼
         awaiting_verify → complete → Human merge
```

Plan before code. Anita signs protocol and evidence. Juha signs machine rules. Agents do not merge.

Halt, and do not mark `complete`, when:

- Engineer and Verifier disagree
- a required gate is blocked or timed out
- `ACP-EVID-001` would fail because the evidence file is missing or has no `command` / `expect`

## Frontmatter

```yaml
---
agent: <agent-name>
timestamp: 2026-10-21T10:00:00+08:00
task_id: <id-shared-across-plan-status-deliverable>
status: planned
source: <where-this-originated>
target: <optional-recipient>
---
```

`timestamp` is ISO-8601 with a timezone offset. `status` depends on the directory.

| Directory | Allowed `status` |
|-----------|------------------|
| `.acp/plan/`, `.acp/status/`, `.acp/deliverables/` | `planned`, `in_progress`, `blocked`, `complete`, `verified` |
| `.acp/buffer/` | `queued`, `claimed`, `in_progress`, `blocked`, `awaiting_verify`, `complete`, `archived` |

Older context files used `pending` and `completed`. Those values warn on legacy files. New plan, status, deliverable, and buffer files fail.

Buffer cards also require `mission_id`, `role_owner`, `plan_path`, and `evidence_path` (`.acp/schemas/mission.schema.json`).

## Directory roles

| Directory | Purpose |
|-----------|---------|
| `contexts/` | Cross-machine context files |
| `.acp/plan/` | Plans. Required sections are motive, out of scope, acceptance, playbook, and distinct Engineer / Verifier |
| `.acp/buffer/` | Claim queue |
| `.acp/status/` | Execution status and the evidence link |
| `.acp/deliverables/` | Final outputs |
| `.acp/evidence/` | `command`, `expect`, `artifact_path`, `last_run` |
| `.acp/crew/` | Roster |
| `.acp/schemas/` | Machine-readable card schema |
| `.acp/logs/` | Traces |
| `archives/` | Dispositioned tasks, still carrying `task_id` |
| `docs/guardrails/` | Rule ids and path boundaries |

## Push / pull

1. `git pull` before editing.
2. One file per context unit.
3. Prefix commit subjects with `[Agent: <name>]` (or `[Planner]`, `[Implementer]`, `[Delivery]`, `[Juha]`).
4. Run `python scripts/acp-lint/lint.py --self-test` before pushing a board change.

## Lint

```bash
python scripts/acp-lint/lint.py --self-test
python scripts/acp-lint/lint.py --base origin/main --mode ci
```

Workflow: `.github/workflows/acp-collab-lint.yml`.

New files fail. Legacy files warn. New diff lines with an Account id or an IAM ARN fail. Bucket-shaped values warn. Details and the known historical exceptions are in `docs/guardrails/KNOWN_DEBT.md`.

## Other repos

This mission does not change product code.

| Repo | What this board does | What it does not do |
|------|----------------------|---------------------|
| `mildone82/agenticworld` | Tracks `.acp/plan/2026-10-21-agenticworld-verification-skill.md`. Evidence for that work can be linked from `.acp/evidence/`. | No product edits, no AWS resources, no secrets. Implementation stays on that repo's `bootstrap` branch. |
| `mildone-fleet` (future) | Copy the idea in `docs/guardrails/boundaries.yaml` (path allowlist plus "wrong write fails"). | Do not copy this repo's plan/status/deliverable layout into the engineering repo. |

### Field map (documentation only)

Hard alignment of `acp_deliverable` is a later mission. Names here are a bridge, not a schema lock.

| agent-share | Later agenticworld concept |
|-------------|----------------------------|
| `.acp/deliverables/` | `acp_deliverable` record |
| `.acp/evidence/` | verify-skill evidence (`command`, `expect`, `result`) |
| `status: complete` or `verified` | Refused unless `evidence_path` exists |
| `blocked` | Blocked gate, including missing cloud credentials when a deploy check is required |

`SKIP` versus `BLOCKED` for the agenticworld verification skill is defined in that plan. Do not treat a skipped deploy check as a pass when the diff touches deploy files.
