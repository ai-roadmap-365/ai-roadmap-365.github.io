import pytest
from examples.ingestion_pipeline import ProductionIngestionPipeline

def test_initial_ingestion_creates_chunks():
    pipeline = ProductionIngestionPipeline()
    text = "word " * 45  # 45 words -> 3 chunks of size 20, 20, 5
    res = pipeline.ingest_document("doc1", text)
    assert res["status"] == "INDEXED_SUCCESS"
    assert res["chunks_created"] == 3
    assert len(pipeline.vector_index) == 3
    assert "doc1" in pipeline.metadata_store

def test_idempotent_skip_on_duplicate_hash():
    pipeline = ProductionIngestionPipeline()
    text = "Unique content text for idempotent hashing verification."
    res1 = pipeline.ingest_document("doc_hash", text)
    res2 = pipeline.ingest_document("doc_hash", text)
    
    assert res1["status"] == "INDEXED_SUCCESS"
    assert res2["status"] == "SKIPPED_UNCHANGED"
    assert res1["hash"] == res2["hash"]

def test_cascade_deletion_on_document_update():
    pipeline = ProductionIngestionPipeline()
    res1 = pipeline.ingest_document("doc_update", "Old version text " * 30)
    assert len(pipeline.vector_index) == 5
    
    res2 = pipeline.ingest_document("doc_update", "New shortened content")
    assert res2["status"] == "INDEXED_SUCCESS"
    assert len(pipeline.vector_index) == 1
    assert "doc_update_c0" in pipeline.vector_index
    assert "doc_update_c3" not in pipeline.vector_index  # Old chunk purged

def test_cascade_delete_document():
    pipeline = ProductionIngestionPipeline()
    pipeline.ingest_document("doc_del", "Text to be deleted " * 25)
    assert "doc_del" in pipeline.metadata_store
    
    res = pipeline.delete_document("doc_del")
    assert res["status"] == "DELETED_CASCADE_SUCCESS"
    assert "doc_del" not in pipeline.metadata_store
    assert len(pipeline.vector_index) == 0

def test_dlq_on_invalid_payload():
    pipeline = ProductionIngestionPipeline()
    res = pipeline.ingest_document("doc_bad", "")
    assert res["status"] == "FAILED_TO_DLQ"
    assert len(pipeline.dead_letter_queue) == 1
    assert pipeline.dead_letter_queue[0]["doc_id"] == "doc_bad"
