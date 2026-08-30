import json
import re
import uuid
import time
from typing import Dict, Any, List, Optional, Tuple

class EvaluationHarnessSuite:
    def __init__(self, baseline_score: float = 0.85, tolerance_delta: float = -0.02):
        self.baseline_score = float(baseline_score)
        self.tolerance_delta = float(tolerance_delta)
        self.dataset: List[Dict[str, Any]] = []
        self.results: List[Dict[str, Any]] = []
        
    def add_benchmark_case(
        self,
        case_id: str,
        category: str,
        query: str,
        ground_truth: str,
        is_golden: bool = False
    ) -> bool:
        if not case_id or not query or not ground_truth:
            return False
        valid_cats = {"happy_path", "hard_negative", "schema_boundary", "adversarial"}
        if category not in valid_cats:
            return False
            
        for c in self.dataset:
            if c["query"].strip().lower() == query.strip().lower():
                return False
                
        self.dataset.append({
            "case_id": str(case_id).strip(),
            "category": category,
            "query": query.strip(),
            "ground_truth": ground_truth.strip(),
            "is_golden": is_golden
        })
        return True
        
    @staticmethod
    def evaluate_exact_match(pred: str, gt: str) -> float:
        return 1.0 if pred.strip().lower() == gt.strip().lower() else 0.0
        
    @staticmethod
    def evaluate_token_f1(pred: str, gt: str) -> float:
        pred_words = set(re.findall(r'\w+', pred.lower()))
        gt_words = set(re.findall(r'\w+', gt.lower()))
        if not pred_words or not gt_words:
            return 0.0
        common = pred_words.intersection(gt_words)
        if not common:
            return 0.0
        p = len(common) / len(pred_words)
        r = len(common) / len(gt_words)
        return (2 * p * r) / (p + r)
        
    @staticmethod
    def evaluate_json_f1(pred_json_str: str, gt_dict: Dict[str, Any]) -> float:
        try:
            pred = json.loads(pred_json_str)
            if not isinstance(pred, dict):
                return 0.0
            correct = sum(1 for k, v in pred.items() if k in gt_dict and str(gt_dict[k]).lower() == str(v).lower())
            total_pred = len(pred)
            total_gt = len(gt_dict)
            if total_pred == 0 or total_gt == 0:
                return 0.0
            p = correct / total_pred
            r = correct / total_gt
            return (2 * p * r) / (p + r) if (p + r) > 0 else 0.0
        except Exception:
            return 0.0

    def run_benchmark_case(self, case_id: str, candidate_prediction: str) -> Optional[Dict[str, Any]]:
        case = next((c for c in self.dataset if c["case_id"] == case_id), None)
        if not case:
            return None
            
        em = self.evaluate_exact_match(candidate_prediction, case["ground_truth"])
        f1 = self.evaluate_token_f1(candidate_prediction, case["ground_truth"])
        composite = round((0.4 * em) + (0.6 * f1), 4)
        passed = composite >= 0.70
        
        res = {
            "case_id": case_id,
            "category": case["category"],
            "exact_match": em,
            "token_f1": round(f1, 4),
            "composite_score": composite,
            "passed": passed,
            "is_golden": case["is_golden"]
        }
        self.results.append(res)
        return res
        
    def evaluate_suite_regression(self) -> Dict[str, Any]:
        if not self.results:
            return {"gate_passed": False, "status": "NO_RESULTS"}
            
        avg_score = round(sum(r["composite_score"] for r in self.results) / len(self.results), 4)
        delta = round(avg_score - self.baseline_score, 4)
        
        failed_golden = [r["case_id"] for r in self.results if r["is_golden"] and not r["passed"]]
        passed_tolerance = delta >= self.tolerance_delta
        passed_golden = len(failed_golden) == 0
        
        gate_passed = passed_tolerance and passed_golden
        
        return {
            "total_evaluated": len(self.results),
            "baseline_score": self.baseline_score,
            "candidate_score": avg_score,
            "delta": delta,
            "tolerance_passed": passed_tolerance,
            "golden_passed": passed_golden,
            "failed_golden_count": len(failed_golden),
            "gate_passed": gate_passed,
            "status": "APPROVED" if gate_passed else "REJECTED"
        }

if __name__ == "__main__":
    suite = EvaluationHarnessSuite(baseline_score=0.80)
    suite.add_benchmark_case("c1", "happy_path", "What is Paris?", "Paris is the capital of France.", is_golden=True)
    suite.run_benchmark_case("c1", "Paris is the capital of France.")
    print("Suite Decision:", suite.evaluate_suite_regression())
