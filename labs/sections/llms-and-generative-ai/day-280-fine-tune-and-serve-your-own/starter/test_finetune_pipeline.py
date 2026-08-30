import pytest
import numpy as np
from finetune_pipeline import LoRAWeightMerger, MockModelServer, ModelEvaluationBenchmark

def test_lora_merging_math():
    np.random.seed(42)
    d_out, d_in, r = 32, 32, 4
    alpha = 8.0
    
    base_w = np.random.randn(d_out, d_in).astype(np.float32)
    lora_a = np.random.randn(r, d_in).astype(np.float32)
    lora_b = np.random.randn(d_out, r).astype(np.float32)

    merged = LoRAWeightMerger.merge_weights(base_w, lora_a, lora_b, r=r, alpha=alpha)
    
    expected_delta = np.matmul(lora_b, lora_a) * (8.0 / 4.0)
    expected_merged = base_w + expected_delta
    
    assert np.allclose(merged, expected_merged, atol=1e-5)

def test_lora_invalid_rank():
    base_w = np.zeros((10, 10))
    lora_a = np.zeros((0, 10))
    lora_b = np.zeros((10, 0))
    with pytest.raises(ValueError, match="LoRA rank r must be > 0"):
        LoRAWeightMerger.merge_weights(base_w, lora_a, lora_b, r=0, alpha=16.0)

def test_json_compliance_evaluation():
    valid_cases = ['{"name": "test"}', '{"status": 200, "items": [1, 2]}']
    invalid_cases = ['Not JSON', '{"broken": json}']
    
    score = ModelEvaluationBenchmark.evaluate_json_compliance(valid_cases + invalid_cases)
    assert score == 50.0 # 2 out of 4 valid

def test_exact_match_evaluation():
    preds = ["SELECT * FROM users;", "  SELECT id FROM items;  ", "INVALID"]
    targets = ["SELECT * FROM users;", "SELECT id FROM items;", "SELECT * FROM orders;"]
    
    em = ModelEvaluationBenchmark.evaluate_exact_match(preds, targets)
    assert em == pytest.approx(66.66, 0.1) # 2 out of 3 match

def test_end_to_end_benchmark_comparison():
    base_srv = MockModelServer(is_finetuned=False)
    ft_srv = MockModelServer(is_finetuned=True)

    test_cases = [
        {"prompt": "Generate JSON schema for user 1042", "target": '{"status": "success", "user_id": 1042, "role": "admin"}'},
        {"prompt": "Generate JSON schema for admin", "target": '{"status": "success", "user_id": 1042, "role": "admin"}'}
    ]

    results = ModelEvaluationBenchmark.run_benchmark_comparison(base_srv, ft_srv, test_cases)
    assert results["finetuned_json_compliance"] == 100.0
    assert results["base_json_compliance"] == 0.0
    assert results["finetuned_exact_match"] == 100.0
    assert results["accuracy_improvement"] == 100.0
