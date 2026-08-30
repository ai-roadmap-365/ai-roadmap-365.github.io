# Day 327 Lab: Evaluating Retrieval: Hit Rate and MRR

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
<!-- generated-links:end -->

## Purpose
Build an Empirical RAG Evaluation Suite in Python calculating Hit Rate@k, Mean Reciprocal Rank (MRR@k), and Faithfulness grounding scores.

## Learning objectives
- Implement Hit Rate@k calculation across benchmark test cases.
- Implement Mean Reciprocal Rank (MRR@k) position-sensitive scoring.
- Calculate Faithfulness grounding metrics for generated responses.
- Construct automated CI regression assertions.

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
- `starter/rag_evaluation.py`: Starter implementation skeleton
- `examples/rag_evaluation.py`: Verified reference implementation
- `tests/test_rag_evaluation.py`: Test suite
- `expected-output/`: Captured execution logs

## How to run
```bash
python3 examples/rag_evaluation.py
```

## What the commands do
- Evaluates sample benchmark queries and computes Hit Rate, MRR, and Faithfulness.

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
- Perfect Hit Rate and MRR calculation on rank 1 hits
- MRR reduction when ground truth ranks lower (rank 2, rank 5)
- Zero score assignment for missed retrievals
- Faithfulness claim alignment checking
- Empty test set handling

## Cleanup
```bash
rm -rf .pytest_cache __pycache__ .venv
```

## Troubleshooting
Ensure ranks are 1-indexed (`rank = 1, 2, ...`).

## Security notes
Runs completely offline on local CPU.

## Extension exercises
Implement Context Precision metric calculation.

## Navigation
Day number: 327 of 365
