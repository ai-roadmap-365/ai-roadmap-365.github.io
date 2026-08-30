from typing import List, Dict, Any, Callable
import json
import time

class TestCase:
    def __init__(self, test_id: str, inputs: Dict[str, Any], assertions: List[Dict[str, Any]]):
        self.test_id = test_id
        self.inputs = inputs
        self.assertions = assertions

class PromptEvaluationHarness:
    def __init__(self, prompt_runner_fn: Callable[[Dict[str, Any]], str]):
        self.prompt_runner = prompt_runner_fn
        self.test_suite: List[TestCase] = []

    def add_test_case(self, test_id: str, inputs: Dict[str, Any], assertions: List[Dict[str, Any]]) -> "PromptEvaluationHarness":
        self.test_suite.append(TestCase(test_id, inputs, assertions))
        return self

    def run_evaluations(self) -> Dict[str, Any]:
        results = []
        passed_count = 0

        for case in self.test_suite:
            start_time = time.time()
            output = self.prompt_runner(case.inputs)
            latency_ms = (time.time() - start_time) * 1000

            case_passed = True
            failure_reasons = []

            for assertion in case.assertions:
                assert_type = assertion["type"]
                if assert_type == "is_json":
                    try:
                        json.loads(output)
                    except Exception:
                        case_passed = False
                        failure_reasons.append("Output failed valid JSON deserialization.")
                elif assert_type == "contains":
                    if assertion["value"] not in output:
                        case_passed = False
                        failure_reasons.append(f"Missing required substring: '{assertion['value']}'")
                elif assert_type == "contains_no":
                    if assertion["value"] in output:
                        case_passed = False
                        failure_reasons.append(f"Forbidden substring detected: '{assertion['value']}'")

            if case_passed:
                passed_count += 1

            results.append({
                "test_id": case.test_id,
                "passed": case_passed,
                "latency_ms": latency_ms,
                "failures": failure_reasons
            })

        total = len(self.test_suite)
        pass_rate = (passed_count / total) if total > 0 else 0.0

        return {
            "total_tests": total,
            "passed_tests": passed_count,
            "pass_rate": pass_rate,
            "results": results
        }

def mock_prompt_runner(inputs: Dict[str, Any]) -> str:
    query = inputs.get("query", "")
    if "error" in query:
        return '{"status": "ERROR", "code": 500}'
    return '{"status": "SUCCESS", "result": "Calculated value"}'

def run_evaluation_demo():
    harness = PromptEvaluationHarness(mock_prompt_runner)
    harness.add_test_case(
        test_id="case_happy_path",
        inputs={"query": "process transaction"},
        assertions=[{"type": "is_json"}, {"type": "contains", "value": "SUCCESS"}, {"type": "contains_no", "value": "Sure!"}]
    )
    harness.add_test_case(
        test_id="case_error_path",
        inputs={"query": "trigger error"},
        assertions=[{"type": "is_json"}, {"type": "contains", "value": "ERROR"}]
    )

    report = harness.run_evaluations()
    print("Prompt Evaluation Demo Completed. Pass Rate:", report["pass_rate"])
    return report

if __name__ == "__main__":
    run_evaluation_demo()
