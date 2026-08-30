import re
from typing import List, Dict, Any

class DocumentChunker:
    def __init__(self, chunk_size: int = 200, overlap: int = 40):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def sliding_window_chunk(self, text: str) -> List[Dict[str, Any]]:
        words = text.split()
        if not words:
            return []
        
        chunks = []
        stride = max(1, self.chunk_size - self.overlap)
        
        for i in range(0, len(words), stride):
            chunk_words = words[i:i + self.chunk_size]
            chunks.append({
                "chunk_id": len(chunks),
                "text": " ".join(chunk_words),
                "word_count": len(chunk_words),
                "start_idx": i,
                "end_idx": i + len(chunk_words)
            })
            if i + self.chunk_size >= len(words):
                break
        return chunks

    def markdown_header_chunk(self, markdown_text: str) -> List[Dict[str, Any]]:
        lines = markdown_text.split("\n")
        chunks = []
        current_header = "Introduction"
        current_lines = []

        for line in lines:
            if line.startswith("#"):
                if current_lines:
                    text_content = "\n".join(current_lines).strip()
                    if text_content:
                        chunks.append({
                            "chunk_id": len(chunks),
                            "header": current_header,
                            "text": text_content
                        })
                    current_lines = []
                current_header = line.strip("# ").strip()
            else:
                current_lines.append(line)

        if current_lines:
            text_content = "\n".join(current_lines).strip()
            if text_content:
                chunks.append({
                    "chunk_id": len(chunks),
                    "header": current_header,
                    "text": text_content
                })
        return chunks

    def create_parent_child_hierarchy(self, text: str, parent_size: int = 400, child_size: int = 100) -> List[Dict[str, Any]]:
        words = text.split()
        if not words:
            return []

        parents = []
        for p_idx in range(0, len(words), parent_size):
            p_words = words[p_idx:p_idx + parent_size]
            parent_id = f"parent_{len(parents)}"
            parent_text = " ".join(p_words)
            
            # Subdivide parent into children
            children = []
            for c_idx in range(0, len(p_words), child_size):
                c_words = p_words[c_idx:c_idx + child_size]
                children.append({
                    "child_id": f"{parent_id}_child_{len(children)}",
                    "parent_id": parent_id,
                    "text": " ".join(c_words)
                })
            
            parents.append({
                "parent_id": parent_id,
                "parent_text": parent_text,
                "children": children
            })
            if p_idx + parent_size >= len(words):
                break
        return parents

def run_chunker_demo():
    chunker = DocumentChunker(chunk_size=10, overlap=3)
    sample_text = "The quick brown fox jumps over the lazy dog and runs across the wide green open meadow."
    chunks = chunker.sliding_window_chunk(sample_text)
    print(f"Chunker Demo Executed. Generated {len(chunks)} overlapping chunks.")
    return chunks

if __name__ == "__main__":
    run_chunker_demo()
