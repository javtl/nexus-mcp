from pathlib import Path

import pytest

import nexus_mcp.authorization as authz_pkg
from nexus_mcp.authorization import ActionType, Decision, RiskLevel, authorize


@pytest.mark.parametrize(
    ("tool", "decision", "action", "risk"),
    [
        ("get_customer", Decision.ALLOW, ActionType.READ, RiskLevel.LOW),
        ("create_order", Decision.ALLOW, ActionType.WRITE, RiskLevel.MEDIUM),
        ("cancel_order", Decision.DENY, ActionType.DESTRUCTIVE, RiskLevel.HIGH),
    ],
)
def test_mvp_policy(tool, decision, action, risk):
    result = authorize(tool)
    assert result.decision is decision
    assert result.action_type is action
    assert result.risk_level is risk
    assert result.tool_name == tool
    assert result.reason


def test_cancel_order_is_not_allowed():
    assert authorize("cancel_order").allowed is False


@pytest.mark.parametrize("name", ["drop_database", "", "GET_CUSTOMER", None, 42])
def test_unknown_tools_are_denied(name):
    result = authorize(name)
    assert result.decision is Decision.DENY
    assert result.action_type is None
    assert result.risk_level is None


def test_result_is_immutable():
    result = authorize("cancel_order")
    with pytest.raises(Exception):
        result.decision = Decision.ALLOW  # type: ignore[misc]


def test_authorization_package_never_imports_tools():
    package_dir = Path(authz_pkg.__file__).parent
    for source_file in package_dir.glob("*.py"):
        text = source_file.read_text(encoding="utf-8")
        assert "nexus_mcp.tools" not in text
        assert "from ..tools" not in text