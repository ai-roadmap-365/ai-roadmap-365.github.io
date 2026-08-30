# Day 294 Lab: Building a Research Agent

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Building a Research Agent
- **Day number:** 294 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-294-building-a-research-agent
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-294-building-a-research-agent` when the site is running.
<!-- generated-links:end -->

## Purpose
Build an autonomous Deep Research Agent capable of multi-hop query decomposition, atomic fact extraction, structured note-taking, and cited Markdown brief synthesis.

## Learning objectives
- Implement query decomposition breaking broad topics into orthogonal sub-queries.
- Extract atomic factual claims with verified source attribution into a Note Store.
- Synthesize executive Markdown briefs with numbered inline citations.
- Verify citation grounding and source deduplication.

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
- `starter/research_agent.py`: Starter implementation skeleton
- `examples/research_agent.py`: Verified reference implementation
- `tests/test_research_agent.py`: Test suite
- `expected-output/`: Captured execution logs

## How to run
```bash
python3 examples/research_agent.py
```

## What the commands do
- Executes agent runtime algorithms and logs state transitions to stdout.

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
- Core state transitions and algorithm logic
- Error observation handling and recovery
- Edge cases and bounds enforcement

## Cleanup
```bash
rm -rf .pytest_cache __pycache__ .venv
```

## Troubleshooting
Verify Python version is >= 3.10 and environment variables are set.

## Security notes
Runs completely offline on local CPU without network calls or API keys.

## Extension exercises
Implement async execution or enhanced caching strategies.

## Navigation
Day number: 294 of 365
