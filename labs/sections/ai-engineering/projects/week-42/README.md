# Week 42 Project: Research Agent

## Overview
Build an end-to-end autonomous **Deep Research Agent** that investigates a complex research question, performs iterative multi-hop web searches, manages an atomic fact note store, and generates a fully cited, grounded research brief in Markdown.

## Requirements
1. **Query Decomposition:** Algorithmically decompose broad user research goals into at least 2 orthogonal sub-queries.
2. **Atomic Fact Extraction:** Parse simulated or live web search results and extract verifiable claims paired with source URLs.
3. **Structured Note Store:** Maintain an in-memory note database with deduplication, claim IDs, and source URLs.
4. **Citation Synthesizer:** Generate a structured Markdown brief with numbered inline citations `[1]`, `[2]` and an accompanying bibliography table.
5. **Evaluation Suite:** Include automated unit tests verifying 100% citation grounding, deduplication, and zero hallucinated URLs.

## Deliverables
- `examples/research_agent_project.py`: Complete verified research agent orchestrator.
- `tests/test_research_agent_project.py`: Pytest automated verification suite.
- `metadata.yml`: Environment and execution declarations.
- `README.md`: Technical documentation and running instructions.

## Expected output
```text
[RESEARCH AGENT] Goal: "State of Solid-State Battery Commercialization"
[DECOMPOSITION] Generated 2 sub-queries: ['solid state energy density', 'solid state manufacturing cost']
[EXTRACTION] Extracted 3 atomic notes into NoteStore.
[SYNTHESIS] Emitted complete Markdown report with 3 inline citations and bibliography table.
[VERIFICATION] All test assertions passed with 100% citation grounding.
```

## Validation
```bash
bash tests/run_tests.sh
```
