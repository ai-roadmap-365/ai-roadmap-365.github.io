import pytest
from examples.evaluation_harness_suite import EvaluationHarnessSuite

def test_add_and_deduplicate_cases():
    suite = EvaluationHarnessSuite()
    assert suite.add_benchmark_case("c1", "happy_path", "Query 1", "Ans 1", is_golden=True) is True
    assert suite.add_benchmark_case("c2", "happy_path", "  query 1  ", "Duplicate", is_golden=False) is False
    assert len(suite.dataset) == 1

def test_multi_tier_metric_scoring():
    suite = EvaluationHarnessSuite()
    suite.add_benchmark_case("c1", "happy_path", "Capital", "Paris is capital", is_golden=False)
    res = suite.run_benchmark_case("c1", "Paris is capital")
    assert res["exact_match"] == 1.0
    assert res["token_f1"] == 1.0
    assert res["composite_score"] == 1.0
    assert res["passed"] is True

def test_json_f1_metric():
    gt = {"name": "Alice", "role": "admin"}
    pred = '{"name": "Alice", "role": "admin"}'
    assert EvaluationHarnessSuite.evaluate_json_f1(pred, gt) == 1.0
    
    partial = '{"name": "Alice", "role": "user"}'
    assert EvaluationHarnessSuite.evaluate_json_f1(partial, gt) == 0.5
    
    invalid = '{"name": "Alice", MALFORMED'
    assert EvaluationHarnessSuite.evaluate_json_f1(invalid, gt) == 0.0

def test_regression_gate_approval():
    suite = EvaluationHarnessSuite(baseline_score=0.80, tolerance_delta=-0.02)
    suite.add_benchmark_case("c1", "happy_path", "Q1", "Answer One", is_golden=True)
    suite.run_benchmark_case("c1", "Answer One")
    report = suite.evaluate_suite_regression()
    assert report["gate_passed"] is True
    assert report["status"] == "APPROVED"
    assert report["delta"] == 0.20

def test_regression_gate_rejection_on_golden_failure():
    suite = EvaluationHarnessSuite(baseline_score=0.50, tolerance_delta=-0.02)
    suite.add_benchmark_case("golden_01", "adversarial", "Q1", "Refused", is_golden=True)
    suite.run_benchmark_case("golden_01", "Accepted forbidden payload")
    report = suite.evaluate_suite_regression()
    assert report["gate_passed"] is False
    assert report["golden_passed"] is False
    assert report["status"] == "REJECTED"
