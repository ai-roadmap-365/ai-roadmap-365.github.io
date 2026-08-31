"""STARTER -- implement each TASK below, then run the tests.

Every function that raises NotImplementedError is yours to write. The
imports, constants and data structures are given; the logic is not.
Run `bash tests/run_tests.sh` to see which tasks are still outstanding.
"""

from typing import Dict, Any, List, Tuple

class AIGovernanceValidator:

    def __init__(self):
        self.prohibited_keywords = ['social_scoring', 'subliminal_manipulation', 'untargeted_facial_scraping', 'biometric_categorization_sensitive']
        self.high_risk_domains = ['recruitment_employment', 'credit_scoring', 'medical_diagnosis', 'law_enforcement', 'critical_infrastructure', 'educational_admission']

    def assess_eu_risk_tier(self, use_case_tag: str, is_gpai: bool=False, training_flops: float=0.0) -> Tuple[str, List[str]]:
        raise NotImplementedError('TASK 1: implement assess_eu_risk_tier.')

    def calculate_disparate_impact(self, protected_selection_rate: float, reference_selection_rate: float) -> Tuple[float, bool]:
        raise NotImplementedError('TASK 2: implement calculate_disparate_impact.')

    def generate_model_card(self, model_id: str, author: str, intended_use: str, risk_tier: str, evaluation_metrics: Dict[str, float], limitations: List[str]) -> Dict[str, Any]:
        raise NotImplementedError('TASK 3: implement generate_model_card.')
if __name__ == '__main__':
    v = AIGovernanceValidator()
    print(v.assess_eu_risk_tier('credit_scoring'))
