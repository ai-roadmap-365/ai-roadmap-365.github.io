import pytest
import time
from examples.core_ai import CoreAIEngine, AnswerPayload

def test_prompt_synthesis_formatting():
    engine = CoreAIEngine(primary_model_fn=lambda p: "")
    prompt = engine.synthesize_prompt("What is X?", [{"id": "doc1", "text": "Content of doc1"}])
    assert "<system_instruction>" in prompt
    assert "<doc id='doc1'>Content of doc1</doc>" in prompt
    assert "<user_query>" in prompt
    assert "What is X?" in prompt

def test_valid_json_schema_parsing():
    def mock_model(p: str) -> str:
        return '```json\n{"summary": "Result summary", "detailed_points": ["A", "B"], "citations": ["doc1"], "confidence_score": 0.92}\n```'
    
    engine = CoreAIEngine(primary_model_fn=mock_model)
    raw, provider = engine.execute_inference_with_fallback("query")
    parsed = engine.parse_and_repair_json(raw)
    assert isinstance(parsed, AnswerPayload)
    assert parsed.summary == "Result summary"
    assert parsed.confidence_score == 0.92
    assert len(parsed.detailed_points) == 2

def test_circuit_breaker_failover():
    def failing_primary(p: str) -> str:
        raise ConnectionError("Primary down")
        
    def healthy_fallback(p: str) -> str:
        return '{"summary": "Fallback answer", "detailed_points": [], "citations": [], "confidence_score": 0.80}'

    engine = CoreAIEngine(primary_model_fn=failing_primary, fallback_model_fn=healthy_fallback, failure_threshold=2)
    
    raw1, prov1 = engine.execute_inference_with_fallback("q")
    assert prov1 == "fallback_model"
    assert engine.circuit_open is False

    raw2, prov2 = engine.execute_inference_with_fallback("q")
    assert prov2 == "fallback_model"
    assert engine.circuit_open is True

def test_primary_timeout_detection():
    def slow_primary(p: str) -> str:
        time.sleep(0.05)
        return "{}"

    def fast_fallback(p: str) -> str:
        return '{"summary": "Fast fallback", "detailed_points": [], "citations": [], "confidence_score": 0.85}'

    engine = CoreAIEngine(primary_model_fn=slow_primary, fallback_model_fn=fast_fallback, timeout_seconds=0.01)
    raw, prov = engine.execute_inference_with_fallback("q")
    assert prov == "fallback_model"

def test_self_healing_repair_loop():
    call_count = 0
    def malformed_then_fixed(p: str) -> str:
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return '{"summary": "Incomplete JSON", "detailed_points": "not_a_list", "citations": [], "confidence_score": 0.5}'
        return '{"summary": "Fixed JSON", "detailed_points": ["Item 1"], "citations": ["doc1"], "confidence_score": 0.9}'

    engine = CoreAIEngine(primary_model_fn=malformed_then_fixed)
    raw, _ = engine.execute_inference_with_fallback("q")
    parsed = engine.parse_and_repair_json(raw, max_retries=1)
    assert parsed.summary == "Fixed JSON"
    assert isinstance(parsed.detailed_points, list)
