# Lab: Day 243 -- Tokens, Context Windows, and Sampling

## Lesson
Day number: 243 of 365.
Course: Course06-SS01 (LLMs and Generative AI - Working with LLMs).
Topic: Tokens, Context Windows, KV Cache, and Probabilistic Sampling.

## Purpose
Build and test a modular probabilistic sampling and KV-cache calculation engine in PyTorch. Implement Temperature scaling, Top-$k$ masking, Top-$p$ Nucleus truncation, and calculate exact KV-cache VRAM consumption across model architectures.

## Learning objectives
- Formulate the exact mathematical KV-cache memory scaling equation.
- Implement Temperature logit scaling ($z_i / T$) and analyze entropy changes.
- Build Top-$k$ and Top-$p$ (Nucleus) cumulative mass logit masking filters.
- Understand the hardware difference between compute-bound prefill and memory-bound token decoding.

## Prerequisites
- Day 242 (Open Weights versus Closed APIs).
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
PyTorch is open-source software maintained by the Linux Foundation under a modified BSD license.

## Installation
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements/requirements.txt
```

## File structure
- `starter/tokens_context_windows_and_sampling_lib.py`: Student scaffold file.
- `examples/tokens_context_windows_and_sampling_lib.py`: Complete reference implementation.
- `tests/test_tokens_context_windows_and_sampling_lib.py`: Pytest automated validation suite.
- `expected-output/`: Verified output logs and baseline values.

## How to run
Execute the reference demonstration script:
```bash
python3 examples/tokens_context_windows_and_sampling_lib.py
```

## What the commands do
- Computes exact KV-cache VRAM footprint for specified context lengths.
- Executes Greedy, Top-$k$, and Top-$p$ sampling over test logit distributions.
- Runs unit test assertions.

## Expected output
```
Sampling Demo: KV Cache (8k context) = 2.50 GB, Greedy Token = 42, Sampled = 42
```

## Validation steps
1. Verify `calculate_kv_cache_bytes` computes exact Key + Value byte sizes.
2. Confirm `sample_next_token` returns deterministic argmax when $T = 0.0$.
3. Confirm Top-$k$ and Top-$p$ filters mask tail probabilities to $-\infty$.
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
- **Probability sum error:** Ensure `F.softmax` is applied after masking logits with $-\infty$.

## Security notes
All sampling algorithms execute locally in process memory.

## Extension exercises
1. Implement the Min-P dynamic sampling filter.
2. Build an automated KV-cache VRAM capacity estimator for multi-GPU servers.

## Navigation

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Tokens, Context Windows, and Sampling
- **Day number:** 243 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-243-tokens-context-windows-and-sampling
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-243-tokens-context-windows-and-sampling` when the site is running.
<!-- generated-links:end -->
