# Crew roster

Authoritative role list for this repo. README tables are narrative; this file wins if they disagree.

| Role | Seat | Writes | Does not |
|------|------|--------|----------|
| Anita | Protocol and evidence | Plans, verification protocol, evidence sign-off | Self-merge; machine-rule code without Juha |
| Implementer | Execution seat (Linus, unless a card says otherwise) | Status, logs, buffer updates, run evidence | Mark `complete` without a verifier; edit guardrail config |
| Juha | Architecture guardrails | `docs/guardrails/`, `scripts/acp-lint/`, CI, schemas, this roster | Business deliverable text that pretends a task is done |
| Mildone | Coordinator | Priority, owners, disposition calls | Skip the verifier or merge as an agent |
| Lauran | Intel | Outer-loop notes that become plans | Product code in this mission |
| Linus | Engineer | Implementation under an owned card | Verify his own card |
| Human | Merge | Merge to `main` after review | — |

Rules that apply to every seat:

- Plan before code. A card in `.acp/buffer/` points at a plan and an evidence path.
- Engineer and Verifier are different agents. Linus does not verify Linus. Anita does not verify her own protocol alone when she is also the engineer.
- No self-merge. Agents stop at `awaiting_verify`.
- Halt when the engineer and verifier disagree, or when a required gate is blocked or timed out. Do not mark the card `complete`.
- Commit subjects start with `[Agent: name]`, `[Planner]`, `[Implementer]`, `[Delivery]`, or `[Juha]`.
