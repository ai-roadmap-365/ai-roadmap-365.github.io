import pytest
from examples.tool_use_and_function_calling_lib import (
    ToolDispatcher,
    calculate_tax,
    get_order_status
)

def test_tool_registration_and_execution():
    dispatcher = ToolDispatcher()
    dispatcher.register_tool("tax", "Calc tax", {}, calculate_tax)

    res = dispatcher.execute_tool("tax", {"amount": 100.0, "state": "CA"})
    assert res == "107.25"

def test_unregistered_tool():
    dispatcher = ToolDispatcher()
    res = dispatcher.execute_tool("unknown", {})
    assert "Error: Tool 'unknown' is not registered." in res

def test_agent_turn_packaging():
    dispatcher = ToolDispatcher()
    dispatcher.register_tool("order", "Order lookup", {}, get_order_status)

    mock_resp = {
        "stop_reason": "tool_use",
        "content": [{
            "type": "tool_use",
            "id": "call_ord_99",
            "name": "order",
            "input": {"order_id": "ORD-101"}
        }]
    }

    turn_output = dispatcher.run_agent_turn(mock_resp)
    assert not turn_output["is_complete"]
    assert turn_output["tool_results"][0]["tool_use_id"] == "call_ord_99"
    assert turn_output["tool_results"][0]["content"] == "Shipped"
