import pytest
from examples.production_rag_app import ProductionRAGApp

def test_full_ingestion_and_idempotency():
    app = ProductionRAGApp()
    res1 = app.ingest_document("d1", "Title", "1.0", "This is an important test document text " * 5)
    res2 = app.ingest_document("d1", "Title", "1.0", "This is an important test document text " * 5)
    
    assert res1["status"] == "INDEXED_SUCCESS"
    assert res2["status"] == "SKIPPED_UNCHANGED"
    assert len(app.parent_store) == 1

def test_small_to_big_grounded_search():
    app = ProductionRAGApp(confidence_threshold=0.40)
    app.ingest_document("sec_policy", "Security Policy", "2.1", "All API access tokens must be rotated every 90 days across production clusters")
    
    res = app.query("API access tokens rotated production")
    assert res["status"] == "SUCCESS"
    assert res["confidence"] >= 0.40
    assert len(res["citations"]) == 1
    assert res["citations"][0]["doc_id"] == "sec_policy"
    assert "[sec_policy: §2.1]" in res["answer"]

def test_refusal_on_irrelevant_query():
    app = ProductionRAGApp(confidence_threshold=0.50)
    app.ingest_document("doc_net", "Networking", "1.0", "Kubernetes ingress controller configuration")
    
    res = app.query("how to prepare strawberry cheesecake")
    assert res["status"] == "REFUSED_LOW_CONFIDENCE"
    assert res["citations"] == []

def test_cascade_deletion_on_update():
    app = ProductionRAGApp()
    app.ingest_document("doc_u", "T", "1", "word " * 60, child_size=10) # 6 chunks
    assert len(app.child_index) == 6
    
    app.ingest_document("doc_u", "T", "1", "word " * 20, child_size=10) # 2 chunks
    assert len(app.child_index) == 2

def test_empty_app_query():
    app = ProductionRAGApp()
    res = app.query("anything")
    assert res["status"] == "REFUSED_EMPTY"
