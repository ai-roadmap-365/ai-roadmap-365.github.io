from typing import Dict, Any, List, Tuple

class AIGovernanceValidator:
    def __init__(self):
        self.prohibited_keywords = [
            "social_scoring", "subliminal_manipulation", 
            "untargeted_facial_scraping", "biometric_categorization_sensitive"
        ]
        self.high_risk_domains = [
            "recruitment_employment", "credit_scoring", "medical_diagnosis", 
            "law_enforcement", "critical_infrastructure", "educational_admission"
        ]

    def assess_eu_risk_tier(self, use_case_tag: str, is_gpai: bool = False, 
                            training_flops: float = 0.0) -> Tuple[str, List[str]]:
        if use_case_tag in self.prohibited_keywords:
            return "UNACCEPTABLE_RISK", ["BANNED: System violates Article 5 of the EU AI Act. Deployment strictly prohibited."]

        if use_case_tag in self.high_risk_domains:
            obligations = [
                "Establish Continuous Risk Management System (Art. 9)",
                "Conduct Data Governance & Bias Testing (Art. 10)",
                "Provide Technical Documentation & Model Card (Art. 11)",
                "Implement Automated Logging & Audit Trails (Art. 12)",
                "Enforce Human Oversight & Kill Switches (Art. 14)",
                "Obtain CE Conformity Mark & Register in EU Database (Art. 49)"
            ]
            return "HIGH_RISK", obligations

        if is_gpai:
            obligations = [
                "Publish Technical Documentation & Copyright Policy (Art. 53)",
                "Provide Summary of Training Content Used"
            ]
            if training_flops >= 1e25:
                obligations.append("GPAI WITH SYSTEMIC RISK: Mandatory adversarial red teaming, energy reporting, and incident notification (Art. 55)")
            return "GPAI", obligations

        return "MINIMAL_RISK", ["Permitted without mandatory legal obligations. Follow voluntary codes of conduct."]

    def calculate_disparate_impact(self, protected_selection_rate: float, 
                                   reference_selection_rate: float) -> Tuple[float, bool]:
        if reference_selection_rate <= 0:
            raise ValueError("Reference selection rate must be strictly positive.")
        
        ratio = round(protected_selection_rate / reference_selection_rate, 4)
        is_compliant = ratio >= 0.80
        return ratio, is_compliant

    def generate_model_card(self, model_id: str, author: str, intended_use: str,
                            risk_tier: str, evaluation_metrics: Dict[str, float],
                            limitations: List[str]) -> Dict[str, Any]:
        return {
            "model_card_version": "1.0",
            "model_id": model_id,
            "author": author,
            "governance_risk_tier": risk_tier,
            "intended_use": intended_use,
            "evaluation_metrics": evaluation_metrics,
            "known_limitations": limitations,
            "human_oversight_mechanism": "Manual review required for confidence scores < 0.85"
        }

if __name__ == "__main__":
    v = AIGovernanceValidator()
    print(v.assess_eu_risk_tier("credit_scoring"))
