"""Vocabulary of the authorization layer."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Decision(str, Enum):
    ALLOW = "ALLOW"
    DENY = "DENY"


class ActionType(str, Enum):
    READ = "READ"
    WRITE = "WRITE"
    DESTRUCTIVE = "DESTRUCTIVE"


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


@dataclass(frozen=True)
class AuthzResult:
    decision: Decision
    tool_name: str
    action_type: ActionType | None
    risk_level: RiskLevel | None
    reason: str

    @property
    def allowed(self) -> bool:
        return self.decision is Decision.ALLOW