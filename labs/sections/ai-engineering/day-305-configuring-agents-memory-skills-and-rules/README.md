# Day 305 Lab: Configuring Agents: Memory, Skills, and Rules

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Configuring Agents: Memory, Skills, and Rules
- **Day number:** 305 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-305-configuring-agents-memory-skills-and-rules
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-305-configuring-agents-memory-skills-and-rules` when the site is running.
<!-- generated-links:end -->

## Purpose
Build an Agent Configuration & Custom Skill Engine in Python that parses `AGENTS.md` repository rules, discovers modular skill packages, extracts YAML frontmatter, and performs intent matching for lazy loading.

## Learning objectives
- Parse repository-level `AGENTS.md` instructions.
- Discover modular skills and extract YAML frontmatter metadata.
- Match user intent against skill triggers for lazy loading.
- Read and bundle skill instructions on demand.

## Prerequisites
- Python 3.10+ installed
- pytest installed
- pyyaml installed

## Supported operating systems
- macOS, Linux, Windows WSL2

## Hardware requirements
- Standard CPU, 512MB RAM

## Required software
- Python 3.10+, pytest, pyyaml

## Free and open-source options
- Python Standard Library, Pytest, PyYAML

## Installation
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements/requirements.txt
```

## File structure
- `starter/agent_config_engine.py`: Starter implementation skeleton
- `examples/agent_config_engine.py`: Verified reference implementation
- `tests/test_agent_config.py`: Test suite
- `expected-output/`: Captured execution logs

## How to run
```bash
python3 examples/agent_config_engine.py
```

## What the commands do
- Loads `AGENTS.md` rules, scans skill directories, matches triggers, and lazy-loads skill content.

## Expected output
```text
Project Rules Status: No AGENTS.md found in workspace root.
```

## Validation steps
Run test runner:
```bash
bash tests/run_tests.sh
```

## Tests
The test suite validates:
- `AGENTS.md` reading and fallback for missing files
- Skill directory scanning and YAML frontmatter extraction
- Intent matching across single and multiple trigger keywords
- Lazy skill content retrieval

## Cleanup
```bash
rm -rf .pytest_cache __pycache__ .venv
```

## Troubleshooting
Verify YAML frontmatter in `SKILL.md` is valid YAML.

## Security notes
Runs completely offline on local CPU.

## Extension exercises
Implement persistent JSON memory recording.

## Navigation
Day number: 305 of 365
