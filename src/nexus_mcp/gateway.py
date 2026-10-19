"""Gateway: the single path to a tool. authorize -> (execute | block) -> audit.

INVARIANT: a tool is never called unless authorization returned ALLOW.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from enum import Enum
from typing import Any

from nexus_mcp.audit import (
    AuditEvent,
    ExecutionStatus,
    JsonlAuditWriter,
    new_request_id,
    sanitize_arguments,
    utc_now_iso,
)
from nexus_mcp.authorization import AuthzResult, Decision, authorize
from nexus_mcp.config import Settings
from nexus_mcp.tools import cancel_order, create_order, get_customer
from nexus_mcp.tools.errors import ToolInputError, ToolNotFoundError

ToolFunc = Callable[..., dict]


class Outcome(str, Enum):
    EXECUTED = "EXECUTED"
    DENIED = "DENIED"
    FAILED = "FAILED"


@dataclass(frozen=True)
class GatewayResult:
    request_id: str
    outcome: Outcome
    decision: Decision
    execution_status: ExecutionStatus
    result: dict | None
    message: str


def default_tools() -> dict[str, ToolFunc]:
    return {
        "get_customer": get_customer,
        "create_order": create_order,
        "cancel_order": cancel_order,
    }


class Gateway:
    def __init__(
        self,
        tools: Mapping[str, ToolFunc],
        audit: Any,  # anything with .write(AuditEvent)
        authorizer: Callable[[str], AuthzResult] = authorize,
    ) -> None:
        self._tools = dict(tools)
        self._audit = audit
        self._authorizer = authorizer

    def call(
        self,
        tool_name: str,
        arguments: Mapping[str, Any] | None = None,
        principal: str | None = None,
    ) -> GatewayResult:
        args = dict(arguments or {})
        request_id = new_request_id()
        authz = self._authorizer(tool_name)

        # 1) DENY: record and return. The tool is NOT looked up and NOT called.
        if authz.decision is not Decision.ALLOW:
            self._record(request_id, authz, args, ExecutionStatus.NOT_EXECUTED, None, principal)
            return GatewayResult(
                request_id, Outcome.DENIED, authz.decision, ExecutionStatus.NOT_EXECUTED,
                None, f"Action denied by policy: {authz.reason}",
            )

        # 2) ALLOW: execute and record the real outcome.
        func = self._tools.get(tool_name)
        if func is None:
            self._record(request_id, authz, args, ExecutionStatus.FAILED, "ToolNotImplemented", principal)
            return GatewayResult(
                request_id, Outcome.FAILED, authz.decision, ExecutionStatus.FAILED,
                None, "Tool is allowed by policy but not implemented.",
            )

        try:
            result = func(**args)
        except (ToolInputError, ToolNotFoundError) as exc:
            self._record(request_id, authz, args, ExecutionStatus.FAILED, type(exc).__name__, principal)
            return GatewayResult(
                request_id, Outcome.FAILED, authz.decision, ExecutionStatus.FAILED, None, str(exc),
            )
        except Exception as exc:  # noqa: BLE001 - unexpected tool failure, do not leak details
            self._record(request_id, authz, args, ExecutionStatus.FAILED, type(exc).__name__, principal)
            return GatewayResult(
                request_id, Outcome.FAILED, authz.decision, ExecutionStatus.FAILED,
                None, "Tool execution failed.",
            )

        self._record(request_id, authz, args, ExecutionStatus.SUCCESS, None, principal)
        return GatewayResult(
            request_id, Outcome.EXECUTED, authz.decision, ExecutionStatus.SUCCESS, result, "OK",
        )

    def _record(
        self,
        request_id: str,
        authz: AuthzResult,
        args: dict[str, Any],
        status: ExecutionStatus,
        error: str | None,
        principal: str | None,
    ) -> None:
        self._audit.write(
            AuditEvent(
                request_id=request_id,
                timestamp=utc_now_iso(),
                tool_name=authz.tool_name,
                arguments=sanitize_arguments(args),
                action_type=authz.action_type,
                risk_level=authz.risk_level,
                decision=authz.decision,
                reason=authz.reason,
                execution_status=status,
                error=error,
                principal=principal,
            )
        )


def build_default_gateway(settings: Settings, tools: Mapping[str, ToolFunc] | None = None) -> Gateway:
    return Gateway(
        tools=tools if tools is not None else default_tools(),
        audit=JsonlAuditWriter(settings.audit_file_path),
    )