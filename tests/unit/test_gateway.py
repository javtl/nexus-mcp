import json

import pytest

from nexus_mcp.audit import ExecutionStatus, JsonlAuditWriter
from nexus_mcp.authorization import Decision
from nexus_mcp.gateway import Gateway, Outcome
from nexus_mcp.tools.errors import ToolInputError


class Spy:
    def __init__(self, result=None, exc=None):
        self.calls = []
        self._result = result if result is not None else {"ok": True}
        self._exc = exc

    def __call__(self, **kwargs):
        self.calls.append(kwargs)
        if self._exc:
            raise self._exc
        return self._result


class BrokenWriter:
    def write(self, event):
        raise OSError("disk full")


def events(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


@pytest.fixture
def audit_path(tmp_path):
    return tmp_path / "audit.jsonl"


def gateway(tools, audit_path):
    return Gateway(tools=tools, audit=JsonlAuditWriter(audit_path))


def test_deny_never_executes_the_tool(audit_path):
    spy = Spy()
    result = gateway({"cancel_order": spy}, audit_path).call("cancel_order", {"order_id": 1042})
    assert spy.calls == []
    assert result.outcome is Outcome.DENIED
    assert result.execution_status is ExecutionStatus.NOT_EXECUTED
    assert result.result is None
    [event] = events(audit_path)
    assert event["decision"] == "DENY" and event["execution_status"] == "NOT_EXECUTED"
    assert event["arguments"] == {"order_id": 1042}


def test_allow_executes_and_audits_success(audit_path):
    spy = Spy(result={"customer_id": 1})
    result = gateway({"get_customer": spy}, audit_path).call("get_customer", {"customer_id": 1})
    assert spy.calls == [{"customer_id": 1}]
    assert result.outcome is Outcome.EXECUTED and result.result == {"customer_id": 1}
    [event] = events(audit_path)
    assert event["decision"] == "ALLOW" and event["execution_status"] == "SUCCESS"


def test_allowed_tool_that_fails_is_audited_as_failed(audit_path):
    spy = Spy(exc=ToolInputError("customer_id must be a positive integer"))
    result = gateway({"get_customer": spy}, audit_path).call("get_customer", {"customer_id": -1})
    assert result.outcome is Outcome.FAILED
    assert "positive integer" in result.message
    [event] = events(audit_path)
    assert event["decision"] == "ALLOW"
    assert event["execution_status"] == "FAILED"
    assert event["error"] == "ToolInputError"


def test_unexpected_exception_does_not_leak_details(audit_path):
    spy = Spy(exc=RuntimeError("secret internal detail"))
    result = gateway({"get_customer": spy}, audit_path).call("get_customer", {"customer_id": 1})
    assert result.message == "Tool execution failed."
    [event] = events(audit_path)
    assert event["error"] == "RuntimeError"
    assert "secret internal detail" not in json.dumps(event)


def test_unknown_tool_is_denied_and_audited(audit_path):
    spy = Spy()
    result = gateway({"drop_database": spy}, audit_path).call("drop_database", {})
    assert spy.calls == []
    assert result.decision is Decision.DENY
    [event] = events(audit_path)
    assert event["tool_name"] == "drop_database" and event["risk_level"] is None


def test_allowed_by_policy_but_not_registered_is_failed(audit_path):
    result = gateway({}, audit_path).call("get_customer", {"customer_id": 1})
    assert result.outcome is Outcome.FAILED
    [event] = events(audit_path)
    assert event["error"] == "ToolNotImplemented"


def test_audit_failure_never_turns_a_deny_into_execution():
    spy = Spy()
    gw = Gateway(tools={"cancel_order": spy}, audit=BrokenWriter())
    with pytest.raises(OSError):
        gw.call("cancel_order", {"order_id": 1})
    assert spy.calls == []


def test_sensitive_arguments_are_redacted_in_audit(audit_path):
    spy = Spy()
    gateway({"get_customer": spy}, audit_path).call(
        "get_customer", {"customer_id": 1, "access_token": "SUPERSECRET"}
    )
    text = audit_path.read_text(encoding="utf-8")
    assert "SUPERSECRET" not in text and "[REDACTED]" in text