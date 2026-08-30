import pytest
import tempfile
from examples.feature_orchestrator import FeatureOrchestrator

def test_execute_quality_gates_passed():
    with tempfile.TemporaryDirectory() as tmpdir:
        orchestrator = FeatureOrchestrator(tmpdir)
        res = orchestrator.execute_quality_gates("python3 -c 'print(\"Gate Passed\")'")
        assert res["exit_code"] == 0
        assert res["passed"] is True
        assert "Gate Passed" in res["stdout"]

def test_execute_quality_gates_failed():
    with tempfile.TemporaryDirectory() as tmpdir:
        orchestrator = FeatureOrchestrator(tmpdir)
        res = orchestrator.execute_quality_gates("python3 -c 'exit(1)'")
        assert res["exit_code"] == 1
        assert res["passed"] is False

def test_generate_walkthrough_artifact():
    orchestrator = FeatureOrchestrator(".")
    test_res = {
        "passed": True,
        "exit_code": 0,
        "stdout": "5 passed in 0.02s",
        "stderr": ""
    }
    walkthrough = orchestrator.generate_walkthrough_artifact(
        feature_name="Multi-Tenancy Middleware",
        files_modified=["models.py", "schemas.py", "routes.py", "tests/test_api.py"],
        test_results=test_res
    )
    assert "# Feature Walkthrough: Multi-Tenancy Middleware" in walkthrough
    assert "- `models.py`" in walkthrough
    assert "- `routes.py`" in walkthrough
    assert "Test Execution Status: `PASSED (100%)`" in walkthrough
    assert "5 passed in 0.02s" in walkthrough
