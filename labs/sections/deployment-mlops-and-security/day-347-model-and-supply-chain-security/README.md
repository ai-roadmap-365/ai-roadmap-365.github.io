# Day 347 Lab: Model and Supply Chain Security

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Model and Supply Chain Security
- **Day number:** 347 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-347-model-and-supply-chain-security
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-347-model-and-supply-chain-security` when the site is running.
<!-- generated-links:end -->

## Purpose
Build a Production Model Supply Chain Security Scanner in Python that audits model directories, blocks dangerous pickle formats, calculates SHA256 checksums, and generates an AI Software Bill of Materials (AIBOM).

## Learning objectives
- Identify and flag insecure serialized model files (`.pt`, `.pkl`, `.bin`).
- Calculate SHA256 cryptographic hashes for supply chain validation.
- Validate SafeTensors compliance across model weight bundles.
- Generate structured CycloneDX-AI bill of materials manifests.

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
- `starter/model_security.py`: Starter implementation skeleton
- `examples/model_security.py`: Verified reference implementation
- `tests/test_model_security.py`: Test suite
- `expected-output/`: Captured execution logs

## How to run
```bash
python3 examples/model_security.py
```

## What the commands do
- Executes directory scans, checks format validation rules, verifies SHA256 hashes, and tests AIBOM JSON generation.

## Expected output
```text
Scanner ready.
```

## Validation steps
Run test runner:
```bash
bash tests/run_tests.sh
```

## Tests
The test suite validates:
- Insecure pickle format detection and rejection
- SafeTensors compliance verification
- SHA256 digest computation accuracy
- AIBOM CycloneDX manifest generation
- Non-existent directory error handling

## Cleanup
```bash
rm -rf .pytest_cache __pycache__ .venv
```

## Troubleshooting
Ensure all files are opened in binary mode (`'rb'`) for hashing.

## Security notes
Runs completely offline on local CPU.

## Extension exercises
Implement an automated converter from `.pt` to `.safetensors`.

## Navigation
Day number: 347 of 365
