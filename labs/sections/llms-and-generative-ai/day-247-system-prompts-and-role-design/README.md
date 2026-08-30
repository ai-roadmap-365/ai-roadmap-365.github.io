# Lab: Day 247 -- System Prompts and Role Design

## Lesson
Day number: 247 of 365.
Course: Course06-SS01 (LLMs and Generative AI - Working with LLMs).
Topic: System Prompts, Role Design, and 3-Tier Guardrail Architecture.

## Purpose
Build and test an automated 3-tier system prompt generator and persona consistency validator in Python. Construct multi-tier system prompts with safety shells, operational boundaries, and persona cores.

## Learning objectives
- Formulate 3-tier system prompts with safety, operational, and persona layers.
- Implement neutral, non-moralizing refusal directives.
- Calibrate communication tones across enterprise domains.
- Structure system prompts to maximize cloud API prefix caching.

## Prerequisites
- Day 246 (Prompting Fundamentals).
- Python 3.11+ with Pytest.

## Supported operating systems
- macOS (Apple Silicon / Intel)
- Linux (Ubuntu, Debian, Fedora, Arch)
- Windows 11 / WSL2

## Hardware requirements
- 1+ CPU cores.
- 1 GB RAM.
- 100 MB disk space.

## Required software
- Python 3.11 or newer.
- pip package manager.
- virtualenv or venv module.

## Free and open-source options
Python is open source under the PSF License.

## Installation
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements/requirements.txt
```

## File structure
- `starter/system_prompts_and_role_design_lib.py`: Student scaffold file.
- `examples/system_prompts_and_role_design_lib.py`: Complete reference implementation.
- `tests/test_system_prompts_and_role_design_lib.py`: Pytest automated validation suite.
- `expected-output/`: Verified output logs and baseline values.

## How to run
Execute the reference demonstration script:
```bash
python3 examples/system_prompts_and_role_design_lib.py
```

## What the commands do
- Compiles 3-tier system prompts.
- Configures custom safety and operational rules.
- Runs unit test assertions.

## Expected output
```
System Prompt Demo Compiled Successfully.
```

## Validation steps
1. Verify `compile` generates matching `<tier1_safety_guardrails>` tags.
2. Confirm `<tier2_operational_boundaries>` rules are rendered.
3. Confirm `<tier3_persona_core>` defines domain role and tone.
4. Ensure all unit test assertions pass.

## Tests
Run the test runner script:
```bash
./tests/run_tests.sh
```

## Cleanup
```bash
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type d -name ".pytest_cache" -exec rm -rf {} +
```

## Troubleshooting
- **Missing tier tag:** Ensure opening and closing tags match exactly.

## Security notes
All prompt generation executes locally in memory.

## Extension exercises
1. Implement a persona consistency evaluator using an automated rubric.
2. Build an automated multi-persona prompt router.

## Navigation

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** System Prompts and Role Design
- **Day number:** 247 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-247-system-prompts-and-role-design
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-247-system-prompts-and-role-design` when the site is running.
<!-- generated-links:end -->
