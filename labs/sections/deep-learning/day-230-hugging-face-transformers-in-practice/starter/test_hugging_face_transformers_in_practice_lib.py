import pytest
import torch
import numpy as np
from examples.hugging_face_transformers_in_practice_lib import MockDataCollatorWithPadding, compute_classification_metrics

def test_dynamic_padding_collator():
    collator = MockDataCollatorWithPadding(pad_token_id=0)
    batch_data = [
        {"input_ids": [1, 2, 3], "label": 1},
        {"input_ids": [4, 5, 6, 7, 8], "label": 0}
    ]
    res = collator(batch_data)
    assert res["input_ids"].shape == (2, 5)
    assert res["attention_mask"].shape == (2, 5)
    assert res["attention_mask"][0].tolist() == [1, 1, 1, 0, 0]
    assert res["labels"].shape == (2,)

def test_metric_computation():
    preds = np.array([1, 0, 1, 1, 0])
    labels = np.array([1, 0, 1, 0, 0])
    metrics = compute_classification_metrics(preds, labels)
    
    assert metrics["accuracy"] == 0.8
    assert metrics["f1"] > 0.7
