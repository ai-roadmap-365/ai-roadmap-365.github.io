import pytest
import torch
from examples.encoder_models_bert_and_friends_lib import BERTMaskedLM

def test_bert_masked_lm_shapes():
    torch.manual_seed(42)
    model = BERTMaskedLM(vocab_size=200, d_model=16, num_layers=2, num_heads=2)
    input_ids = torch.randint(0, 200, (3, 6))
    logits = model(input_ids)
    assert logits.shape == (3, 6, 200)

def test_weight_tying():
    model = BERTMaskedLM(vocab_size=100, d_model=16)
    assert model.mlm_decoder.weight.data_ptr() == model.token_embeddings.weight.data_ptr()
