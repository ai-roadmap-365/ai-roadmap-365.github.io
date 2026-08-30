# Lab: Day 229 -- Decoder Models: The GPT Family

## Lesson
Day number: 229 of 365.
Course: Course05-SS02 (Deep Learning - Sequence Models and Transformers).
Topic: GPT Decoder Architecture and Autoregressive Generation.

## Purpose
Build and test the `MiniatureGPT` causal language model architecture in PyTorch. Implement causal lower-triangular masking, construct the autoregressive decoder pipeline with Pre-LN residual streams, implement the temperature and top-k token generation rollout loop, and test autoregressive token generation.

## Learning objectives
- Implement the GPT causal autoregressive Transformer decoder architecture.
- Construct the Causal Attention Mask to prevent future token information leakage.
- Implement the autoregressive generation loop with temperature-scaled multinomial sampling.
- Verify dimensional compatibility and generation sequence rollout length.

## Prerequisites
- Day 228 (Encoder Models: BERT and Friends).
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
- `starter/decoder_models_the_gpt_family_lib.py`: Student scaffold file.
- `examples/decoder_models_the_gpt_family_lib.py`: Complete reference implementation.
- `tests/test_decoder_models_the_gpt_family_lib.py`: Pytest automated validation suite.
- `expected-output/`: Verified output logs and baseline values.

## How to run
Execute the reference demonstration script:
```bash
python3 examples/decoder_models_the_gpt_family_lib.py
```

## What the commands do
- Executes forward passes through the GPT causal model.
- Evaluates autoregressive generation rollouts.
- Runs unit test assertions.

## Expected output
```
GPT Demo: Prompt Len = 4, Generated Len = 8
```

## Validation steps
1. Verify `MiniatureGPT.forward` outputs a tensor of shape `(batch_size, seq_len, vocab_size)`.
2. Confirm `MiniatureGPT.generate` returns a tensor of shape `(batch_size, prompt_len + max_new_tokens)`.
3. Ensure all unit test assertions pass.

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
- **Causal mask dimension error:** Ensure the square subsequent mask matches `seq_len = x.size(1)` on the matching device.

## Security notes
All neural computations execute in local process memory.

## Extension exercises
1. Implement Top-p (Nucleus) sampling.
2. Implement an explicit KV-Cache module.

## Navigation

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Decoder Models: The GPT Family
- **Day number:** 229 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-229-decoder-models-the-gpt-family
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-229-decoder-models-the-gpt-family` when the site is running.
<!-- generated-links:end -->
