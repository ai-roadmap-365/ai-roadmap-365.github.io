# Lab: Day 193 -- Saving and Versioning Models

## Lesson
Day number: 193 of 365.
Course: Course04-SS03 (Beyond Supervised Learning).
Topic: Model Persistence, Serialization Formats, and Enterprise Model Registries.

## Purpose
Build a complete, thread-safe Enterprise Model Registry in pure Python. You will implement cryptographic SHA-256 artifact hashing, register model versions with lineage metadata, enforce stage promotion state transitions, and ensure strict production uniqueness.

## Learning objectives
- Analyze serialization security trade-offs (pickle vs ONNX vs safetensors).
- Generate SHA-256 cryptographic hashes to verify binary artifact integrity.
- Implement semantic versioning (MAJOR.MINOR.PATCH) and lineage catalogs.
- Enforce stage promotion rules (Staging -> Production -> Archived).

## Prerequisites
- Python standard library (`hashlib`, `dataclasses`, dictionaries).
- Core understanding of software versioning and deployment stages.

## Supported operating systems
- macOS (Apple Silicon / Intel)
- Linux (Ubuntu, Debian, Fedora, Arch)
- Windows 11 / WSL2

## Hardware requirements
- 1+ CPU cores.
- 512 MB RAM.
- 50 MB disk space.

## Required software
- Python 3.11 or newer.
- pip package manager.
- virtualenv or venv module.

## Free and open-source options
All tools used in this lab (Python, pytest) are free and open-source under BSD/MIT licenses.

## Installation
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements/requirements.txt
```

## File structure
- `starter/saving_and_versioning_models_lib.py`: Student scaffold file.
- `examples/saving_and_versioning_models_lib.py`: Complete reference implementation.
- `tests/test_saving_and_versioning_models_lib.py`: Pytest automated validation suite.
- `expected-output/`: Verified output logs and baseline values.

## How to run
Execute the reference demonstration script:
```bash
python3 examples/saving_and_versioning_models_lib.py
```

## What the commands do
- Registers model versions `1.0.0` and `1.1.0`.
- Computes cryptographic SHA-256 checksums.
- Promotes `1.1.0` to Production, archiving `1.0.0`.

## Expected output
```
Registry Demo: Active Production Version = 1.1.0
```

## Validation steps
1. Check that SHA-256 hashes are 64 hexadecimal characters.
2. Verify that promoting a new version to PRODUCTION automatically archives the old version.
3. Ensure all unit test assertions pass.

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
- **Invalid Stage Error:** Ensure stage strings match `"STAGING"`, `"PRODUCTION"`, `"ARCHIVED"`, or `"REJECTED"`.

## Security notes
All computations execute locally without external network transmission.

## Extension exercises
1. Implement **Pydantic Schema Validation** during model registration.
2. Export registry metadata to a formatted JSON Model Card.

## Navigation

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Saving and Versioning Models
- **Day number:** 193 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-193-saving-and-versioning-models
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-193-saving-and-versioning-models` when the site is running.
<!-- generated-links:end -->
