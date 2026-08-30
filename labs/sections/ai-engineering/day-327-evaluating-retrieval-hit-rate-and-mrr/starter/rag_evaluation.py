from typing import Dict, Any, List, Optional

class RAGEvaluationSuite:
    def __init__(self, k: int = 5):
        self.k = int(k)
        
    def evaluate_retrieval(self, test_cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        total_queries = len(test_cases)
        if total_queries == 0:
            return {f"hit_rate@{self.k}": 0.0, f"mrr@{self.k}": 0.0, "total_evaluated": 0}
            
        hits = 0
        reciprocal_ranks = []
        
        for case in test_cases:
            target_id = case["target_doc_id"]
            retrieved_ids = case["retrieved_doc_ids"][: self.k]
            
            if target_id in retrieved_ids:
                hits += 1
                rank = retrieved_ids.index(target_id) + 1
                reciprocal_ranks.append(1.0 / rank)
            else:
                reciprocal_ranks.append(0.0)
                
        hit_rate = round(hits / total_queries, 4)
        mrr = round(sum(reciprocal_ranks) / total_queries, 4)
        
        return {
            f"hit_rate@{self.k}": hit_rate,
            f"mrr@{self.k}": mrr,
            "total_evaluated": total_queries
        }

    def evaluate_faithfulness(self, generated_claims: List[str], context_text: str) -> float:
        if not generated_claims:
            return 1.0
        supported = 0
        context_lower = context_text.lower()
        for claim in generated_claims:
            words = claim.lower().split()
            overlap = sum(1 for w in words if w in context_lower)
            if overlap / max(1, len(words)) >= 0.60:
                supported += 1
        return round(supported / len(generated_claims), 4)

if __name__ == "__main__":
    suite = RAGEvaluationSuite(k=5)
    cases = [{"target_doc_id": "d1", "retrieved_doc_ids": ["d1", "d2"]}]
    print(suite.evaluate_retrieval(cases))
