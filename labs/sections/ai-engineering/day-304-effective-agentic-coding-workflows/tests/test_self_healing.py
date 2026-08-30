import pytest
from examples.self_healing_runner import SelfHealingTestRunner

def test_execute_passing_command():
    runner = SelfHealingTestRunner(".")
    res = runner.execute_test_command("python3 -c 'print(\"Passed\")'")
    assert res["exit_code"] == 0
    assert res["passed"] is True
    assert "Passed" in res["stdout"]

def test_execute_failing_command():
    runner = SelfHealingTestRunner(".")
    res = runner.execute_test_command("python3 -c 'assert False, \"Failed Assertion\"'")
    assert res["exit_code"] != 0
    assert res["passed"] is False
    assert "AssertionError" in res["combined_output"]

def test_extract_traceback_diagnostics():
    sample_trace = """
Traceback (most recent call last):
  File "calculator.py", line 42, in divide
    return a / b
ZeroDivisionError: division by zero
"""
    runner = SelfHealingTestRunner(".")
    diag = runner.extract_traceback_diagnostics(sample_trace)
    assert diag["failing_file"] == "calculator.py"
    assert diag["line_number"] == 42
    assert diag["error_type"] == "ZeroDivisionError"
    assert diag["error_message"] == "division by zero"

def test_format_repair_prompt():
    runner = SelfHealingTestRunner(".")
    diag = {
        "failing_file": "auth.py",
        "line_number": 15,
        "error_type": "ValueError",
        "error_message": "Invalid token"
    }
    prompt = runner.format_repair_prompt(diag, "Raw log output")
    assert "# TEST FAILURE DETECTED" in prompt
    assert "Failing File: auth.py" in prompt
    assert "Line Number: 15" in prompt
    assert "ValueError: Invalid token" in prompt
    assert "## Instructions:" in prompt
