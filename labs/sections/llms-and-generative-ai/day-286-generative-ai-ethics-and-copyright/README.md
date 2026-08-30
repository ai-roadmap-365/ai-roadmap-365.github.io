# Day 286 Lab: Generative AI Ethics, pHash & C2PA Provenance

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Generative AI Ethics and Copyright
- **Day number:** 286 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-286-generative-ai-ethics-and-copyright
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-286-generative-ai-ethics-and-copyright` when the site is running.
<!-- generated-links:end -->

## Purpose
Build a copyright risk and content provenance verification engine in Python and NumPy implementing 64-bit Perceptual Hashing (pHash), Hamming distance matching, and C2PA cryptographic manifest signing.

## Learning objectives
- Implement 64-bit Perceptual Hashing (pHash) using 2D DCT transformations.
- Calculate Hamming distance between binary media fingerprints.
- Construct and verify cryptographically bound C2PA provenance manifests.
- Audit generated media against protected copyright and trademark databases.

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
- `starter/ethics_copyright.py`: Starter implementation skeleton
- `examples/ethics_copyright.py`: Verified reference implementation
- `tests/test_ethics_copyright.py`: Test suite
- `expected-output/`: Captured execution logs

## How to run
```bash
python3 examples/ethics_copyright.py
```

## What the commands do
- Computes perceptual hashes, executes C2PA manifest verification, and audits IP risks.

## Expected output
```text
[PHASH] Hash generated: 9f8a3c2e1b4d5e6f
[C2PA] Manifest verification PASSED with SHA-256 match.
```

## Validation steps
Run test runner:
```bash
bash tests/run_tests.sh
```

## Tests
The test suite validates:
- Deterministic pHash generation on identical visual arrays
- Near-duplicate tolerance under Gaussian noise perturbations
- C2PA payload hash integrity and tamper detection
- Database scanning for memorization risks

## Cleanup
```bash
rm -rf .pytest_cache __pycache__ .venv
```

## Troubleshooting
Ensure images are converted to 2D grayscale before computing DCT.

## Security notes
Runs completely offline on local CPU.

## Extension exercises
Implement an LSB watermark embedder to hide an invisible 8-bit signature in spatial images.

## Navigation
Day number: 286 of 365
