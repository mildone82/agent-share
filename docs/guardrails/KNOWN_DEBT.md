# Known debt

These items already exist on `main`. The linter warns on the old files and fails the same pattern in new files. This PR does not rewrite historical deliverable prose and does not copy account identifiers into new files.

| Item | Where | Lint behavior |
|------|--------|----------------|
| S3 inventory plan contained an AWS account id, an IAM user id, and an IAM ARN | Now `archives/2026-06-07-aws-s3-inventory-report.md` with `disposition: archive` | Historical lines stay in that file. A new diff line with an Account id or IAM ARN fails `ACP-SEC-001`. |
| S3 deliverable still contains the same identifiers and a bucket inventory | `.acp/deliverables/2026-06-07-aws-s3-inventory-report-complete.md` | Unchanged. Gitleaks path-allowlists this file and the archived plan. `acp-collab-lint` still scans added lines. |
| Status filename has no date prefix | `.acp/status/aws-s3-inventory-report-001-progress.md` | `ACP-NAME-001` warns. New status files need `YYYY-MM-DD-...-progress.md`. |
| Status and deliverable frontmatter use `completed` | Same status file and the deliverable | `ACP-FM-001` warns. Legal value is `complete`. |
| Plan body pointed at `deliverables/2026-06-07-aws-s3-inventory-report.md` | Archived plan prose, left as written | Real file is `.acp/deliverables/2026-06-07-aws-s3-inventory-report-complete.md`. |
| Context demo uses `completed` | `contexts/2026-06-07-demo-context-share.md` | Contexts are warn-only. |
| `archives/.gitkeep` used to describe `contexts/` | Corrected in this PR | — |
| Role allowlists are not a required CI check yet | `boundaries.yaml` | Run `--role` locally. Self-test covers an implementer edit of `README.md`. The landing PR spans planner and guardrail paths, so CI does not force a single role. |

Do not paste account ids, IAM ARNs, or bucket inventories from the archived plan into plans, evidence, or this file.
