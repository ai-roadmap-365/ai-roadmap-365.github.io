import re
from typing import List, Dict, Any
from collections import Counter

class GroundedVerifier:
    def __init__(self, context: str):
        self.context = context.lower()

    def verify_claim(self, claim: str) -> bool:
        claim_clean = claim.strip()
        numbers = re.findall(r'\b\d+(?:\.\d+)?\b', claim_clean)
        words = [w.lower() for w in re.findall(r'\b[A-Za-z]{4,}\b', claim_clean)]

        # All numbers must be in context
        for num in numbers:
            if num not in self.context:
                return False

        # Lexical overlap
        if not words:
            return True
        matched = [w for w in words if w in self.context]
        return (len(matched) / len(words)) >= 0.60

def self_consistency_vote(candidates: List[str]) -> str:
    if not candidates:
        return ""
    counts = Counter(candidates)
    most_common = counts.most_common(1)[0][0]
    return most_common

def run_hallucination_demo():
    context = "In fiscal year 2024, Acme Corp reported total revenue of $150 million, representing 25% growth year over year."
    verifier = GroundedVerifier(context)

    claim_true = "Acme Corp reported revenue of $150 million with 25% growth."
    claim_false = "Acme Corp reported profit of $999 billion."

    res_true = verifier.verify_claim(claim_true)
    res_false = verifier.verify_claim(claim_false)

    paths = ["42", "42", "10", "42", "42"]
    consensus = self_consistency_vote(paths)

    print(f"Hallucination Demo: True Claim Grounded = {res_true}, False Claim Grounded = {res_false}, Consensus = {consensus}")
    return res_true, res_false, consensus

if __name__ == "__main__":
    run_hallucination_demo()
