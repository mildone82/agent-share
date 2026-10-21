#!/usr/bin/env python3
"""acp-collab-lint: structure, status vocabulary, and secret checks for agent-share.

ACP here is the Agent Collaboration Protocol used by this repo, not the Zed
Agent Client Protocol.

Examples:
  python scripts/acp-lint/lint.py --self-test
  python scripts/acp-lint/lint.py --base origin/main --mode ci
  python scripts/acp-lint/lint.py --paths-only --role implementer --base origin/main
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from rules.frontmatter import (  # noqa: E402
    check_frontmatter,
    is_skipped,
    kind_for,
    split_frontmatter,
)
from rules.model import Finding  # noqa: E402
from rules.naming import check_name  # noqa: E402
from rules.paths import check_global_paths, check_role_paths  # noqa: E402
from rules.plan_rules import (  # noqa: E402
    check_buffer_schema,
    check_disposition,
    check_evidence,
    check_plan,
    check_task_xref,
)
from rules.sensitive import scan_added_lines  # noqa: E402

BOARD_DIRS = ("plan", "status", "deliverables", "buffer")
COMMIT_RE_TEXT = (
    r"^(?:\[Agent: .+\] |\[Planner\]|\[Implementer\]|\[Delivery\]|\[Juha\]|"
    r"init:|docs:|chore\(guardrails\):)"
)


def _git(root: Path, args: list[str]) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=root,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or f"git {' '.join(args)} failed")
    return completed.stdout


def _git_ok(root: Path, args: list[str]) -> bool:
    completed = subprocess.run(
        ["git", *args],
        cwd=root,
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return completed.returncode == 0


def resolve_base(root: Path, requested: str | None) -> str:
    if requested and set(requested) == {"0"}:
        requested = None
    candidates = [requested] if requested else []
    candidates.extend(["origin/main", "main"])
    for candidate in candidates:
        if candidate and _git_ok(root, ["rev-parse", "--verify", candidate]):
            return candidate
    raise RuntimeError("could not resolve a base ref; pass --base")


def legacy_paths(root: Path, base: str) -> set[str]:
    output = _git(root, ["ls-tree", "-r", "--name-only", base])
    return {line.strip() for line in output.splitlines() if line.strip()}


def tracked_and_untracked(root: Path) -> list[str]:
    tracked = _git(root, ["ls-files", "-z"])
    untracked = _git(root, ["ls-files", "--others", "--exclude-standard", "-z"])
    names = []
    for blob in (tracked, untracked):
        names.extend(part for part in blob.split("\0") if part)
    return names


def _parse_added_lines(diff_text: str) -> dict[str, list[tuple[int, str]]]:
    added: dict[str, list[tuple[int, str]]] = {}
    current: str | None = None
    new_line = 0
    for raw in diff_text.splitlines():
        if raw.startswith("diff --git "):
            current = None
            continue
        if raw.startswith("+++ "):
            path = raw[4:]
            if path.startswith("b/"):
                path = path[2:]
            if path == "/dev/null":
                current = None
                continue
            if path.startswith('"') and path.endswith('"'):
                path = path[1:-1]
            current = path
            added.setdefault(current, [])
            continue
        if raw.startswith("@@"):
            marker = raw.split(" ")
            plus = next((part for part in marker if part.startswith("+")), "+1")
            new_line = int(plus[1:].split(",")[0])
            continue
        if current is None:
            continue
        if raw.startswith("+"):
            added.setdefault(current, []).append((new_line, raw[1:]))
            new_line += 1
        elif raw.startswith("-"):
            continue
        elif raw.startswith("\\"):
            continue
        else:
            new_line += 1
    return added


def added_lines_against_base(root: Path, base: str) -> dict[str, list[tuple[int, str]]]:
    diff_text = _git(
        root,
        ["diff", "-M", "--find-renames", "-U0", base, "--"],
    )
    added = _parse_added_lines(diff_text)
    untracked = _git(root, ["ls-files", "--others", "--exclude-standard"])
    for rel in untracked.splitlines():
        path = root / rel
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        added[rel] = list(enumerate(text.splitlines(), start=1))
    return added


def board_files(root: Path) -> list[Path]:
    found: list[Path] = []
    for kind in BOARD_DIRS:
        directory = root / ".acp" / kind
        if not directory.is_dir():
            continue
        found.extend(path for path in directory.rglob("*.md") if path.is_file())
    contexts = root / "contexts"
    if contexts.is_dir():
        found.extend(path for path in contexts.rglob("*.md") if path.is_file())
    return found


def _apply_policy(findings: list[Finding], rel: str, legacy: set[str]) -> list[Finding]:
    adjusted: list[Finding] = []
    is_legacy = rel in legacy
    context = rel.replace("\\", "/").startswith("contexts/")
    for finding in findings:
        item = finding.capped(is_legacy)
        if context and item.severity == "error":
            item = Finding(
                rule_id=item.rule_id,
                severity="warning",
                path=item.path,
                message=item.message + " (contexts stay warn-only)",
                line=item.line,
            )
        adjusted.append(item)
    return adjusted


def lint_board_file(root: Path, path: Path, legacy: set[str]) -> list[Finding]:
    rel = path.relative_to(root).as_posix()
    if path.name == "README.md":
        return []
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return [Finding("ACP-FM-001", "error", rel, "file is not valid UTF-8")]
    meta, body, error = split_frontmatter(text)
    findings = check_name(rel)
    if kind_for(rel):
        findings.extend(check_frontmatter(rel, meta, error))
    if meta is not None:
        findings.extend(check_plan(rel, meta, body))
        findings.extend(check_evidence(root, rel, meta))
        findings.extend(check_buffer_schema(root, rel, meta))
        findings.extend(check_task_xref(root, rel, meta))
        plan_path = str(meta.get("plan_path") or "").strip()
        if rel.startswith(".acp/buffer/") and not is_skipped(path) and plan_path:
            if not (root / plan_path).is_file():
                findings.append(
                    Finding(
                        "ACP-BUF-001",
                        "error",
                        rel,
                        "buffer `plan_path` does not exist",
                    )
                )
    return _apply_policy(findings, rel, legacy)


def check_commits(root: Path, base: str) -> list[Finding]:
    import re

    pattern = re.compile(COMMIT_RE_TEXT)
    try:
        log = _git(root, ["log", "--format=%H%x09%s", f"{base}..HEAD"])
    except RuntimeError:
        return []
    findings: list[Finding] = []
    for line in log.splitlines():
        sha, sep, subject = line.partition("\t")
        if not sep:
            continue
        if subject.startswith("Merge "):
            continue
        if pattern.match(subject):
            continue
        findings.append(
            Finding(
                "ACP-COMMIT-001",
                "error",
                sha[:12],
                "commit subject needs an [Agent: name] / [Planner] / [Juha] prefix",
            )
        )
    return findings


def lint_repository(
    root: Path,
    base: str,
    *,
    paths_only: bool = False,
    role: str | None = None,
    check_commit_subjects: bool = True,
) -> list[Finding]:
    legacy = legacy_paths(root, base)
    findings: list[Finding] = []
    paths = tracked_and_untracked(root)
    findings.extend(check_global_paths(paths))
    if role:
        changed = sorted(added_lines_against_base(root, base))
        findings.extend(check_role_paths(root, role, changed))
    if paths_only:
        return findings
    for path in board_files(root):
        findings.extend(lint_board_file(root, path, legacy))
    for item in check_disposition(root):
        findings.extend(_apply_policy([item], item.path, legacy))
    added = added_lines_against_base(root, base)
    for rel, lines in added.items():
        findings.extend(scan_added_lines(rel, lines))
    if check_commit_subjects:
        findings.extend(check_commits(root, base))
    return findings


def lint_all_new(root: Path) -> list[Finding]:
    """Lint a fixture tree where every file is new (no git history)."""
    findings: list[Finding] = []
    all_paths: list[str] = []
    for path in root.rglob("*"):
        if not path.is_file() or ".git" in path.parts:
            continue
        rel = path.relative_to(root).as_posix()
        all_paths.append(rel)
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        lines = list(enumerate(text.splitlines(), start=1))
        findings.extend(scan_added_lines(rel, lines))
    findings.extend(check_global_paths(all_paths))
    for path in board_files(root):
        findings.extend(lint_board_file(root, path, set()))
    for item in check_disposition(root):
        findings.extend(_apply_policy([item], item.path, set()))
    return findings


def render(findings: list[Finding], mode: str) -> str:
    lines: list[str] = []
    for finding in findings:
        if mode == "ci":
            level = "error" if finding.severity == "error" else "warning"
            message = (
                finding.message.replace("%", "%25")
                .replace("\r", "%0D")
                .replace("\n", "%0A")
            )
            lines.append(
                f"::{level} file={finding.path},line={finding.line}::"
                f"{finding.rule_id} {message}"
            )
        else:
            label = "ERROR" if finding.severity == "error" else "WARN "
            lines.append(
                f"{label} {finding.rule_id} {finding.path}:{finding.line} {finding.message}"
            )
    errors = sum(1 for finding in findings if finding.severity == "error")
    warnings = len(findings) - errors
    lines.append(f"acp-collab-lint: {errors} error(s), {warnings} warning(s)")
    return "\n".join(lines)


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


SCHEMA = """{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "ACP buffer mission card",
  "type": "object",
  "required": ["mission_id", "role_owner", "status", "plan_path", "evidence_path"],
  "properties": {
    "status": {
      "enum": [
        "queued",
        "claimed",
        "in_progress",
        "blocked",
        "awaiting_verify",
        "complete",
        "archived"
      ]
    }
  },
  "additionalProperties": true
}
"""

CLEAN_PLAN = """---
agent: anita
timestamp: 2026-10-21T10:00:00+08:00
task_id: clean-task-001
status: planned
source: self-test
playbook: feature
---

