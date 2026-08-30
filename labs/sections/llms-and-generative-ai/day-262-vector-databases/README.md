# Lab: Day 262 -- Vector Databases

## Lesson
Day number: 262 of 365.
Course: Course06-SS02 (LLMs and Generative AI - Retrieval and Customization).
Topic: Vector Databases, Approximate Nearest Neighbors, HNSW, and IVF-PQ.

## Purpose
Build and test an In-Memory Navigable Small World (NSW) Vector Index in Python. Implement graph-based vector insertion, bidirectional neighbor linking, greedy beam search traversal, and analyze `efSearch` recall tuning.

## Learning objectives
- Implement graph-based vector index insertion with bounded neighborhood connectivity.
- Execute greedy logarithmic search traversal with priority candidate queues.
- Tune `efSearch` to observe trade-offs between graph recall and traversal steps.
- Compare NSW graph retrieval against flat linear scans.

## Prerequisites
- Day 261 (Semantic Similarity Search).
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
- `starter/vector_databases_lib.py`: Student scaffold file.
- `examples/vector_databases_lib.py`: Complete reference implementation.
- `tests/test_vector_databases_lib.py`: Pytest automated validation suite.
- `expected-output/`: Verified output logs and baseline values.

## How to run
Execute the reference demonstration script:
```bash
python3 examples/vector_databases_lib.py
```

## What the commands do
- Builds in-memory NSW graph index.
- Links vectors with bidirectional edges.
- Executes greedy graph traversal search.
- Runs unit test assertions.

## Expected output
```
NSW Demo Executed. Top Match: Doc 0 with score 1.0000
```

## Validation steps
1. Verify nodes establish bidirectional graph links.
2. Confirm greedy search discovers top nearest neighbors.
3. Validate higher efSearch improves candidate exploration.
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
- **Disconnected graph components:** Ensure the entry node has valid outgoing connections to subsequent nodes.

## Security notes
All computations execute locally in memory.

## Extension exercises
1. Implement a 2-layer HNSW graph with an upper sparse skip layer.
2. Measure Recall@5 vs efSearch on 1,000 synthetic vectors.

## Navigation

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Vector Databases
- **Day number:** 262 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-262-vector-databases
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-262-vector-databases` when the site is running.
<!-- generated-links:end -->
