"""Global denylist and optional per-role path boundaries."""

from __future__ import annotations

import re
from pathlib import Path

import yaml

from rules.model import Finding

# Filename denylist from the guardrail draft. `*secret*` is intentionally not
# applied inside scripts/acp-lint/, so the scanner module can exist.
GLOBAL_DENY = (
    "**/.env",
    "**/.env.*",
    "**/credentials*",
    "**/*secret*",
    "**/*.pem",
    "**/*.key",
    "**/id_rsa*",
    "**/.aws/credentials",
    "**/kubeconfig*",
    "**/node_modules/**",
    "**/__pycache__/**",
    "**/.venv/**",
    "**/dist/**",
    "**/build/**",
    "**/*.pyc",
)
LINT_PREFIX = "scripts/acp-lint/"


def _normalize(value: str) -> str:
    value = value.replace("\\", "/")
    while value.startswith("./"):
        value = value[2:]
    return value.lstrip("/")


def _match(path: str, pattern: str) -> bool:
    """Glob match. `**` crosses directories; a single `*` does not."""
    path = _normalize(path)
    pattern = _normalize(pattern)
    regex_parts: list[str] = []
    index = 0
    while index < len(pattern):
        if pattern.startswith("**/", index):
            regex_parts.append("(?:.*/)?")
            index += 3
        elif pattern.startswith("**", index):
            regex_parts.append(".*")
            index += 2
        elif pattern[index] == "*":
            regex_parts.append("[^/]*")
            index += 1
        elif pattern[index] == "?":
            regex_parts.append("[^/]")
            index += 1
        else:
            regex_parts.append(re.escape(pattern[index]))
            index += 1
    return re.fullmatch("".join(regex_parts), path) is not None


def globally_denied(rel: str) -> bool:
    norm = rel.replace("\\", "/")
    for pattern in GLOBAL_DENY:
        if pattern == "**/*secret*" and norm.startswith(LINT_PREFIX):
            continue
        if _match(norm, pattern):
            return True
    return False


def check_global_paths(paths: list[str]) -> list[Finding]:
    findings = []
    for rel in paths:
        if globally_denied(rel):
            findings.append(
                Finding(
                    "ACP-PATH-001",
                    "error",
                    rel,
                    "path is on the global denylist (secrets, credentials, or build output)",
                )
            )
    return findings


def load_boundaries(root: Path) -> dict:
    path = root / "docs/guardrails/boundaries.yaml"
    if not path.is_file():
        return {}
    loaded = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(loaded, dict):
        return {}
    return loaded


def path_allowed(rel: str, patterns: list[str]) -> bool:
    return any(_match(rel, pattern) for pattern in patterns)


def check_role_paths(root: Path, role: str, paths: list[str]) -> list[Finding]:
    boundaries = load_boundaries(root)
    roles = boundaries.get("roles") or {}
    spec = roles.get(role)
    if not isinstance(spec, dict):
        return [
            Finding(
                "ACP-PATH-001",
                "error",
                "docs/guardrails/boundaries.yaml",
                f"unknown role `{role}`",
            )
        ]
    allow = list(spec.get("allow") or [])
    deny = list(spec.get("deny") or [])
    findings: list[Finding] = []
    for rel in paths:
        norm = rel.replace("\\", "/")
        if path_allowed(norm, deny) or not path_allowed(norm, allow):
            findings.append(
                Finding(
                    "ACP-PATH-001",
                    "error",
                    norm,
                    f"role `{role}` may not write this path",
                )
            )
    return findings
