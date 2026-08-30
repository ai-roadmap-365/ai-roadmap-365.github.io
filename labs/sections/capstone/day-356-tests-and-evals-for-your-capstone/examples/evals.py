import json
from typing import List, Dict, Any, Tuple

class CapstoneEvaluationEngine:
    def __init__(self, faithfulness_threshold: float = 0.90, recall_threshold: float = 0.85):
        self.faithfulness_threshold = faithfulness_threshold
        self.recall_threshold = recall_threshold

    def calculate_faithfulness(self, answer_claims: List[str], context_text: str) -> Tuple[float, List[str]]:
        supported = []
        unsupported = []
        context_lower = context_text.lower()

        for claim in answer_claims:
            claim_tokens = [tok for tok in claim.lower().split() if len(tok) > 3]
            matches = sum(1 for tok in claim_tokens if tok in context_lower)
            if len(claim_tokens) > 0 and (matches / len(claim_tokens)) >= 0.6:
                supported.append(claim)
            else:
                unsupported.append(claim)

        score = len(supported) / (len(answer_claims) or 1.0)
        return round(score, 3), unsupported

    def calculate_context_recall(self, ground_truth_points: List[str], context_text: str) -> float:
        found = 0
        context_lower = context_text.lower()
        for point in ground_truth_points:
            pt_tokens = [tok for tok in point.lower().split() if len(tok) > 3]
            matches = sum(1 for tok in pt_tokens if tok in context_lower)
            if len(pt_tokens) > 0 and (matches / len(pt_tokens)) >= 0.6:
                found += 1
        return round(found / (len(ground_truth_points) or 1.0), 3)

    def evaluate_benchmark_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        faithfulness, unsupp = self.calculate_faithfulness(item["answer_claims"], item["retrieved_context"])
        recall = self.calculate_context_recall(item["ground_truth_points"], item["retrieved_context"])
        
        passed = (faithfulness >= self.faithfulness_threshold) and (recall >= self.recall_threshold)
        return {
            "query_id": item["id"],
            "faithfulness": faithfulness,
            "context_recall": recall,
            "unsupported_claims": unsupp,
            "status": "PASS" if passed else "FAIL"
        }

    def run_eval_suite(self, benchmark_items: List[Dict[str, Any]]) -> Dict[str, Any]:
        results = [self.evaluate_benchmark_item(item) for item in benchmark_items]
        avg_faithfulness = round(sum(r["faithfulness"] for r in results) / len(results), 3)
        avg_recall = round(sum(r["context_recall"] for r in results) / len(results), 3)
        total_passed = sum(1 for r in results if r["status"] == "PASS")
        pass_rate = round((total_passed / len(results)) * 100.0, 1)

        return {
            "total_benchmark_queries": len(results),
            "average_faithfulness": avg_faithfulness,
            "average_context_recall": avg_recall,
            "pass_rate_percentage": pass_rate,
            "overall_quality_gate": "PASSED" if pass_rate >= 80.0 else "FAILED",
            "detailed_results": results
        }

if __name__ == "__main__":
    benchmark = [{
        "id": "q1",
        "ground_truth_points": ["Uptime is 99.9%"],
        "retrieved_context": "The system uptime is 99.9% guaranteed.",
        "answer_claims": ["Uptime is 99.9%"]
    }]
    engine = CapstoneEvaluationEngine()
    print(engine.run_eval_suite(benchmark))
