import json
from typing import Dict, Any, List

class ArchitectureLinter:
    def __init__(self):
        self.required_sections = [
            "1. System Overview & Problem Statement",
            "2. High-Level Component Topology",
            "3. Data Flow & Sequence Diagrams",
            "4. Data Schemas & Storage Design",
            "5. Latency & Resource Budgets",
            "6. Failure Mode & Resilience Strategies",
            "7. Security & Compliance Architecture"
        ]

    def lint_add_document(self, text: str) -> Dict[str, Any]:
        missing_sections = [s for s in self.required_sections if s.lower() not in text.lower()]
        has_circuit_breaker = any(term in text.lower() for term in ["circuit breaker", "fallback model", "failover"])
        has_latency_sla = any(term in text.lower() for term in ["latency budget", "p95 latency", "response time budget"])
        
        errors = []
        if missing_sections:
            errors.append(f"Missing mandatory sections: {missing_sections}")
        if not has_circuit_breaker:
            errors.append("Architecture lacks circuit breaker / fallback model resilience specification.")
        if not has_latency_sla:
            errors.append("Architecture lacks p95 latency budget table.")

        score = max(0, 100 - (len(missing_sections) * 10) - (0 if has_circuit_breaker else 20) - (0 if has_latency_sla else 15))
        return {
            "score": score,
            "status": "APPROVED" if score >= 80 and not errors else "REJECTED",
            "errors": errors,
            "missing_sections": missing_sections
        }

if __name__ == "__main__":
    linter = ArchitectureLinter()
    print(linter.lint_add_document("Sample ADD text"))
