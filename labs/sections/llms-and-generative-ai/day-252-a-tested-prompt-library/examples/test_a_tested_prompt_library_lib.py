import pytest
from examples.a_tested_prompt_library_lib import PromptEvaluationHarness

def test_evaluation_harness_pass_rate():
    def mock_runner(inputs):
        return '{"status": "OK", "id": 100}'

    harness = PromptEvaluationHarness(mock_runner)
    harness.add_test_case("test_1", {"query": "q1"}, [{"type": "is_json"}, {"type": "contains", "value": "OK"}])
    harness.add_test_case("test_2", {"query": "q2"}, [{"type": "contains_no", "value": "INVALID"}])

    report = harness.run_evaluations()
    assert report["total_tests"] == 2
    assert report["passed_tests"] == 2
    assert report["pass_rate"] == 1.0

def test_assertion_failure_tracking():
    def mock_runner(inputs):
        return "Sure! Here is your invalid text output."

    harness = PromptEvaluationHarness(mock_runner)
    harness.add_test_case("test_fail", {"query": "fail"}, [{"type": "is_json"}, {"type": "contains_no", "value": "Sure!"}])

    report = harness.run_evaluations()
    assert report["passed_tests"] == 0
    assert len(report["results"][0]["failures"]) == 2

def test_empty_test_suite_handling():
    harness = PromptEvaluationHarness(lambda x: "")
    report = harness.run_evaluations()

    assert report["total_tests"] == 0
    assert report["pass_rate"] == 0.0
