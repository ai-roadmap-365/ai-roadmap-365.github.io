# Day 352 Lab: Architecture and Design Document

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Architecture and Design Document
- **Day number:** 352 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-352-architecture-and-design-document
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-352-architecture-and-design-document` when the site is running.
<!-- generated-links:end -->

## Purpose
Build an automated System Architecture & Design Document (ADD) Linter in Python that validates architectural completeness across C4 topologies, OpenAPI contracts, schemas, and failure domains.

## Learning objectives
- Structure a C4 architectural blueprint in Markdown.
- Validate OpenAPI endpoints and JSON tool calling contracts.
- Audit circuit breaker timeouts and fallback cascades.
- Calculate architectural compliance scores in CI/CD.

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
- `starter/architecture_linter.py`: Starter implementation skeleton
- `examples/architecture_linter.py`: Verified reference implementation
- `tests/test_architecture_linter.py`: Test suite
- `expected-output/`: Captured execution logs

## How to run
```bash
python3 examples/architecture_linter.py
```

## What the commands do
- Evaluates sample architectural markdown documents and verifies structural completeness.

## Expected output
```text
{'score': 0, 'status': 'REJECTED', 'errors': ["Missing mandatory sections: ['1. System Overview & Problem Statement', '2. High-Level Component Topology', '3. Data Flow & Sequence Diagrams', '4. Data Schemas & Storage Design', '5. Latency & Resource Budgets', '6. Failure Mode & Resilience Strategies', '7. Security & Compliance Architecture']", 'Architecture lacks circuit breaker / fallback model resilience specification.', 'Architecture lacks p95 latency budget table.'], 'missing_sections': ['1. System Overview & Problem Statement', '2. High-Level Component Topology', '3. Data Flow & Sequence Diagrams', '4. Data Schemas & Storage Design', '5. Latency & Resource Budgets', '6. Failure Mode & Resilience Strategies', '7. Security & Compliance Architecture']}
```

## Validation steps
Run test runner:
```bash
bash tests/run_tests.sh
```

## Tests
The test suite validates:
- Mandatory section header verification
- OpenAPI endpoint contract auditing
- Latency and SLA budget verification
- Circuit breaker resilience checking
- Compliance scoring and violation reporting

## Cleanup
```bash
rm -rf .pytest_cache __pycache__ .venv
```

## Troubleshooting
Ensure all mandatory section titles match the linter specification.

## Security notes
Runs locally with zero external network calls.

## Extension exercises
Implement an automated markdown-to-OpenAPI JSON exporter.

## Navigation
Day number: 352 of 365
