import pytest

from nexus_mcp.tools.cancel_order import cancel_order
from nexus_mcp.tools.create_order import create_order, reset_orders
from nexus_mcp.tools.get_customer import get_customer
from nexus_mcp.tools.errors import ToolInputError, ToolNotFoundError

@pytest.fixture(autouse=True)
def _reset():
    reset_orders()


def test_get_customer_returns_known_customer():
    assert get_customer(1)["name"] == "Ada Lovelace"


def test_get_customer_returns_a_copy():
    get_customer(1)["name"] = "changed"
    assert get_customer(1)["name"] == "Ada Lovelace"


def test_get_customer_unknown_raises_not_found():
    with pytest.raises(ToolNotFoundError):
        get_customer(999)


@pytest.mark.parametrize("bad", [0, -1, "1", None, True, 1.5])
def test_get_customer_rejects_invalid_id(bad):
    with pytest.raises(ToolInputError):
        get_customer(bad)


def test_create_order_is_deterministic():
    items = [{"sku": "A-1", "quantity": 2}]
    first = create_order(1, items)
    second = create_order(1, items)
    assert first["order_id"] == 1001
    assert second["order_id"] == 1002
    assert first["status"] == "CREATED"


@pytest.mark.parametrize(
    "items",
    [[], None, "x", [1], [{"quantity": 1}], [{"sku": "", "quantity": 1}],
     [{"sku": "A", "quantity": 0}]],
)
def test_create_order_rejects_invalid_items(items):
    with pytest.raises(ToolInputError):
        create_order(1, items)


def test_cancel_order_direct_call_works_but_is_not_exposed_by_policy():
    # Direct tool test only. Through Nexus this tool is denied by policy.
    assert cancel_order(1042) == {"order_id": 1042, "status": "CANCELLED"}