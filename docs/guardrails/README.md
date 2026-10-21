# Guardrails

Machine checks for the agent-share board. ACP in this repo means **Agent Collaboration Protocol** (context exchange over git). It is not the Zed Agent Client Protocol and not the PyPI `acplint` package. The workflow and script are named `acp-collab-lint` so those projects are not confused.

Human merge only. Agents stop at `awaiting_verify`.

## What is enforced

| Check | Rule | New files | Files already on `main` |
|-------|------|-----------|-------------------------|
| Frontmatter and status vocabulary | `ACP-FM-001` | fail | warn |
| `YYYY-MM-DD-...` names | `ACP-NAME-001` | fail | warn |
| Plan sections and Engineer ≠ Verifier | `ACP-PLAN-001` | fail | warn |
| `complete` / `verified` need evidence | `ACP-EVID-001` | fail | warn |
| Stale S3 plan disposition | `ACP-DISP-001` | fail | warn |
| Buffer card schema | `ACP-BUF-001` | fail | warn |
| `task_id` has a plan or archive | `ACP-XREF-001` | fail | warn |
| Account id or IAM ARN in a new diff line | `ACP-SEC-001` | fail | fail on new lines |
| Bucket-shaped values in a new diff line | `ACP-SEC-001` | warn | warn on new lines |
| Denied paths (`.env`, keys, `*secret*` filenames) | `ACP-PATH-001` | fail | fail |
| Commit subject prefix | `ACP-COMMIT-001` | fail | — |
| Role path allowlist | `ACP-PATH-001` | fail when `--role` is set | — |

Status vocabulary depends on the directory:

- `.acp/plan/`, `.acp/status/`, `.acp/deliverables/`: `planned`, `in_progress`, `blocked`, `complete`, `verified`
- `.acp/buffer/`: `queued`, `claimed`, `in_progress`, `blocked`, `awaiting_verify`, `complete`, `archived`

Emoji labels in prose (`🟡 PLANNED` and the rest) are display aliases. CI reads frontmatter only.

## Run

```bash
python scripts/acp-lint/lint.py --self-test
python scripts/acp-lint/lint.py --base origin/main --mode ci
python scripts/acp-lint/lint.py --base origin/main --role implementer
```

`--self-test` builds a throwaway tree, proves a clean fixture exits 0, and proves planted defects are caught (bad status, bad filename, missing evidence, missing plan section, Account/IAM ARN, missing S3 disposition, and a role writing outside `boundaries.yaml`).

CI workflow: `.github/workflows/acp-collab-lint.yml` (not `guardrails.yml`).

## Layout

| File | Purpose |
|------|---------|
| `RULES.md` | Rule ids and what each one checks |
| `boundaries.yaml` | Role to path allow / deny |
| `KNOWN_DEBT.md` | Historical drift that still warns |
| `../../scripts/acp-lint/lint.py` | The checker |
| `../../.pre-commit-config.yaml` | Local hooks, including this lint |

Role boundaries are opt-in via `--role` until commits are single-purpose. This landing PR touches planner paths and guardrail paths together; the self-test still shows a non-Juha edit of `README.md` failing when the role is `implementer`.

## Halt

- Engineer and Verifier disagree: stop. Do not mark `complete`.
- A required gate is blocked or timed out: stop.
- Evidence file missing while status is `complete` or `verified`: the lint fails.
- No agent merges its own pull request.
