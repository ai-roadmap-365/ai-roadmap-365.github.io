import re
import hashlib
import numpy as np
from typing import List, Set, Dict

class DocumentRefinery:
    def __init__(self, num_perm: int = 32):
        self.num_perm = num_perm
        self.stopwords = {"the", "and", "is", "of", "in", "to", "a", "with", "for", "on"}

    def passes_gopher_heuristics(self, text: str) -> bool:
        words = re.findall(r'\b\w+\b', text.lower())
        if len(words) < 8:
            return False

        mean_len = sum(len(w) for w in words) / len(words)
        if mean_len < 3.0 or mean_len > 10.0:
            return False

        stopword_count = sum(1 for w in words if w in self.stopwords)
        if stopword_count < 2:
            return False

        symbols = sum(1 for c in text if not c.isalnum() and not c.isspace())
        if (symbols / max(len(text), 1)) > 0.20:
            return False

        return True

    def compute_minhash_signature(self, text: str, k: int = 3) -> List[int]:
        words = text.lower().split()
        if len(words) < k:
            shingles = set(words)
        else:
            shingles = {" ".join(words[i:i+k]) for i in range(len(words) - k + 1)}

        sig = []
        for i in range(self.num_perm):
            min_val = float('inf')
            for s in shingles:
                h = int(hashlib.md5(f"{i}_{s}".encode()).hexdigest(), 16)
                if h < min_val:
                    min_val = h
            sig.append(int(min_val % 1000000))
        return sig

    def estimate_jaccard(self, sig_a: List[int], sig_b: List[int]) -> float:
        matches = sum(1 for a, b in zip(sig_a, sig_b) if a == b)
        return float(matches / len(sig_a))

def run_pipeline_demo():
    refinery = DocumentRefinery(num_perm=64)
    doc_clean = "The deep learning model is trained on massive datasets to predict the next word in the sequence."
    doc_spam = "BUY NOW $$$ CLICK HERE 12345 !@#$ !!!"

    passed_clean = refinery.passes_gopher_heuristics(doc_clean)
    passed_spam = refinery.passes_gopher_heuristics(doc_spam)

    sig_a = refinery.compute_minhash_signature(doc_clean)
    sig_b = refinery.compute_minhash_signature(doc_clean + " Extra minor addition.")
    jaccard = refinery.estimate_jaccard(sig_a, sig_b)

    print(f"Data Pipeline Demo: Clean Passed = {passed_clean}, Spam Passed = {passed_spam}, Estimated Jaccard = {jaccard:.3f}")
    return passed_clean, passed_spam, jaccard

if __name__ == "__main__":
    run_pipeline_demo()
