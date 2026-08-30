import pytest
import os
from examples.dataset_curator import EvalDatasetCurator

def test_add_record_valid():
    curator = EvalDatasetCurator()
    assert curator.add_record("id_01", "happy_path", "Hello", "Hi there") is True
    assert len(curator.records) == 1

def test_add_record_invalid_category_or_empty():
    curator = EvalDatasetCurator()
    assert curator.add_record("id_02", "unknown_category", "Hello", "Hi") is False
    assert curator.add_record("id_03", "happy_path", "", "Hi") is False
    assert curator.add_record("id_04", "happy_path", "Hello", "") is False

def test_deduplication():
    curator = EvalDatasetCurator()
    assert curator.add_record("id_01", "happy_path", "What is Python?", "A language") is True
    assert curator.add_record("id_02", "happy_path", "  what is python?  ", "Duplicate") is False
    assert len(curator.records) == 1

def test_stratified_counts():
    curator = EvalDatasetCurator()
    curator.add_record("id_01", "happy_path", "Query 1", "Ans 1")
    curator.add_record("id_02", "hard_negative", "Query 2", "Ans 2")
    curator.add_record("id_03", "adversarial", "Query 3", "Ans 3")
    counts = curator.get_stratified_counts()
    assert counts["happy_path"] == 1
    assert counts["hard_negative"] == 1
    assert counts["adversarial"] == 1
    assert counts["schema_boundary"] == 0

def test_jsonl_export_and_import(tmp_path):
    curator = EvalDatasetCurator()
    curator.add_record("id_01", "happy_path", "Query 1", "Ans 1")
    curator.add_record("id_02", "schema_boundary", "Query 2", "Ans 2")
    
    file_path = str(tmp_path / "test_eval.jsonl")
    exported_count = curator.export_jsonl(file_path)
    assert exported_count == 2
    assert os.path.exists(file_path)
    
    new_curator = EvalDatasetCurator()
    loaded_count = new_curator.load_jsonl(file_path)
    assert loaded_count == 2
    assert len(new_curator.records) == 2
