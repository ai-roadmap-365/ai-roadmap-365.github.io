# Project: Week 40 -- Local Fine-Tuned Model

## Overview
Build an end-to-end local fine-tuning, weight merging, quantization, serving, and quantitative evaluation system in Python. The project takes a specialized domain dataset (Text-to-Structured-SQL), prepares clean ChatML training pairs, applies Low-Rank Adaptation (LoRA), folds the trained delta weights into base tensors, quantizes the resulting model into INT8/INT4 format, exposes a local streaming API server, and automatically benchmarks performance against the un-tuned base model.

## Learning objectives
- Curate and validate a domain-specific instruction dataset formatted in ChatML format with token masking.
- Implement LoRA forward pass and parameter estimation across attention projection matrices.
- Perform permanent weight merging via W_merged = W_base + (B * A) * (alpha / r).
- Implement symmetric linear INT8 quantization and compute reconstruction Mean Squared Error (MSE).
- Construct a local inference engine with simulated PagedAttention virtual block memory management.
- Build an automated evaluation suite measuring JSON / SQL syntax validity and Exact Match (EM) accuracy gains.

## Architecture
```
local_finetuned_model/
  ├── __init__.py
  ├── dataset_builder.py     # Data curation, token masking & ChatML formatting
  ├── lora_engine.py         # LoRA adapter initialization and forward pass
  ├── weight_merger.py       # Adapter folding: W_base + (B @ A) * (alpha / r)
  ├── quantizer.py           # INT8 / INT4 symmetric quantization and GGUF packing
  ├── serving_engine.py      # PagedAttention memory allocator & continuous batching
  └── benchmark_evaluator.py # Automated syntax validity & Exact Match benchmarking
tests/
  ├── test_dataset.py        # Token masking and format assertions
  ├── test_merger.py         # Exact weight merging numerical assertions
  ├── test_quantizer.py      # Quantization MSE and compression assertions
  └── test_evaluator.py      # Comparative benchmark scoring assertions
```

## Core Functional Components

### 1. Dataset Builder (`dataset_builder.py`)
- Ingests raw question-SQL pairs and formats them into standard ChatML prompts (`<|im_start|>`).
- Validates token lengths and verifies loss masking on non-assistant tokens.

### 2. LoRA Engine (`lora_engine.py`)
- Initializes low-rank decomposition matrices A and B for rank r=8.
- Computes parameter efficiency: verifies <1% parameter count relative to base weights.

### 3. Weight Merger (`weight_merger.py`)
- Folds trained LoRA adapters into base weights using exact scaling factor alpha / r.
- Validates numerical stability and preserves tensor shapes.

### 4. INT8 Quantizer (`quantizer.py`)
- Computes scale factor s = max(|W|) / 127.0.
- Quantizes float tensors to signed INT8 and dequantizes with <0.001 MSE reconstruction loss.

### 5. Serving Engine (`serving_engine.py`)
- Simulates a PagedAttention memory manager with 16-token physical blocks.
- Implements continuous iteration-level request batching and early eviction.

### 6. Benchmark Evaluator (`benchmark_evaluator.py`)
- Evaluates base vs fine-tuned models on 50 golden test cases.
- Computes SQL/JSON Syntax Validity Rate, Exact Match (EM), and Token F1.

## Deliverables
1. Complete Python package in `local_finetuned_model/`.
2. Fully passing automated test suite in `tests/`.
3. Execution log demonstrating >40% improvement in syntax validity over base model.

## Expected output
When executing the Local Fine-Tuned Model project verification suite:
```text
======================================================================
WEEK 40 PROJECT: LOCAL FINE-TUNED MODEL VERIFICATION SUITE
======================================================================
[1/4] Testing Dataset Builder & Loss Masking:
      - ChatML Prompt Packaging: PASSED (<|im_start|> formatting validated)
      - Prompt Token Loss Masking (-100): PASSED (100% prompt tokens masked)
      - Target Response Token Verification: PASSED (Active cross-entropy loss)

[2/4] Testing LoRA Forward Pass & Permanent Weight Merging:
      - Low-Rank Decomposition (r=8, alpha=16): PASSED (Delta initialized to 0)
      - Weight Merging W_base + (B @ A) * (alpha/r): PASSED (Bit-exact match)
      - Parameter Efficiency Ratio: PASSED (0.78% trainable parameter footprint)

[3/4] Testing Symmetric INT8 Quantization & GGUF Parser:
      - Header Struct Unpacking: PASSED (Validated 'GGUF' magic & version 3)
      - INT8 Scale Computation: PASSED (Scale: 0.007874)
      - Reconstruction MSE Loss: PASSED (0.00000512 < 0.001 threshold)
      - Memory Compression Ratio: PASSED (75.0% memory reduction)

[4/4] Testing PagedAttention Serving & Comparative Evaluation:
      - Paged Block Allocation: PASSED (16-token non-contiguous blocks)
      - Continuous Iteration Batching: PASSED (Zero head-of-line blocking)
      - Base Model SQL Syntax Validity: 52.0% [FAIL]
      - Fine-Tuned Model SQL Syntax Validity: 100.0% [PASS]
      - Accuracy Improvement: +48.0% [PASS]

======================================================================
ALL 4 PROJECT SUBSYSTEMS VERIFIED -- 18 TESTS PASSED (100% GREEN)
======================================================================
```

## Validation
Execute the project verification test suite:
```bash
pytest tests/ -v
```
All tests must pass with 0 errors, validating dataset formatting, LoRA weight merging, INT8 quantization, PagedAttention block allocation, and comparative evaluation metrics.
