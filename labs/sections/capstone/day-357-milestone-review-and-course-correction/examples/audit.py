import time
import json
from typing import Dict, Any, List, Tuple

class Milestone1AuditSuite:
    def __init__(self, max_latency_ms: float = 1500.0, min_faithfulness: float = 0.90):
        self.max_latency_ms = max_latency_ms
        self.min_faithfulness = min_faithfulness

    def profile_vertical_slice(self, mock_pipeline_fn) -> Dict[str, Any]:
        t0 = time.perf_counter()
        breakdown, result = mock_pipeline_fn()
        total_time_ms = round((time.perf_counter() - t0) * 1000.0, 2)

        return {
            "total_latency_ms": total_time_ms,
            "latency_budget_ms": self.max_latency_ms,
            "latency_compliant": total_time_ms <= self.max_latency_ms,
            "component_breakdown_ms": breakdown,
            "output_result": result
        }

    def audit_milestone(self, pipeline_fn, eval_metrics: Dict[str, float]) -> Dict[str, Any]:
        profile = self.profile_vertical_slice(pipeline_fn)
        
        faithfulness_pass = eval_metrics.get("faithfulness", 0.0) >= self.min_faithfulness
        latency_pass = profile["latency_compliant"]
        schema_pass = profile["output_result"].get("schema_valid", False)

        all_passed = faithfulness_pass and latency_pass and schema_pass

        return {
            "milestone": "CAPSTONE_MILESTONE_1",
            "overall_status": "APPROVED" if all_passed else "REJECTED",
            "checks": {
                "latency_budget": "PASS" if latency_pass else "FAIL",
                "faithfulness_accuracy": "PASS" if faithfulness_pass else "FAIL",
                "schema_integrity": "PASS" if schema_pass else "FAIL"
            },
            "metrics": {
                "measured_latency_ms": profile["total_latency_ms"],
                "faithfulness_score": eval_metrics.get("faithfulness", 0.0)
            }
        }

if __name__ == "__main__":
    def sample_pipeline():
        return {"ingress": 1.0, "retrieval": 5.0, "reasoning": 5.0}, {"schema_valid": True, "answer": "Done"}
    auditor = Milestone1AuditSuite()
    print(auditor.audit_milestone(sample_pipeline, {"faithfulness": 0.95}))
