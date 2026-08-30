import pytest
from examples.eval_harness import CompleteEvalHarness

def test_evaluate_case_perfect_match():
    harness = CompleteEvalHarness()
    res = harness.evaluate_case("c1", "happy_path", "San Francisco", "San Francisco", is_golden=False)
    assert res["score"] == 1.0
    assert res["passed"] is True

def test_evaluate_case_partial_match():
    harness = CompleteEvalHarness()
    res = harness.evaluate_case("c2", "happy_path", "The capital is Paris", "Paris is the capital", is_golden=False)
    assert res["score"] > 0.4
    assert len(harness.results) == 1

def test_report_approved_on_improvement():
    harness = CompleteEvalHarness(baseline_composite_score=0.80, tolerance_delta=-0.02)
    harness.evaluate_case("c1", "happy_path", "Exact", "Exact", is_golden=True)
    harness.evaluate_case("c2", "happy_path", "Exact", "Exact", is_golden=False)
    report = harness.generate_report()
    assert report["gate_passed"] is True
    assert report["status"] == "APPROVED"
    assert report["delta"] == 0.20

def test_report_rejected_on_regression():
    harness = CompleteEvalHarness(baseline_composite_score=0.95, tolerance_delta=-0.02)
    harness.evaluate_case("c1", "happy_path", "Wrong", "Right", is_golden=False)
    report = harness.generate_report()
    assert report["gate_passed"] is False
    assert report["status"] == "REJECTED"
    assert report["delta"] < -0.02

def test_report_rejected_on_golden_failure():
    harness = CompleteEvalHarness(baseline_composite_score=0.40, tolerance_delta=-0.02)
    harness.evaluate_case("golden_01", "happy_path", "Wrong Answer", "Correct Ground Truth", is_golden=True)
    harness.evaluate_case("normal_02", "happy_path", "Exact", "Exact", is_golden=False)
    report = harness.generate_report()
    assert report["gate_passed"] is False
    assert "golden_01" in report["failed_golden_cases"]
    assert report["status"] == "REJECTED"
