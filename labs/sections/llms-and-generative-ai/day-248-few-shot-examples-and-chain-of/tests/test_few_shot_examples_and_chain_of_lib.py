import pytest
from examples.few_shot_examples_and_chain_of_lib import FewShotCoTEngine

def test_few_shot_cot_compilation():
    engine = FewShotCoTEngine("Math Solver")
    engine.add_exemplar("1+1", "1 plus 1 is 2", "2")
    prompt = engine.compile_prompt("2+2")

    assert "<instructions>" in prompt
    assert "<examples>" in prompt
    assert '<example id="1">' in prompt
    assert "<reasoning>1 plus 1 is 2</reasoning>" in prompt
    assert "<query>\n2+2\n</query>" in prompt
    assert "<scratchpad>" in prompt

def test_self_consistency_majority_voting():
    samples = ["A", "B", "A", "A", "C"]
    result = FewShotCoTEngine.aggregate_self_consistency(samples)

    assert result["consensus_answer"] == "A"
    assert result["confidence"] == 0.6
    assert result["votes"] == {"A": 3, "B": 1, "C": 1}
    assert result["total_samples"] == 5

def test_self_consistency_empty_validation():
    with pytest.raises(ValueError):
        FewShotCoTEngine.aggregate_self_consistency([])
