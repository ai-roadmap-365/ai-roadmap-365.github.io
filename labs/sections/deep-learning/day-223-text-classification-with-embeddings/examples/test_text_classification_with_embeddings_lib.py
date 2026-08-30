import pytest
import torch
from examples.text_classification_with_embeddings_lib import EmbeddingBagClassifier, TextCNN

def test_embedding_bag_classifier():
    torch.manual_seed(42)
    model = EmbeddingBagClassifier(vocab_size=100, embed_dim=16, num_classes=3)
    x = torch.randint(0, 100, (4, 10))
    logits = model(x)
    assert logits.shape == (4, 3)

def test_textcnn_classifier():
    torch.manual_seed(42)
    model = TextCNN(vocab_size=100, embed_dim=16, num_classes=2, num_filters=8, filter_sizes=[2, 3, 4])
    x = torch.randint(0, 100, (3, 8))
    logits = model(x)
    assert logits.shape == (3, 2)
