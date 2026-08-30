import re
from typing import List, Dict, Any

class RAGTriadEvaluator:
    def __init__(self):
        pass

    def evaluate_faithfulness(self, context: str, answer: str) -> Dict[str, Any]:
        sentences = [s.strip() for s in re.split(r'[.!?]', answer) if s.strip()]
        if not sentences:
            return {"faithfulness_score": 1.0, "total_claims": 0, "supported_claims": 0, "details": []}

        context_lower = context.lower()
        supported = 0
        claim_results = []

        for s in sentences:
            words = [w for w in re.findall(r'\w+', s.lower()) if len(w) > 3]
            if not words:
                supported += 1
                claim_results.append({"claim": s, "supported": True})
                continue
            
            matches = sum(1 for w in words if w in context_lower)
            is_supported = (matches / len(words)) >= 0.5
            if is_supported:
                supported += 1
            claim_results.append({"claim": s, "supported": is_supported})

        score = supported / len(sentences)
        return {
            "faithfulness_score": score,
            "total_claims": len(sentences),
            "supported_claims": supported,
            "details": claim_results
        }

    def evaluate_context_relevance(self, query: str, context: str) -> float:
        q_words = set(re.findall(r'\w+', query.lower()))
        c_sentences = [s.strip() for s in re.split(r'[.!?]', context) if s.strip()]
        if not c_sentences or not q_words:
            return 0.0

        relevant_sentences = 0
        for s in c_sentences:
            s_words = set(re.findall(r'\w+', s.lower()))
            if q_words.intersection(s_words):
                relevant_sentences += 1

        return relevant_sentences / len(c_sentences)

def run_evaluation_demo():
    evaluator = RAGTriadEvaluator()
    context = "PostgreSQL 16 supports bidirectional logical replication. Max connections default to 100."
    good_answer = "PostgreSQL 16 provides bidirectional logical replication."
    hallucinated_answer = "PostgreSQL 16 was released in 1985 and supports quantum indexing."

    f_good = evaluator.evaluate_faithfulness(context, good_answer)
    f_bad = evaluator.evaluate_faithfulness(context, hallucinated_answer)

    print(f"Good Answer Faithfulness: {f_good['faithfulness_score']:.2f}")
    print(f"Hallucinated Answer Faithfulness: {f_bad['faithfulness_score']:.2f}")
    return f_good, f_bad

if __name__ == "__main__":
    run_evaluation_demo()
