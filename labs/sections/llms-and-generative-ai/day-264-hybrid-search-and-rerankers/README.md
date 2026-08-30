# Lab: Day 264 -- Hybrid Search and Re-Ranking

## Lesson
Day number: 264 of 365.
Course: Course06-SS02 (LLMs and Generative AI - Retrieval and Customization).
Topic: Hybrid Search, BM25, Reciprocal Rank Fusion (RRF), and Re-Ranking.

## Purpose
Build and test an End-to-End Hybrid Search & Re-Ranking Pipeline in Python. Implement BM25 lexical keyword scoring, Reciprocal Rank Fusion (RRF) rank combination, and evaluate candidate merging.

## Learning objectives
- Implement BM25 term frequency saturation and document length normalization.
- Execute Reciprocal Rank Fusion (RRF) to merge heterogeneous candidate rankings.
- Explain the trade-offs between Bi-Encoders and Cross-Encoders.
- Build a robust two-stage retrieval pipeline.

## Prerequisites
- Day 263 (Chunking Strategies).
- Python 3.11+ with Pytest.

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
Pure Python standard math libraries are open source.

## Installation
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements/requirements.txt
```

## File structure
- `starter/hybrid_search_lib.py`: Student scaffold file.
- `examples/hybrid_search_lib.py`: Complete reference implementation.
- `tests/test_hybrid_search_lib.py`: Pytest automated validation suite.
- `expected-output/`: Verified output logs and baseline values.

## How to run
Execute the reference demonstration script:
```bash
python3 examples/hybrid_search_lib.py
```

## What the commands do
- Indexes document corpus with BM25 term weights.
- Executes BM25 keyword search.
- Merges candidate lists with RRF rank fusion.
- Runs unit test assertions.

## Expected output
```
Hybrid Demo Executed. Top Match: Error 504 Gateway Timeout on API gateway with RRF score 0.0325
```

## Validation steps
1. Verify BM25 ranks exact keyword matches highest.
2. Confirm RRF scores combine inverse rank positions.
3. Validate candidate deduplication during fusion.
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
- **Zero IDF scores:** Add the smoothing constant 1.0 to the logarithmic IDF formula.

## Security notes
All computations execute locally in memory.

## Extension exercises
1. Implement linear convex alpha score fusion.
2. Integrate a local FlashRank ONNX cross-encoder.

## Navigation

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Hybrid Search and Rerankers
- **Day number:** 264 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-264-hybrid-search-and-rerankers
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-264-hybrid-search-and-rerankers` when the site is running.
<!-- generated-links:end -->
