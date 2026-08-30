# Lab: Day 221 -- LSTMs and GRUs

## Lesson
Day number: 221 of 365.
Course: Course05-SS02 (Deep Learning - Sequence Models and Transformers).
Topic: Gated Recurrent Units (LSTMs and GRUs).

## Purpose
Build and test custom LSTM and GRU neural cells in PyTorch. Implement the mathematical gating equations for Forget, Input, Output, and Update gates from first principles, and verify hidden state and cell state propagation.

## Learning objectives
- Implement the 4-gate LSTM cell forward equations and Constant Error Carousel.
- Implement the 2-gate GRU cell forward update equations.
- Verify dimensional compatibility and activation ranges in recurrent states.
- Compare parameter complexity between LSTM and GRU cell architectures.

## Prerequisites
- Day 220 (Recurrent Neural Networks).
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
- `starter/lstms_and_grus_lib.py`: Student scaffold file.
- `examples/lstms_and_grus_lib.py`: Complete reference implementation.
- `tests/test_lstms_and_grus_lib.py`: Pytest automated validation suite.
- `expected-output/`: Verified output logs and baseline values.

## How to run
Execute the reference demonstration script:
```bash
python3 examples/lstms_and_grus_lib.py
```

## What the commands do
- Executes forward passes through custom LSTM and GRU cells.
- Verifies output tensor dimensions and forget gate bias initialization.
- Runs unit test assertions.

## Expected output
```
LSTM/GRU Demo: LSTM h Shape = torch.Size([4, 16]), GRU h Shape = torch.Size([4, 16])
```

## Validation steps
1. Verify `CustomLSTMCell.forward` returns valid `h_t` and `c_t` tensors.
2. Confirm `CustomGRUCell.forward` returns valid `h_t` tensor matching hidden dimensions.
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
- **Dimensions mismatch in chunk:** Ensure linear projection maps to `4 * hidden_dim` for LSTM and `2 * hidden_dim` for GRU reset/update gates.

## Security notes
All neural gating routines execute locally in memory.

## Extension exercises
1. Implement a complete multi-layer Bidirectional LSTM classifier with PackedSequence support.
2. Add peephole connections connecting cell state to gate activations.

## Navigation

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** LSTMs and GRUs
- **Day number:** 221 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-221-lstms-and-grus
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-221-lstms-and-grus` when the site is running.
<!-- generated-links:end -->