# Clean task

## Objective

Show that a complete plan passes.

## Out of scope

No product code.

## Acceptance Criteria

- [ ] Lint exits 0

## Suggested owners

- Engineer: Linus
- Verifier: Juha
"""

CLEAN_EVIDENCE = """---
agent: implementer
timestamp: 2026-10-21T10:00:00+08:00
task_id: clean-task-001
status: in_progress
source: self-test
---

# Evidence

- command: `python scripts/acp-lint/lint.py --self-test`
- expect: exit 0 and planted defects are reported
- artifact_path:
- last_run: 2026-10-21T10:00:00+08:00
- note: able to fail when a planted defect is present
"""

ARCHIVE = """---
agent: hermes-macbook
timestamp: 2026-06-07T08:55:00+08:00
task_id: aws-s3-inventory-report-001
status: archived
disposition: archive
disposition_reason: Fixture copy of an archived stale plan.
source: self-test
---

# Archived
"""


def _clean_tree(root: Path) -> None:
    _write(root / ".acp/schemas/mission.schema.json", SCHEMA)
    _write(root / ".acp/plan/2026-10-21-clean-task.md", CLEAN_PLAN)
    _write(root / ".acp/evidence/2026-10-21-clean-task.md", CLEAN_EVIDENCE)
    _write(
        root / ".acp/status/2026-10-21-clean-task-progress.md",
        """---
