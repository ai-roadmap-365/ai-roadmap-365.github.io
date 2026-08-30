import pytest
from examples.production_assistant import ProductionAssistantEngine

def test_index_and_process_grounded_query():
    assistant = ProductionAssistantEngine(confidence_threshold=0.50)
    assistant.index_document("doc_ret", "Return Policy", "3.2", "Footwear returns accepted within 30 days of purchase in original packaging")
    
    res = assistant.process_query("Footwear returns purchase")
    assert res["status"] == "SUCCESS"
    assert res["confidence_score"] >= 0.50
    assert len(res["citations"]) == 1
    assert res["citations"][0]["doc_id"] == "doc_ret"
    assert "[doc_ret: §3.2]" in res["answer"]
    assert "telemetry" in res

def test_refusal_on_low_confidence():
    assistant = ProductionAssistantEngine(confidence_threshold=0.60)
    assistant.index_document("doc_db", "Postgres", "1.0", "PostgreSQL database vacuuming guide")
    
    res = assistant.process_query("how to bake chocolate cookies with vanilla icing")
    assert res["status"] == "REFUSED_LOW_CONFIDENCE"
    assert res["citations"] == []
    assert "sufficient verified documentation" in res["answer"].lower()

def test_empty_knowledge_base():
    assistant = ProductionAssistantEngine()
    res = assistant.process_query("anything")
    assert res["status"] == "REFUSED_EMPTY_KNOWLEDGE_BASE"
    assert res["citations"] == []

def test_citation_payload_structure():
    assistant = ProductionAssistantEngine(confidence_threshold=0.30)
    assistant.index_document("sec_10k", "Annual Report", "Item 1A", "Risk factors include currency volatility and interest rate changes")
    
    res = assistant.process_query("Risk factors currency volatility")
    assert res["status"] == "SUCCESS"
    citation = res["citations"][0]
    assert citation["doc_id"] == "sec_10k"
    assert citation["section"] == "Item 1A"
    assert citation["title"] == "Annual Report"

def test_telemetry_latency_tracking():
    assistant = ProductionAssistantEngine()
    assistant.index_document("d1", "T", "1", "alpha beta gamma")
    res = assistant.process_query("alpha beta")
    assert "latency_ms" in res["telemetry"]
    assert res["telemetry"]["candidates_evaluated"] == 1
