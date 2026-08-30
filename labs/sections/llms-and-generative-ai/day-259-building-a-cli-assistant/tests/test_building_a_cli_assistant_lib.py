import pytest
from examples.building_a_cli_assistant_lib import (
    CLIAssistantCore
)

def test_context_builder_and_system_pinning():
    assistant = CLIAssistantCore("System instructions here.", max_history_turns=2)
    ctx = assistant.build_message_context("First question")

    assert len(ctx) == 2
    assert ctx[0]["role"] == "system"
    assert ctx[0]["content"] == "System instructions here."
    assert ctx[1]["role"] == "user"
    assert ctx[1]["content"] == "First question"

def test_sliding_window_eviction():
    assistant = CLIAssistantCore("Sys", max_history_turns=2) # Max 4 items in deque (2 pairs)
    assistant.record_turn("Q1", "A1")
    assistant.record_turn("Q2", "A2")
    assistant.record_turn("Q3", "A3") # Q1, A1 should be evicted

    ctx = assistant.build_message_context("Q4")
    # Expected: sys + Q2 + A2 + Q3 + A3 + Q4 = 6 items
    assert len(ctx) == 6
    assert ctx[1]["content"] == "Q2"
    assert ctx[3]["content"] == "Q3"
    assert ctx[5]["content"] == "Q4"

def test_slash_commands():
    assistant = CLIAssistantCore("Sys")
    assistant.register_tool("test_tool", lambda: "ok")
    assistant.record_turn("Q", "A", tokens=500, cost=0.002)

    assert "Available commands" in assistant.handle_slash_command("/help")
    assert "$0.0020" in assistant.handle_slash_command("/cost")
    assert "test_tool" in assistant.handle_slash_command("/tools")

    clear_res = assistant.handle_slash_command("/clear")
    assert "cleared" in clear_res
    assert len(assistant.history) == 0

def test_tool_registration():
    assistant = CLIAssistantCore("Sys")
    assistant.register_tool("add", lambda a, b: a + b)
    assert assistant.tools["add"](10, 5) == 15
