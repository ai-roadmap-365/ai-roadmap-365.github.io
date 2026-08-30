## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
<!-- generated-links:end -->

# Week 47 Project: Production RAG Assistant Engine

## Purpose
Build a complete, end-to-end **Production RAG Assistant Engine** in Python integrating:
1. **Asynchronous Idempotent Ingestion** with SHA-256 content hashing and cascade deletion.
2. **Hierarchical Document Chunking** with small-to-big parent document expansion.
3. **Hybrid Search & Reranking** combining BM25 keyword matching and dense vector cosine scoring.
4. **Strict Refusal Guardrails** rejecting ungrounded out-of-domain queries.
5. **Verifiable Grounded Citations** and OpenTelemetry execution telemetry.

## System Architecture

```text
[User Prompt]
      │
      ▼
[Query Transformation & Routing]
      │
      ▼
[Hybrid Retrieval: BM25 + Vector Search]
      │
      ▼
[Cross-Encoder Reranking & Small-to-Big Parent Expansion]
      │
      ▼
[Confidence Gate: Score >= 0.60?]
      ├── YES -> Generate Answer with Grounded Citations [Doc-ID: §Section]
      └── NO  -> Graceful Refusal (Zero Hallucination)
```

## Requirements
- Python 3.10+
- pytest

## Installation
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements/requirements.txt
```

## Running the Project
```bash
python3 examples/production_rag_app.py
```

## Running Tests
```bash
bash tests/run_tests.sh
```

## Testing Specifications
- Ingestion of multiple parent documents with SHA-256 deduplication
- Hybrid search ranking combining keyword and vector scoring
- Small-to-big parent retrieval resolving complete context
- Refusal guardrail execution on low-confidence queries
- Citation accuracy and telemetry metrics logging
