import pytest
from examples.query_router import QueryTransformRouter

def test_route_to_sql():
    router = QueryTransformRouter()
    route = router.classify_and_route("What is the total sales revenue for 2026?")
    assert route == "TEXT2SQL_DATABASE"

def test_route_to_vector_rag():
    router = QueryTransformRouter()
    route = router.classify_and_route("How to configure SAML SSO authentication?")
    assert route == "VECTOR_RAG"

def test_route_to_direct_llm_bypass():
    router = QueryTransformRouter()
    route = router.classify_and_route("Hello there!")
    assert route == "DIRECT_LLM_BYPASS"

def test_generate_hyde_document():
    router = QueryTransformRouter()
    doc = router.generate_hyde_document("Fix memory leak in Node.js")
    assert "Fix memory leak in Node.js" in doc
    assert "Technical Documentation:" in doc
    assert len(doc.split()) > 10

def test_expand_query_diversity():
    router = QueryTransformRouter()
    variants = router.expand_query("PostgreSQL index bloat")
    assert len(variants) == 4
    assert variants[0] == "PostgreSQL index bloat"
    assert "troubleshooting steps" in variants[2]
