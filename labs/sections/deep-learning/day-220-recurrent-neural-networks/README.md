# Lab: Day 220 -- Recurrent Neural Networks

## Lesson
Day number: 220 of 365.
Course: Course05-SS02 (Deep Learning - Sequence Models and Transformers).
Topic: Recurrent Neural Networks and Sequential State Modeling.

## Purpose
Build and test a custom Recurrent Neural Network (RNN) from first principles in PyTorch. Implement the recurrent hidden state transition equations, construct temporal sequence unrolling loops, and implement gradient norm clipping to stabilize recurrent optimization.

## Learning objectives
- Implement simple recurrent cell state updates (W_xh, W_hh, W_hy).
- Unroll recurrent networks over arbitrary variable-length sequences.
- Compute global L2 gradient norms and apply gradient clipping.
- Verify gradient propagation stability through sequential backpropagation.

## Prerequisites
- Day 219 (Word Embeddings).
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
- `starter/recurrent_neural_networks_lib.py`: Student scaffold file.
- `examples/recurrent_neural_networks_lib.py`: Complete reference implementation.
- `tests/test_recurrent_neural_networks_lib.py`: Pytest automated validation suite.
- `expected-output/`: Verified output logs and baseline values.

## How to run
Execute the reference demonstration script:
```bash
python3 examples/recurrent_neural_networks_lib.py
```

## What the commands do
- Unrolls a custom RNN over multi-step sequential input tensors.
- Performs backpropagation and measures global gradient norm.
- Clips gradient norm to threshold C=1.0 and executes unit test assertions.

## Expected output
```
RNN Demo: Logits Shape = torch.Size([2, 2]), Grad Norm = 2.1481
```

## Validation steps
1. Verify `SimpleRNNModel.forward` outputs a tensor of shape `(batch_size, num_classes)`.
2. Confirm `clip_gradient_norm` rescales large gradients to exactly `max_norm`.
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
- **Exploding Loss to NaN:** Ensure gradient clipping is called before `optimizer.step()`.

## Security notes
All neural forward and backward passes execute in local memory.

## Extension exercises
1. Implement a bidirectional recurrent unrolling loop (BiRNN).
2. Implement character-level language generation with temperature sampling.

## Navigation

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Recurrent Neural Networks
- **Day number:** 220 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-220-recurrent-neural-networks
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-220-recurrent-neural-networks` when the site is running.
<!-- generated-links:end -->
