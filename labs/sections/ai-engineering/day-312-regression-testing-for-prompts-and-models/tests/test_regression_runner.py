import pytest
from examples.regression_runner import RegressionTestRunner

def test_regression_gate_approved_on_improvement():
    runner = RegressionTestRunner(tolerance_delta=-0.02)
    base = {"accuracy": 0.85, "schema_validity": 1.0, "failed_golden_cases": []}
    cand = {"accuracy": 0.89, "schema_validity": 1.0, "failed_golden_cases": []}
    res = runner.evaluate_regression(base, cand)
    assert res["gate_passed"] is True
    assert res["status"] == "APPROVED"
    assert res["accuracy_delta"] == 0.04

def test_regression_gate_approved_within_tolerance():
    runner = RegressionTestRunner(tolerance_delta=-0.02)
    base = {"accuracy": 0.90, "schema_validity": 1.0, "failed_golden_cases": []}
    cand = {"accuracy": 0.89, "schema_validity": 1.0, "failed_golden_cases": []}
    res = runner.evaluate_regression(base, cand)
    assert res["gate_passed"] is True
    assert res["status"] == "APPROVED"
    assert res["accuracy_delta"] == -0.01

def test_regression_gate_rejected_on_severe_accuracy_drop():
    runner = RegressionTestRunner(tolerance_delta=-0.02)
    base = {"accuracy": 0.90, "schema_validity": 1.0, "failed_golden_cases": []}
    cand = {"accuracy": 0.84, "schema_validity": 1.0, "failed_golden_cases": []}
    res = runner.evaluate_regression(base, cand)
    assert res["gate_passed"] is False
    assert res["status"] == "REJECTED"
    assert res["accuracy_delta"] == -0.06

def test_regression_gate_rejected_on_schema_invalidity():
    runner = RegressionTestRunner(tolerance_delta=-0.02)
    base = {"accuracy": 0.80, "schema_validity": 1.0, "failed_golden_cases": []}
    cand = {"accuracy": 0.95, "schema_validity": 0.90, "failed_golden_cases": []}
    res = runner.evaluate_regression(base, cand)
    assert res["gate_passed"] is False
    assert res["schema_validity_passed"] is False
    assert res["status"] == "REJECTED"

def test_regression_gate_rejected_on_golden_failure():
    runner = RegressionTestRunner(tolerance_delta=-0.02)
    base = {"accuracy": 0.85, "schema_validity": 1.0, "failed_golden_cases": []}
    cand = {"accuracy": 0.90, "schema_validity": 1.0, "failed_golden_cases": ["case_auth_01"]}
    res = runner.evaluate_regression(base, cand)
    assert res["gate_passed"] is False
    assert res["golden_invariants_passed"] is False
    assert res["failed_golden_count"] == 1
    assert res["status"] == "REJECTED"
