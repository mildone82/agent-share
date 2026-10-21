"""Shared finding type for acp-collab-lint."""

from dataclasses import dataclass


@dataclass
class Finding:
    rule_id: str
    severity: str  # "error" or "warning"
    path: str
    message: str
    line: int = 1

    def capped(self, legacy: bool) -> "Finding":
        """Legacy files warn. Secrets keep the severity chosen by the scanner."""
        if legacy and self.severity == "error" and not self.rule_id.startswith("ACP-SEC-"):
            return Finding(
                rule_id=self.rule_id,
                severity="warning",
                path=self.path,
                message=self.message + " (legacy file: warn)",
                line=self.line,
            )
        return self
