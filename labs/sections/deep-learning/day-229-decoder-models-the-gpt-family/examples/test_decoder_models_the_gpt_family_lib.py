import pytest
import torch
from examples.decoder_models_the_gpt_family_lib import MiniatureGPT

def test_miniature_gpt_forward():
    torch.manual_seed(42)
    model = MiniatureGPT(vocab_size=100, d_model=16, num_layers=2, num_heads=2)
    x = torch.randint(0, 100, (2, 6))
    logits = model(x)
    assert logits.shape == (2, 6, 100)

def test_autoregressive_generation():
    torch.manual_seed(42)
    model = MiniatureGPT(vocab_size=100, d_model=16, num_layers=2, num_heads=2)
    prompt = torch.randint(0, 100, (1, 3))
    out = model.generate(prompt, max_new_tokens=4)
    assert out.shape == (1, 7) # 3 prompt + 4 new = 7 tokens
