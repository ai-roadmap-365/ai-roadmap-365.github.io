# Lab: Day 228 -- Encoder Models: BERT and Friends

## Lesson
Day number: 228 of 365.
Course: Course05-SS02 (Deep Learning - Sequence Models and Transformers).
Topic: BERT Encoder Architecture and Masked Language Modeling.

## Purpose
Build and test the `BERTMaskedLM` architecture in PyTorch. Implement token and positional embedding lookup, construct the multi-layer bidirectional Transformer encoder stack, implement the masked language model projection head with weight tying, and test vocabulary logit outputs.

## Learning objectives
- Implement the BERT bidirectional Transformer encoder architecture.
- Construct the Masked Language Model (MLM) head with GELU activation and LayerNorm.
- Enforce weight tying between input token embeddings and output decoder matrices.
- Verify dimensional compatibility and vocabulary logits output shapes.

## Prerequisites
- Day 227 (The Transformer Architecture).
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
- `starter/encoder_models_bert_and_friends_lib.py`: Student scaffold file.
- `examples/encoder_models_bert_and_friends_lib.py`: Complete reference implementation.
- `tests/test_encoder_models_bert_and_friends_lib.py`: Pytest automated validation suite.
- `expected-output/`: Verified output logs and baseline values.

## How to run
Execute the reference demonstration script:
```bash
python3 examples/encoder_models_bert_and_friends_lib.py
```

## What the commands do
- Executes forward passes through the BERT Masked LM model.
- Verifies weight tying and vocabulary projection logits.
- Runs unit test assertions.

## Expected output
```
BERT Demo: Logits Shape = torch.Size([2, 8, 100])
```

## Validation steps
1. Verify `BERTMaskedLM.forward` outputs a tensor of shape `(batch_size, seq_len, vocab_size)`.
2. Confirm `mlm_decoder.weight` shares the same underlying memory pointer as `token_embeddings.weight`.
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
- **Weight tying dimension error:** Ensure `vocab_size` and `d_model` match exactly between embedding and linear layers.

## Security notes
All neural computations execute in local process memory.

## Extension exercises
1. Implement dynamic masking collation in PyTorch.
2. Build a sequence classification head on the `[CLS]` token.

## Navigation

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Encoder Models: BERT and Friends
- **Day number:** 228 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-228-encoder-models-bert-and-friends
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-228-encoder-models-bert-and-friends` when the site is running.
<!-- generated-links:end -->
