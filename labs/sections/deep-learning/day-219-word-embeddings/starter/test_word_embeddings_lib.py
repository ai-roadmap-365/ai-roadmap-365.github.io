import pytest
import torch
from examples.word_embeddings_lib import SkipGramNegativeSampling, compute_cosine_similarity

def test_skipgram_loss_computation():
    torch.manual_seed(42)
    model = SkipGramNegativeSampling(vocab_size=50, embed_dim=8)
    center = torch.tensor([1, 2])
    context = torch.tensor([3, 4])
    negatives = torch.tensor([[10, 11], [12, 13]])
    
    loss = model(center, context, negatives)
    assert isinstance(loss, torch.Tensor)
    assert loss.ndim == 0
    assert loss.item() > 0.0

def test_cosine_similarity_bounds():
    v1 = torch.tensor([1.0, 0.0, 0.0])
    v2 = torch.tensor([1.0, 0.0, 0.0])
    v3 = torch.tensor([-1.0, 0.0, 0.0])
    v4 = torch.tensor([0.0, 1.0, 0.0])

    assert pytest.approx(compute_cosine_similarity(v1, v2), 1e-4) == 1.0
    assert pytest.approx(compute_cosine_similarity(v1, v3), 1e-4) == -1.0
    assert pytest.approx(compute_cosine_similarity(v1, v4), 1e-4) == 0.0
