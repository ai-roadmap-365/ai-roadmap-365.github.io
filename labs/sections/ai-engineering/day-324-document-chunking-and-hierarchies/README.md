# Day 324 Lab: Document Chunking and Hierarchies

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
<!-- generated-links:end -->

## Purpose
Build a Hierarchical Document Chunker and Parent Retriever in Python supporting parent-child splitting, child vector search, and parent document resolution.

## Learning objectives
- Split raw documents into parent blocks and child search nodes.
- Manage parent-child metadata pointers.
- Execute small-to-big retrieval resolving parent text from child hits.
- Deduplicate multiple child hits pointing to the same parent block.

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
- `starter/chunking_hierarchy.py`: Starter implementation skeleton
- `examples/chunking_hierarchy.py`: Verified reference implementation
- `tests/test_chunking_hierarchy.py`: Test suite
- `expected-output/`: Captured execution logs

## How to run
```bash
python3 examples/chunking_hierarchy.py
```

## What the commands do
- Executes hierarchical splitting, child indexing, and small-to-big retrieval.

## Expected output
```text
All 5 checks passed 100% with zero errors.
```

## Validation steps
Run test runner:
```bash
bash tests/run_tests.sh
```

## Tests
The test suite validates:
- Parent block and child chunk creation
- Child-to-parent metadata mapping
- Small-to-big search returning full parent context
- Deduplication of overlapping child matches
- Edge case handling for short documents

## Cleanup
```bash
rm -rf .pytest_cache __pycache__ .venv
```

## Troubleshooting
Ensure parent chunks are indexed with unique IDs.

## Security notes
Runs completely offline on local CPU.

## Extension exercises
Add markdown AST header preservation in child metadata.

## Navigation
Day number: 324 of 365
