# Day 325 Lab: Query Transformation and Routing

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
<!-- generated-links:end -->

## Purpose
Build a Query Transformation and Semantic Routing Engine in Python supporting HyDE synthetic document generation, multi-query expansion, and intent routing.

## Learning objectives
- Classify queries to route between SQL, Vector RAG, and Direct LLM bypass.
- Implement Hypothetical Document Embeddings (HyDE) transformation templates.
- Expand single queries into diverse multi-query variations.
- Evaluate routing precision and latency benefits.

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
- `starter/query_router.py`: Starter implementation skeleton
- `examples/query_router.py`: Verified reference implementation
- `tests/test_query_router.py`: Test suite
- `expected-output/`: Captured execution logs

## How to run
```bash
python3 examples/query_router.py
```

## What the commands do
- Executes query classification, HyDE generation, and multi-query expansion.

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
- Routing SQL aggregation queries to `TEXT2SQL_DATABASE`
- Routing documentation queries to `VECTOR_RAG`
- Routing conversational greetings to `DIRECT_LLM_BYPASS`
- Correct HyDE passage synthesis
- Generating 4 diverse expanded query variants

## Cleanup
```bash
rm -rf .pytest_cache __pycache__ .venv
```

## Troubleshooting
Ensure direct LLM bypass checks precede keyword searches.

## Security notes
Runs completely offline on local CPU.

## Extension exercises
Implement step-back question derivation.

## Navigation
Day number: 325 of 365
