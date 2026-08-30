# Lab: Day 261 -- Semantic Similarity Search

## Lesson
Day number: 261 of 365.
Course: Course06-SS02 (LLMs and Generative AI - Retrieval and Customization).
Topic: Semantic Similarity Search, Exact k-NN, Vectorized BLAS, and Top-K Heaps.

## Purpose
Build and test a high-performance Exact k-NN Semantic Search Engine in Python. Implement vectorized matrix dot product retrieval, Top-K bounded selection with `np.argpartition`, and metadata pre-filtering.

## Learning objectives
- Implement vectorized matrix-vector dot product scoring across normalized vector databases.
- Optimize Top-K extraction using `np.argpartition` to avoid $O(N \log N)$ sorting bottlenecks.
- Implement structured metadata pre-filtering over vector corpora.
- Measure search latency scaling across collections up to 50,000 vectors.

## Prerequisites
- Day 260 (What Embeddings Are).
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
- `starter/semantic_similarity_search_lib.py`: Student scaffold file.
- `examples/semantic_similarity_search_lib.py`: Complete reference implementation.
- `tests/test_semantic_similarity_search_lib.py`: Pytest automated validation suite.
- `expected-output/`: Verified output logs and baseline values.

## How to run
Execute the reference demonstration script:
```bash
python3 examples/semantic_similarity_search_lib.py
```

## What the commands do
- Builds in-memory vector index.
- Normalizes vectors and executes query dot products.
- Runs unit test assertions.

## Expected output
```
k-NN Demo Executed. Top Match: 0 with score 0.9950
```

## Validation steps
1. Verify dot product matches cosine similarity on unit-normalized vectors.
2. Confirm Top-K extraction returns exact descending ranked order.
3. Validate metadata filtering excludes non-matching tags.
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
- **Zero division warning:** Ensure zero-length vectors have their norm defaulted to 1.0.

## Security notes
All computations execute locally in memory.

## Extension exercises
1. Implement a batch query search method executing matrix-matrix multiplications (`np.dot(Q, D.T)`).
2. Measure latency differences between float32 and float16 tensors.

## Navigation

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Semantic Similarity Search
- **Day number:** 261 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-261-semantic-similarity-search
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-261-semantic-similarity-search` when the site is running.
<!-- generated-links:end -->
