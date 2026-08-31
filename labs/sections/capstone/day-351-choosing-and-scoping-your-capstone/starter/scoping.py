"""STARTER -- implement each TASK below, then run the tests.

Every function that raises NotImplementedError is yours to write. The
imports, constants and data structures are given; the logic is not.
Run `bash tests/run_tests.sh` to see which tasks are still outstanding.
"""

import json
from typing import Dict, Any, List, Tuple

class CapstoneScopingValidator:

    def __init__(self, project_charter: Dict[str, Any]):
        self.charter = project_charter
        self.pillars = ['data_ingestion', 'core_ai_reasoning', 'automated_evals', 'cloud_deployment', 'observability', 'security_hardening']

    def validate_pillars(self) -> Tuple[bool, List[str]]:
        raise NotImplementedError('TASK 1: implement validate_pillars.')

    def evaluate_feasibility(self) -> Dict[str, Any]:
        raise NotImplementedError('TASK 2: implement evaluate_feasibility.')
if __name__ == '__main__':
    charter = {'title': 'Enterprise Financial Analyst Assistant', 'archetype': 'enterprise_rag', 'slas': {'p95_latency_ms': 450, 'min_eval_accuracy': 0.88, 'monthly_budget_usd': 30}, 'engineering_pillars': {'data_ingestion': {'enabled': True, 'method': 'hybrid_vector_bm25'}, 'core_ai_reasoning': {'enabled': True, 'method': 'fastapi_structured_llm'}, 'automated_evals': {'enabled': True, 'method': 'ragas_triad_suite'}, 'cloud_deployment': {'enabled': True, 'method': 'docker_compose_k8s'}, 'observability': {'enabled': True, 'method': 'opentelemetry_prometheus'}, 'security_hardening': {'enabled': True, 'method': 'pii_vault_prompt_waf'}}}
    validator = CapstoneScopingValidator(charter)
    print(json.dumps(validator.evaluate_feasibility(), indent=2))
