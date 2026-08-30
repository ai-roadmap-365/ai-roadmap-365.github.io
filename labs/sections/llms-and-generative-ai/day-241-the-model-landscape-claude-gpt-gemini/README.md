# Lab: Day 241 -- The Model Landscape: Claude, GPT, Gemini, Llama

## Lesson
Day number: 241 of 365.
Course: Course06-SS01 (LLMs and Generative AI - Working with LLMs).
Topic: Frontier LLM Landscape, Model Routing, and Cost Optimization.

## Purpose
Build and test a modular model routing and cost calculation engine in Python. Implement heuristic and keyword query classification, dispatch prompts to appropriate cost/latency tiers, calculate multi-tier API billing costs, and simulate blended enterprise cost savings.

## Learning objectives
- Analyze the operational trade-offs between Claude 3.5 Sonnet, GPT-4o, Gemini 2.0 Flash, and open-weights models.
- Implement rule-based and keyword-driven semantic query dispatching.
- Calculate exact multi-tier API costs incorporating input/output token pricing and prompt caching discounts.
- Simulate blended fleet cost savings comparing monolithic routing vs multi-tier routing.

## Prerequisites
- Day 240 (Pretraining, Fine-Tuning, and RLHF).
- Python 3.11+ with PyTorch and NumPy.

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
- `starter/the_model_landscape_claude_gpt_gemini_lib.py`: Student scaffold file.
- `examples/the_model_landscape_claude_gpt_gemini_lib.py`: Complete reference implementation.
- `tests/test_the_model_landscape_claude_gpt_gemini_lib.py`: Pytest automated validation suite.
- `expected-output/`: Verified output logs and baseline values.

## How to run
Execute the reference demonstration script:
```bash
python3 examples/the_model_landscape_claude_gpt_gemini_lib.py
```

## What the commands do
- Evaluates query routing decisions across code, classification, and long-context prompts.
- Computes API query costs with prompt caching discounts.
- Runs unit test assertions.

## Expected output
```
Router Demo: Code -> claude-3.5-sonnet, Quick -> gpt-4o-mini, Long -> gemini-2.0-flash, Sonnet Cost = $0.1650, Cached = $0.0525
```

## Validation steps
1. Verify code queries route to `claude-3.5-sonnet`.
2. Confirm short classification queries route to `gpt-4o-mini`.
3. Confirm long context queries ($> 150k$ tokens) route to `gemini-2.0-flash`.
4. Confirm `is_cached=True` applies a $75\%$ input token discount.
5. Ensure all unit test assertions pass.

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
- **Cost scaling error:** Ensure token counts are divided by $1,000,000$ when multiplying by rate card prices.

## Security notes
All routing calculations execute locally in process memory.

## Extension exercises
1. Implement a latency-aware router incorporating provider status checks.
2. Build an automated fallback cascade handling simulated 429 rate limit exceptions.

## Navigation

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** The Model Landscape: Claude, GPT, Gemini, Llama
- **Day number:** 241 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-241-the-model-landscape-claude-gpt-gemini
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-241-the-model-landscape-claude-gpt-gemini` when the site is running.
<!-- generated-links:end -->
