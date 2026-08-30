import pytest
from examples.code_review_scanner import AICodeReviewScanner

def test_clean_code_passes():
    scanner = AICodeReviewScanner(["math", "typing", "pytest"])
    code = """
import math
def circle_area(r: float) -> float:
    return math.pi * r * r
"""
    res = scanner.scan_code(code)
    assert res["passed"] is True
    assert res["issue_count"] == 0

def test_unapproved_dependency_detected():
    scanner = AICodeReviewScanner(["math"])
    code = "import phantom_jwt_lib\nfrom secret_crypto import decrypt"
    res = scanner.scan_code(code)
    assert res["passed"] is False
    assert res["issue_count"] == 2
    rules = [i["rule"] for i in res["issues"]]
    assert "UNAPPROVED_DEPENDENCY" in rules

def test_insecure_shell_detected():
    scanner = AICodeReviewScanner(["os"])
    code = "import os\nos.system('rm -rf /tmp/data')"
    res = scanner.scan_code(code)
    assert res["passed"] is False
    assert any(i["rule"] == "INSECURE_SHELL_EXECUTION" for i in res["issues"])

def test_weak_assertion_detected():
    scanner = AICodeReviewScanner(["pytest"])
    code = "def test_login():\n    assert True"
    res = scanner.scan_code(code)
    assert res["passed"] is False
    assert any(i["rule"] == "WEAK_ASSERTION" for i in res["issues"])
