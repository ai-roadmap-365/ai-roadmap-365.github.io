import pytest
from examples.prompting_fundamentals_lib import PromptCompiler

def test_prompt_compilation_structure():
    compiler = PromptCompiler(role="Auditor", task="Review code")
    compiler.add_step("Check auth")
    compiler.add_constraint("Output concisely")
    compiler.set_output_schema("JSON object")

    prompt = compiler.compile("print('hello')", tag="code")
    assert "<role_and_task>" in prompt
    assert "Role: Auditor" in prompt
    assert "<code>" in prompt
    assert "print('hello')" in prompt
    assert "</code>" in prompt
    assert "<execution_steps>" in prompt
    assert "1. Check auth" in prompt
    assert "<constraints>" in prompt
    assert "- Output concisely" in prompt
    assert "<output_format>" in prompt

def test_recency_ordering():
    compiler = PromptCompiler(role="Writer", task="Summarize")
    compiler.set_output_schema("Markdown list")
    prompt = compiler.compile("Document body", tag="doc")

    # Verify <role_and_task> comes first and <output_format> comes last
    idx_role = prompt.find("<role_and_task>")
    idx_doc = prompt.find("<doc>")
    idx_out = prompt.find("<output_format>")

    assert idx_role < idx_doc < idx_out

def test_empty_steps_and_constraints():
    compiler = PromptCompiler(role="Bot", task="Echo")
    prompt = compiler.compile("Input text")
    assert "<execution_steps>" not in prompt
    assert "<constraints>" not in prompt
    assert "<input_data>" in prompt
