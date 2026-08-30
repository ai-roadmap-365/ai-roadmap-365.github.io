import pytest
from examples.rag_eval_lib import (
    RAGTriadEvaluator
)

def test_faithfulness_grounded_answer():
    evaluator = RAGTriadEvaluator()
    context = "The enterprise SLA guarantees 99.99% uptime with 24/7 dedicated support."
    answer = "The enterprise SLA guarantees 99.99% uptime."
    res = evaluator.evaluate_faithfulness(context, answer)
    assert res["faithfulness_score"] == 1.0
    assert res["supported_claims"] == 1

def test_faithfulness_hallucinated_claims():
    evaluator = RAGTriadEvaluator()
    context = "The server runs on port 8080."
    answer = "The server runs on port 8080. It also mines bitcoin automatically."
    res = evaluator.evaluate_faithfulness(context, answer)
    assert res["faithfulness_score"] == 0.5
    assert res["total_claims"] == 2
    assert res["supported_claims"] == 1

def test_context_relevance_calculation():
    evaluator = RAGTriadEvaluator()
    query = "database connection timeout"
    context = "Database connection timeout is 30 seconds. Weather is sunny today. Cats are mammals."
    score = evaluator.evaluate_context_relevance(query, context)
    assert round(score, 2) == 0.33

def test_empty_string_handling():
    evaluator = RAGTriadEvaluator()
    assert evaluator.evaluate_faithfulness("", "")["faithfulness_score"] == 1.0
    assert evaluator.evaluate_context_relevance("", "") == 0.0
