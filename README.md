# Agent Share

Multi-agent context exchange hub. Agents share plans, status, and evidence through git. Humans merge.

**ACP** in this repository means the **Agent Collaboration Protocol**: files under `.acp/` plus `contexts/`, exchanged with push and pull. It is not the Zed Agent Client Protocol and not the PyPI `acplint` package. The checker is `acp-collab-lint`.

## Crew

`.acp/crew/ROSTER.md` is authoritative. This table is the short form.

| Role | Person | Job |
|------|--------|-----|
| Intel | Lauran | Outer-loop notes that become plans |
| Coordinator | Mildone | Owners, priority, disposition |
| Protocol / evidence | Anita | Verification protocol and evidence sign-off |
| Guardrails | Juha | Directory boundaries, lint, CI |
| Engineer | Linus | Implementation under an owned card |
| Merge | Human | The only seat that merges to `main` |

The implementer seat is whoever owns the buffer card (Linus unless the card says otherwise). Engineer and Verifier are different agents. No self-merge. If they disagree, or a required gate is blocked or timed out, halt and do not mark the card `complete`.

Plan before code. Open a plan, then a buffer card, then status and evidence.

## Directory structure

```
agent-share/
├── README.md
├── docs/guardrails/          # boundaries, rule ids, known debt
├── scripts/acp-lint/         # acp-collab-lint
├── .github/workflows/acp-collab-lint.yml
├── .acp/
│   ├── plan/                 # plans (before code)
│   ├── buffer/               # claim queue, one mission per file
│   ├── status/               # execution status
│   ├── deliverables/         # final outputs
│   ├── evidence/             # command + expect records
│   ├── crew/                 # roster
│   ├── schemas/              # mission.schema.json
│   └── logs/                 # traces
├── contexts/                 # cross-machine context files
├── snippets/                 # reusable snippets
└── archives/                 # dispositioned tasks
```

## Workflow

```
Planner                         Implementer                    Verifier
   │                                 │                              │
   ▼                                 ▼                              ▼
.acp/plan/ + buffer card      claim → in_progress          awaiting_verify
   │                                 │                              │
   ▼                                 ▼                              ▼
push                          status + evidence             Human merges
```

1. Pull.
2. Write `.acp/plan/YYYY-MM-DD-task-name.md` using `.acp/plan/_TEMPLATE.md`.
3. Add `.acp/buffer/YYYY-MM-DD-task-name.md` with one `role_owner`.
4. Implementer sets the card to `claimed` or `in_progress` and updates `.acp/status/`.
5. Evidence goes in `.acp/evidence/`. `complete` and `verified` require it.
6. Verifier moves the card to `awaiting_verify` review, then `complete`.
7. A Human merges. Agents do not.

## File names

| Directory | Pattern | Example |
|-----------|---------|---------|
| `plan/` | `YYYY-MM-DD-task-name.md` | `2026-10-21-fleet-acp-guardrails.md` |
| `buffer/` | `YYYY-MM-DD-task-name.md` | `2026-10-21-fleet-acp-guardrails.md` |
| `status/` | `YYYY-MM-DD-task-name-progress.md` | `2026-10-21-fleet-acp-guardrails-progress.md` |
| `deliverables/` | `YYYY-MM-DD-task-name-complete.md` | `2026-06-07-aws-s3-inventory-report-complete.md` |
| `logs/` | `YYYY-MM-DD-task-name-log.md` | `2026-10-21-fleet-acp-guardrails-log.md` |

## Status values

Frontmatter is the machine value. Emoji in prose is a display alias only.

### Plans, status, deliverables

| Frontmatter | Display |
|-------------|---------|
| `planned` | 🟡 PLANNED |
| `in_progress` | 🔵 IN_PROGRESS |
| `blocked` | 🟠 BLOCKED |
| `complete` | 🟢 COMPLETE |
| `verified` | ✅ VERIFIED |

### Buffer

`queued`, `claimed`, `in_progress`, `blocked`, `awaiting_verify`, `complete`, `archived`.

See `.acp/buffer/README.md`.

## Guardrails

Rules, role paths, and historical exceptions: [`docs/guardrails/README.md`](docs/guardrails/README.md).

```bash
python scripts/acp-lint/lint.py --self-test
python scripts/acp-lint/lint.py --base origin/main --mode ci
```

Pull requests and pushes to `main` run `.github/workflows/acp-collab-lint.yml`. New board files fail on a bad name, bad status, a plan missing its required sections, or `complete` without evidence. Files that already existed on `main` warn. New diff lines that contain an Account id or an IAM ARN fail. Bucket-shaped values warn.

Commit subjects use `[Agent: name]`, `[Planner]`, `[Implementer]`, `[Delivery]`, or `[Juha]`.

## Quick start

```bash
gh repo clone mildone82/agent-share
python scripts/acp-lint/lint.py --self-test
```

Copy `.acp/plan/_TEMPLATE.md` to a dated plan file, add a buffer card, then:

```bash
git add .acp/plan/2026-10-21-my-task.md .acp/buffer/2026-10-21-my-task.md
git commit -m "[Planner] Add my-task plan"
git push
```

## Rules

1. One task per file.
2. Update status so it matches the work.
3. Archive finished tasks under `archives/` and keep `task_id`.
4. Write Markdown a human and an agent can both read.
5. Link the plan, the buffer card, and the evidence path.
6. Do not add secrets. Do not copy account ids from archived tasks into new files.
