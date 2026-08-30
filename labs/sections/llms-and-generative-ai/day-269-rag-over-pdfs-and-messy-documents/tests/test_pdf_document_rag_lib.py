from pdf_document_rag_lib import DocumentChunker, SparseBM25, HybridRanker, PromptSynthesizer

def test_document_chunker():
    chunker = DocumentChunker(chunk_size=10, overlap=2)
    text = "one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen"
    chunks = chunker.chunk_document("doc_01", "Numbers", text)
    assert len(chunks) >= 2
    assert chunks[0]["chunk_id"] == "doc_01#chunk_0"
    assert chunks[0]["title"] == "Numbers"
    assert len(chunks[0]["text"].split()) == 10

def test_sparse_bm25():
    bm25 = SparseBM25()
    chunks = [
        {"chunk_id": "c1", "title": "Caching", "text": "Anthropic prompt caching reduces latency and token costs."},
        {"chunk_id": "c2", "title": "Tools", "text": "Tool calling allows LLMs to execute structured JSON schemas."},
        {"chunk_id": "c3", "title": "Vision", "text": "Multimodal vision models inspect images and diagrams."}
    ]
    bm25.index(chunks)
    results = bm25.search("prompt caching latency", top_k=2)
    assert len(results) == 2
    assert results[0][0] == 0
    assert results[0][1] > 0.0

def test_hybrid_ranker():
    ranker = HybridRanker(rrf_k=60)
    list_a = [0, 1, 2]
    list_b = [1, 0, 3]
    fused = ranker.fuse_ranks(list_a, list_b)
    top_docs = [idx for idx, score in fused[:2]]
    assert 0 in top_docs
    assert 1 in top_docs

def test_prompt_synthesizer():
    chunks = [
        {"chunk_id": "c1", "title": "Prompt Cache Guide", "text": "Cache write costs $3.75 per million tokens."}
    ]
    prompt = PromptSynthesizer.format_context("What is the cost?", chunks)
    assert "[1] Title: Prompt Cache Guide" in prompt
    assert "Cache write costs $3.75 per million tokens." in prompt
    assert "Question: What is the cost?" in prompt

if __name__ == "__main__":
    test_document_chunker()
    test_sparse_bm25()
    test_hybrid_ranker()
    test_prompt_synthesizer()
    print("All 4 unit tests passed successfully.")
