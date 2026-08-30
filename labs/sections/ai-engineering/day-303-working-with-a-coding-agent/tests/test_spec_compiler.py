import pytest
import tempfile
import os
from examples.spec_compiler import SpecCompiler

def test_bundle_context_existing_files():
    with tempfile.TemporaryDirectory() as tmpdir:
        sample = os.path.join(tmpdir, "models.py")
        with open(sample, "w", encoding="utf-8") as f:
            f.write("class User:\n    pass\n")
            
        compiler = SpecCompiler(tmpdir)
        context = compiler.bundle_context(["models.py"])
        assert "### File: models.py" in context
        assert "class User:" in context

def test_bundle_context_missing_file():
    with tempfile.TemporaryDirectory() as tmpdir:
        compiler = SpecCompiler(tmpdir)
        context = compiler.bundle_context(["missing.py"])
        assert "### File: missing.py (NOT FOUND)" in context

def test_compile_prompt_full_sections():
    with tempfile.TemporaryDirectory() as tmpdir:
        fpath = os.path.join(tmpdir, "api.py")
        with open(fpath, "w", encoding="utf-8") as f:
            f.write("def login(): pass\n")
            
        compiler = SpecCompiler(tmpdir)
        prompt = compiler.compile_prompt(
            goal="Add JWT Authentication",
            target_files=["api.py"],
            constraints=["Use pyjwt", "Set 1h expiry"],
            non_goals=["Do not change password hashing"],
            verification_command="pytest tests/test_auth.py"
        )
        
        assert "# TASK OBJECTIVE\nAdd JWT Authentication" in prompt
        assert "### File: api.py" in prompt
        assert "- Use pyjwt" in prompt
        assert "- Set 1h expiry" in prompt
        assert "- Do not change password hashing" in prompt
        assert "`pytest tests/test_auth.py`" in prompt
        assert "# INSTRUCTION FOR AGENT" in prompt
