# Week 44 Capstone Project: Agent-Built Feature Pipeline

## Project Overview
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
<!-- generated-links:end -->

Ship an end-to-end, reviewed, tested, and documented software feature using an autonomous AI coding agent pipeline. This project implements a comprehensive **Agent Feature Pipeline Engine in Python** that orchestrates specification compiling, AST repo-mapping, TDD test authoring, atomic multi-file patch application, self-healing test execution, security code auditing, and walkthrough generation.

## Project Requirements
1. **Specification Compiler:** Parse and bundle context files, hard constraints, and non-goals.
2. **AST Repo-Map:** Extract class and function signatures across workspace files.
3. **Atomic Patch Application:** Apply targeted search-and-replace edits across multiple files.
4. **Self-Healing Test Gate:** Execute test runner and parse tracebacks for self-correction.
5. **Code Review & Security Audit:** Audit imports against slopsquatting whitelist and detect insecure shell executions.
6. **Walkthrough Generator:** Compile a comprehensive Walkthrough artifact for human peer review.

## File Structure
- `starter/agent_feature_pipeline.py`: Starter implementation skeleton
- `examples/agent_feature_pipeline.py`: Verified reference implementation
- `tests/test_agent_feature_pipeline.py`: Test suite
- `expected-output/`: Captured execution logs

## How to Run
```bash
python3 examples/agent_feature_pipeline.py
```

## Validation Steps
```bash
bash tests/run_tests.sh
```

## Expected Output
```text
All 5 checks passed 100% with zero errors.
```
