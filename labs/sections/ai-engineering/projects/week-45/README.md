# Week 45 Capstone Project: Evaluation Harness

## Project Overview
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
<!-- generated-links:end -->

Build a comprehensive, production-grade **AI Evaluation Harness Suite** that unites all Week 45 concepts:
1. **Stratified Dataset Management:** Load, validate, de-duplicate, and categorize JSONL benchmark records across `happy_path`, `hard_negative`, `schema_boundary`, and `adversarial` categories.
2. **Multi-Tier Metric Scoring Engine:** Calculate Exact Match, JSON Schema Field F1, Token Overlap F1, and Rubric-Anchored LLM Judge scores.
3. **Guardrail Screening:** Apply PII redaction and prompt injection checks before evaluation execution.
4. **Distributed Tracing & Token Accounting:** Track hierarchical span trees, duration timing, and token economics.
5. **CI/CD Regression Gate Decision:** Compare candidate composite performance against pinned golden baselines, verify zero golden invariant failures, enforce tolerance thresholds, and generate formatted Markdown regression reports.

## Project Requirements
1. **Dataset Ingestion & Validation:** Load JSONL datasets, ensure mandatory schema fields, and reject invalid categories.
2. **Deterministic & Semantic Scoring:** Implement Exact Match, Token Overlap F1, and JSON Field F1 calculations.
3. **Composite Metric Aggregation:** Compute weighted overall scores across stratified benchmark slices.
4. **Automated Regression Threshold Gate:** Enforce tolerance limits and abort deployments on critical golden invariant failures.

## File Structure
- `starter/evaluation_harness_suite.py`: Starter implementation skeleton
- `examples/evaluation_harness_suite.py`: Complete verified reference solution
- `tests/test_evaluation_harness_suite.py`: Comprehensive test suite
- `expected-output/`: Verified execution logs

## How to Run
```bash
python3 examples/evaluation_harness_suite.py
```

## Validation
```bash
bash tests/run_tests.sh
```

## Expected output
```text
Suite Decision: {'total_evaluated': 1, 'baseline_score': 0.8, 'candidate_score': 1.0, 'delta': 0.2, 'tolerance_passed': True, 'golden_passed': True, 'failed_golden_count': 0, 'gate_passed': True, 'status': 'APPROVED'}
```

## Security Notes
Executes entirely in isolated local Python environment with zero production network access.