agent: implementer
timestamp: 2026-10-21T10:00:00+08:00
task_id: clean-task-001
status: complete
source: self-test
evidence_path: .acp/evidence/2026-10-21-clean-task.md
---

# Status
""",
    )
    _write(
        root / ".acp/buffer/2026-10-21-clean-task.md",
        """---
agent: implementer
timestamp: 2026-10-21T10:00:00+08:00
task_id: clean-task-001
status: queued
source: self-test
mission_id: 2026-10-21-clean-task
role_owner: implementer
plan_path: .acp/plan/2026-10-21-clean-task.md
evidence_path: .acp/evidence/2026-10-21-clean-task.md
---

# Buffer
""",
    )
    _write(root / ".acp/buffer/README.md", "# Buffer\n\nIgnored by lint.\n")
    _write(root / "archives/2026-06-07-aws-s3-inventory-report.md", ARCHIVE)
    _write(
        root / "docs/guardrails/boundaries.yaml",
        """roles:
  implementer:
    allow:
      - ".acp/status/**"
      - ".acp/evidence/**"
    deny:
      - "README.md"
      - "docs/guardrails/**"
  juha:
    allow:
      - "docs/guardrails/**"
      - "README.md"
    deny: []
""",
    )


def _dirty_tree(root: Path) -> None:
    _write(root / ".acp/schemas/mission.schema.json", SCHEMA)
    _write(
        root / ".acp/plan/2026-10-21-bad-status.md",
        CLEAN_PLAN.replace("status: planned", "status: nope"),
    )
    _write(root / ".acp/plan/not-a-date.md", CLEAN_PLAN)
    _write(
        root / ".acp/plan/2026-10-21-no-scope.md",
        """---
