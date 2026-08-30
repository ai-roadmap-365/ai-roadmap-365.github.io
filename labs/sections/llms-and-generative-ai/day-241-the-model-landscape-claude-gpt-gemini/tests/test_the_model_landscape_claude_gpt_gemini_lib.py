import pytest
from examples.the_model_landscape_claude_gpt_gemini_lib import ModelRouter

def test_router_dispatch_decisions():
    router = ModelRouter()
    
    # Code prompt should go to Claude Sonnet
    code_prompt = "def merge_sort(arr):
    if len(arr) <= 1: return arr"
    assert router.route_query(code_prompt) == "claude-3.5-sonnet"

    # Fast classification prompt should go to GPT-4o-mini
    simple_prompt = "Classify sentiment: Great movie!"
    assert router.route_query(simple_prompt, token_count=20) == "gpt-4o-mini"

    # Long document should go to Gemini Flash
    assert router.route_query("Document text", token_count=200000) == "gemini-2.0-flash"

def test_cost_calculation():
    router = ModelRouter()
    # 1M input + 1M output on Sonnet = $3 + $15 = $18
    cost = router.calculate_cost("claude-3.5-sonnet", 1000000, 1000000)
    assert cost == pytest.approx(18.00, rel=1e-3)

def test_prompt_caching_discount():
    router = ModelRouter()
    cost_regular = router.calculate_cost("claude-3.5-sonnet", 1000000, 0, is_cached=False)
    cost_cached = router.calculate_cost("claude-3.5-sonnet", 1000000, 0, is_cached=True)

    assert cost_regular == pytest.approx(3.00, rel=1e-3)
    assert cost_cached == pytest.approx(0.75, rel=1e-3) # 75% discount
