import pytest
from examples.personal_mcp_server import PersonalMCPServer

def test_save_and_search_memo():
    server = PersonalMCPServer(":memory:")
    msg = server.save_memo("Release Notes", "Deployed v1.0.0 to prod", "release,v1")
    assert "ID 1" in msg
    
    results = server.search_memos("Deployed")
    assert len(results) == 1
    assert results[0]["title"] == "Release Notes"
    assert results[0]["tags"] == "release,v1"

def test_search_memos_no_match():
    server = PersonalMCPServer(":memory:")
    server.save_memo("Note 1", "Just some thoughts", "ideas")
    results = server.search_memos("nonexistent_word")
    assert len(results) == 0

def test_todo_management_and_resource():
    server = PersonalMCPServer(":memory:")
    assert server.get_pending_todos_resource() == "No pending todos."
    
    server.add_todo("Review pull request #42")
    server.add_todo("Update documentation")
    
    res = server.get_pending_todos_resource()
    assert "Review pull request #42" in res
    assert "Update documentation" in res

def test_generate_standup_prompt():
    server = PersonalMCPServer(":memory:")
    server.add_todo("Refactor database schema")
    
    prompt = server.generate_standup_prompt("fix: resolve connection timeout")
    assert len(prompt) == 1
    text = prompt[0]["content"]["text"]
    assert "fix: resolve connection timeout" in text
    assert "Refactor database schema" in text
    assert "**1. Completed Yesterday**" in text
