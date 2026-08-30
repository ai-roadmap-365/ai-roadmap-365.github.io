# Lab: Day 240 -- Pretraining, Fine-Tuning, and RLHF

## Lesson
Day number: 240 of 365.
Course: Course06-SS01 (LLMs and Generative AI - Working with LLMs).
Topic: Pretraining, Supervised Fine-Tuning, and Direct Preference Optimization (DPO).

## Purpose
Build and test a complete preference alignment module in PyTorch. Implement the Bradley-Terry preference probability function, compute Direct Preference Optimization (DPO) loss across winning and losing response tensors, and verify implicit reward margin separation.

## Learning objectives
- Implement the Bradley-Terry pairwise preference probability formulation.
- Build the Direct Preference Optimization (DPO) implicit reward loss function.
- Compute implicit reward margins between chosen and rejected responses.
- Understand the role of the KL-divergence parameter $eta$ in policy stability.

## Prerequisites
- Day 239 (How Large Language Models Are Trained).
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
PyTorch is open-source software maintained by the Linux Foundation under a modified BSD license.

## Installation
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements/requirements.txt
```

## File structure
- `starter/pretraining_fine_tuning_and_rlhf_lib.py`: Student scaffold file.
- `examples/pretraining_fine_tuning_and_rlhf_lib.py`: Complete reference implementation.
- `tests/test_pretraining_fine_tuning_and_rlhf_lib.py`: Pytest automated validation suite.
- `expected-output/`: Verified output logs and baseline values.

## How to run
Execute the reference demonstration script:
```bash
python3 examples/pretraining_fine_tuning_and_rlhf_lib.py
```

## What the commands do
- Evaluates Bradley-Terry preference probabilities.
- Computes DPO loss and implicit reward margins on test tensors.
- Runs unit test assertions.

## Expected output
```
Alignment Demo: BT Prob = 0.973, DPO Loss = 0.4741, Mean Margin = 0.4000
```

## Validation steps
1. Verify `compute_bradley_terry_probability` returns $0.5$ when rewards are equal.
2. Confirm `compute_dpo_loss` yields $pprox \ln(2) pprox 0.6931$ when policy equals reference.
3. Confirm implicit reward margins increase as policy likelihood on chosen tokens improves.
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
- **Underflow in Bradley-Terry sigmoid:** Use `math.exp(-diff)` safely clamped within $[-20, 20]$.

## Security notes
All alignment calculations execute locally in process memory.

## Extension exercises
1. Implement the Kahneman-Tversky Optimization (KTO) loss function.
2. Build an automated prompt-masking dataset collator for SFT.

## Navigation

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Pretraining, Fine-Tuning, and RLHF
- **Day number:** 240 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-240-pretraining-fine-tuning-and-rlhf
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-240-pretraining-fine-tuning-and-rlhf` when the site is running.
<!-- generated-links:end -->
