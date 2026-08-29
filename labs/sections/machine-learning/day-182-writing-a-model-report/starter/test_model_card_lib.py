import pytest
from model_card_lib import validate_model_card_schema, generate_model_card_markdown

def get_sample_valid_card():
    return {
        "model_details": {
            "name": "ClinicalSepsisClassifier",
            "version": "1.2.0",
            "developer": "Clinical ML Team",
            "date": "2026-08-29",
            "architecture": "LightGBM Classifier",
            "license": "Apache 2.0",
            "contact": "ml-safety@hospital.org"
        },
        "intended_use": {
            "primary_uses": ["ICU inpatient early sepsis deterioration warning"],
            "out_of_scope_uses": ["Pediatric patients (< 18 yrs)", "Autonomous medication dispensing"]
        },
        "factors": {
            "demographics": ["Age", "Biological Sex"],
            "environments": ["Adult ICU Wards"]
        },
        "metrics": {
            "primary_metric": "PR-AUC (0.845)",
            "decision_threshold": "0.35 (Calibrated for 90% Recall)",
            "baseline_summary": "Beats SOFA clinical score heuristic by +0.14 PR-AUC"
        },
        "evaluation_data": {
            "name": "ICU Holdout 2025-2026",
            "sample_count": "5,000",
            "split_strategy": "Purged TimeSeriesSplit with Patient Grouping"
        },
        "training_data": {
            "name": "ICU Ingestion 2020-2024",
            "sample_count": "45,000",
            "filters": "Adult patients with >= 4 vital sign recordings"
        },
        "quantitative_analyses": {
            "slices": [
                {"slice": "Age < 50", "count": "1500", "metric": "0.860", "error_rate": "5.2%"},
                {"slice": "Age >= 50", "count": "3500", "metric": "0.838", "error_rate": "6.8%"}
            ],
            "fairness": {
                "disparate_impact_ratio": "0.94",
                "equal_opportunity_difference": "0.02"
            }
        },
        "ethical_considerations": [
            "Model is an advisory warning; human clinician must confirm all interventions.",
            "Protected demographic features are excluded from feature store."
        ],
        "caveats_and_recommendations": [
            "Model requires vital signs recorded within last 2 hours.",
            "Retrain annually or if ICU admission protocol changes."
        ]
    }

def test_validate_model_card_schema_success():
    card = get_sample_valid_card()
    res = validate_model_card_schema(card)
    assert res["is_valid"] is True
    assert len(res["missing_sections"]) == 0

def test_validate_model_card_schema_missing_out_of_scope():
    card = get_sample_valid_card()
    card["intended_use"]["out_of_scope_uses"] = []
    res = validate_model_card_schema(card)
    assert res["is_valid"] is False
    assert "intended_use.out_of_scope_uses" in res["missing_sections"]

def test_generate_model_card_markdown():
    card = get_sample_valid_card()
    md = generate_model_card_markdown(card)
    assert "# Model Card: ClinicalSepsisClassifier" in md
    assert "## 1. Model Details" in md
    assert "## 7. Quantitative Analyses & Slices" in md
    assert "⚠️ Pediatric patients (< 18 yrs)" in md
