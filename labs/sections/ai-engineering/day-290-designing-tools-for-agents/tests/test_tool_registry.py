import pytest
from typing import Dict, Any
from examples.tool_registry import ToolDefinition, ProductionToolRegistry

def mock_calculator(expr: str) -> str:
    return str(eval(expr, {"__builtins__": None}, {}))

def mock_create_order(item_id: str, quantity: int) -> Dict[str, Any]:
    return {"order_id": "ord_9901", "item": item_id, "qty": quantity, "status": "confirmed"}

@pytest.fixture
def registry():
    reg = ProductionToolRegistry(cache_ttl_seconds=60)
    
    calc_schema = {
        "type": "object",
        "properties": {"expr": {"type": "string"}},
        "required": ["expr"]
    }
    reg.register(ToolDefinition("calculate", "Computes math", calc_schema, mock_calculator, is_mutating=False))
    
    order_schema = {
        "type": "object",
        "properties": {
            "item_id": {"type": "string"},
            "quantity": {"type": "integer"}
        },
        "required": ["item_id", "quantity"]
    }
    reg.register(ToolDefinition("create_order", "Places order", order_schema, mock_create_order, is_mutating=True))
    
    return reg

def test_schema_export(registry):
    schemas = registry.get_schemas()
    assert len(schemas) == 2
    assert schemas[0]["name"] == "calculate"
    assert schemas[1]["name"] == "create_order"

def test_parameter_coercion_string_to_int(registry):
    # Quantity passed as string "4" should coerce to integer 4
    res = registry.execute("create_order", {"item_id": "sku_12", "quantity": "4"})
    assert res["success"] is True
    assert res["result"]["qty"] == 4
    assert res["cached"] is False

def test_missing_required_parameter(registry):
    res = registry.execute("create_order", {"quantity": 5})
    assert res["success"] is False
    assert "Missing required parameter: 'item_id'" in res["error"]

def test_idempotency_cache_suppression(registry):
    args = {"item_id": "sku_widget", "quantity": 2}
    res1 = registry.execute("create_order", args, idempotency_key="key_abc")
    assert res1["success"] is True
    assert res1["cached"] is False
    
    # Duplicate call with identical key should return cached without executing
    res2 = registry.execute("create_order", args, idempotency_key="key_abc")
    assert res2["success"] is True
    assert res2["cached"] is True
    assert res2["result"] == res1["result"]

def test_unknown_tool_rejection(registry):
    res = registry.execute("delete_database", {})
    assert res["success"] is False
    assert "not registered" in res["error"]
