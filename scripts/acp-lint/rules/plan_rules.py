"""ACP-PLAN-001, ACP-EVID-001, ACP-DISP-001, and buffer schema checks."""

from __future__ import annotations

import json
import re
from pathlib import Path

from rules.frontmatter import BUFFER_STATUS, as_str, is_skipped, split_frontmatter
from rules.model import Finding

HEADING = {
    "motive": re.compile(
        r"(?m)^#{1,6}\s+.*(?:(?<!非)目标|动机|Objective|Reproduction|Why\b)"
    ),
    "out_of_scope": re.compile(
        r"(?m)^#{1,6}\s+.*(?:非目标|范围外|Out of scope|Non-goals|Non-goal)"
    ),
    "acceptance": re.compile(r"(?m)^#{1,6}\s+.*(?:验收|Acceptance)"),
}
OWNER_ENGINEER = re.compile(r"(?im)^[\s>*-]*Engineer\s*[:：]\s*(.+?)\s*$")
OWNER_VERIFIER = re.compile(r"(?im)^[\s>*-]*Verifier\s*[:：]\s*(.+?)\s*$")
EVIDENCE_LABELS = ("command", "expect", "artifact_path", "last_run")
ABLE_TO_FAIL = re.compile(r"(?i)able to fail|planted defect|故意")
COMPLETE_STATUSES = {"complete", "verified"}
STALE_PLAN = ".acp/plan/2026-06-07-aws-s3-inventory-report.md"
STALE_NAME = "2026-06-07-aws-s3-inventory-report.md"
STALE_TASK = "aws-s3-inventory-report-001"


def check_plan(rel: str, meta: dict, body: str) -> list[Finding]:
    norm = rel.replace("\\", "/")
    if not norm.startswith(".acp/plan/") or Path(norm).name == "README.md":
        return []
    findings: list[Finding] = []
    if not HEADING["motive"].search(body):
        findings.append(
            Finding(
                "ACP-PLAN-001",
                "error",
                rel,
                "plan is missing a motive / objective heading (目标, 动机, Objective, or Reproduction)",
            )
        )
    if not HEADING["out_of_scope"].search(body):
        findings.append(
            Finding(
                "ACP-PLAN-001",
                "error",
                rel,
                "plan is missing an out-of-scope heading (非目标, 范围外, or Out of scope)",
            )
        )
    if not HEADING["acceptance"].search(body):
        findings.append(
            Finding(
                "ACP-PLAN-001",
                "error",
                rel,
                "plan is missing an acceptance heading (验收 or Acceptance)",
            )
        )
    playbook = as_str(meta.get("playbook"))
    if not playbook and not re.search(r"(?i)playbook", body):
        findings.append(
            Finding(
                "ACP-PLAN-001",
                "error",
                rel,
                "plan is missing `playbook` frontmatter or a playbook section",
            )
        )
    engineer = OWNER_ENGINEER.search(body)
    verifier = OWNER_VERIFIER.search(body)
    if not engineer or not verifier:
        findings.append(
            Finding(
                "ACP-PLAN-001",
                "error",
                rel,
                "plan must name Engineer and Verifier under Suggested owners",
            )
        )
    elif engineer.group(1).casefold() == verifier.group(1).casefold():
        findings.append(
            Finding(
                "ACP-PLAN-001",
                "error",
                rel,
                "Engineer and Verifier must be different agents",
            )
        )
    return findings


def _evidence_text_ok(text: str) -> str | None:
    missing = [
        label
        for label in EVIDENCE_LABELS
        if not re.search(rf"(?i)\b{label}\b\s*[:：]", text)
    ]
    if missing:
        return "evidence file is missing " + ", ".join(missing)
    if not ABLE_TO_FAIL.search(text):
        return "evidence file has no able-to-fail / planted-defect item"
    return None


def check_evidence(root: Path, rel: str, meta: dict) -> list[Finding]:
    norm = rel.replace("\\", "/")
    kind = None
    for name in ("plan", "status", "deliverables", "buffer"):
        if norm.startswith(f".acp/{name}/"):
            kind = name
            break
    if kind is None or is_skipped(Path(norm)):
        return []
    status = as_str(meta.get("status"))
    if status not in COMPLETE_STATUSES:
        return []
    evidence_rel = as_str(meta.get("evidence_path"))
    if not evidence_rel:
        return [
            Finding(
                "ACP-EVID-001",
                "error",
                rel,
                f"status `{status}` requires frontmatter `evidence_path`",
            )
        ]
    evidence_file = root / evidence_rel
    if not evidence_file.is_file():
        return [
            Finding(
                "ACP-EVID-001",
                "error",
                rel,
                f"evidence file `{evidence_rel}` does not exist",
            )
        ]
    problem = _evidence_text_ok(evidence_file.read_text(encoding="utf-8"))
    if problem:
        return [Finding("ACP-EVID-001", "error", rel, problem)]
    return []


