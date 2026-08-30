import pytest
from examples.chat_stream_frontend import ChatStreamFrontendEngine

def test_optimistic_user_message():
    engine = ChatStreamFrontendEngine()
    asst_placeholder = engine.submit_user_message("Explain quantum computing")
    assert len(engine.messages) == 2
    assert engine.messages[0]["role"] == "user"
    assert engine.messages[0]["content"] == "Explain quantum computing"
    assert asst_placeholder["role"] == "assistant"
    assert engine.is_streaming is True

def test_append_stream_tokens():
    engine = ChatStreamFrontendEngine()
    engine.submit_user_message("Count to 3")
    engine.append_stream_token("1, ")
    engine.append_stream_token("2, ")
    res = engine.append_stream_token("3.")
    assert res == "1, 2, 3."
    assert engine.messages[-1]["content"] == "1, 2, 3."

def test_smart_auto_scroll_behavior():
    engine = ChatStreamFrontendEngine()
    # At bottom (< 50px)
    assert engine.set_viewport_scroll(10.0) == "AUTO_SCROLL_STICK"
    assert engine.is_scrolled_to_bottom is True
    
    # Scrolled up (> 50px)
    assert engine.set_viewport_scroll(150.0) == "AUTO_SCROLL_LOCKED"
    assert engine.is_scrolled_to_bottom is False

def test_abort_stream_preserves_partial():
    engine = ChatStreamFrontendEngine()
    engine.submit_user_message("Generate code")
    engine.append_stream_token("def add(a, b):")
    abort_res = engine.abort_stream()
    assert abort_res["status"] == "ABORTED"
    assert abort_res["partial_content"] == "def add(a, b):"
    assert engine.is_streaming is False
    assert engine.messages[-1]["status"] == "aborted"
    
    # New token after abort should return None
    assert engine.append_stream_token(" return a + b") is None

def test_complete_stream():
    engine = ChatStreamFrontendEngine()
    engine.submit_user_message("Hello")
    engine.append_stream_token("World")
    done_res = engine.complete_stream()
    assert done_res["status"] == "COMPLETED"
    assert done_res["final_content"] == "World"
    assert engine.messages[-1]["status"] == "completed"
