---
agent: implementer
timestamp: 2026-10-21T12:30:00+08:00
task_id: fleet-acp-guardrails-001
status: in_progress
source: cursor-cloud-agent
target: anita
---

# Evidence: fleet-acp-guardrails

Able to fail: the self-test plants broken files and expects the linter to catch them. A clean fixture must pass.

## E1 — planted defects are caught

- command: `python scripts/acp-lint/lint.py --self-test`
- expect: exit 0, clean fixture has 0 errors, and at least 3 planted rule ids are reported (including `ACP-FM-001`, `ACP-NAME-001`, `ACP-EVID-001`, `ACP-PLAN-001`, `ACP-SEC-001`, `ACP-DISP-001`)
- artifact_path:
- last_run: 2026-10-21T02:10:00+00:00
- result: pass. Caught ACP-BUF-001, ACP-DISP-001, ACP-EVID-001, ACP-FM-001, ACP-NAME-001, ACP-PATH-001, ACP-PLAN-001, ACP-SEC-001, ACP-XREF-001. Clean fixture 0 errors. Legacy file warned and did not fail. Bucket-shaped value warned and did not fail.

## E2 — this tree has no new-file errors

- command: `python scripts/acp-lint/lint.py --base origin/main --mode local`
- expect: exit 0. Legacy warnings are allowed for the historical status filename, `completed`, and the context demo.
- artifact_path:
- last_run: 2026-10-21T02:10:00+00:00
- result: pass. 0 errors, 4 legacy warnings (`ACP-NAME-001` and `ACP-FM-001` on the old status file, `ACP-FM-001` on the old deliverable, `ACP-FM-001` on the context demo).

## E3 — role boundary can fail

- command: covered inside `--self-test` (implementer writing `README.md`)
- expect: `ACP-PATH-001` error for that role; Juha path allowed
- artifact_path:
- last_run: 2026-10-21T02:10:00+00:00
- result: pass
