import json

import pytest

from nexus_mcp.config import Settings
from nexus_mcp.gateway import Outcome, build_default_gateway, default_tools
from nexus_mcp.tools.create_order import reset_orders


class Spy:
    def __init__(self):
        self.calls = []

    def __call__(self, **kwargs):
        self.calls.append(kwargs)
        return {"order_id": kwargs.get("order_id"), "status": "CANCELLED"}


@pytest.fixture(autouse=True)
def _reset_orders():
    reset_orders()


@pytest.fixture
def audit_path(tmp_path):
    return tmp_path / "audit.jsonl"


def make_gateway(audit_path, tools=None):
    settings = Settings(host="127.0.0.1", port=8000, public_url=None, audit_file_path=str(audit_path))
    return build_default_gateway(settings, tools=tools)


def read_events(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def test_scenario_a_allowed_read(audit_path):
    result = make_gateway(audit_path).call("get_customer", {"customer_id": 1})
    assert result.outcome is Outcome.EXECUTED and result.result["name"] == "Ada Lovelace"
    [event] = read_events(audit_path)
    assert (event["tool_name"], event["decision"], event["execution_status"]) == (
        "get_customer", "ALLOW", "SUCCESS")


def test_scenario_b_allowed_write(audit_path):
    result = make_gateway(audit_path).call(
        "create_order", {"customer_id": 1, "items": [{"sku": "A-1", "quantity": 2}]}
    )
    assert result.outcome is Outcome.EXECUTED and result.result["order_id"] == 1001
    [event] = read_events(audit_path)
    assert (event["tool_name"], event["decision"], event["execution_status"]) == (
        "create_order", "ALLOW", "SUCCESS")
    assert event["risk_level"] == "MEDIUM"


def test_scenario_c_denied_destructive_is_not_executed(audit_path):
    spy = Spy()
    tools = default_tools()
    tools["cancel_order"] = spy          # real policy + real audit, spy as the tool
    result = make_gateway(audit_path, tools).call("cancel_order", {"order_id": 1042})
    assert spy.calls == []               # PROOF: the tool was never invoked
    assert result.outcome is Outcome.DENIED and "denied" in result.message.lower()
    [event] = read_events(audit_path)
    assert (event["decision"], event["execution_status"], event["risk_level"]) == (
        "DENY", "NOT_EXECUTED", "HIGH")
    assert event["reason"]


def test_full_session_produces_one_event_per_attempt(audit_path):
    gw = make_gateway(audit_path)
    gw.call("get_customer", {"customer_id": 1})
    gw.call("create_order", {"customer_id": 1, "items": [{"sku": "A-1", "quantity": 1}]})
    gw.call("cancel_order", {"order_id": 1042})
    gw.call("get_customer", {"customer_id": 999})   # allowed but fails
    statuses = [(e["tool_name"], e["execution_status"]) for e in read_events(audit_path)]
    assert statuses == [
        ("get_customer", "SUCCESS"),
        ("create_order", "SUCCESS"),
        ("cancel_order", "NOT_EXECUTED"),
        ("get_customer", "FAILED"),
    ]