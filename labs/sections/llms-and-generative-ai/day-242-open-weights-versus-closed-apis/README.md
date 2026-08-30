# Lab: Day 242 -- Open Weights versus Closed APIs

## Lesson
Day number: 242 of 365.
Course: Course06-SS01 (LLMs and Generative AI - Working with LLMs).
Topic: Open Weights vs. Closed APIs, Total Cost of Ownership (TCO), and vLLM Serving.

## Purpose
Build and test an automated Total Cost of Ownership (TCO) and inference throughput simulator in Python. Calculate monthly break-even thresholds, evaluate high-volume vs low-volume enterprise deployment scenarios, and determine the optimal infrastructure choice.

## Learning objectives
- Formulate the TCO break-even equation comparing GPU server rental against API token charges.
- Evaluate deployment decisions based on daily token volume thresholds.
- Understand the operational role of vLLM PagedAttention and continuous batching.
- Assess data sovereignty and regulatory compliance constraints.

## Prerequisites
- Day 241 (The Model Landscape: Claude, GPT, Gemini, Llama).
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
Python and standard math libraries are open source.

## Installation
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements/requirements.txt
```

## File structure
- `starter/open_weights_versus_closed_apis_lib.py`: Student scaffold file.
- `examples/open_weights_versus_closed_apis_lib.py`: Complete reference implementation.
- `tests/test_open_weights_versus_closed_apis_lib.py`: Pytest automated validation suite.
- `expected-output/`: Verified output logs and baseline values.

## How to run
Execute the reference demonstration script:
```bash
python3 examples/open_weights_versus_closed_apis_lib.py
```

## What the commands do
- Computes daily break-even token thresholds.
- Evaluates deployment recommendations across volume scenarios.
- Runs unit test assertions.

## Expected output
```
TCO Demo: Break-Even = 247.56M Tok/Day, Low Vol = Closed API, High Vol = Self-Hosted
```

## Validation steps
1. Verify `calculate_break_even` computes exact break-even daily tokens.
2. Confirm `evaluate_decision` recommends Closed API for volumes below break-even.
3. Confirm `evaluate_decision` recommends Self-Hosted for volumes above break-even.
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
- **Break-even scaling error:** Ensure monthly token totals are converted to daily averages by dividing by 30.

## Security notes
All TCO simulations execute locally in process memory.

## Extension exercises
1. Implement an automated GPU cluster reservation amortization tool.
2. Build a latency simulator measuring tokens/second under varying batch sizes.

## Navigation

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Open Weights versus Closed APIs
- **Day number:** 242 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-242-open-weights-versus-closed-apis
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-242-open-weights-versus-closed-apis` when the site is running.
<!-- generated-links:end -->
