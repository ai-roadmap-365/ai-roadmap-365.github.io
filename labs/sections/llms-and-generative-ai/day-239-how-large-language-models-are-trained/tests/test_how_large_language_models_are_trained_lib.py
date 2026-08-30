import pytest
from examples.how_large_language_models_are_trained_lib import DocumentRefinery

def test_gopher_heuristics():
    refinery = DocumentRefinery()
    doc_valid = "Artificial intelligence and language models are transforming modern computer science with deep learning."
    doc_short = "Hi there"
    doc_symbols = "#$$%^^&&! @@@!!! 1234"

    assert refinery.passes_gopher_heuristics(doc_valid) is True
    assert refinery.passes_gopher_heuristics(doc_short) is False
    assert refinery.passes_gopher_heuristics(doc_symbols) is False

def test_minhash_duplicate_detection():
    refinery = DocumentRefinery(num_perm=64)
    text1 = "Transformers use self attention to process sequence data efficiently across GPU clusters."
    text2 = "Transformers use self attention to process sequence data efficiently across GPU clusters and nodes."
    text3 = "Quantum computing uses qubits and superposition to solve complex cryptographic algorithms."

    sig1 = refinery.compute_minhash_signature(text1)
    sig2 = refinery.compute_minhash_signature(text2)
    sig3 = refinery.compute_minhash_signature(text3)

    jaccard_near = refinery.estimate_jaccard(sig1, sig2)
    jaccard_diff = refinery.estimate_jaccard(sig1, sig3)

    assert jaccard_near > 0.60
    assert jaccard_diff < 0.20
