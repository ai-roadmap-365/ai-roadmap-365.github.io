import pytest
import torch
from examples.a_sentiment_analysis_project_lib import BiLSTMAttentionSentiment

def test_bilstm_attention_sentiment_forward():
    torch.manual_seed(42)
    model = BiLSTMAttentionSentiment(vocab_size=100, embed_dim=16, hidden_dim=8, num_classes=2)
    x = torch.randint(0, 100, (4, 10))
    logits, weights = model(x)
    
    assert logits.shape == (4, 2)
    assert weights.shape == (4, 10)
    for s in weights.sum(dim=1):
        assert pytest.approx(s.item(), 1e-5) == 1.0

def test_token_attribution_explainability():
    torch.manual_seed(42)
    model = BiLSTMAttentionSentiment(vocab_size=100, embed_dim=16, hidden_dim=8, num_classes=2)
    x = torch.randint(0, 100, (1, 6))
    saliency, weights = model.explain_tokens(x, target_class=1)
    
    assert saliency.shape == (6,)
    assert weights.shape == (6,)
