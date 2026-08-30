# Lab: Day 218 -- Text Preprocessing and Tokenization

## Lesson
Day number: 218 of 365.
Course: Course05-SS02 (Deep Learning - Sequence Models and Transformers).
Topic: Text Preprocessing and Tokenization Foundations.

## Purpose
Build and test a complete text preprocessing and tokenization toolkit in Python. Implement regular expression pre-tokenization, train a Byte-Pair Encoding (BPE) merge registry from scratch on text corpora, manage special tokens and vocabulary indexing, and generate padded batch tensors with attention masks.

## Learning objectives
- Implement regex-based word and punctuation splitting rules.
- Train Byte-Pair Encoding (BPE) subword merge rules from frequency statistics.
- Construct vocabulary registries with special tokens (<pad>, <unk>, <bos>, <eos>).
- Pad variable-length integer token sequences and construct corresponding binary attention masks.

## Prerequisites
- Day 217 (Your Own Image Classifier).
- Python 3.11+ with standard library modules.

## Supported operating systems
- macOS (Apple Silicon / Intel)
- Linux (Ubuntu, Debian, Fedora, Arch)
- Windows 11 / WSL2

## Hardware requirements
- 1+ CPU cores.
- 512 MB RAM.
- 50 MB disk space.

## Required software
- Python 3.11 or newer.
- pip package manager.
- virtualenv or venv module.

## Free and open-source options
All tokenization routines use Python standard library modules (`re`, `collections`) and open-source `pytest`.

## Installation
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements/requirements.txt
```

## File structure
- `starter/text_preprocessing_and_tokenization_lib.py`: Student scaffold file.
- `examples/text_preprocessing_and_tokenization_lib.py`: Complete reference implementation.
- `tests/test_text_preprocessing_and_tokenization_lib.py`: Pytest automated validation suite.
- `expected-output/`: Verified output logs and baseline values.

## How to run
Execute the reference demonstration script:
```bash
python3 examples/text_preprocessing_and_tokenization_lib.py
```

## What the commands do
- Executes regex pre-tokenization across sample sentences.
- Trains a BPE merge model on text corpus and encodes unseen words into subwords.
- Formats token sequences into padded rectangular batches with attention masks.

## Expected output
```
Tokenization Demo: Vocab Size = 15, Merges = 5, Padded Len = 3
```

## Validation steps
1. Verify `regex_pre_tokenize` separates words, contractions, and punctuation correctly.
2. Confirm `BPETokenizer.train` successfully discovers and records subword bigram merges.
3. Check that `pad_and_mask_batch` generates identical max-length vectors with matching binary masks.

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
- **Infinite Loop in Merge:** Ensure bigram counts terminate when no remaining pairs exist in vocabulary.

## Security notes
All tokenization and vocabulary generation algorithms execute locally without network access.

## Extension exercises
1. Implement Byte-level BPE supporting raw UTF-8 binary encoding.
2. Add BPE-dropout stochastic subword sampling.

## Navigation

<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Text Preprocessing and Tokenization
- **Day number:** 218 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-218-text-preprocessing-and-tokenization
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-218-text-preprocessing-and-tokenization` when the site is running.
<!-- generated-links:end -->
