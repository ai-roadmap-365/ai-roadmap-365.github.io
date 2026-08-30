# Week 51 Capstone Project: Capstone Milestone 1 - Working Vertical Slice

## Purpose
Assemble and execute the complete, integrated **Capstone Milestone 1 Working Vertical Slice**: combining hybrid dense + BM25 retrieval, reciprocal rank fusion, core AI reasoning with XML prompt enclosure, circuit breaker model routing, sandboxed tool dispatching, Pydantic structured output validation, and automated RAG Triad evaluation in Python.

## Learning objectives
- Integrate the hybrid retrieval pipeline with BM25 and vector search.
- Connect the core AI reasoning engine with Pydantic schema validation.
- Implement sandboxed tool execution for agentic capabilities.
- Execute automated evaluation benchmarks scoring Faithfulness and Context Recall.
- Certify the working vertical slice with 100% passing unit and integration tests.

## Prerequisites
- Python 3.10+ installed
- pydantic and pytest installed

## Supported operating systems
- macOS, Linux, Windows WSL2

## Hardware requirements
- Standard CPU, 1GB RAM

## Required software
- Python 3.10+, pytest, pydantic

## Free and open-source options
- Python Standard Library, Pytest, Pydantic

## Installation
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements/requirements.txt
```

## File structure
- `starter/vertical_slice.py`: Starter implementation skeleton
- `examples/vertical_slice.py`: Verified reference implementation
- `tests/test_vertical_slice.py`: Integration test suite
- `expected-output/`: Captured execution logs

## How to run
```bash
python3 examples/vertical_slice.py
```

## What the commands do
- Executes an end-to-end user query through hybrid retrieval, reasoning, sandboxed tool dispatch, structured validation, and automated evaluation.

## Expected output
```text
All 6 integration checks passed 100% with zero errors.
[VERTICAL SLICE] Ingress query processed successfully.
[RETRIEVAL] Hybrid RRF returned top 2 grounded documents.
[REASONING] Core LLM generated type-safe AnswerPayload.
[AGENT TOOL] Sandboxed calculation tool executed with zero exceptions.
[EVALUATION] RAG Triad Faithfulness = 0.96 (Target >= 0.90).
[VERDICT] CAPSTONE MILESTONE 1 CERTIFIED.
```

## Validation steps
Run test runner:
```bash
bash tests/run_tests.sh
```

## Tests
The test suite validates:
- End-to-end query processing through all architectural layers
- Hybrid retrieval with Reciprocal Rank Fusion
- Pydantic structured JSON output validation
- Sandboxed tool calling and execution recovery
- RAG Triad Faithfulness and Context Recall compliance
- End-to-end latency budget (<1,500ms)

## Cleanup
```bash
rm -rf .pytest_cache __pycache__ .venv
```

## Troubleshooting
Ensure all internal modules return JSON-serializable dictionaries.

## Security notes
Runs locally with zero external network calls.

## Extension exercises
Deploy a FastAPI HTTP server exposing the vertical slice via `/api/v1/query`.

## Navigation
Project: Week 51 Capstone Milestone 1