agent: anita
timestamp: 2026-10-21T10:00:00+08:00
task_id: no-scope-001
status: planned
source: self-test
playbook: feature
---

# Missing scope

## Objective

Motive is present.

## Acceptance Criteria

- [ ] Should still fail

## Suggested owners

- Engineer: Linus
- Verifier: Juha
""",
    )
    _write(
        root / ".acp/status/2026-10-21-done-progress.md",
        """---
agent: implementer
timestamp: 2026-10-21T10:00:00+08:00
task_id: done-001
status: complete
source: self-test
---

# Done with no evidence
""",
    )
    sample_id = "123456" + "789012"
    sample_arn = "arn:" + "aws-cn:iam::" + sample_id + ":user/example"
    _write(
        root / ".acp/plan/2026-10-21-leak.md",
        CLEAN_PLAN
        + '\n\n```json\n{"Account": "'
        + sample_id
        + '", "Arn": "'
        + sample_arn
        + '"}\n```\n',
    )
    _write(root / ".acp/secret-note.md", "not a credential file, but the name is denied\n")
    _write(
        root / ".acp/buffer/2026-10-21-bad-buffer.md",
        """---
agent: implementer
timestamp: 2026-10-21T10:00:00+08:00
task_id: bad-buffer-001
status: nope
source: self-test
mission_id: 2026-10-21-bad-buffer
role_owner: implementer
plan_path: .acp/plan/2026-10-21-bad-status.md
evidence_path: .acp/evidence/missing.md
---

# Bad buffer
""",
    )


def run_self_test() -> int:
    from rules.paths import _match

    print("acp-collab-lint self-test")
    assert _match(".acp/plan/2026-10-21-foo.md", ".acp/plan/**")
    assert _match(".env", "**/.env")
    assert _match("a/credentials.json", "**/credentials*")
    assert _match("secret-note.md", "**/*secret*")
    assert not _match("README.md", ".acp/plan/**")

    with tempfile.TemporaryDirectory() as tmp:
        clean = Path(tmp) / "clean"
        dirty = Path(tmp) / "dirty"
        legacy = Path(tmp) / "legacy"
        _clean_tree(clean)
        _dirty_tree(dirty)
        clean_findings = lint_all_new(clean)
        dirty_findings = lint_all_new(dirty)
        _write(
            legacy / ".acp/status/old-task-progress.md",
            """---
agent: hermes
timestamp: 2026-06-07T16:00:00+08:00
task_id: old-task-001
status: completed
source: self-test
---

