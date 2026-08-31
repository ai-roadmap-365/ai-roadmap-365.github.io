# Day 310 Lab: Building Evaluation Datasets

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Building Evaluation Datasets
- **Day number:** 310 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-310-building-evaluation-datasets
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-310-building-evaluation-datasets` when the site is running.
<!-- generated-links:end -->

## Purpose
Implement an Evaluation Dataset Curator in Python that loads, validates, de-duplicates, stratifies, and exports JSONL evaluation datasets.

## Learning objectives
- Load and parse JSONL evaluation files.
- Validate record schemas and filter illegal categories.
- De-duplicate queries using normalized string matching.
- Compute stratified category distribution counts and export clean JSONL benchmarks.

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
- `starter/dataset_curator.py`: Starter implementation skeleton
- `examples/dataset_curator.py`: Verified reference implementation
- `tests/test_dataset_curator.py`: Test suite
- `expected-output/`: Captured execution logs

## How to run
```bash
python3 examples/dataset_curator.py
```

## What the commands do
- Curates, validates, and exports stratified evaluation datasets in JSONL format.

## Expected output
```text
Stratified counts: {'happy_path': 1, 'hard_negative': 0, 'schema_boundary': 0, 'adversarial': 0}
```

## Validation steps
Run test runner:
```bash
bash tests/run_tests.sh
```

## Tests
The test suite validates:
- Record insertion and category validation
- Normalized query de-duplication
- Stratified category counting
- JSONL file loading and exporting

## Cleanup
```bash
rm -rf .pytest_cache __pycache__ .venv *.jsonl
```

## Troubleshooting
Ensure input records contain non-empty `id`, `query`, and `expected_output` fields.

## Security notes
Runs completely offline on local CPU.

## Extension exercises
Add JSON schema validation for complex structured outputs.

## Navigation
Day number: 310 of 365
