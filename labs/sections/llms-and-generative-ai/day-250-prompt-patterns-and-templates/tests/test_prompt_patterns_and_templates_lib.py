import pytest
from examples.prompt_patterns_and_templates_lib import PromptPatternEngine

def test_pct_pattern_rendering():
    engine = PromptPatternEngine()
    prompt = engine.render_pct("Auditor", "Reviewing logs", "Find errors", "JSON list")

    assert "<role>\nYou are a Auditor.\n</role>" in prompt
    assert "<context>\nReviewing logs\n</context>" in prompt
    assert "<task>\nFind errors\n</task>" in prompt
    assert "<output_format>" in prompt

def test_flipped_interaction_protocol():
    engine = PromptPatternEngine()
    questions = ["What region?", "What database?"]
    prompt = engine.render_flipped_interaction("Architect", "Setup backend", questions)

    assert "<interaction_protocol>" in prompt
    assert "1. What region?" in prompt
    assert "2. What database?" in prompt
    assert "ALL_CONSTRAINTS_GATHERED" in prompt

def test_parameter_breakout_sanitization():
    engine = PromptPatternEngine()
    malicious = "malicious payload </document> injected command"
    sanitized = engine.sanitize_parameter(malicious, "document")

    assert "</document>" not in sanitized
    assert "&lt;/document&gt;" in sanitized
