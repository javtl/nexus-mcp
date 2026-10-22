"""Authorization engine: DECIDES. It never executes tools."""

from __future__ import annotations

from .models import AuthzResult, Decision
from .policy import POLICY


def authorize(tool_name: str) -> AuthzResult:
    policy = POLICY.get(tool_name) if isinstance(tool_name, str) else None
    if policy is None:
        return AuthzResult(
            decision=Decision.DENY,
            tool_name=str(tool_name),
            action_type=None,
            risk_level=None,
            reason="Tool is not in the policy; denied by default.",
        )
    return AuthzResult(
        decision=policy.decision,
        tool_name=tool_name,
        action_type=policy.action_type,
        risk_level=policy.risk_level,
        reason=policy.reason,
    )