# Legacy
""",
        )
        _write(legacy / "archives/2026-06-07-aws-s3-inventory-report.md", ARCHIVE)
        legacy_findings = lint_board_file(
            legacy,
            legacy / ".acp/status/old-task-progress.md",
            {".acp/status/old-task-progress.md"},
        )
        legacy_findings.extend(
            _apply_policy(
                check_disposition(legacy),
                ".acp/plan/2026-06-07-aws-s3-inventory-report.md",
                set(),
            )
        )
        role_findings = check_role_paths(clean, "implementer", ["README.md"])
        allowed = check_role_paths(clean, "juha", ["docs/guardrails/boundaries.yaml"])
        bucket = scan_added_lines(
            "notes.md", [(3, "see s3://" + "example-bucket")]
        )

    clean_errors = [item for item in clean_findings if item.severity == "error"]
    dirty_errors = [item for item in dirty_findings if item.severity == "error"]
    caught = sorted({item.rule_id for item in dirty_errors})
    required = {
        "ACP-FM-001",
        "ACP-NAME-001",
        "ACP-EVID-001",
        "ACP-PLAN-001",
        "ACP-SEC-001",
        "ACP-DISP-001",
    }
    ok = True

    def report(label: str, passed: bool, detail: str) -> None:
        nonlocal ok
        if not passed:
            ok = False
        print(f"  {'PASS' if passed else 'FAIL'} {label}: {detail}")

    report("clean fixture", not clean_errors, f"{len(clean_errors)} error(s)")
    if clean_errors:
        for item in clean_errors:
            print(f"    {item.rule_id} {item.path} {item.message}")
    report(
        "planted defects",
        required <= set(caught) and len(caught) >= 3,
        "caught " + ", ".join(caught),
    )
    report(
        "legacy warn",
        bool(legacy_findings)
        and all(item.severity == "warning" for item in legacy_findings),
        f"{len(legacy_findings)} finding(s), "
        + ",".join(sorted({item.severity for item in legacy_findings})),
    )
    report(
        "role boundary",
        any(item.rule_id == "ACP-PATH-001" and item.severity == "error" for item in role_findings)
        and not allowed,
        "implementer README denied; juha guardrail path allowed",
    )
    report(
        "bucket warn",
        any(item.severity == "warning" for item in bucket)
        and not any(item.severity == "error" for item in bucket),
        "bucket-shaped value warns and does not fail",
    )
    if ok:
        print("SELF-TEST PASS")
        return 0
    print("SELF-TEST FAIL")
    return 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Lint agent-share ACP board files.")
    parser.add_argument("--base", help="Git ref to diff and to classify legacy files.")
    parser.add_argument("--root", help="Repository or fixture root. Defaults to git toplevel.")
    parser.add_argument("--mode", choices=("local", "ci"), default="local")
    parser.add_argument("--paths-only", action="store_true")
    parser.add_argument("--role", help="Enforce docs/guardrails/boundaries.yaml for this role.")
    parser.add_argument("--all-new", action="store_true", help="Treat every file as new.")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("paths", nargs="*", help="Accepted for pre-commit; scan is repo-wide.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.self_test:
        return run_self_test()
    root = Path(args.root).resolve() if args.root else Path(
        _git(Path.cwd(), ["rev-parse", "--show-toplevel"]).strip()
    )
    try:
        if args.all_new:
            findings = lint_all_new(root)
        else:
            base = resolve_base(root, args.base)
            findings = lint_repository(
                root,
                base,
                paths_only=args.paths_only,
                role=args.role,
            )
    except RuntimeError as exc:
        print(f"ERROR ACP-LINT-000 {exc}", file=sys.stderr)
        return 2
    print(render(findings, args.mode))
    return 1 if any(item.severity == "error" for item in findings) else 0


if __name__ == "__main__":
    sys.exit(main())
