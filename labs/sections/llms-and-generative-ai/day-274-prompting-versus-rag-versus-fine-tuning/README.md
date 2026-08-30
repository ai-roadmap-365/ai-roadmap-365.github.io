# Day 274 Lab: Customization Strategy Decision Engine

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Prompting versus RAG versus Fine-Tuning
- **Day number:** 274 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-274-prompting-versus-rag-versus-fine-tuning
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-274-prompting-versus-rag-versus-fine-tuning` when the site is running.
<!-- generated-links:end -->

## Purpose
Build and test a multi-criteria decision engine in Python that evaluates project requirements and recommends the optimal LLM customization paradigm (Prompting, RAG, LoRA, or Full Fine-Tuning).

## Learning objectives
- Implement multi-dimensional requirement evaluation for AI systems.
- Calculate economic break-even request volume thresholds between few-shot prompting and fine-tuning.
- Execute automated regression test suites verifying boundary condition handling.

## Prerequisites
- Python 3.10+ installed
- pytest installed

## Supported operating systems
- macOS, Linux, Windows WSL2

## Hardware requirements
- Standard CPU, 512MB RAM

## Required software
- Python 3.10+, pytest

## Free and open-source options
- Python Standard Library (dataclasses, typing)

## Installation
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements/requirements.txt
```

## File structure
- `starter/customization_decision_engine.py`: Starter implementation skeleton
- `examples/customization_decision_engine.py`: Verified reference implementation
- `tests/test_customization_decision_engine.py`: Test suite
- `expected-output/`: Captured execution logs

## How to run
```bash
python3 examples/customization_decision_engine.py
```

## What the commands do
- Evaluates sample project profiles across RAG, LoRA, and Prompting archetypes.
- Outputs recommended paradigm and economic analysis.

## Expected output
```text
[DECISION] Strategy: RAG_Hybrid | Score: 92.5/100
[BREAK-EVEN] Break-even request threshold: 31,746 queries
```

## Validation steps
Run the test runner:
```bash
bash tests/run_tests.sh
```

## Tests
The test suite validates:
- Dynamic knowledge scoring logic prioritizing RAG
- Strict syntax and large sample dataset scoring prioritizing LoRA
- Cost break-even formula correctness
- Strict score bounding between 0.0 and 100.0

## Cleanup
```bash
rm -rf .pytest_cache __pycache__ .venv
```

## Troubleshooting
If tests fail with division by zero in break-even analysis, verify that savings per request is non-zero.

## Security notes
No API keys or cloud credentials required. Runs entirely offline on local CPU.

## Extension exercises
Add Monte Carlo variance modeling to compute standard deviation of projected annual costs.

## Navigation
Day number: 274 of 365
