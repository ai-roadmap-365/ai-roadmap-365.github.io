import pytest
from examples.speculative_decoding import SpeculativeDecodingEngine

def test_prefix_cache_lookup():
    engine = SpeculativeDecodingEngine()
    engine.register_prefix_cache("You are a helpful coding assistant", "kv_block_system")
    
    match, kv_id = engine.lookup_prefix("You are a helpful coding assistant. Write a Python script.")
    assert match is True
    assert kv_id == "kv_block_system"
    
    miss, kv_miss = engine.lookup_prefix("Completely different prompt")
    assert miss is False
    assert kv_miss == "CACHE_MISS"

def test_perfect_speculative_acceptance_with_bonus():
    engine = SpeculativeDecodingEngine()
    draft = ["the", "quick", "brown"]
    truth = ["the", "quick", "brown", "fox", "jumps"]
    
    # 3 draft tokens match -> all 3 accepted + 1 bonus target token ("fox") = 4 tokens total!
    res = engine.execute_speculative_step(draft, truth)
    assert res["accepted_count"] == 3
    assert res["rejected_index"] is None
    assert res["emitted_tokens"] == ["the", "quick", "brown", "fox"]
    assert res["speedup_factor"] == 4.0

def test_partial_speculative_acceptance_with_rejection():
    engine = SpeculativeDecodingEngine()
    draft = ["the", "slow", "brown", "fox"]
    truth = ["the", "quick", "brown", "fox"]
    
    # Token 0 ("the") matches; Token 1 ("slow" != "quick") fails -> replaced with "quick"
    res = engine.execute_speculative_step(draft, truth)
    assert res["accepted_count"] == 1
    assert res["rejected_index"] == 1
    assert res["emitted_tokens"] == ["the", "quick"]
    assert res["speedup_factor"] == 2.0

def test_immediate_first_token_rejection():
    engine = SpeculativeDecodingEngine()
    draft = ["wrong", "tokens", "here"]
    truth = ["correct", "words", "here"]
    
    # Token 0 fails immediately -> replaced with "correct"
    res = engine.execute_speculative_step(draft, truth)
    assert res["accepted_count"] == 0
    assert res["rejected_index"] == 0
    assert res["emitted_tokens"] == ["correct"]
    assert res["speedup_factor"] == 1.0

def test_empty_draft_tokens():
    engine = SpeculativeDecodingEngine()
    res = engine.execute_speculative_step([], ["only_target"])
    assert res["emitted_tokens"] == ["only_target"]
    assert res["speedup_factor"] == 1.0
