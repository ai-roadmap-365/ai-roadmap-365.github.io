import pytest
from examples.mcp_resources_prompts import MCPResourcePromptEngine

def test_resources_list_and_read():
    engine = MCPResourcePromptEngine()
    engine.register_resource("memo://plan", "Quarterly Plan", "text/markdown", lambda: "# Q3 Plan\n- Ship MCP")
    
    list_res = engine.handle_request("resources/list")
    assert len(list_res["resources"]) == 1
    assert list_res["resources"][0]["uri"] == "memo://plan"
    
    read_res = engine.handle_request("resources/read", {"uri": "memo://plan"})
    assert read_res["contents"][0]["text"] == "# Q3 Plan\n- Ship MCP"
    assert read_res["contents"][0]["mimeType"] == "text/markdown"

def test_resource_not_found():
    engine = MCPResourcePromptEngine()
    with pytest.raises(ValueError) as exc:
        engine.handle_request("resources/read", {"uri": "nonexistent://file"})
    assert "not found" in str(exc.value)

def test_prompts_list_and_get():
    engine = MCPResourcePromptEngine()
    engine.register_prompt(
        "code_review",
        "Perform code review",
        [{"name": "diff", "required": True}],
        lambda diff: [{"role": "user", "content": {"type": "text", "text": f"Review diff:\n{diff}"}}]
    )
    
    list_res = engine.handle_request("prompts/list")
    assert len(list_res["prompts"]) == 1
    assert list_res["prompts"][0]["name"] == "code_review"
    
    get_res = engine.handle_request("prompts/get", {"name": "code_review", "arguments": {"diff": "+ x = 1"}})
    assert get_res["description"] == "Perform code review"
    assert len(get_res["messages"]) == 1
    assert "Review diff:\n+ x = 1" in get_res["messages"][0]["content"]["text"]

def test_prompt_not_found():
    engine = MCPResourcePromptEngine()
    with pytest.raises(ValueError) as exc:
        engine.handle_request("prompts/get", {"name": "unknown_prompt"})
    assert "not found" in str(exc.value)

def test_unsupported_method():
    engine = MCPResourcePromptEngine()
    with pytest.raises(ValueError) as exc:
        engine.handle_request("invalid/method")
    assert "Unsupported method" in str(exc.value)
