# Rule catalog

Repeated review comments become a rule id here and a check in `scripts/acp-lint/`. An exception belongs in the PR body as `Guardrail-Exception: <rule-id> — <reason>` and still needs a Human review. Exceptions do not change the default allowlist.

| ID | Check |
|----|--------|
| `ACP-NAME-001` | New plan, buffer, and deliverable files match `YYYY-MM-DD-<slug>.md`. New status files match `YYYY-MM-DD-<slug>-progress.md`. Deliverables use the `-complete.md` suffix. Older undated `*-progress.md` names warn. `_TEMPLATE.md` and `README.md` are exempt. |
| `ACP-FM-001` | `agent`, `timestamp` (ISO-8601 with offset), `task_id`, `status`, and `source` are present. `status` must use that directory's vocabulary. |
| `ACP-XREF-001` | A status or deliverable `task_id` exists on a plan under `.acp/plan/` or `archives/`. |
| `ACP-SEC-001` | New diff lines fail on an IAM ARN, an Account field with a 12-digit id, a cloud access-key id, a private-key header, or a GitHub/Slack/bearer token. Bucket-shaped values (an `s3://` URL or a bucket assignment) warn. Messages do not echo the value. |
| `ACP-PATH-001` | Denied filenames and directories cannot be added (dotenv files, credential files, key material, `*secret*` filenames, virtualenvs, build output). `scripts/acp-lint/` is exempt from the filename pattern so the scanner can live there. With `--role`, paths must match `boundaries.yaml`. |
| `ACP-COMMIT-001` | Subjects on the branch start with `[Agent: name] `, `[Planner]`, `[Implementer]`, `[Delivery]`, `[Juha]`, `init:`, `docs:`, or `chore(guardrails):`. |
| `ACP-PLAN-001` | A new plan has a motive heading, an out-of-scope heading, an acceptance heading, a playbook (`playbook:` or a heading), and Suggested owners whose Engineer and Verifier are different agents. |
| `ACP-EVID-001` | `status` of `complete` or `verified` requires `evidence_path`. The file must exist and include `command`, `expect`, `artifact_path`, `last_run`, and an able-to-fail note. |
| `ACP-DISP-001` | `.acp/plan/2026-06-07-aws-s3-inventory-report.md` cannot stay pending with no disposition. Close it by moving it to `archives/` with `status: archived`, `disposition: archive`, and `disposition_reason`, or keep it and set `disposition: reopen` plus an owner. |
| `ACP-BUF-001` | Buffer cards match `.acp/schemas/mission.schema.json`: `mission_id`, `role_owner`, `status`, `plan_path`, `evidence_path`. `plan_path` must exist. |

`contexts/` keep the same frontmatter keys but stay warn-only so the original demo file does not block the board.
