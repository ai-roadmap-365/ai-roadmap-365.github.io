import pytest
from examples.scoping import CapstoneScopingValidator

@pytest.fixture
def valid_charter():
    return {
        "title": "Medical Diagnostic Assistant",
        "archetype": "enterprise_rag",
        "slas": {"p95_latency_ms": 400, "min_eval_accuracy": 0.90, "monthly_budget_usd": 50},
        "engineering_pillars": {
            "data_ingestion": {"enabled": True},
            "core_ai_reasoning": {"enabled": True},
            "automated_evals": {"enabled": True},
            "cloud_deployment": {"enabled": True},
            "observability": {"enabled": True},
            "security_hardening": {"enabled": True}
        }
    }

def test_valid_charter_evaluation(valid_charter):
    validator = CapstoneScopingValidator(valid_charter)
    res = validator.evaluate_feasibility()
    assert res["feasibility_score"] == 100.0
    assert res["feasibility_grade"] == "EXCELLENT"
    assert res["is_approved_for_build"] is True
    assert len(res["warnings"]) == 0

def test_missing_pillars_penalty(valid_charter):
    del valid_charter["engineering_pillars"]["observability"]
    del valid_charter["engineering_pillars"]["security_hardening"]
    validator = CapstoneScopingValidator(valid_charter)
    res = validator.evaluate_feasibility()
    assert res["feasibility_score"] == 80.0
    assert len(res["warnings"]) == 2

def test_excessive_latency_sla_penalty(valid_charter):
    valid_charter["slas"]["p95_latency_ms"] = 2500
    validator = CapstoneScopingValidator(valid_charter)
    res = validator.evaluate_feasibility()
    assert res["feasibility_score"] == 85.0
    assert any("latency" in w for w in res["warnings"])

def test_low_eval_accuracy_sla_penalty(valid_charter):
    valid_charter["slas"]["min_eval_accuracy"] = 0.65
    validator = CapstoneScopingValidator(valid_charter)
    res = validator.evaluate_feasibility()
    assert res["feasibility_score"] == 85.0
    assert any("accuracy" in w for w in res["warnings"])

def test_unviable_charter_rejection():
    charter = {"title": "Vague Unbounded App"}
    validator = CapstoneScopingValidator(charter)
    res = validator.evaluate_feasibility()
    assert res["feasibility_score"] < 50.0
    assert res["feasibility_grade"] == "AT_RISK"
    assert res["is_approved_for_build"] is False
