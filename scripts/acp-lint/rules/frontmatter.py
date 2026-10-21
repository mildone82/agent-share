"""Frontmatter parse and status vocabulary checks."""

from __future__ import annotations

import datetime as dt
import re
from pathlib import Path

import yaml

from rules.model import Finding

PLAN_STATUS = {"planned", "in_progress", "blocked", "complete", "verified"}
BUFFER_STATUS = {
    "queued",
    "claimed",
    "in_progress",
    "blocked",
    "awaiting_verify",
    "complete",
    "archived",
}
REQUIRED_KEYS = ("agent", "timestamp", "task_id", "status", "source")
BUFFER_KEYS = ("mission_id", "role_owner", "plan_path", "evidence_path")
ISO_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:Z|[+-]\d{2}:\d{2})$"
)
SKIP_BASENAMES = {"README.md"}


def is_skipped(path: Path) -> bool:
    name = path.name
    return name in SKIP_BASENAMES or name.startswith("_")


def split_frontmatter(text: str) -> tuple[dict | None, str, str | None]:
    """Return (mapping, body, error). mapping is None when frontmatter is absent."""
    if text.startswith("\ufeff"):
        text = text.lstrip("\ufeff")
    if not text.startswith("---"):
        return None, text, "missing YAML frontmatter"
    parts = text.split("---", 2)
    if len(parts) < 3 or not parts[1].strip():
        return None, text, "frontmatter block is empty or unclosed"
    try:
        loaded = yaml.safe_load(parts[1])
    except yaml.YAMLError as exc:
        return None, parts[2], f"frontmatter YAML is invalid ({exc.__class__.__name__})"
    if not isinstance(loaded, dict):
        return None, parts[2], "frontmatter must be a mapping"
    return loaded, parts[2], None


def as_str(value) -> str:
    if isinstance(value, dt.datetime):
        return value.isoformat()
    if value is None:
        return ""
    return str(value).strip()


def kind_for(rel: str) -> str | None:
    norm = rel.replace("\\", "/")
    for kind in ("plan", "status", "deliverables", "buffer"):
        if norm.startswith(f".acp/{kind}/"):
            return kind
    if norm.startswith("contexts/"):
        return "context"
    return None


def check_frontmatter(rel: str, meta: dict | None, error: str | None) -> list[Finding]:
    kind = kind_for(rel)
    if kind is None:
        return []
    findings: list[Finding] = []
    if error or meta is None:
        findings.append(
            Finding("ACP-FM-001", "error", rel, error or "missing YAML frontmatter")
        )
        return findings

    for key in REQUIRED_KEYS:
        if key not in meta or as_str(meta.get(key)) == "":
            findings.append(
                Finding("ACP-FM-001", "error", rel, f"frontmatter `{key}` is required")
            )

    timestamp = meta.get("timestamp")
    if isinstance(timestamp, dt.datetime):
        stamp = as_str(timestamp)
    else:
        stamp = as_str(timestamp)
    if stamp and not ISO_RE.match(stamp):
        findings.append(
            Finding(
                "ACP-FM-001",
                "error",
                rel,
                "frontmatter `timestamp` must be ISO-8601 with a timezone offset",
            )
        )

    status = as_str(meta.get("status"))
    if kind == "buffer":
        allowed = BUFFER_STATUS
        label = "buffer"
    elif kind == "context":
        allowed = PLAN_STATUS
        label = "context"
    else:
        allowed = PLAN_STATUS
        label = kind
    if status and status not in allowed:
        findings.append(
            Finding(
                "ACP-FM-001",
                "error",
                rel,
                f"`status: {status}` is not in the {label} vocabulary",
            )
        )

    if kind == "buffer":
        for key in BUFFER_KEYS:
            if key not in meta or as_str(meta.get(key)) == "":
                findings.append(
                    Finding(
                        "ACP-BUF-001",
                        "error",
                        rel,
                        f"buffer card requires frontmatter `{key}`",
                    )
                )
    return findings
