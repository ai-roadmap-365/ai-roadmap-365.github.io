import pytest
import tempfile
import os
from examples.agent_config_engine import AgentConfigEngine

def test_load_project_rules_exists():
    with tempfile.TemporaryDirectory() as tmpdir:
        agents_file = os.path.join(tmpdir, "AGENTS.md")
        with open(agents_file, "w", encoding="utf-8") as f:
            f.write("# Project Rules\nUse pytest and ruff.")
            
        engine = AgentConfigEngine(tmpdir)
        rules = engine.load_project_rules()
        assert "# Project Rules" in rules
        assert "Use pytest and ruff." in rules

def test_load_project_rules_missing():
    with tempfile.TemporaryDirectory() as tmpdir:
        engine = AgentConfigEngine(tmpdir)
        rules = engine.load_project_rules()
        assert "No AGENTS.md found" in rules

def test_discover_and_match_skills():
    with tempfile.TemporaryDirectory() as tmpdir:
        skill_dir = os.path.join(tmpdir, ".agents", "skills", "db_migrate")
        os.makedirs(skill_dir, exist_ok=True)
        
        skill_file = os.path.join(skill_dir, "SKILL.md")
        with open(skill_file, "w", encoding="utf-8") as f:
            f.write("""---
name: db_migrate
description: Database migration assistant
triggers:
  - migrate
  - database migration
---
# Migration Instructions
Run alembic upgrade head.
""")
            
        engine = AgentConfigEngine(tmpdir)
        catalog = engine.discover_skills()
        assert len(catalog) == 1
        assert catalog[0]["name"] == "db_migrate"
        assert "migrate" in catalog[0]["triggers"]
        
        matched = engine.match_skill("Please perform a database migration on users")
        assert matched is not None
        assert matched["name"] == "db_migrate"
        
        content = engine.read_skill_content(matched["skill_path"])
        assert "Run alembic upgrade head." in content

def test_match_skill_no_match():
    with tempfile.TemporaryDirectory() as tmpdir:
        engine = AgentConfigEngine(tmpdir)
        matched = engine.match_skill("Write a CSS animation")
        assert matched is None
