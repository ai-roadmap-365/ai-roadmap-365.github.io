import json
from typing import List, Dict, Any, Optional

class CompleteEvalHarness:
    def __init__(self, baseline_composite_score: float = 0.85, tolerance_delta: float = -0.02):
        self.baseline_score = float(baseline_composite_score)
        self.tolerance_delta = float(tolerance_delta)
        self.results: List[Dict[str, Any]] = []
        
    def evaluate_case(self, case_id: str, category: str, prediction: str, ground_truth: str, is_golden: bool = False) -> Dict[str, Any]:
        norm_pred = str(prediction).strip().lower()
        norm_gt = str(ground_truth).strip().lower()
        
        exact_match = 1.0 if norm_pred == norm_gt else 0.0
        
        pred_words = set(norm_pred.split())
        gt_words = set(norm_gt.split())
        common = pred_words.intersection(gt_words)
        
        if pred_words and gt_words and common:
            p = len(common) / len(pred_words)
            r = len(common) / len(gt_words)
            overlap_f1 = (2 * p * r) / (p + r)
        else:
            overlap_f1 = 0.0
            
        score = (0.5 * exact_match) + (0.5 * overlap_f1)
        passed = score >= 0.70
        
        result = {
            "case_id": case_id,
            "category": category,
            "score": round(score, 4),
            "passed": passed,
            "is_golden": is_golden
        }
        self.results.append(result)
        return result
        
    def generate_report(self) -> Dict[str, Any]:
        if not self.results:
            return {"status": "EMPTY", "gate_passed": False}
            
        total_score = sum(r["score"] for r in self.results)
        candidate_composite = round(total_score / len(self.results), 4)
        delta = round(candidate_composite - self.baseline_score, 4)
        
        failed_golden = [r["case_id"] for r in self.results if r["is_golden"] and not r["passed"]]
        
        gate_passed = (delta >= self.tolerance_delta) and (len(failed_golden) == 0)
        
        return {
            "total_cases": len(self.results),
            "baseline_score": self.baseline_score,
            "candidate_score": candidate_composite,
            "delta": delta,
            "failed_golden_cases": failed_golden,
            "gate_passed": gate_passed,
            "status": "APPROVED" if gate_passed else "REJECTED"
        }

if __name__ == "__main__":
    harness = CompleteEvalHarness(baseline_composite_score=0.80)
    harness.evaluate_case("c1", "happy_path", "Paris", "Paris", is_golden=True)
    print("Report:", harness.generate_report())
