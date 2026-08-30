# Project: Week 36 -- Reusable Prompt Library

## Overview
Build an enterprise-grade, version-controlled, tested library of parameterized prompts covering 5 critical recurring software engineering and data tasks. Each prompt template implements modern prompt design patterns (Persona-Context-Task, XML delimiter sandboxing, few-shot CoT exemplars, structured JSON schemas, and parameter breakout sanitization), backed by automated regression test suites and assertion evaluators.

## Learning objectives
- Implement 5 parameterized prompt templates using Jinja2 modular design principles.
- Apply Chain-of-Thought (CoT) reasoning scratchpads and few-shot demonstration exemplars.
- Enforce strict JSON output schemas with Pydantic contracts and regex auto-repair fallback pipelines.
- Defend all template parameter slots against direct and indirect prompt injection attacks.
- Execute automated regression test suites measuring pass rate, latency, and schema adherence.

## Architecture
```
prompts/
  ├── base/
  │   └── _guardrails.j2         # Centralized safety shell and preamble bans
  ├── templates/
  │   ├── code_review.j2         # 1. Code Security & Architecture Review
  │   ├── sql_generator.j2       # 2. Text-to-SQL Schema Synthesizer
  │   ├── incident_extractor.j2  # 3. Structured JSON Incident Report Extractor
  │   ├── technical_cot.j2       # 4. Multi-Step Troubleshooting with CoT Scratchpad
  │   └── audience_summary.j2    # 5. Dual Executive/Engineer Summary Synthesizer
tests/
  ├── test_prompt_library.py     # Automated regression assertion suite
  └── golden_dataset.json        # 50+ benchmark cases across all 5 tasks
```

## The 5 Recurring Production Prompt Tasks

### Task 1: Code Security & Vulnerability Review (`code_review.j2`)
- **Pattern:** Persona-Context-Task (PCT) + Delimiter Sandboxing.
- **Parameters:** `language`, `code_snippet`, `severity_threshold`.
- **Output:** Structured JSON listing security vulnerabilities (CWE ID, line number, mitigation patch).

### Task 2: Text-to-SQL Synthesizer (`sql_generator.j2`)
- **Pattern:** Few-Shot In-Context Learning + Directional Stimulus.
- **Parameters:** `dialect`, `database_schema`, `user_question`.
- **Output:** Valid SQL query wrapped in `<sql_query>` tags with zero conversational markdown fluff.

### Task 3: Incident Report Extractor (`incident_extractor.j2`)
- **Pattern:** Constrained JSON Output + Pydantic Schema.
- **Parameters:** `raw_slack_log`, `service_name`.
- **Output:** Strict JSON payload with `incident_id`, `severity` (LOW/MED/HIGH/CRITICAL), `root_cause`, and `action_items`.

### Task 4: Multi-Step Diagnostic Troubleshooting (`technical_cot.j2`)
- **Pattern:** Least-to-Most Decomposition + Chain of Thought (CoT).
- **Parameters:** `error_stack_trace`, `system_environment`.
- **Output:** Step-by-step reasoning inside `<scratchpad>` followed by root-cause diagnosis in `<diagnosis>`.

### Task 5: Dual Audience Summary Synthesizer (`audience_summary.j2`)
- **Pattern:** Audience Persona Pattern.
- **Parameters:** `technical_postmortem`, `business_impact`.
- **Output:** Two distinct sections: `<executive_brief>` (financial impact, no jargon) and `<engineering_deep_dive>` (PR patches, stack traces).

## Expected output
When running the full test suite across all 5 prompt templates against the golden benchmark dataset:
```
======================================================================
WEEK 36 PROJECT: REUSABLE PROMPT LIBRARY REGRESSION SUITE
======================================================================
[1/5] Testing 'code_review' Template:
  - Happy Path (Python SQL Injection): Passed (CWE-89 detected)
  - Delimiter Breakout Attack: Passed (Tag properly escaped)
  - Schema Adherence: 100% JSON valid

[2/5] Testing 'sql_generator' Template:
  - Postgres Dialect JOIN Query: Passed
  - Preamble Suppression Check: Passed (Zero conversational filler)

[3/5] Testing 'incident_extractor' Template:
  - Corrupted Unescaped Quotes: Auto-repaired & Parsed
  - Required Field Assertion: 100% compliant

[4/5] Testing 'technical_cot' Template:
  - Scratchpad Reasoning Step Count: 4 distinct deduction steps
  - Self-Consistency Verification (k=5): 100% consensus

[5/5] Testing 'audience_summary' Template:
  - Executive Brief Tag Validation: Passed
  - Engineering Deep Dive Tag Validation: Passed

----------------------------------------------------------------------
FINAL REGRESSION SUMMARY:
  Total Benchmark Cases: 25
  Passed: 25 | Failed: 0 | Pass Rate: 100.0%
  Average Latency: 0.14ms per assertion
  Status: PRODUCTION READY (All CI/CD Quality Gates Green)
======================================================================
```

## Validation
Execute the automated test suite to verify all 5 templates:
```bash
pytest tests/ -v
```

All 25 regression cases must pass with 100% schema validity and zero security leaks.
