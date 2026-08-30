import pytest
from examples.llm_judge import LLMJudgeEvaluator

def test_build_rubric_prompt():
    prompt = LLMJudgeEvaluator.build_rubric_prompt("Query", "Context", "Answer")
    assert "FAITHFULNESS" in prompt
    assert "Evaluation Rubric:" in prompt
    assert "Query" in prompt
    assert "Context" in prompt

def test_parse_judge_response_valid():
    raw = '{"reasoning": "All facts match context.", "score": 5, "passed": true}'
    res = LLMJudgeEvaluator.parse_judge_response(raw)
    assert res["score"] == 5
    assert res["passed"] is True
    assert "All facts match" in res["reasoning"]

def test_parse_judge_response_with_markdown_wrapper():
    raw = 'Here is the evaluation:\n```json\n{"reasoning": "Minor issue", "score": 3}\n```'
    res = LLMJudgeEvaluator.parse_judge_response(raw)
    assert res["score"] == 3
    assert res["passed"] is False

def test_parse_judge_response_malformed():
    raw = "I think the answer is okay."
    res = LLMJudgeEvaluator.parse_judge_response(raw)
    assert res["score"] == 1
    assert res["passed"] is False

def test_resolve_pairwise_swap():
    assert LLMJudgeEvaluator.resolve_pairwise_swap("A", "B") == "candidate"
    assert LLMJudgeEvaluator.resolve_pairwise_swap("B", "A") == "baseline"
    assert LLMJudgeEvaluator.resolve_pairwise_swap("A", "A") == "position_bias_inconsistent"
    assert LLMJudgeEvaluator.resolve_pairwise_swap("TIE", "B") == "tie"
