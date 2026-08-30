# Lab: Day 248 -- Few-Shot Examples and Chain of Thought

## Lesson
Day number: 248 of 365.
Course: Course06-SS01 (LLMs and Generative AI - Working with LLMs).
Topic: Few-Shot In-Context Learning, Chain of Thought, and Self-Consistency.

## Purpose
Build and test a modular Few-Shot Chain-of-Thought compilation engine and Self-Consistency voting aggregator in Python. Construct exemplar pools with XML tags, compile multi-turn CoT scratchpads, and evaluate majority consensus across stochastic rollout distributions.

## Learning objectives
- Formulate XML-delimited Few-Shot exemplar pools.
- Construct Chain-of-Thought scratchpads to expand autoregressive compute.
- Implement Self-Consistency majority voting over stochastic sample paths.
- Prevent exemplar biases (majority label bias, recency bias).

## Prerequisites
- Day 247 (System Prompts and Role Design).
- Python 3.11+ with Pytest.

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
Python and standard math libraries are open source.

## Installation
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements/requirements.txt
```

## File structure
- `starter/few_shot_examples_and_chain_of_lib.py`: Student scaffold file.
- `examples/few_shot_examples_and_chain_of_lib.py`: Complete reference implementation.
- `tests/test_few_shot_examples_and_chain_of_lib.py`: Pytest automated validation suite.
- `expected-output/`: Verified output logs and baseline values.

## How to run
Execute the reference demonstration script:
```bash
python3 examples/few_shot_examples_and_chain_of_lib.py
```

## What the commands do
- Compiles Few-Shot CoT XML prompts.
- Aggregates stochastic sampled rollouts.
- Runs unit test assertions.

## Expected output
```
CoT Demo Compiled Successfully. Consensus: 224
```

## Validation steps
1. Verify `compile_prompt` generates `<examples>` and `<scratchpad>` tags.
2. Confirm `aggregate_self_consistency` computes consensus mode and confidence.
3. Validate empty list handling raises `ValueError`.
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
- **Empty sample list:** Pass at least 1 sample to `aggregate_self_consistency`.

## Security notes
All prompt generation executes locally in memory.

## Extension exercises
1. Implement a dynamic cosine-similarity exemplar retriever.
2. Build a Tree-of-Thoughts breadth-first search navigator.

## Navigation

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Few-Shot Examples and Chain of Thought
- **Day number:** 248 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-248-few-shot-examples-and-chain-of
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-248-few-shot-examples-and-chain-of` when the site is running.
<!-- generated-links:end -->
