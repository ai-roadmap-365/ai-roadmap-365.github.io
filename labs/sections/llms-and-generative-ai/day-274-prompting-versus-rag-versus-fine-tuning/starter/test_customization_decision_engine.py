import pytest
from customization_decision_engine import ProjectRequirements, CustomizationStrategyEngine

@pytest.fixture
def engine():
    return CustomizationStrategyEngine()

def test_rag_recommendation_for_dynamic_knowledge(engine):
    req = ProjectRequirements(
        task_complexity=0.6,
        knowledge_dynamism=0.95,
        strict_style_adherence=0.3,
        data_privacy_budget=0.5,
        inference_latency_sla_ms=400,
        labeled_data_volume=50,
        monthly_request_volume=20000,
        monthly_budget_usd=1000.0
    )
    res = engine.evaluate_strategy(req)
    assert res["recommended_strategy"] == "RAG_Hybrid"
    assert res["scores"]["RAG_Hybrid"] > res["scores"]["PEFT_LoRA"]
    assert "dynamism" in res["reasoning"].lower()

def test_lora_recommendation_for_strict_style_and_samples(engine):
    req = ProjectRequirements(
        task_complexity=0.7,
        knowledge_dynamism=0.1,
        strict_style_adherence=0.95,
        data_privacy_budget=0.8,
        inference_latency_sla_ms=120,
        labeled_data_volume=2500,
        monthly_request_volume=300000,
        monthly_budget_usd=3000.0
    )
    res = engine.evaluate_strategy(req)
    assert res["recommended_strategy"] == "PEFT_LoRA"
    assert res["scores"]["PEFT_LoRA"] > res["scores"]["Prompting_FewShot"]

def test_prompting_recommendation_for_low_volume_and_simple_task(engine):
    req = ProjectRequirements(
        task_complexity=0.2,
        knowledge_dynamism=0.2,
        strict_style_adherence=0.1,
        data_privacy_budget=0.1,
        inference_latency_sla_ms=800,
        labeled_data_volume=10,
        monthly_request_volume=1000,
        monthly_budget_usd=200.0
    )
    res = engine.evaluate_strategy(req)
    assert res["recommended_strategy"] == "Prompting_FewShot"

def test_cost_break_even_calculation(engine):
    metrics = engine.calculate_cost_break_even(
        prompt_tokens_per_req=3000,
        completion_tokens_per_req=500,
        prompting_cost_per_m=5.0,
        fine_tuned_cost_per_m=2.0,
        fine_tuning_setup_cost_usd=500.0
    )
    assert metrics["prompting_cost_per_request"] == 0.0175
    assert metrics["savings_per_request"] > 0
    assert 25000 < metrics["break_even_requests"] < 40000

def test_score_boundaries(engine):
    req = ProjectRequirements(
        task_complexity=1.0,
        knowledge_dynamism=1.0,
        strict_style_adherence=1.0,
        data_privacy_budget=1.0,
        inference_latency_sla_ms=50,
        labeled_data_volume=0,
        monthly_request_volume=10000000,
        monthly_budget_usd=100000.0
    )
    res = engine.evaluate_strategy(req)
    for score in res["scores"].values():
        assert 0.0 <= score <= 100.0
