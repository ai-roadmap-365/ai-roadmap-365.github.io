# Week 35 Project: Model Comparison Study

## Overview
In this weekly capstone project, you will design, execute, and document an end-to-end empirical **Model Comparison Study** comparing two accessible foundation models (e.g. Claude 3.5 Sonnet vs. Gemini 2.0 Flash or LLaMA-3.1-8B vs. GPT-4o-mini) across a standardized 10-task evaluation benchmark.

You will measure task accuracy, token-level cost economics, latency distributions, failure modes, and positional judge bias, producing a publication-ready comparative report with statistical bootstrap confidence intervals.

## Objectives
- Construct a standardized 10-task benchmark suite spanning factual extraction, multi-hop reasoning, JSON code generation, math problem solving, and summarization.
- Implement an automated headless evaluation pipeline executing candidate models against deterministic assertions and dual-pass LLM-as-a-Judge rubrics.
- Compute Bradley-Terry ELO tournament updates and 95% bootstrap confidence intervals for model win rates.
- Profile latency percentiles (p50, p95, p99) and token consumption to build an empirical Cost-Quality Pareto frontier.
- Document qualitative failure modes (hallucination, sycophancy, truncation, schema violations) and formulate production model routing recommendations.

## Project Structure
```
week-35/
├── README.md
├── benchmark/
│   ├── tasks.json              # 10 standardized evaluation prompt definitions
│   └── rubrics.json            # Structured evaluation rubrics and grading criteria
├── src/
│   ├── evaluator.py            # Headless model runner and dual-pass judge harness
│   ├── metrics.py              # Bradley-Terry ELO, pass@k, and bootstrap statistics
│   └── reporter.py             # Cost-Quality Pareto plotter and report generator
└── reports/
    └── model_comparison_study.md # Final empirical findings and architectural recommendations
```

## Step-by-Step Implementation Guide

### 1. Define the 10-Task Benchmark Suite
Create `benchmark/tasks.json` containing 10 diverse, challenging prompts:
- **Task 1 (JSON Extraction):** Structured entity parsing with nested schemas.
- **Task 2 (Multi-Hop Logic):** Relational reasoning across 3 interdependent clues.
- **Task 3 (Python Code Synthesis):** Algorithmic problem with 5 hidden unit tests.
- **Task 4 (Mathematical Proof):** Step-by-step arithmetic and modular algebra.
- **Task 5 (Factual QA & Grounding):** Document needle-in-a-haystack verification.
- **Task 6 (Adversarial Robustness):** Resisting false premise injection and sycophancy.
- **Task 7 (Constraint Satisfaction):** Word length and character exclusion constraints.
- **Task 8 (SQL Query Generation):** Multi-table join and aggregation query.
- **Task 9 (Summarization & Compression):** Zero-shot technical paper abstract distillation.
- **Task 10 (Creative Translation):** Idiomatic cross-lingual translation.

### 2. Implement the Headless Evaluation Runner
In `src/evaluator.py`, build the automated test executor:
- Execute each prompt against Model A and Model B with identical sampling configurations ($T = 0.0$ for code/math, $T = 0.7$ for reasoning).
- Record exact input tokens, output tokens, TTFT (Time-To-First-Token), and total latency.
- Evaluate deterministic tasks with programmatic assertions (pytest AST / JSON schema validators).
- Evaluate subjective tasks using a Dual-Pass Position-Debiased LLM Judge (averaging Pass 1 `[A, B]` and Pass 2 `[B, A]`).

### 3. Compute Metrics and Statistical Significance
In `src/metrics.py`:
- Calculate raw accuracy percentages per category.
- Update Bradley-Terry ELO ratings starting from base $1000.0$.
- Resample outcomes $1,000$ times with replacement to calculate the $95\%$ bootstrap confidence interval.
- Calculate blended cost per 1,000 requests using published token pricing.

### 4. Synthesize the Comparative Findings Report
In `reports/model_comparison_study.md`, document:
- Executive Summary & Recommended Production Route.
- Cost-Quality Pareto Frontier Analysis.
- Latency Percentile Comparison.
- Detailed Failure Mode Case Studies.

## Expected output
When you run the benchmark harness, the output must demonstrate complete evaluation execution:
```
================================================================================
WEEK 35 PROJECT: MODEL COMPARISON STUDY BENCHMARK HARNESS
================================================================================
Evaluating Models: [Model A: Claude-3.5-Sonnet] vs [Model B: Gemini-2.0-Flash]
Benchmark Suite: 10 Standardized Tasks (3 Runs Each = 30 Total Trials)

[1/10] Task: JSON Schema Extraction ................... A: PASS | B: PASS
[2/10] Task: Multi-Hop Relational Logic ............... A: PASS | B: FAIL (Hallucination)
[3/10] Task: Python Algorithm Synthesis ............... A: PASS (100% tests) | B: PASS (100% tests)
[4/10] Task: Grade School Math (GSM) .................. A: PASS | B: PASS
[5/10] Task: Needle-in-a-Haystack Retrieval ........... A: PASS | B: PASS
[6/10] Task: Adversarial Sycophancy Test .............. A: PASS (Resisted) | B: FAIL (Sycophantic)
[7/10] Task: Strict Length Constraints ................ A: PASS | B: PASS
[8/10] Task: Complex SQL Join Synthesis ............... A: PASS | B: PASS
[9/10] Task: Technical Abstract Distillation .......... A: PASS (Judge: 9.2) | B: PASS (Judge: 8.8)
[10/10] Task: Idiomatic Translation ................... A: PASS (Judge: 9.5) | B: PASS (Judge: 9.0)

================================================================================
STATISTICAL BENCHMARK SUMMARY & PARETO ANALYSIS
================================================================================
Model A (Claude-3.5-Sonnet):
  - Accuracy: 100.0% (10/10 Tasks)
  - ELO Rating: 1048.0
  - Avg Latency: 1.42s (p95: 2.10s)
  - Blended Cost / 1k Tasks: $1.85

Model B (Gemini-2.0-Flash):
  - Accuracy: 80.0% (8/10 Tasks)
  - ELO Rating: 952.0
  - Avg Latency: 0.38s (p95: 0.52s) [3.7x Faster]
  - Blended Cost / 1k Tasks: $0.09 [20.5x Cheaper]

Head-to-Head Win Rate: Model A Wins 70.0% [95% CI: 53.3% - 86.7%] (Statistically Significant)

RECOMMENDATION: Deploy Hybrid Cascading Router (Route 80% simple traffic to Gemini 2.0 Flash, fallback complex multi-hop to Claude 3.5 Sonnet for 75% cost reduction).
```

## Validation
1. Verify that all 10 tasks in `benchmark/tasks.json` execute to completion without runtime exceptions.
2. Confirm that dual-pass judge swapping is implemented to prevent positional bias.
3. Validate that ELO ratings satisfy zero-sum conservation ($R_A + R_B = 2000.0$).
4. Verify that $95\%$ bootstrap confidence intervals are computed from $B \ge 1,000$ iterations.
5. Ensure `reports/model_comparison_study.md` contains complete cost, latency, and qualitative failure analysis.
