import json
from typing import Dict, Any, List, Tuple

class CapstoneScopingValidator:
    def __init__(self, project_charter: Dict[str, Any]):
        self.charter = project_charter
        self.pillars = [
            "data_ingestion",
            "core_ai_reasoning",
            "automated_evals",
            "cloud_deployment",
            "observability",
            "security_hardening"
        ]

    def validate_pillars(self) -> Tuple[bool, List[str]]:
        missing = []
        for p in self.pillars:
            if p not in self.charter.get("engineering_pillars", {}):
                missing.append(f"Missing mandatory pillar: {p}")
            elif not self.charter["engineering_pillars"][p].get("enabled", False):
                missing.append(f"Pillar disabled: {p}")
        return len(missing) == 0, missing

    def evaluate_feasibility(self) -> Dict[str, Any]:
        score = 100.0
        warnings = []

        slas = self.charter.get("slas", {})
        if "p95_latency_ms" not in slas or slas["p95_latency_ms"] > 1000:
            score -= 15.0
            warnings.append("p95 latency SLA missing or exceeding 1000ms threshold")

        if "min_eval_accuracy" not in slas or slas["min_eval_accuracy"] < 0.80:
            score -= 15.0
            warnings.append("Evaluation accuracy target missing or below 80%")

        valid_pillars, missing_pillars = self.validate_pillars()
        if not valid_pillars:
            score -= 10.0 * len(missing_pillars)
            warnings.extend(missing_pillars)

        grade = "EXCELLENT" if score >= 85 else ("VIABLE" if score >= 70 else "AT_RISK")

        return {
            "project_name": self.charter.get("title", "Untitled Capstone"),
            "feasibility_score": max(0.0, score),
            "feasibility_grade": grade,
            "warnings": warnings,
            "is_approved_for_build": score >= 70.0
        }

if __name__ == "__main__":
    charter = {
        "title": "Enterprise Financial Analyst Assistant",
        "archetype": "enterprise_rag",
        "slas": {"p95_latency_ms": 450, "min_eval_accuracy": 0.88, "monthly_budget_usd": 30},
        "engineering_pillars": {
            "data_ingestion": {"enabled": True, "method": "hybrid_vector_bm25"},
            "core_ai_reasoning": {"enabled": True, "method": "fastapi_structured_llm"},
            "automated_evals": {"enabled": True, "method": "ragas_triad_suite"},
            "cloud_deployment": {"enabled": True, "method": "docker_compose_k8s"},
            "observability": {"enabled": True, "method": "opentelemetry_prometheus"},
            "security_hardening": {"enabled": True, "method": "pii_vault_prompt_waf"}
        }
    }
    validator = CapstoneScopingValidator(charter)
    print(json.dumps(validator.evaluate_feasibility(), indent=2))
