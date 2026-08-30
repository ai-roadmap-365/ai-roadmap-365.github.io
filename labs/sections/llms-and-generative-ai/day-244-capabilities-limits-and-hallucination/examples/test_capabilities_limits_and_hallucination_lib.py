import pytest
from examples.capabilities_limits_and_hallucination_lib import (
    GroundedVerifier,
    self_consistency_vote
)

def test_grounded_verification():
    context = "Tesla produced 1.85 million vehicles in 2023, delivering 1.81 million to customers."
    verifier = GroundedVerifier(context)

    # Valid claim
    assert verifier.verify_claim("Tesla produced 1.85 million vehicles in 2023.") is True

    # Missing number hallucination
    assert verifier.verify_claim("Tesla produced 5.00 million vehicles in 2023.") is False

def test_self_consistency_majority_vote():
    votes = ["Option A", "Option B", "Option A", "Option A", "Option C"]
    assert self_consistency_vote(votes) == "Option A"

def test_empty_candidates():
    assert self_consistency_vote([]) == ""
