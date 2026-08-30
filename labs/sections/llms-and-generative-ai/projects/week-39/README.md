# Project: Week 39 -- Documentation Q&A Assistant

## Overview
Build an enterprise-grade, end-to-end Documentation Q&A Assistant in Python capable of ingesting complex multi-page technical documentation, executing hybrid sparse-dense retrieval with cross-encoder re-ranking, generating streaming responses with inline sentence-level citations (`[1]`, `[2]`), and continuously evaluating answer quality against the RAG Triad (Faithfulness, Answer Relevance, Context Precision).

## Learning objectives
- Ingest and parse complex documentation corpora (Markdown and PDF documents), preserving section hierarchies, code blocks, and structured tables.
- Build a hybrid retrieval engine combining dense vector cosine similarity with Okapi BM25 sparse keyword search via Reciprocal Rank Fusion (RRF with `k=60`).
- Apply a high-precision Cross-Encoder neural re-ranker to score candidate passages and eliminate distractor noise.
- Construct citation-grounded system prompts that strictly constrain LLM generation to provided facts and enforce bracketed source citations.
- Implement an inline claim attribution validator that parses generated citations and verifies factual alignment against retrieved source passages.
- Build an automated RAG evaluation test harness computing Faithfulness, Answer Relevance, and Context Precision scores across golden evaluation datasets.
- Execute automated regression test suites validating document ingestion, hybrid search, citation attribution, and quality benchmarks.

## Architecture
```
doc_assistant/
  ├── __init__.py
  ├── parser.py              # Multi-format doc parser (Markdown & PDF tables)
  ├── embedder.py            # Dense embedding generator & vector index
  ├── bm25.py                # Okapi BM25 sparse keyword inverted index
  ├── hybrid_retriever.py    # Sparse + Dense search & Reciprocal Rank Fusion
  ├── reranker.py            # Cross-encoder neural re-ranking filter
  ├── generator.py           # Grounded prompt synthesis & streaming LLM inference
  ├── citation_tracker.py    # Inline citation parser & claim grounding validator
  └── evaluator.py           # RAG Triad metrics (Faithfulness, Relevance, Precision)
tests/
  ├── test_parser.py         # Multi-format parsing and chunking assertions
  ├── test_hybrid.py         # BM25 + Dense RRF fusion and rank deduplication
  ├── test_citations.py      # Inline bracket citation parsing and claim attribution
  └── test_evaluator.py      # RAG Triad automated scoring assertions
```

## Core Functional Components

### 1. Multi-Format Document Parser (`parser.py`)
- Ingests Markdown files and multi-column PDFs with embedded tables.
- Preserves document hierarchy and breadcrumb paths (`Guide > Setup > API Keys`).
- Implements structure-aware chunking (350 tokens, 50 token overlap) without breaking code snippets or Markdown tables.

### 2. Dense Vector Indexer (`embedder.py`)
- Computes dense vector representations for all indexed document chunks.
- Performs cosine similarity calculations to surface Top-50 semantic candidate chunks.

### 3. Sparse BM25 Keyword Search (`bm25.py`)
- Builds an inverted index mapping tokens to document frequencies.
- Computes Okapi BM25 scores (`k_1 = 1.5`, `b = 0.75`) for exact term, error code, and identifier matching.

### 4. Hybrid Retrieval & RRF Fusion Engine (`hybrid_retriever.py`)
- Executes sparse BM25 and dense vector search in parallel.
- Fuses rankings via Reciprocal Rank Fusion: `RRF_Score(d) = sum(1 / (60 + rank_m(d)))`.
- Deduplicates candidates and outputs Top-40 candidate passages.

### 5. Cross-Encoder Re-Ranker (`reranker.py`)
- Evaluates pairwise cross-attention relevance for Top-40 candidates.
- Filters out low-confidence distractor chunks (confidence `< 0.35`).
- Selects the final Top-5 high-precision passages for prompt assembly.

### 6. Grounded Generator & Citation Tracker (`generator.py`, `citation_tracker.py`)
- Packages Top-5 context chunks into structured prompts with numbered source tags (`[1]`, `[2]`).
- Streams synthesized responses from the LLM.
- Validates that every factual claim in the response references a valid source ID and matches ground-truth context facts.

### 7. RAG Triad Quality Evaluator (`evaluator.py`)
- Evaluates responses across a golden benchmark set of 50 technical queries.
- Computes:
  - **Faithfulness:** Ratio of claims supported by retrieved context (Target `> 0.95`).
  - **Answer Relevance:** Semantic similarity between user query and synthesized answer (Target `> 0.90`).
  - **Context Precision:** Ratio of relevant chunks in retrieved Top-5 context (Target `> 0.85`).

## Expected output
When executing the Documentation Q&A Assistant regression suite:
```
======================================================================
WEEK 39 PROJECT: DOCUMENTATION Q&A ASSISTANT VERIFICATION SUITE
======================================================================
[1/4] Testing Multi-Format Document Parser:
      - Markdown & Table Extraction: PASSED (Tables preserved in Markdown)
      - Sliding Window Chunker (350/50): PASSED (Zero syntax truncation)
      - Header Breadcrumb Preservation: PASSED (Preserved 3-level hierarchy)

[2/4] Testing Hybrid Retrieval & Cross-Encoder Re-Ranker:
      - Sparse BM25 Search: PASSED (Matched exact API parameter 'cache_control')
      - Dense Vector Search: PASSED (Matched semantic query 'save token costs')
      - Reciprocal Rank Fusion (k=60): PASSED (Unified Top-40 candidates)
      - Cross-Encoder Re-Ranking: PASSED (Selected Top-5 precision passages)

[3/4] Testing Grounded Generation & Citation Attribution:
      - Structured Prompt Packaging: PASSED (Numbered tags [1]-[5] formatted)
      - Inline Citation Extraction: PASSED (Parsed 8 bracketed source citations)
      - Claim-Level Grounding Check: PASSED (100% claims verified against context)

[4/4] Testing RAG Triad Automated Evaluation Harness:
      - Evaluated 50 Golden Benchmark Queries: PASSED (Total latency: 1.12s)
      - Faithfulness Score: 0.98 [PASS] (Target > 0.95)
      - Answer Relevance Score: 0.94 [PASS] (Target > 0.90)
      - Context Precision Score: 0.89 [PASS] (Target > 0.85)

======================================================================
ALL 4 PROJECT SUBSYSTEMS VERIFIED -- 16 TESTS PASSED (100% GREEN)
======================================================================
```

## Validation
Execute the project verification test suite:
```bash
pytest tests/ -v
```
All tests must pass with 0 errors, validating document chunking, hybrid retrieval, cross-encoder re-ranking, citation attribution, and RAG Triad evaluation metrics.
