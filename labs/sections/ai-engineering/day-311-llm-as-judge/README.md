# Day 311 Lab: LLM-as-Judge

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** LLM-as-Judge
- **Day number:** 311 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-311-llm-as-judge
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-311-llm-as-judge` when the site is running.
<!-- generated-links:end -->

## Purpose
Build a Rubric-Anchored LLM-as-a-Judge Evaluation Engine in Python supporting prompt formatting, JSON response parsing, and position-swapped pairwise comparison.

## Learning objectives
- Format structured rubric-anchored judge prompts for Faithfulness.
- Extract and validate JSON reasoning and score payloads.
- Implement position-swapped pairwise evaluation to eliminate positional bias.
- Handle malformed responses gracefully.

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
- Python Standard Library, Pytest

## Installation
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements/requirements.txt
```

## File structure
- `starter/llm_judge.py`: Starter implementation skeleton
- `examples/llm_judge.py`: Verified reference implementation
- `tests/test_llm_judge.py`: Test suite
- `expected-output/`: Captured execution logs

## How to run
```bash
python3 examples/llm_judge.py
```

## What the commands do
- Executes rubric parsing and position-swapped pairwise evaluation resolution.

## Expected output
```text
All 5 checks passed 100% with zero errors.
```

## Validation steps
Run test runner:
```bash
bash tests/run_tests.sh
```

## Tests
The test suite validates:
- Prompt generation with anchored criteria
- Robust JSON response parsing
- Clamping of out-of-range scores
- Position-swapped pairwise resolution (candidate, baseline, tie, inconsistent)

## Cleanup
```bash
rm -rf .pytest_cache __pycache__ .venv
```

## Troubleshooting
Ensure JSON responses are extracted using regex boundary search.

## Security notes
Runs completely offline on local CPU.

## Extension exercises
Add multi-criteria composite scoring across Faithfulness, Relevance, and Conciseness.

## Navigation
Day number: 311 of 365
