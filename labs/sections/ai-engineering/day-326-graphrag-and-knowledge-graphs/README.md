# Day 326 Lab: GraphRAG and Knowledge Graphs

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
<!-- generated-links:end -->

## Purpose
Build a GraphRAG and Multi-Hop Traversal Engine in Python supporting entity-relation graphs, 2-hop local traversal, and global community summary retrieval.

## Learning objectives
- Model entities and directed relationships in graph memory.
- Execute local multi-hop traversal along relational edges.
- Register and query hierarchical community executive summaries.
- Differentiate Local vs Global retrieval use cases.

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
- `starter/graphrag_engine.py`: Starter implementation skeleton
- `examples/graphrag_engine.py`: Verified reference implementation
- `tests/test_graphrag_engine.py`: Test suite
- `expected-output/`: Captured execution logs

## How to run
```bash
python3 examples/graphrag_engine.py
```

## What the commands do
- Executes graph construction, 2-hop local traversal, and global community summary search.

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
- Entity and relationship addition
- 2-hop local path traversal
- Handling unknown start entities gracefully
- Global community summary registration and query matching
- Multi-community relevance scoring

## Cleanup
```bash
rm -rf .pytest_cache __pycache__ .venv
```

## Troubleshooting
Ensure circular edges do not cause infinite loops.

## Security notes
Runs completely offline on local CPU.

## Extension exercises
Implement hierarchical community roll-ups.

## Navigation
Day number: 326 of 365
