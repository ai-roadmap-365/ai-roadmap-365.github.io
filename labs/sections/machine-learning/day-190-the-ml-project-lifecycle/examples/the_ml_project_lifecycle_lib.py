from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class ModelEvaluationReport:
    model_name: str
    version: str
    overall_pr_auc: float
    slice_pr_auc: Dict[str, float]
    p99_latency_ms: float
    memory_mb: float
    has_schema_validation: bool
    has_fallback_circuit_breaker: bool

class DeploymentQualityGateEngine:
    def __init__(self, min_pr_auc_improvement: float = 0.015, max_slice_drop: float = 0.02,
                 max_p99_latency_ms: float = 20.0, max_memory_mb: float = 2000.0):
        self.min_pr_auc_improvement = min_pr_auc_improvement
        self.max_slice_drop = max_slice_drop
        self.max_p99_latency_ms = max_p99_latency_ms
        self.max_memory_mb = max_memory_mb

    def evaluate_gates(self, candidate: ModelEvaluationReport, champion: ModelEvaluationReport) -> Dict[str, Any]:
        results = {"passed_all": True, "checks": {}}

        # Gate 1: Overall Metric Superiority
        improvement = candidate.overall_pr_auc - champion.overall_pr_auc
        gate1_passed = improvement >= self.min_pr_auc_improvement
        results["checks"]["metric_superiority"] = {
            "passed": gate1_passed,
            "improvement": round(improvement, 4),
            "required": self.min_pr_auc_improvement
        }

        # Gate 2: Subgroup Slice Regression
        slice_passed = True
        slice_details = {}
        for s_name, champ_score in champion.slice_pr_auc.items():
            cand_score = candidate.slice_pr_auc.get(s_name, 0.0)
            diff = cand_score - champ_score
            passed = diff >= -self.max_slice_drop
            slice_details[s_name] = {"diff": round(diff, 4), "passed": passed}
            if not passed:
                slice_passed = False

        results["checks"]["slice_regression"] = {
            "passed": slice_passed,
            "details": slice_details
        }

        # Gate 3: Operational Latency and Memory SLA
        lat_passed = candidate.p99_latency_ms <= self.max_p99_latency_ms
        mem_passed = candidate.memory_mb <= self.max_memory_mb
        results["checks"]["operational_sla"] = {
            "passed": lat_passed and mem_passed,
            "latency_p99_ms": candidate.p99_latency_ms,
            "memory_mb": candidate.memory_mb
        }

        # Gate 4: Safety, Schema, and Circuit Breakers
        safety_passed = candidate.has_schema_validation and candidate.has_fallback_circuit_breaker
        results["checks"]["safety_infrastructure"] = {
            "passed": safety_passed,
            "schema_validated": candidate.has_schema_validation,
            "circuit_breaker": candidate.has_fallback_circuit_breaker
        }

        results["passed_all"] = gate1_passed and slice_passed and lat_passed and mem_passed and safety_passed
        return results

def run_lifecycle_demo():
    champ = ModelEvaluationReport(
        model_name="churn_classifier", version="v1.0.0",
        overall_pr_auc=0.8420,
        slice_pr_auc={"mobile": 0.835, "desktop": 0.850, "international": 0.810},
        p99_latency_ms=8.5, memory_mb=450.0,
        has_schema_validation=True, has_fallback_circuit_breaker=True
    )
    cand = ModelEvaluationReport(
        model_name="churn_classifier", version="v1.1.0",
        overall_pr_auc=0.8650,
        slice_pr_auc={"mobile": 0.860, "desktop": 0.871, "international": 0.805},
        p99_latency_ms=11.2, memory_mb=620.0,
        has_schema_validation=True, has_fallback_circuit_breaker=True
    )
    engine = DeploymentQualityGateEngine()
    eval_res = engine.evaluate_gates(cand, champ)
    print(f"ML Lifecycle Demo: Candidate Passed All Gates = {eval_res['passed_all']}")
    return engine, eval_res

if __name__ == "__main__":
    run_lifecycle_demo()
