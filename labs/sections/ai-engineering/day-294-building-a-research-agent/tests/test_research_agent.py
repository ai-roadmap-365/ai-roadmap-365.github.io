import pytest
from examples.research_agent import NoteStore, DeepResearchAgent

def test_note_store_deduplication():
    store = NoteStore()
    id1 = store.add_note("Fact A", "Title 1", "https://url1.com")
    id2 = store.add_note("Fact A", "Title 1", "https://url1.com")
    assert id1 == 1
    assert id2 == 1
    assert len(store.get_all()) == 1

def test_query_decomposition():
    agent = DeepResearchAgent()
    queries = agent.decompose_query("Solid-state battery roadmap")
    assert len(queries) == 2
    assert "solid state energy density" in queries
    assert "solid state manufacturing cost" in queries

def test_end_to_end_research_synthesis():
    agent = DeepResearchAgent()
    brief = agent.execute_research("Solid-State Batteries")
    assert "# Research Brief: Solid-State Batteries" in brief
    assert "450 Wh/kg" in brief
    assert "$95/kWh" in brief
    assert "## Verified Sources" in brief
    assert "[1] [Nature Energy 2025](https://nature.com/art1)" in brief

def test_empty_search_fallback():
    agent = DeepResearchAgent()
    brief = agent.execute_research("Unknown Futuristic Technology")
    assert "No verified findings discovered." in brief

def test_note_citation_keys_match():
    agent = DeepResearchAgent()
    brief = agent.execute_research("Solid-State Batteries")
    notes = agent.note_store.get_all()
    for note in notes:
        assert f"[{note['id']}]" in brief
