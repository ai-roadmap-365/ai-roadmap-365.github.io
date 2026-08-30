import pytest
from examples.system_prompts_and_role_design_lib import SystemPromptCompiler

def test_system_prompt_3_tier_structure():
    compiler = SystemPromptCompiler("Security Auditor", "Staff")
    prompt = compiler.compile()

    assert "<tier1_safety_guardrails>" in prompt
    assert "</tier1_safety_guardrails>" in prompt
    assert "<tier2_operational_boundaries>" in prompt
    assert "</tier2_operational_boundaries>" in prompt
    assert "<tier3_persona_core>" in prompt
    assert "</tier3_persona_core>" in prompt
    assert "Role: Staff Security Auditor" in prompt

def test_custom_rule_addition():
    compiler = SystemPromptCompiler("DBA")
    compiler.add_safety_rule("No DROP TABLE commands")
    compiler.add_operational_rule("Use SQL syntax highlighting")
    prompt = compiler.compile()

    assert "- No DROP TABLE commands" in prompt
    assert "- Use SQL syntax highlighting" in prompt

def test_tone_configuration():
    compiler = SystemPromptCompiler("Support Agent")
    compiler.set_tone(["Empathetic", "Patient", "Clear"])
    prompt = compiler.compile()

    assert "Tone: Empathetic, Patient, Clear" in prompt
