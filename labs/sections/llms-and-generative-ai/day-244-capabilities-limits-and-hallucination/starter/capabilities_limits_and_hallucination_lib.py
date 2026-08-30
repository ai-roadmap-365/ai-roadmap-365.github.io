import re
from typing import List, Dict, Any
from collections import Counter

class GroundedVerifier:
    def __init__(self, context: str):
        self.context = context.lower()

    def verify_claim(self, claim: str) -> bool:
        # TODO: Return True if all numbers in claim are in context and word overlap >= 0.6
        pass

def self_consistency_vote(candidates: List[str]) -> str:
    # TODO: Return the majority vote candidate
    pass
