import pytest
from examples.rag_evaluation import RAGEvaluationSuite

def test_perfect_retrieval_metrics():
    suite = RAGEvaluationSuite(k=5)
    cases = [
        {"target_doc_id": "doc_a", "retrieved_doc_ids": ["doc_a", "doc_b"]},
        {"target_doc_id": "doc_b", "retrieved_doc_ids": ["doc_b", "doc_c"]}
    ]
    metrics = suite.evaluate_retrieval(cases)
    assert metrics["hit_rate@5"] == 1.0
    assert metrics["mrr@5"] == 1.0
    assert metrics["total_evaluated"] == 2

def test_mrr_decay_with_lower_ranks():
    suite = RAGEvaluationSuite(k=5)
    cases = [
        {"target_doc_id": "doc_1", "retrieved_doc_ids": ["doc_1"]},          # rank 1 -> 1.0
        {"target_doc_id": "doc_2", "retrieved_doc_ids": ["x", "doc_2"]},     # rank 2 -> 0.5
        {"target_doc_id": "doc_3", "retrieved_doc_ids": ["a", "b", "c", "d", "doc_3"]} # rank 5 -> 0.2
    ]
    # MRR = (1.0 + 0.5 + 0.2) / 3 = 1.7 / 3 ~ 0.5667
    metrics = suite.evaluate_retrieval(cases)
    assert metrics["hit_rate@5"] == 1.0
    assert pytest.approx(metrics["mrr@5"], 0.001) == 0.5667

def test_missed_retrieval():
    suite = RAGEvaluationSuite(k=3)
    cases = [
        {"target_doc_id": "target", "retrieved_doc_ids": ["other1", "other2", "other3"]}
    ]
    metrics = suite.evaluate_retrieval(cases)
    assert metrics["hit_rate@3"] == 0.0
    assert metrics["mrr@3"] == 0.0

def test_faithfulness_evaluation():
    suite = RAGEvaluationSuite()
    context = "PostgreSQL VACUUM cleans dead tuples and updates database statistics."
    claims_grounded = ["PostgreSQL VACUUM cleans dead tuples", "It updates statistics"]
    claims_hallucinated = ["PostgreSQL VACUUM brews hot coffee", "It flies rockets to Mars"]
    
    score_grounded = suite.evaluate_faithfulness(claims_grounded, context)
    score_hallucinated = suite.evaluate_faithfulness(claims_hallucinated, context)
    
    assert score_grounded == 1.0
    assert score_hallucinated == 0.0

def test_empty_test_set():
    suite = RAGEvaluationSuite(k=5)
    metrics = suite.evaluate_retrieval([])
    assert metrics["total_evaluated"] == 0
    assert metrics["hit_rate@5"] == 0.0
