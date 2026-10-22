"""Audit event model. One AuditEvent = one attempted tool call."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from nexus_mcp.authorization import ActionType, Decision, RiskLevel


class ExecutionStatus(str, Enum):
    NOT_EXECUTED = "NOT_EXECUTED"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


def new_request_id() -> str:
    return uuid.uuid4().hex


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class AuditEvent:
    request_id: str
    timestamp: str
    tool_name: str
    arguments: dict[str, Any]
    action_type: ActionType | None
    risk_level: RiskLevel | None
    decision: Decision
    reason: str
    execution_status: ExecutionStatus
    error: str | None = None       # exception class name only, never a message with data
    principal: str | None = None   # filled by authentication on Day 4

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "request_id": self.request_id,
            "tool_name": self.tool_name,
            "arguments": self.arguments,
            "action_type": self.action_type.value if self.action_type else None,
            "risk_level": self.risk_level.value if self.risk_level else None,
            "decision": self.decision.value,
            "reason": self.reason,
            "execution_status": self.execution_status.value,
            "error": self.error,
            "principal": self.principal,
        }