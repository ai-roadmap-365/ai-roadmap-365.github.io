import json

REQUIRED_SECTIONS = [
    "model_details",
    "intended_use",
    "factors",
    "metrics",
    "evaluation_data",
    "training_data",
    "quantitative_analyses",
    "ethical_considerations",
    "caveats_and_recommendations"
]

def validate_model_card_schema(card_data):
    """
    Validate whether a model card dictionary conforms to the Mitchell et al. 2019 standard.
    """
    missing = [sec for sec in REQUIRED_SECTIONS if sec not in card_data or not card_data[sec]]
    if missing:
        return {
            "is_valid": False,
            "missing_sections": missing,
            "error": f"Model Card is missing mandatory sections: {missing}"
        }
        
    # Verify Intended Use has Out-of-Scope declarations
    intended = card_data.get("intended_use", {})
    if "out_of_scope_uses" not in intended or not intended["out_of_scope_uses"]:
        return {
            "is_valid": False,
            "missing_sections": ["intended_use.out_of_scope_uses"],
            "error": "Model Card MUST explicitly specify out-of-scope / prohibited use cases."
        }
        
    return {"is_valid": True, "missing_sections": []}

def generate_model_card_markdown(card_data):
    """
    Render a production Model Card in GitHub-flavored Markdown.
    """
    val = validate_model_card_schema(card_data)
    if not val["is_valid"]:
        raise ValueError(val["error"])
        
    md = f"""# Model Card: {card_data['model_details']['name']} (v{card_data['model_details']['version']})

## 1. Model Details
- **Organization / Developer:** {card_data['model_details']['developer']}
- **Release Date:** {card_data['model_details']['date']}
- **Model Architecture:** {card_data['model_details']['architecture']}
- **License:** {card_data['model_details']['license']}
- **Contact:** {card_data['model_details']['contact']}

## 2. Intended Use
### Primary Intended Uses
{chr(10).join(f"- {u}" for u in card_data['intended_use']['primary_uses'])}

### Out-of-Scope & Prohibited Uses
{chr(10).join(f"- ⚠️ {u}" for u in card_data['intended_use']['out_of_scope_uses'])}

## 3. Factors & Demographic Subgroups
- **Demographic Slices:** {', '.join(card_data['factors']['demographics'])}
- **Operational Environments:** {', '.join(card_data['factors']['environments'])}

## 4. Metrics & Evaluation Setup
- **Primary Optimization Metric:** {card_data['metrics']['primary_metric']}
- **Decision Threshold:** {card_data['metrics']['decision_threshold']}
- **Baseline Comparison:** {card_data['metrics']['baseline_summary']}

## 5. Evaluation Data
- **Dataset:** {card_data['evaluation_data']['name']} ({card_data['evaluation_data']['sample_count']} records)
- **Validation Split Strategy:** {card_data['evaluation_data']['split_strategy']}

## 6. Training Data
- **Dataset:** {card_data['training_data']['name']} ({card_data['training_data']['sample_count']} records)
- **Ingestion Filters:** {card_data['training_data']['filters']}

## 7. Quantitative Analyses & Slices
| Subgroup Slice | Sample Count | Primary Metric Value | Error Rate |
| --- | --- | --- | --- |
"""
    for row in card_data['quantitative_analyses']['slices']:
        md += f"| {row['slice']} | {row['count']} | {row['metric']} | {row['error_rate']} |\n"
        
    md += f"""
### Fairness Audit Summary
- **Demographic Parity Ratio (Disparate Impact):** {card_data['quantitative_analyses']['fairness']['disparate_impact_ratio']}
- **Equal Opportunity Difference (TPR Delta):** {card_data['quantitative_analyses']['fairness']['equal_opportunity_difference']}

## 8. Ethical Considerations & Risk Mitigations
{chr(10).join(f"- {e}" for e in card_data['ethical_considerations'])}

## 9. Caveats and Recommendations
{chr(10).join(f"- {c}" for c in card_data['caveats_and_recommendations'])}
"""
    return md
