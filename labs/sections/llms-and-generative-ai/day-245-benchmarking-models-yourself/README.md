# Lab: Day 245 -- Benchmarking Models Yourself

## Lesson
Day number: 245 of 365.
Course: Course06-SS01 (LLMs and Generative AI - Working with LLMs).
Topic: Benchmarking Models Yourself, Bradley-Terry ELO, pass@k, and LLM-as-a-Judge.

## Purpose
Build and test a complete modular LLM evaluation and benchmarking engine in Python. Calculate Bradley-Terry ELO tournament ratings across pairwise model battles, implement the unbiased combinatorial pass@k coding metric, and compute statistical confidence intervals.

## Learning objectives
- Formulate the Bradley-Terry ELO ranking update rules for pairwise LLM battles.
- Implement the unbiased combinatorial pass@k estimation metric.
- Design dual-pass position-swapped LLM-as-a-Judge harnesses.
- Compute non-parametric bootstrap confidence intervals to evaluate statistical significance.

## Prerequisites
- Day 244 (Capabilities, Limits, and Hallucination).
- Python 3.11+ with PyTorch, NumPy, and Pytest.

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
NumPy and Pytest are free and open-source scientific software.

## Installation
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements/requirements.txt
```

## File structure
- `starter/benchmarking_models_yourself_lib.py`: Student scaffold file.
- `examples/benchmarking_models_yourself_lib.py`: Complete reference implementation.
- `tests/test_benchmarking_models_yourself_lib.py`: Pytest automated validation suite.
- `expected-output/`: Verified output logs and baseline values.

## How to run
Execute the reference demonstration script:
```bash
python3 examples/benchmarking_models_yourself_lib.py
```

## What the commands do
- Executes Bradley-Terry ELO updates across model matchups.
- Calculates exact pass@1 and pass@3 metrics for code generation.
- Runs unit test assertions.

## Expected output
```
Benchmarking Demo: ELO A = 1016.0, ELO B = 984.0, pass@1 = 40.0%, pass@3 = 83.33%
```

## Validation steps
1. Verify `update_match` computes symmetric zero-sum ELO rating updates.
2. Confirm `compute_pass_at_k` matches combinatorial baseline equations.
3. Confirm edge cases ($c=0$ and $c=n$) evaluate cleanly.
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
- **Pass@k zero division:** Ensure $n \ge k$ and $n > 0$.

## Security notes
All benchmarking calculations run locally in process memory.

## Extension exercises
1. Implement a non-parametric Bootstrap confidence interval calculator.
2. Build an automated multi-criteria rubric scoring harness.

## Navigation

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Benchmarking Models Yourself
- **Day number:** 245 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-245-benchmarking-models-yourself
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-245-benchmarking-models-yourself` when the site is running.
<!-- generated-links:end -->
