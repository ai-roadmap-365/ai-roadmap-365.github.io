import pytest
from examples.e2e_rag_lib import (
    EndToEndRAGSystem
)

def test_rag_ingestion_and_retrieval():
    rag = EndToEndRAGSystem()
    docs = [
        {"title": "Doc 1", "text": "PostgreSQL 16 logical replication guide"},
        {"title": "Doc 2", "text": "Redis caching and eviction policies"}
    ]
    rag.ingest_corpus(docs)
    results = rag.retrieve("PostgreSQL replication", top_k=1)
    assert len(results) == 1
    assert results[0]["doc"]["title"] == "Doc 1"
    assert results[0]["score"] > 0.0

def test_high_confidence_generation_with_citation():
    rag = EndToEndRAGSystem(confidence_threshold=0.20)
    docs = [{"title": "SLA", "text": "Uptime guarantee is 99.99%"}]
    rag.ingest_corpus(docs)
    response = rag.query("Uptime guarantee")
    assert "99.99%" in response["answer"]
    assert "[1]" in response["answer"]
    assert len(response["citations"]) == 1

def test_low_confidence_fallback_refusal():
    rag = EndToEndRAGSystem(confidence_threshold=0.50)
    docs = [{"title": "Doc A", "text": "Apples are red"}]
    rag.ingest_corpus(docs)
    response = rag.query("quantum mechanics wave equations")
    assert "I do not have sufficient documentation" in response["answer"]
    assert response["confidence"] == 0.0

def test_prompt_synthesis_formatting():
    rag = EndToEndRAGSystem()
    items = [{"doc": {"title": "Test", "text": "Sample text"}, "score": 1.0}]
    prompt = rag.synthesize_prompt("Test question", items)
    assert "Sample text" in prompt
    assert "[1] Source: Test" in prompt
    assert "Question: Test question" in prompt
