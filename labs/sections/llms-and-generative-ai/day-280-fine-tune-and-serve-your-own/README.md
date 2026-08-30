# Day 280 Lab: End-to-End Fine-Tuning Pipeline

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Fine-Tune and Serve Your Own Model
- **Day number:** 280 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-280-fine-tune-and-serve-your-own
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-280-fine-tune-and-serve-your-own` when the site is running.
<!-- generated-links:end -->

## Purpose
Build an end-to-end Python pipeline that merges LoRA adapter weights into base tensors, exposes a local mock serving endpoint, and quantitatively evaluates accuracy and schema compliance gains.

## Learning objectives
- Implement exact LoRA weight merging: $W_{\text{merged}} = W_{\text{base}} + (B \cdot A) \cdot (\alpha / r)$.
- Simulate local REST model serving endpoints.
- Build an automated evaluation benchmark computing JSON compliance and Exact Match (EM).
- Quantify performance improvements over baseline models.

## Prerequisites
- Python 3.10+ installed
- NumPy and pytest installed

## Supported operating systems
- macOS, Linux, Windows WSL2

## Hardware requirements
- Standard CPU, 512MB RAM

## Required software
- Python 3.10+, numpy, pytest

## Free and open-source options
- Python Standard Library, NumPy

## Installation
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements/requirements.txt
```

## File structure
- `starter/finetune_pipeline.py`: Starter implementation skeleton
- `examples/finetune_pipeline.py`: Verified reference implementation
- `tests/test_finetune_pipeline.py`: Test suite
- `expected-output/`: Captured execution logs

## How to run
```bash
python3 examples/finetune_pipeline.py
```

## What the commands do
- Executes LoRA adapter weight merging, simulates local inference, and runs benchmark evaluation.

## Expected output
```text
[PIPELINE] Merged LoRA Adapter into base model.
[BENCHMARK] Fine-Tuned Model achieved 100% JSON Schema Compliance vs 0% Base Model.
```

## Validation steps
Run test runner:
```bash
bash tests/run_tests.sh
```

## Tests
The test suite validates:
- Matrix multiplication and scaling for weight merging
- JSON syntax validation logic
- Exact match string parsing
- Comparative benchmark metrics

## Cleanup
```bash
rm -rf .pytest_cache __pycache__ .venv
```

## Troubleshooting
Ensure matrix dimensions for LoRA $B$ and $A$ align with $(d_{\text{out}}, r) \times (r, d_{\text{in}})$.

## Security notes
Runs completely offline on local CPU without third-party network access.

## Extension exercises
Add AST-based SQL query parsing evaluation using `sqlparse`.

## Navigation
Day number: 280 of 365
