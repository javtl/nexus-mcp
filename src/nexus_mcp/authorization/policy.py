"""MVP policy as data. Edit here to change what is allowed (ADR-008)."""

from __future__ import annotations

from dataclasses import dataclass

from .models import ActionType, Decision, RiskLevel


@dataclass(frozen=True)
class ToolPolicy:
    action_type: ActionType
    risk_level: RiskLevel
    decision: Decision
    reason: str


POLICY: dict[str, ToolPolicy] = {
    "get_customer": ToolPolicy(
        ActionType.READ, RiskLevel.LOW, Decision.ALLOW,
        "READ action with LOW risk is allowed by the MVP policy.",
    ),
    "create_order": ToolPolicy(
        ActionType.WRITE, RiskLevel.MEDIUM, Decision.ALLOW,
        "WRITE action with MEDIUM risk is allowed by the MVP policy.",
    ),
    "cancel_order": ToolPolicy(
        ActionType.DESTRUCTIVE, RiskLevel.HIGH, Decision.DENY,
        "DESTRUCTIVE action with HIGH risk is denied by the MVP policy.",
    ),
}