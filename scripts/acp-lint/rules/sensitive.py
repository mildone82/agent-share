"""Secret and bucket scans over added diff lines only."""

from __future__ import annotations

import re

from rules.model import Finding

ARN_RE = re.compile(r"arn:aws[a-z0-9-]*:iam::[0-9]{12}:[A-Za-z0-9_./+=,@-]+", re.I)
ACCOUNT_RE = re.compile(
    r"(?i)(?:[\"']account[\"']\s*:\s*[\"'][0-9]{12}[\"']|\baccount\b[^0-9\n]{0,16}[0-9]{12}\b)"
)
KEY_RE = re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b")
PRIVATE_KEY_RE = re.compile(r"-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----")
# Split so this source file does not contain the literal it detects.
AWS_SECRET_RE = re.compile("(?i)aws_" + "secret_" + "access_key")
GITHUB_RE = re.compile(r"\b(?:ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})\b")
SLACK_RE = re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b")
BEARER_RE = re.compile(r"Bearer\s+[A-Za-z0-9\-._~+/]{20,}")
# Quoted assignments only, so `bucket = helper()` in code is not a bucket name.
BUCKET_RE = re.compile(
    "(?i)(?:"
    + "s3://"
    + r"[a-z0-9][a-z0-9.-]{1,61}[a-z0-9]"
    + r"|\bbucket(?:\s+name)?\s*[:=]\s*['\"`][a-z0-9][a-z0-9.-]{1,61}[a-z0-9]['\"`]"
    + ")"
)

SECRET_PATTERNS = (
    (ARN_RE, "IAM ARN"),
    (ACCOUNT_RE, "Account id"),
    (KEY_RE, "cloud access key id"),
    (PRIVATE_KEY_RE, "private key"),
    (AWS_SECRET_RE, "cloud secret access key"),
    (GITHUB_RE, "GitHub token"),
    (SLACK_RE, "Slack token"),
    (BEARER_RE, "bearer token"),
)


def scan_added_lines(rel: str, lines: list[tuple[int, str]]) -> list[Finding]:
    """`lines` are (line_number, text) that were added in the diff."""
    findings: list[Finding] = []
    seen: set[tuple[str, int, str]] = set()
    for lineno, text in lines:
        for pattern, label in SECRET_PATTERNS:
            if pattern.search(text):
                key = ("ACP-SEC-001", lineno, label)
                if key in seen:
                    continue
                seen.add(key)
                findings.append(
                    Finding(
                        "ACP-SEC-001",
                        "error",
                        rel,
                        f"new diff introduces a {label}; remove it (value not shown)",
                        lineno,
                    )
                )
        if BUCKET_RE.search(text):
            key = ("bucket", lineno)
            if key in seen:
                continue
            seen.add(key)
            findings.append(
                Finding(
                    "ACP-SEC-001",
                    "warning",
                    rel,
                    "new diff introduces a bucket-shaped value",
                    lineno,
                )
            )
    return findings
