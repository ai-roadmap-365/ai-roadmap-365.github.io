# Lab: Day 244 -- Capabilities, Limits, and Hallucination

## Lesson
Day number: 244 of 365.
Course: Course06-SS01 (LLMs and Generative AI - Working with LLMs).
Topic: Capabilities, Cognitive Limits, Hallucination, and Grounding.

## Purpose
Build and test an automated grounded factuality verifier and Self-Consistency majority voting engine in Python. Extract numerical and named entities, verify citation grounding against source documents, and implement consensus voting.

## Learning objectives
- Distinguish intrinsic confabulation from ungrounded extrinsic extrapolation.
- Implement lexical and numerical citation verification algorithms.
- Build Self-Consistency consensus majority voting over multiple reasoning paths.
- Analyze long-context retrieval degradation in deep documents.

## Prerequisites
- Day 243 (Tokens, Context Windows, and Sampling).
- Python 3.11+ with PyTorch and NumPy.

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
Python and standard regex/collections modules are free and open source.

## Installation
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements/requirements.txt
```

## File structure
- `starter/capabilities_limits_and_hallucination_lib.py`: Student scaffold file.
- `examples/capabilities_limits_and_hallucination_lib.py`: Complete reference implementation.
- `tests/test_capabilities_limits_and_hallucination_lib.py`: Pytest automated validation suite.
- `expected-output/`: Verified output logs and baseline values.

## How to run
Execute the reference demonstration script:
```bash
python3 examples/capabilities_limits_and_hallucination_lib.py
```

## What the commands do
- Evaluates grounded vs hallucinated claims against a reference context.
- Aggregates multi-path reasoning outputs via majority voting.
- Runs unit test assertions.

## Expected output
```
Hallucination Demo: True Claim Grounded = True, False Claim Grounded = False, Consensus = 42
```

## Validation steps
1. Verify `verify_claim` returns `True` for factually grounded sentences.
2. Confirm `verify_claim` flags ungrounded numerical claims as `False`.
3. Confirm `self_consistency_vote` extracts the consensus majority winner.
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
- **False negative on grounding:** Ensure case differences are normalized to lowercase before matching.

## Security notes
All grounding verification checks execute locally in memory.

## Extension exercises
1. Implement a token-level predictive entropy calculation heuristic.
2. Build an automated citation matcher verifying exact paragraph spans.

## Navigation

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Capabilities, Limits, and Hallucination
- **Day number:** 244 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-244-capabilities-limits-and-hallucination
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-244-capabilities-limits-and-hallucination` when the site is running.
<!-- generated-links:end -->
