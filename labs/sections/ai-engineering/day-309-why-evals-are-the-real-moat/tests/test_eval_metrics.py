import pytest
from examples.eval_metrics import EvalMetricEngine

def test_exact_match():
    assert EvalMetricEngine.exact_match("San Francisco", "san francisco  ") == 1.0
    assert EvalMetricEngine.exact_match("New York", "Boston") == 0.0

def test_json_field_f1_perfect_match():
    pred = '{"name": "Alice", "role": "Admin"}'
    gt = {"name": "Alice", "role": "Admin"}
    res = EvalMetricEngine.json_field_f1(pred, gt)
    assert res["valid_json"] == 1.0
    assert res["precision"] == 1.0
    assert res["recall"] == 1.0
    assert res["f1"] == 1.0

def test_json_field_f1_partial_match():
    pred = '{"name": "Alice", "role": "User"}'
    gt = {"name": "Alice", "role": "Admin"}
    res = EvalMetricEngine.json_field_f1(pred, gt)
    assert res["valid_json"] == 1.0
    assert res["precision"] == 0.5
    assert res["recall"] == 0.5
    assert res["f1"] == 0.5

def test_json_field_f1_invalid_json():
    pred = '{"name": "Alice", BROKEN JSON'
    gt = {"name": "Alice"}
    res = EvalMetricEngine.json_field_f1(pred, gt)
    assert res["valid_json"] == 0.0
    assert res["f1"] == 0.0

def test_token_overlap_f1():
    pred = "The capital of France is Paris."
    gt = "Paris is the capital of France."
    f1 = EvalMetricEngine.token_overlap_f1(pred, gt)
    assert f1 == 1.0
    
    partial = EvalMetricEngine.token_overlap_f1("Paris is nice", "Tokyo is nice")
    assert 0.0 < partial < 1.0
