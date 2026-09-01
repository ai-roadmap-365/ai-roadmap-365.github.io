# Day 276 Lab: Dataset Processing & Validation Pipeline

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Building Fine-Tuning Datasets
- **Day number:** 276 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-276-building-fine-tuning-datasets
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-276-building-fine-tuning-datasets` when the site is running.
<!-- generated-links:end -->

## Purpose
Build a robust fine-tuning dataset curation and preprocessing pipeline in Python supporting Alpaca/ShareGPT conversion to ChatML, n-gram decontamination filtering, token length analytics, and response-only loss masking.

## Learning objectives
- Convert Alpaca and ShareGPT schemas to standardized ChatML format.
- Execute automated n-gram decontamination against benchmark query sets.
- Calculate token length statistics (mean, median, P95, max).
- Construct PyTorch-compatible `-100` response loss masks.

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
- Python Standard Library

## Installation
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements/requirements.txt
```

## File structure
- `starter/dataset_pipeline.py`: Starter implementation
- `examples/dataset_pipeline.py`: Reference implementation
- `tests/test_dataset_pipeline.py`: Unit test suite
- `expected-output/`: Captured execution logs

## How to run
```bash
python3 examples/dataset_pipeline.py
```

## What the commands do
- Processes conversation datasets, applies decontamination filters, and formats ChatML sequences with response loss masks.

## Expected output
```text
[DATASET] Ingested 100 samples | Decontaminated: 2 matches
[MASKING] System/User masked with -100 | Assistant tokens preserved
```

## Validation steps
Run test runner:
```bash
bash tests/run_tests.sh
```

## Tests
The test suite validates:
- Correct schema translation from Alpaca and ShareGPT to ChatML
- N-gram overlap detection and sample decontamination
- Token summary statistics calculation
- Exact prompt token masking (-100) and response token retention

## Cleanup
```bash
rm -rf .pytest_cache __pycache__ .venv
```

## Troubleshooting
Verify regex word extraction `re.findall(r'\b\w+\b', text.lower())` correctly captures clean tokens.

## Security notes
Runs completely offline on local CPU. Zero network transmission.

## Extension exercises
Implement dynamic multi-sample sequence packing up to 2,048 tokens.

## Navigation
Day number: 276 of 365