def _load_meta(path: Path) -> dict | None:
    if not path.is_file():
        return None
    meta, _body, error = split_frontmatter(path.read_text(encoding="utf-8"))
    if error or meta is None:
        return None
    return meta


def check_disposition(root: Path) -> list[Finding]:
    """ACP-DISP-001 for the stale June 2026 S3 inventory plan."""
    stale = root / STALE_PLAN
    if stale.is_file():
        meta = _load_meta(stale) or {}
        disposition = as_str(meta.get("disposition")).lower()
        status = as_str(meta.get("status")).lower()
        if disposition == "reopen":
            owner = as_str(meta.get("owner")) or as_str(meta.get("role_owner"))
            if not owner:
                return [
                    Finding(
                        "ACP-DISP-001",
                        "error",
                        STALE_PLAN,
                        "disposition reopen requires `owner` or `role_owner`",
                    )
                ]
            return []
        return [
            Finding(
                "ACP-DISP-001",
                "error",
                STALE_PLAN,
                "stale S3 plan is still under .acp/plan/ without disposition reopen "
                f"(status={status or 'missing'}). Archive it or reopen it with an owner.",
            )
        ]

    archives = root / "archives"
    if archives.is_dir():
        for path in archives.rglob("*.md"):
            meta = _load_meta(path) or {}
            task_id = as_str(meta.get("task_id"))
            if path.name != STALE_NAME and task_id != STALE_TASK:
                continue
            disposition = as_str(meta.get("disposition")).lower()
            status = as_str(meta.get("status")).lower()
            reason = as_str(meta.get("disposition_reason"))
            rel = path.relative_to(root).as_posix()
            if disposition == "archive" and status == "archived" and reason:
                return []
            return [
                Finding(
                    "ACP-DISP-001",
                    "error",
                    rel,
                    "archived S3 plan needs status archived, disposition archive, "
                    "and disposition_reason",
                )
            ]
    return [
        Finding(
            "ACP-DISP-001",
            "error",
            STALE_PLAN,
            "stale S3 plan has no archive disposition and no reopen owner",
        )
    ]


def check_task_xref(root: Path, rel: str, meta: dict) -> list[Finding]:
    """Status and deliverable files must point at a plan task_id still on disk."""
    norm = rel.replace("\\", "/")
    if not (norm.startswith(".acp/status/") or norm.startswith(".acp/deliverables/")):
        return []
    if Path(norm).name == "README.md" or Path(norm).name.startswith("_"):
        return []
    task_id = as_str(meta.get("task_id"))
    if not task_id:
        return []
    for folder in (root / ".acp" / "plan", root / "archives"):
        if not folder.is_dir():
            continue
        for path in folder.rglob("*.md"):
            other, _body, error = split_frontmatter(path.read_text(encoding="utf-8"))
            if error or not other:
                continue
            if as_str(other.get("task_id")) == task_id:
                return []
    return [
        Finding(
            "ACP-XREF-001",
            "error",
            rel,
            f"task_id `{task_id}` has no plan under .acp/plan/ or archives/",
        )
    ]


def check_buffer_schema(root: Path, rel: str, meta: dict) -> list[Finding]:
    norm = rel.replace("\\", "/")
    if not norm.startswith(".acp/buffer/") or is_skipped(Path(norm)):
        return []
    schema_path = root / ".acp/schemas/mission.schema.json"
    if not schema_path.is_file():
        return [
            Finding(
                "ACP-BUF-001",
                "error",
                rel,
                "missing .acp/schemas/mission.schema.json",
            )
        ]
    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return [
            Finding(
                "ACP-BUF-001",
                "error",
                ".acp/schemas/mission.schema.json",
                "mission schema is not valid JSON",
            )
        ]
    required = schema.get("required") or []
    properties = schema.get("properties") or {}
    findings: list[Finding] = []
    for key in required:
        if key not in meta or as_str(meta.get(key)) == "":
            findings.append(
                Finding(
                    "ACP-BUF-001",
                    "error",
                    rel,
                    f"schema requires `{key}`",
                )
            )
    status_schema = (properties.get("status") or {}).get("enum") or sorted(BUFFER_STATUS)
    status = as_str(meta.get("status"))
    if status and status not in status_schema:
        findings.append(
            Finding(
                "ACP-BUF-001",
                "error",
                rel,
                f"schema rejects buffer status `{status}`",
            )
        )
    return findings
