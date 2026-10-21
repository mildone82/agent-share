# Buffer queue

One mission per file. Filename: `YYYY-MM-DD-<slug>.md`.

`role_owner` is the single executor. `reviewers` may list more people; they do not take execution.

## Status

```
{queued,claimed,in_progress,blocked,awaiting_verify,complete,archived}
```

| Status | Meaning |
|--------|---------|
| `queued` | Waiting for an owner to claim it |
| `claimed` | Owner accepted, work not started |
| `in_progress` | Owner is doing the work |
| `blocked` | Stopped on a person, decision, or missing input |
| `awaiting_verify` | Ready for a verifier who is not the owner |
| `complete` | Verifier accepted. Requires an evidence file |
| `archived` | Closed and kept for history |

## Card frontmatter

Required: `mission_id`, `role_owner`, `status`, `plan_path`, `evidence_path`, plus the shared ACP keys `agent`, `timestamp`, `task_id`, `source`.

Validate cards with `.acp/schemas/mission.schema.json`. Plan, status, and deliverable files use a different status vocabulary (`planned`, `in_progress`, `blocked`, `complete`, `verified`).
