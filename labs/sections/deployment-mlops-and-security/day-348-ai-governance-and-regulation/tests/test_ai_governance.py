import pytest
from examples.ai_governance import AIGovernanceValidator

def test_high_risk_classification():
    gov = AIGovernanceValidator()
    tier, reqs = gov.assess_eu_risk_tier("recruitment_employment")
    assert tier == "HIGH_RISK"
    assert len(reqs) == 6
    assert any("Risk Management System" in r for r in reqs)

def test_prohibited_unacceptable_risk_flagged():
    gov = AIGovernanceValidator()
    tier, reqs = gov.assess_eu_risk_tier("social_scoring")
    assert tier == "UNACCEPTABLE_RISK"
    assert "BANNED" in reqs[0]

def test_gpai_systemic_risk_classification():
    gov = AIGovernanceValidator()
    tier, reqs = gov.assess_eu_risk_tier("general_assistant", is_gpai=True, training_flops=2e25)
    assert tier == "GPAI"
    assert any("SYSTEMIC RISK" in r for r in reqs)

def test_disparate_impact_fairness_calculation():
    gov = AIGovernanceValidator()
    
    # 17% vs 20% -> 0.85 -> Compliant (>= 0.80)
    ratio, compliant = gov.calculate_disparate_impact(0.17, 0.20)
    assert ratio == 0.85
    assert compliant is True
    
    # 12% vs 20% -> 0.60 -> Non-compliant (< 0.80)
    ratio_bad, compliant_bad = gov.calculate_disparate_impact(0.12, 0.20)
    assert ratio_bad == 0.60
    assert compliant_bad is False

def test_model_card_generation():
    gov = AIGovernanceValidator()
    card = gov.generate_model_card(
        model_id="fin-gpt-v1",
        author="FinCorp Security",
        intended_use="Loan application risk assessment",
        risk_tier="HIGH_RISK",
        evaluation_metrics={"accuracy": 0.94, "disparate_impact": 0.88},
        limitations=["Do not use for commercial mortgages > $10M"]
    )
    assert card["model_id"] == "fin-gpt-v1"
    assert card["governance_risk_tier"] == "HIGH_RISK"
    assert len(card["known_limitations"]) == 1
