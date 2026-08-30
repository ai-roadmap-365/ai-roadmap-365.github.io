import pytest
from examples.evals import CapstoneEvaluationEngine

def test_perfect_faithfulness_calculation():
    engine = CapstoneEvaluationEngine()
    context = "The product price is $49.99 and includes free shipping."
    claims = ["Product price is $49.99", "Includes free shipping"]
    score, unsupp = engine.calculate_faithfulness(claims, context)
    assert score == 1.0
    assert len(unsupp) == 0

def test_hallucination_detection_lowers_faithfulness():
    engine = CapstoneEvaluationEngine()
    context = "The product price is $49.99."
    claims = ["Product price is $49.99", "Free diamond necklace included with every order"]
    score, unsupp = engine.calculate_faithfulness(claims, context)
    assert score == 0.5
    assert len(unsupp) == 1
    assert "Free diamond necklace" in unsupp[0]

def test_context_recall_calculation():
    engine = CapstoneEvaluationEngine()
    context = "Server memory is 64GB DDR5 RAM."
    gt = ["Memory is 64GB DDR5", "Storage is 2TB NVMe"]
    score = engine.calculate_context_recall(gt, context)
    assert score == 0.5

def test_benchmark_suite_pass_gate():
    engine = CapstoneEvaluationEngine(faithfulness_threshold=0.90, recall_threshold=0.85)
    suite = [
        {
            "id": "q1",
            "ground_truth_points": ["SLA is 99.9%"],
            "retrieved_context": "The SLA uptime is 99.9%.",
            "answer_claims": ["SLA is 99.9%"]
        },
        {
            "id": "q2",
            "ground_truth_points": ["Support is 24/7"],
            "retrieved_context": "Customer support is available 24/7.",
            "answer_claims": ["Support is 24/7"]
        }
    ]
    report = engine.run_eval_suite(suite)
    assert report["overall_quality_gate"] == "PASSED"
    assert report["pass_rate_percentage"] == 100.0
    assert report["average_faithfulness"] == 1.0

def test_benchmark_suite_failure_gate():
    engine = CapstoneEvaluationEngine(faithfulness_threshold=0.90, recall_threshold=0.85)
    # Suite with 100% hallucinations
    suite = [{
        "id": "q1",
        "ground_truth_points": ["Expected fact A"],
        "retrieved_context": "Completely unrelated context text.",
        "answer_claims": ["Hallucinated claim X"]
    }]
    report = engine.run_eval_suite(suite)
    assert report["overall_quality_gate"] == "FAILED"
    assert report["pass_rate_percentage"] == 0.0
