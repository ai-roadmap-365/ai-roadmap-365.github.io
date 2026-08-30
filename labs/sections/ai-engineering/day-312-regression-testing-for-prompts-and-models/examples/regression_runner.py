from typing import Dict, Any, List

class RegressionTestRunner:
    def __init__(self, tolerance_delta: float = -0.02):
        self.tolerance_delta = tolerance_delta
        
    def evaluate_regression(
        self,
        baseline_results: Dict[str, Any],
        candidate_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        base_accuracy = float(baseline_results.get("accuracy", 0.0))
        cand_accuracy = float(candidate_results.get("accuracy", 0.0))
        
        delta = round(cand_accuracy - base_accuracy, 4)
        
        base_schema_validity = float(baseline_results.get("schema_validity", 1.0))
        cand_schema_validity = float(candidate_results.get("schema_validity", 1.0))
        
        passed_schema = cand_schema_validity >= 1.0
        passed_tolerance = delta >= self.tolerance_delta
        
        cand_failed_golden = candidate_results.get("failed_golden_cases", [])
        passed_golden = len(cand_failed_golden) == 0
        
        gate_passed = passed_schema and passed_tolerance and passed_golden
        
        return {
            "gate_passed": gate_passed,
            "baseline_accuracy": base_accuracy,
            "candidate_accuracy": cand_accuracy,
            "accuracy_delta": delta,
            "schema_validity_passed": passed_schema,
            "golden_invariants_passed": passed_golden,
            "failed_golden_count": len(cand_failed_golden),
            "status": "APPROVED" if gate_passed else "REJECTED"
        }

if __name__ == "__main__":
    runner = RegressionTestRunner(tolerance_delta=-0.02)
    base = {"accuracy": 0.90, "schema_validity": 1.0, "failed_golden_cases": []}
    cand = {"accuracy": 0.92, "schema_validity": 1.0, "failed_golden_cases": []}
    print("Report:", runner.evaluate_regression(base, cand))
