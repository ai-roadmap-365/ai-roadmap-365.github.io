import pytest
from examples.chunking_hierarchy import HierarchicalChunker

def test_chunking_creates_parents_and_children():
    chunker = HierarchicalChunker(child_chunk_size_words=10, parent_chunk_size_words=20)
    text = "word " * 50  # 50 words
    chunker.chunk_and_index_document("doc1", text)
    
    # 50 words / 20 = 3 parents (20, 20, 10)
    assert len(chunker.parent_store) == 3
    assert len(chunker.child_index) == 5

def test_search_small_to_big_returns_full_parent():
    chunker = HierarchicalChunker(child_chunk_size_words=5, parent_chunk_size_words=15)
    doc_text = "The quick brown fox jumps over the lazy dog. Artificial intelligence revolutionizes software development pipelines across cloud platforms."
    chunker.chunk_and_index_document("doc_fox", doc_text)
    
    res = chunker.search_small_to_big("Artificial intelligence pipelines")
    assert len(res) >= 1
    assert "Artificial intelligence revolutionizes" in res[0]["parent_text"]
    assert "matched_child_id" in res[0]

def test_deduplication_of_parent_results():
    chunker = HierarchicalChunker(child_chunk_size_words=5, parent_chunk_size_words=20)
    doc_text = "apple banana cherry date elderberry fig grape honeydew kiwi lemon mango nectarine orange papaya quince raspberry strawberry tangerine uva watermelon"
    chunker.chunk_and_index_document("doc_fruits", doc_text)
    
    # Query matching words in child 0 and child 1 of parent 0
    res = chunker.search_small_to_big("apple banana fig grape")
    assert len(res) == 1  # Only 1 unique parent returned
    assert res[0]["parent_id"] == "doc_fruits_p0"

def test_empty_document_handling():
    chunker = HierarchicalChunker()
    chunker.chunk_and_index_document("empty_doc", "")
    assert len(chunker.parent_store) == 0
    assert len(chunker.child_index) == 0
    res = chunker.search_small_to_big("anything")
    assert res == []

def test_no_overlap_zero_score():
    chunker = HierarchicalChunker(5, 10)
    chunker.chunk_and_index_document("d1", "one two three four five six seven eight")
    res = chunker.search_small_to_big("completely unrelated text")
    assert res == []
