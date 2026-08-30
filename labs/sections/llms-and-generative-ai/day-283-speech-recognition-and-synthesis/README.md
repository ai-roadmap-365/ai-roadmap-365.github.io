# Day 283 Lab: Speech Recognition & Synthesis Pipeline

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Speech: Recognition and Synthesis
- **Day number:** 283 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-283-speech-recognition-and-synthesis
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-283-speech-recognition-and-synthesis` when the site is running.
<!-- generated-links:end -->

## Purpose
Build a speech AI processing pipeline in Python and NumPy implementing 80-channel Log-Mel Spectrogram extraction, CTC greedy sequence decoding, and Word Error Rate (WER) Levenshtein evaluation.

## Learning objectives
- Transform 1D audio waveforms into 2D time-frequency Log-Mel Spectrograms.
- Implement the CTC greedy collapse decoding algorithm.
- Calculate Word Error Rate (WER) and Character Error Rate (CER).
- Benchmark transcription accuracy under simulated acoustic noise.

## Prerequisites
- Python 3.10+ installed
- NumPy and pytest installed

## Supported operating systems
- macOS, Linux, Windows WSL2

## Hardware requirements
- Standard CPU, 512MB RAM

## Required software
- Python 3.10+, numpy, pytest

## Free and open-source options
- Python Standard Library, NumPy

## Installation
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements/requirements.txt
```

## File structure
- `starter/speech_pipeline.py`: Starter implementation skeleton
- `examples/speech_pipeline.py`: Verified reference implementation
- `tests/test_speech_pipeline.py`: Test suite
- `expected-output/`: Captured execution logs

## How to run
```bash
python3 examples/speech_pipeline.py
```

## What the commands do
- Extracts spectrograms, executes CTC decoding, and calculates WER metrics.

## Expected output
```text
[MEL SPECTROGRAM] Extracted 80x100 features from 1.0s audio.
[CTC DECODE] Decoded tokens to: 'hello world'
[WER] Calculated WER: 0.0% on exact match.
```

## Validation steps
Run test runner:
```bash
bash tests/run_tests.sh
```

## Tests
The test suite validates:
- 80-channel Log-Mel Spectrogram dimension preservation
- CTC greedy collapse with blank token removal
- Levenshtein Word Error Rate calculation across substitutions, insertions, and deletions

## Cleanup
```bash
rm -rf .pytest_cache __pycache__ .venv
```

## Troubleshooting
Verify that WER properly normalizes by the length of the reference sentence.

## Security notes
Runs completely offline on local CPU.

## Extension exercises
Implement dynamic time warping (DTW) to compute alignment distance between two spoken audio waveforms.

## Navigation
Day number: 283 of 365
