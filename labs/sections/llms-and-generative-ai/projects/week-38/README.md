# Project: Week 38 -- Semantic Search Engine

## Overview
Build an enterprise-grade, modular Semantic Search Engine over your own personal notes and technical documentation in Python. The search engine integrates the complete retrieval stack developed across Days 260–266: Markdown document parsing and structure-aware chunking, dense embedding generation, vector indexing with cosine similarity, sparse lexical keyword search (BM25), Reciprocal Rank Fusion (RRF), cross-encoder re-ranking, and automated RAG Triad retrieval-quality evaluation (MRR@10, NDCG@10, and Context Relevance).

## Learning objectives
- Ingest and parse complex multi-file Markdown corpora, splitting text into semantically coherent, structure-aware chunks with sliding overlaps.
- Generate high-dimensional dense embeddings and build an in-memory cosine similarity vector index.
- Implement a sparse Okapi BM25 index with term frequency saturation and document length normalization.
- Fuse heterogeneous candidate rankings using Reciprocal Rank Fusion (RRF) with configurable smoothing constants (`k=60`).
- Apply a Cross-Encoder re-ranker stage to score query-document token interactions and select high-precision Top-K passages.
- Benchmark retrieval quality across a golden evaluation dataset of test queries, computing Mean Reciprocal Rank (MRR@10), NDCG@10, and Context Relevance.
- Execute automated regression test suites validating chunking boundaries, BM25 scores, RRF fusion arithmetic, and evaluation metrics.

## Architecture
```
semantic_search/
  ├── __init__.py
  ├── parser.py              # Markdown header parsing & structure-aware chunking
  ├── embedder.py            # Dense embedding generator & cosine similarity engine
  ├── bm25.py                # Okapi BM25 sparse inverted index & term scorer
  ├── hybrid_engine.py       # Dual-retrieval executor & Reciprocal Rank Fusion (RRF)
  ├── reranker.py            # Cross-encoder neural re-ranking filter
  └── evaluator.py           # Retrieval quality metrics (MRR@10, NDCG@10, Context Relevance)
tests/
  ├── test_parser.py         # Chunking boundary and metadata preservation assertions
  ├── test_bm25.py           # BM25 term saturation and IDF calculation assertions
  ├── test_hybrid_engine.py  # RRF rank aggregation and deduplication assertions
  └── test_evaluator.py      # MRR, NDCG, and RAG Triad relevance score assertions
```

## Core Functional Components

### 1. Markdown Parser & Structure Chunker (`parser.py`)
- Traverses documentation directories and extracts Markdown sections while preserving header hierarchy breadcrumbs (e.g. `Architecture > Storage > Indexing`).
- Enforces structure-aware chunking (target size: 512 tokens, 64 token overlap) without severing code blocks or table rows.
- Attaches document metadata (file path, header path, line ranges) to each chunk payload.

### 2. Dense Vector Indexer (`embedder.py`)
- Computes dense latent vectors for all ingested chunks.
- Builds an in-memory vector index supporting exact and approximate nearest neighbor (ANN) cosine similarity search.
- Returns Top-50 semantic candidate passages per query.

### 3. Sparse BM25 Indexer (`bm25.py`)
- Builds an inverted index mapping lowercased, tokenized vocabulary terms to document frequencies.
- Computes Okapi BM25 scores with tunable parameters (`k_1 = 1.5`, `b = 0.75`).
- Returns Top-50 exact keyword candidate passages per query.

### 4. Hybrid Search & RRF Fusion Engine (`hybrid_engine.py`)
- Simultaneously queries the BM25 sparse index and the Dense vector index via parallel async tasks.
- Merges disparate ranking lists using Reciprocal Rank Fusion: `RRF_Score(d) = sum(1 / (60 + rank_m(d)))`.
- Deduplicates candidates and outputs a consolidated Top-40 candidate pool.

### 5. Cross-Encoder Re-Ranker (`reranker.py`)
- Evaluates pairwise query-document relevance for all Top-40 candidates.
- Prunes passages falling below confidence thresholds (`score < 0.30`).
- Returns the final Top-5 high-precision passages for prompt synthesis or user display.

### 6. Retrieval Quality Evaluator (`evaluator.py`)
- Evaluates retrieval performance across a golden evaluation dataset of 50 test queries.
- Computes standard Information Retrieval metrics:
  - **MRR@10 (Mean Reciprocal Rank):** Average reciprocal rank of the first ground-truth passage.
  - **NDCG@10:** Graded relevance ranking quality.
  - **Context Relevance:** Ratio of signal sentences to total retrieved sentences.

## Expected output
When executing the semantic search engine demonstration and automated test suite:
```
======================================================================
WEEK 38 PROJECT: SEMANTIC SEARCH ENGINE VERIFICATION SUITE
======================================================================
[1/4] Testing Markdown Parser & Structure Chunker:
      - Header Breadcrumb Preservation: PASSED (Hierarchy: Auth > Tokens > Expiry)
      - Sliding Window Overlap (512/64): PASSED (Zero chunk boundary truncation)
      - Metadata Payload Attachment: PASSED (File paths and line numbers preserved)

[2/4] Testing Hybrid Retrieval & RRF Fusion:
      - Sparse BM25 Search: PASSED (Matched exact error code 'ERR_504')
      - Dense Vector Cosine Search: PASSED (Matched semantic concept 'sluggish latency')
      - Reciprocal Rank Fusion (k=60): PASSED (Unified Top-40 candidate pool generated)

[3/4] Testing Cross-Encoder Neural Re-Ranker:
      - Pairwise Cross-Attention Scoring: PASSED (Top-5 precision passages selected)
      - Low-Confidence Pruning (Score < 0.30): PASSED (Distractor passages filtered)

[4/4] Testing Retrieval Quality Benchmark Suite:
      - Evaluated 50 Golden Benchmark Queries: PASSED (Execution time: 0.85s)
      - MRR@10 Score: 0.94 [PASS] (Target > 0.85)
      - NDCG@10 Score: 0.91 [PASS] (Target > 0.80)
      - Context Relevance: 0.88 [PASS] (Target > 0.75)

======================================================================
ALL 4 PROJECT SUBSYSTEMS VERIFIED -- 14 TESTS PASSED (100% GREEN)
======================================================================
```

## Validation
Execute the project regression suite to verify complete compliance:
```bash
pytest tests/ -v
```
All tests must pass with 0 errors, validating document chunking, sparse-dense hybrid retrieval, RRF fusion, and retrieval quality metrics.
