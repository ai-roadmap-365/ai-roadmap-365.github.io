import pytest
from examples.threat_modeling import AIThreatModelScorer

def test_dread_score_calculation_and_severity():
    scorer = AIThreatModelScorer()
    # 9, 8, 8, 9, 8 -> sum=42 / 5 = 8.4 -> CRITICAL
    t = scorer.add_threat("T1", "Indirect Injection", "Tampering", "LLM01", 9, 8, 8, 9, 8, "Exploit")
    
    assert t["composite_score"] == 8.4
    assert t["severity"] == "CRITICAL"
    assert t["owasp_id"] == "LLM01"

def test_severity_tier_classification():
    scorer = AIThreatModelScorer()
    # High: 6, 6, 6, 6, 6 -> 6.0
    t_high = scorer.add_threat("T2", "Prompt Leak", "Info Disc", "LLM06", 6, 6, 6, 6, 6, "Desc")
    assert t_high["severity"] == "HIGH"
    
    # Medium: 4, 4, 4, 4, 4 -> 4.0
    t_med = scorer.add_threat("T3", "DoS", "DoS", "LLM04", 4, 4, 4, 4, 4, "Desc")
    assert t_med["severity"] == "MEDIUM"
    
    # Low: 2, 2, 2, 2, 2 -> 2.0
    t_low = scorer.add_threat("T4", "Minor", "Info", "LLM09", 2, 2, 2, 2, 2, "Desc")
    assert t_low["severity"] == "LOW"

def test_invalid_dread_criteria_raises_error():
    scorer = AIThreatModelScorer()
    with pytest.raises(ValueError):
        scorer.add_threat("T_ERR", "Bad Score", "Spoofing", "LLM01", 11, 5, 5, 5, 5, "Out of bounds")
        
    with pytest.raises(ValueError):
        scorer.add_threat("T_ERR2", "Bad Score 0", "Spoofing", "LLM01", 0, 5, 5, 5, 5, "Zero score")

def test_prioritized_remediation_sorting():
    scorer = AIThreatModelScorer()
    scorer.add_threat("T_LOW", "Low Risk", "DoS", "LLM04", 2, 2, 2, 2, 2, "Low")
    scorer.add_threat("T_CRIT", "Crit Risk", "Elevation", "LLM01", 10, 10, 9, 10, 9, "Crit")
    scorer.add_threat("T_HIGH", "High Risk", "Info", "LLM06", 6, 6, 6, 6, 6, "High")
    
    plan = scorer.get_prioritized_remediation_plan()
    assert len(plan) == 3
    assert plan[0]["threat_id"] == "T_CRIT"
    assert plan[1]["threat_id"] == "T_HIGH"
    assert plan[2]["threat_id"] == "T_LOW"

def test_empty_threat_model():
    scorer = AIThreatModelScorer()
    assert len(scorer.get_prioritized_remediation_plan()) == 0
