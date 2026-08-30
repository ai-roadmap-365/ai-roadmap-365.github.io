import pytest
import tempfile
import os
from examples.agent_feature_pipeline import AgentFeaturePipeline

def test_generate_repo_map():
    with tempfile.TemporaryDirectory() as tmpdir:
        sample = os.path.join(tmpdir, "service.py")
        with open(sample, "w", encoding="utf-8") as f:
            f.write("class UserService:\n    def get_user(self, user_id: int):\n        pass\n")
            
        pipeline = AgentFeaturePipeline(tmpdir)
        repo_map = pipeline.generate_repo_map()
        assert "File: service.py" in repo_map
        assert "class UserService:" in repo_map
        assert "def get_user(self, user_id: int):" in repo_map

def test_apply_patch_success():
    with tempfile.TemporaryDirectory() as tmpdir:
        sample = os.path.join(tmpdir, "auth.py")
        with open(sample, "w", encoding="utf-8") as f:
            f.write("def authenticate(token):\n    return False\n")
            
        pipeline = AgentFeaturePipeline(tmpdir)
        pipeline.apply_patch("auth.py", "return False", "return token == 'valid'")
        with open(sample, "r", encoding="utf-8") as f:
            content = f.read()
        assert "return token == 'valid'" in content

def test_audit_security():
    pipeline = AgentFeaturePipeline(".", approved_packages=["math", "typing"])
    safe_code = "import math\ndef calc(): return math.sqrt(4)"
    assert pipeline.audit_security(safe_code)["passed"] is True
    
    unsafe_code = "import os\nos.system('ls')\nimport malicious_crypto"
    audit = pipeline.audit_security(unsafe_code)
    assert audit["passed"] is False
    rules = [i["rule"] for i in audit["issues"]]
    assert "INSECURE_SHELL" in rules
    assert "UNAPPROVED_DEPENDENCY" in rules

def test_run_tests_and_format_walkthrough():
    with tempfile.TemporaryDirectory() as tmpdir:
        pipeline = AgentFeaturePipeline(tmpdir)
        res = pipeline.run_tests("python3 -c 'print(\"All 4 tests passed\")'")
        assert res["passed"] is True
        
        walkthrough = pipeline.format_walkthrough("OAuth2 Feature", ["auth.py", "routes.py"], res)
        assert "# Feature Walkthrough: OAuth2 Feature" in walkthrough
        assert "- `auth.py`" in walkthrough
        assert "Status: `PASSED (100%)`" in walkthrough
        assert "All 4 tests passed" in walkthrough
