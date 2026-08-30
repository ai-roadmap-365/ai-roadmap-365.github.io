import pytest
import tempfile
import os
from examples.coding_agent_engine import CodingAgentEngine

def test_generate_repo_map():
    with tempfile.TemporaryDirectory() as tmpdir:
        sample_file = os.path.join(tmpdir, "calculator.py")
        with open(sample_file, "w", encoding="utf-8") as f:
            f.write("class Calculator:\n    def add(self, a, b):\n        return a + b\n")
            
        engine = CodingAgentEngine(tmpdir)
        repo_map = engine.generate_repo_map()
        assert "File: calculator.py" in repo_map
        assert "class Calculator:" in repo_map
        assert "def add(self, a, b):" in repo_map

def test_apply_search_replace_success():
    with tempfile.TemporaryDirectory() as tmpdir:
        sample_file = os.path.join(tmpdir, "math_ops.py")
        with open(sample_file, "w", encoding="utf-8") as f:
            f.write("def divide(a, b):\n    return a / b\n")
            
        engine = CodingAgentEngine(tmpdir)
        search_block = "    return a / b"
        replace_block = "    if b == 0:\n        return 0\n    return a / b"
        
        msg = engine.apply_search_replace("math_ops.py", search_block, replace_block)
        assert "Successfully updated math_ops.py" in msg
        
        with open(sample_file, "r", encoding="utf-8") as f:
            updated = f.read()
        assert "if b == 0:" in updated

def test_apply_search_replace_missing_file():
    with tempfile.TemporaryDirectory() as tmpdir:
        engine = CodingAgentEngine(tmpdir)
        with pytest.raises(FileNotFoundError):
            engine.apply_search_replace("nonexistent.py", "a", "b")

def test_apply_search_replace_target_not_found():
    with tempfile.TemporaryDirectory() as tmpdir:
        sample_file = os.path.join(tmpdir, "app.py")
        with open(sample_file, "w", encoding="utf-8") as f:
            f.write("x = 10\n")
            
        engine = CodingAgentEngine(tmpdir)
        with pytest.raises(ValueError) as exc:
            engine.apply_search_replace("app.py", "y = 20", "y = 30")
        assert "not found" in str(exc.value)

def test_run_verification_tests():
    with tempfile.TemporaryDirectory() as tmpdir:
        engine = CodingAgentEngine(tmpdir)
        res = engine.run_verification_tests("python3 -c 'print(\"Tests OK\")'")
        assert res["passed"] is True
        assert "Tests OK" in res["stdout"]
