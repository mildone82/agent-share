"""Filename conventions for ACP board files."""

from __future__ import annotations

import re
from pathlib import Path

from rules.frontmatter import is_skipped
from rules.model import Finding

PATTERNS = {
    "plan": re.compile(r"^\d{4}-\d{2}-\d{2}-[a-z0-9][a-z0-9.-]*\.md$"),
    "status": re.compile(r"^\d{4}-\d{2}-\d{2}-[a-z0-9][a-z0-9.-]*-progress\.md$"),
    "deliverables": re.compile(r"^\d{4}-\d{2}-\d{2}-[a-z0-9][a-z0-9.-]*-complete\.md$"),
    "buffer": re.compile(r"^\d{4}-\d{2}-\d{2}-[a-z0-9][a-z0-9.-]*\.md$"),
}
LEGACY_STATUS = re.compile(r"^.+-progress\.md$")


def check_name(rel: str) -> list[Finding]:
    norm = rel.replace("\\", "/")
    path = Path(norm)
    if is_skipped(path):
        return []
    for kind, pattern in PATTERNS.items():
        prefix = f".acp/{kind}/"
        if not norm.startswith(prefix):
            continue
        # Only the directory entry itself, not nested READMEs already skipped.
        if pattern.match(path.name):
            return []
        message = f"{kind} filename must match {pattern.pattern}"
        if kind == "status" and LEGACY_STATUS.match(path.name):
            message += " (dated name required for new files; undated task_id form is legacy-only)"
        return [Finding("ACP-NAME-001", "error", rel, message)]
    return []
