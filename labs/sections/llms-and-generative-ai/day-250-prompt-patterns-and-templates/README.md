# Lab: Day 250 -- Prompt Patterns and Templates

## Lesson
Day number: 250 of 365.
Course: Course06-SS01 (LLMs and Generative AI - Working with LLMs).
Topic: Prompt Design Patterns, Jinja2 Templating, and Parameter Sanitization.

## Purpose
Build and test an extensible Prompt Pattern Engine and parameter sanitization pipeline in Python. Implement the Persona-Context-Task and Flipped Interaction patterns, and enforce XML parameter escaping.

## Learning objectives
- Formulate the Persona-Context-Task (PCT) architectural pattern.
- Implement the Flipped Interaction active interview pattern.
- Sanitize dynamic template inputs to prevent parameter breakouts.
- Structure modular Jinja2 templates for prefix caching alignment.

## Prerequisites
- Day 249 (Structured Output: Getting Reliable JSON).
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
Python and standard string tools are open source.

## Installation
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements/requirements.txt
```

## File structure
- `starter/prompt_patterns_and_templates_lib.py`: Student scaffold file.
- `examples/prompt_patterns_and_templates_lib.py`: Complete reference implementation.
- `tests/test_prompt_patterns_and_templates_lib.py`: Pytest automated validation suite.
- `expected-output/`: Verified output logs and baseline values.

## How to run
Execute the reference demonstration script:
```bash
python3 examples/prompt_patterns_and_templates_lib.py
```

## What the commands do
- Renders PCT and Flipped Interaction prompts.
- Sanitizes dynamic input payloads.
- Runs unit test assertions.

## Expected output
```
Prompt Pattern Demo Rendered Successfully. Sanitized: untrusted&lt;/code_snippet&gt;exploit
```

## Validation steps
1. Verify `render_pct` generates `<role>`, `<context>`, and `<task>` tags.
2. Confirm `render_flipped_interaction` formats ordered questions.
3. Validate `sanitize_parameter` replaces closing tags with escaped entities.
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
- **Unescaped tag breakout:** Ensure `sanitize_parameter` is called on all untrusted strings.

## Security notes
Parameter sanitization prevents prompt injections and delimiter breakout attacks.

## Extension exercises
1. Implement the Question Refinement pattern in Python.
2. Build an automated Meta-Prompt generation pipeline.

## Navigation

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Prompt Patterns and Templates
- **Day number:** 250 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-250-prompt-patterns-and-templates
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-250-prompt-patterns-and-templates` when the site is running.
<!-- generated-links:end -->
