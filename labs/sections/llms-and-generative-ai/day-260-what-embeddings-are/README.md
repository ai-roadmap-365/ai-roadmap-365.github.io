# Lab: Day 260 -- What Embeddings Are

## Lesson
Day number: 260 of 365.
Course: Course06-SS02 (LLMs and Generative AI - Retrieval and Customization).
Topic: Dense Embeddings, Vector Spaces, and Similarity Mathematics.

## Purpose
Build and test a Pure NumPy Vector Similarity Engine. Implement L2 vector normalization, cosine similarity, Euclidean distance, multi-document semantic ranking, and Matryoshka dimension truncation.

## Learning objectives
- Normalize multi-dimensional vectors to unit sphere length.
- Calculate cosine similarity and Euclidean distance between vectors.
- Rank a collection of candidate document vectors against an incoming query vector.
- Implement Matryoshka sub-vector truncation and re-normalization.

## Prerequisites
- Day 259 (Building a CLI Assistant).
- Python 3.11+ with NumPy and Pytest.

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
NumPy and Python standard libraries are open source.

## Installation
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements/requirements.txt
```

## File structure
- `starter/what_embeddings_are_lib.py`: Student scaffold file.
- `examples/what_embeddings_are_lib.py`: Complete reference implementation.
- `tests/test_what_embeddings_are_lib.py`: Pytest automated validation suite.
- `expected-output/`: Verified output logs and baseline values.

## How to run
Execute the reference demonstration script:
```bash
python3 examples/what_embeddings_are_lib.py
```

## What the commands do
- Normalizes sample vectors.
- Computes cosine similarity and L2 distance.
- Runs unit test assertions.

## Expected output
```
Embeddings Demo Executed. Cosine Sim: 1.0000, L2 Dist: 0.0000
```

## Validation steps
1. Verify L2 normalization produces vectors of length 1.0.
2. Confirm identical vectors produce cosine similarity 1.0.
3. Validate orthogonal vectors produce cosine similarity 0.0.
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
- **Zero division error:** Handle zero-magnitude vectors gracefully in normalization functions.

## Security notes
All vector arithmetic runs locally in memory.

## Extension exercises
1. Implement a K-Means vector clustering algorithm in pure NumPy.
2. Build an embedding dimensionality reduction benchmark.

## Navigation

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** What Embeddings Are
- **Day number:** 260 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-260-what-embeddings-are
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-260-what-embeddings-are` when the site is running.
<!-- generated-links:end -->
