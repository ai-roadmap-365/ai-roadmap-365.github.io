import pytest
from examples.text_preprocessing_and_tokenization_lib import regex_pre_tokenize, BPETokenizer, pad_and_mask_batch

def test_regex_pre_tokenize():
    text = "Hello, world! It's 2026."
    tokens = regex_pre_tokenize(text)
    assert "Hello" in tokens
    assert "world" in tokens
    assert "," in tokens
    assert "2026" in tokens

def test_bpe_training_and_encoding():
    corpus = ["low lower lowest", "new newer newest", "wide wider widest"]
    tok = BPETokenizer(num_merges=4)
    tok.train(corpus)
    assert len(tok.merges) > 0
    assert len(tok.vocab) >= 4 # Includes special tokens

    ids = tok.encode("lowest")
    assert isinstance(ids, list)
    assert len(ids) > 0

def test_pad_and_mask_batch():
    batch = [[10, 20, 30], [40, 50]]
    padded, masks = pad_and_mask_batch(batch, pad_idx=0)
    assert padded[0] == [10, 20, 30]
    assert padded[1] == [40, 50, 0]
    assert masks[0] == [1, 1, 1]
    assert masks[1] == [1, 1, 0]
