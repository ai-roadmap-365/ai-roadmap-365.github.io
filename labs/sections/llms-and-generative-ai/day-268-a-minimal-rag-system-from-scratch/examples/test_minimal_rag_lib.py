import pytest
from minimal_rag_lib import DocumentChunker, SparseBM25, HybridRanker, PromptSynthesizer

def test_document_chunker():
    chunker = DocumentChunker(chunk_size=10, overlap=2)
    sample_text = " ".join([f"word{i}" for i in range(25)])
    chunks = chunker.chunk_document("doc1", "Test Doc", sample_text)
    assert len(chunks) >= 3
    assert chunks[0]["doc_id"] == "doc1"
    assert chunks[0]["title"] == "Test Doc"
    assert len(chunks[0]["text"].split()) == 10

def test_sparse_bm25():
    bm25 = SparseBM25()
    chunks = [
        {"chunk_id": "c1", "title": "Doc 1", "text": "Claude 3.5 Sonnet supports prompt caching and tool use."},
        {"chunk_id": "c2", "title": "Doc 2", "text": "PostgreSQL database configuration for pgvector storage."},
        {"chunk_id": "c3", "title": "Doc 3", "text": "Prompt caching reduces API cost by ninety percent."}
    ]
    bm25.index(chunks)
    results = bm25.search("prompt caching", top_k=2)
    assert len(results) == 2
    top_doc_idx = results[0][0]
    assert top_doc_idx in (0, 2)
    assert results[0][1] > 0.0

def test_hybrid_ranker():
    ranker = HybridRanker(rrf_k=60)
    sparse_ranks = [0, 1, 2]
    dense_ranks = [2, 0, 3]
    fused = ranker.fuse_ranks(sparse_ranks, dense_ranks)
    assert len(fused) == 4
    # Item 0 appears at rank 1 in list_a and rank 2 in list_b
    assert fused[0][0] == 0

def test_prompt_synthesizer():
    chunks = [
        {"chunk_id": "c1", "title": "Pricing", "text": "Prompt cache read tokens cost $0.30 per million."}
    ]
    prompt = PromptSynthesizer.format_context("What is prompt cache read cost?", chunks)
    assert "[1] Title: Pricing" in prompt
    assert "$0.30 per million" in prompt
    assert "Question: What is prompt cache read cost?" in prompt
