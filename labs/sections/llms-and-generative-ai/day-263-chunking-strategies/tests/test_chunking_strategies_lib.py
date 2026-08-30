import pytest
from examples.chunking_strategies_lib import (
    DocumentChunker
)

def test_sliding_window_chunking():
    chunker = DocumentChunker(chunk_size=5, overlap=2)
    text = "one two three four five six seven eight nine ten"
    chunks = chunker.sliding_window_chunk(text)

    assert len(chunks) == 3
    assert chunks[0]["text"] == "one two three four five"
    assert chunks[1]["text"] == "four five six seven eight"
    assert chunks[2]["text"] == "seven eight nine ten"

def test_markdown_header_chunking():
    chunker = DocumentChunker()
    md = """# Title
This is intro text.
## Section 1
Content of section 1.
## Section 2
Content of section 2."""
    
    chunks = chunker.markdown_header_chunk(md)
    assert len(chunks) == 3
    assert chunks[0]["header"] == "Title"
    assert chunks[0]["text"] == "This is intro text."
    assert chunks[1]["header"] == "Section 1"
    assert chunks[2]["header"] == "Section 2"

def test_parent_child_hierarchy():
    chunker = DocumentChunker()
    text = "word " * 300
    hierarchy = chunker.create_parent_child_hierarchy(text, parent_size=100, child_size=25)
    
    assert len(hierarchy) == 3
    assert len(hierarchy[0]["children"]) == 4
    assert hierarchy[0]["children"][0]["parent_id"] == "parent_0"

def test_empty_string_handling():
    chunker = DocumentChunker()
    assert chunker.sliding_window_chunk("") == []
    assert chunker.markdown_header_chunk("") == []
    assert chunker.create_parent_child_hierarchy("") == []
