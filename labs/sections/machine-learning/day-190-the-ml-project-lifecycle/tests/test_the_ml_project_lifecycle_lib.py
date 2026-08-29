import pytest
from examples.the_ml_project_lifecycle_lib import ModelEvaluationReport, DeploymentQualityGateEngine

def test_quality_gate_passes_superior_candidate():
    champ = ModelEvaluationReport(
        model_name="fraud_model", version="v1.0",
        overall_pr_auc=0.800,
        slice_pr_auc={"tier1": 0.820, "tier2": 0.780},
        p99_latency_ms=10.0, memory_mb=500.0,
        has_schema_validation=True, has_fallback_circuit_breaker=True
    )
    cand = ModelEvaluationReport(
        model_name="fraud_model", version="v1.1",
        overall_pr_auc=0.825, # +0.025 improvement
        slice_pr_auc={"tier1": 0.830, "tier2": 0.810},
        p99_latency_ms=12.0, memory_mb=600.0,
        has_schema_validation=True, has_fallback_circuit_breaker=True
    )
    engine = DeploymentQualityGateEngine(min_pr_auc_improvement=0.015)
    res = engine.evaluate_gates(cand, champ)
    assert res["passed_all"] is True
    assert res["checks"]["metric_superiority"]["passed"] is True

def test_quality_gate_blocks_slice_regression():
    champ = ModelEvaluationReport(
        model_name="fraud_model", version="v1.0",
        overall_pr_auc=0.800,
        slice_pr_auc={"tier1": 0.820, "tier2": 0.780},
        p99_latency_ms=10.0, memory_mb=500.0,
        has_schema_validation=True, has_fallback_circuit_breaker=True
    )
    cand = ModelEvaluationReport(
        model_name="fraud_model", version="v1.1",
        overall_pr_auc=0.830, # +0.030 improvement
        slice_pr_auc={"tier1": 0.890, "tier2": 0.730}, # -0.050 drop on tier2!
        p99_latency_ms=12.0, memory_mb=600.0,
        has_schema_validation=True, has_fallback_circuit_breaker=True
    )
    engine = DeploymentQualityGateEngine(max_slice_drop=0.02)
    res = engine.evaluate_gates(cand, champ)
    assert res["passed_all"] is False
    assert res["checks"]["slice_regression"]["passed"] is False
