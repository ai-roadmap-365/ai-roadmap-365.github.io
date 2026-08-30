# Lab: Day 263 -- Chunking Strategies

## Lesson
Day number: 263 of 365.
Course: Course06-SS02 (LLMs and Generative AI - Retrieval and Customization).
Topic: Document Chunking Strategies, Sliding Windows, Markdown Parsing, and Hierarchies.

## Purpose
Build and test a Multi-Strategy Document Chunker in Python. Implement fixed sliding windows with token overlaps, Markdown structure-aware splitting with breadcrumbs, and parent-child hierarchical chunk trees.

## Learning objectives
- Implement sliding window token chunking with parameterized boundary overlaps.
- Extract logical document sections from Markdown files while maintaining heading context.
- Build parent-child hierarchical chunk mappings to decouple retrieval matching from generation context.
- Prevent semantic boundary severance in structured documents.

## Prerequisites
- Day 262 (Vector Databases).
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
Pure Python standard libraries are open source.

## Installation
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements/requirements.txt
```

## File structure
- `starter/chunking_strategies_lib.py`: Student scaffold file.
- `examples/chunking_strategies_lib.py`: Complete reference implementation.
- `tests/test_chunking_strategies_lib.py`: Pytest automated validation suite.
- `expected-output/`: Verified output logs and baseline values.

## How to run
Execute the reference demonstration script:
```bash
python3 examples/chunking_strategies_lib.py
```

## What the commands do
- Executes sliding window token chunking.
- Parses Markdown documents into section chunks.
- Builds parent-child hierarchy structures.
- Runs unit test assertions.

## Expected output
```
Chunker Demo Executed. Generated 3 overlapping chunks.
```

## Validation steps
1. Verify sliding windows maintain exact overlap counts.
2. Confirm Markdown parser preserves heading text.
3. Validate child chunks reference parent document IDs.
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
- **Infinite loop:** Verify overlap is strictly less than chunk_size.

## Security notes
All computations execute locally.

## Extension exercises
1. Implement a Python AST chunker splitting along function declarations.
2. Implement cosine-distance semantic chunking.

## Navigation

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Chunking Strategies
- **Day number:** 263 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-263-chunking-strategies
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-263-chunking-strategies` when the site is running.
<!-- generated-links:end -->
