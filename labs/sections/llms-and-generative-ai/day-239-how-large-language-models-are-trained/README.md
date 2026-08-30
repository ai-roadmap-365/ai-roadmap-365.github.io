# Lab: Day 239 -- How Large Language Models Are Trained

## Lesson
Day number: 239 of 365.
Course: Course06-SS01 (LLMs and Generative AI - Working with LLMs).
Topic: Industrial LLM Pre-Training, Web Data Filtering, and MinHash Deduplication.

## Purpose
Build and test an industrial LLM data preprocessing pipeline in Python. Implement Gopher rule-based quality heuristics, build a MinHash LSH near-duplicate detector, and verify that clean text passes while spam and duplicate documents are rejected.

## Learning objectives
- Implement Gopher rule-based document quality filtering heuristics.
- Build a MinHash LSH signature generator to estimate Jaccard similarity.
- Filter out SEO spam, symbol-dense noise, and short text documents.
- Understand binary token memory mapping principles for cluster DataLoaders.

## Prerequisites
- Day 238 (Section Project: Reproducing a Paper).
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
- `starter/how_large_language_models_are_trained_lib.py`: Student scaffold file.
- `examples/how_large_language_models_are_trained_lib.py`: Complete reference implementation.
- `tests/test_how_large_language_models_are_trained_lib.py`: Pytest automated validation suite.
- `expected-output/`: Verified output logs and baseline values.

## How to run
Execute the reference demonstration script:
```bash
python3 examples/how_large_language_models_are_trained_lib.py
```

## What the commands do
- Evaluates Gopher heuristics on clean and spam text samples.
- Generates MinHash signatures and computes Jaccard similarity estimates.
- Runs unit test assertions.

## Expected output
```
Data Pipeline Demo: Clean Passed = True, Spam Passed = False, Estimated Jaccard = 0.906
```

## Validation steps
1. Verify `passes_gopher_heuristics` rejects text under 8 words or with excessive symbols.
2. Confirm `compute_minhash_signature` generates `num_perm` integer hash values.
3. Confirm `estimate_jaccard` detects near-duplicate text ($> 0.60$) and differentiates unique text ($< 0.20$).
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
- **Noisy Jaccard estimates:** Increase `num_perm` from 32 to 64.

## Security notes
All data filtering executes locally in process memory.

## Extension exercises
1. Implement a regex-based PII scrubber removing emails and credit cards.
2. Build an educational quality heuristic scoring function.

## Navigation

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** How Large Language Models Are Trained
- **Day number:** 239 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-239-how-large-language-models-are-trained
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-239-how-large-language-models-are-trained` when the site is running.
<!-- generated-links:end -->
