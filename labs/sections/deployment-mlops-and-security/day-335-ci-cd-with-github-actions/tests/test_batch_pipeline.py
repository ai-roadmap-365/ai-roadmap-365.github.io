import pytest
from examples.batch_pipeline import DistributedBatchPipeline

def test_successful_batch_and_checkpoint():
    pipeline = DistributedBatchPipeline(max_retries=3)
    pipeline.enqueue_batch("b1", [{"id": "doc1"}, {"id": "doc2"}])
    
    res = pipeline.run_worker_cycle()
    assert res["batches_completed"] == 1
    assert res["batches_quarantined_dlq"] == 0
    assert "b1" in pipeline.completed_checkpoints
    assert pipeline.completed_checkpoints["b1"]["item_count"] == 2

def test_idempotent_skip():
    pipeline = DistributedBatchPipeline(max_retries=3)
    pipeline.completed_checkpoints["b1"] = {"status": "COMPLETED"}
    
    # Process already-completed batch
    pipeline.enqueue_batch("b1", [{"id": "doc1"}])
    res = pipeline.run_worker_cycle()
    assert res["batches_completed"] == 1
    assert len(pipeline.dead_letter_queue) == 0

def test_dlq_quarantine_on_poison_pill():
    pipeline = DistributedBatchPipeline(max_retries=2)
    # Batch contains corrupted item
    pipeline.enqueue_batch("b_bad", [{"id": "ok1"}, {"id": "corrupt1", "is_corrupted": True}])
    
    res = pipeline.run_worker_cycle()
    assert res["batches_completed"] == 0
    assert res["batches_quarantined_dlq"] == 1
    assert len(pipeline.dead_letter_queue) == 1
    assert pipeline.dead_letter_queue[0]["batch_id"] == "b_bad"
    assert "b_bad" not in pipeline.completed_checkpoints

def test_multi_batch_mixed_workload():
    pipeline = DistributedBatchPipeline(max_retries=2)
    pipeline.enqueue_batch("b1", [{"id": "d1"}])
    pipeline.enqueue_batch("b2_bad", [{"id": "d2", "is_corrupted": True}])
    pipeline.enqueue_batch("b3", [{"id": "d3"}])
    
    res = pipeline.run_worker_cycle()
    assert res["batches_completed"] == 2
    assert res["batches_quarantined_dlq"] == 1
    assert len(pipeline.completed_checkpoints) == 2

def test_empty_queue_run():
    pipeline = DistributedBatchPipeline()
    res = pipeline.run_worker_cycle()
    assert res["batches_completed"] == 0
    assert res["batches_quarantined_dlq"] == 0
