import pytest
import numpy as np
from examples.serving_a_model_over_an_api_lib import (
    ModelServingEngine, SingleFeatureInput
)

def test_model_serving_lifecycle_and_predictions():
    engine = ModelServingEngine()
    # Before loading, health is not ready and predict raises error
    h1 = engine.health_check()
    assert h1.is_live is True
    assert h1.is_ready is False

    with pytest.raises(RuntimeError):
        engine.predict_single(SingleFeatureInput(10.0, 50.0, 1))

    # Load weights
    engine.load_model(weights=np.array([0.01, 0.02, 0.5]), bias=-1.0)
    assert engine.health_check().is_ready is True

    # Valid prediction
    res = engine.predict_single(SingleFeatureInput(12.0, 100.0, 3))
    assert "churn_probability" in res
    assert 0.0 <= res["churn_probability"] <= 1.0
    assert res["used_fallback"] is False

def test_serving_validation_and_batch():
    engine = ModelServingEngine()
    engine.load_model(weights=np.array([0.01, 0.02, 0.5]), bias=-1.0)

    # Negative inputs raise ValueError
    with pytest.raises(ValueError):
        engine.predict_single(SingleFeatureInput(-5.0, 50.0, 1))

    # Batch endpoint
    batch = [
        SingleFeatureInput(12.0, 80.0, 0),
        SingleFeatureInput(2.0, 120.0, 4)
    ]
    batch_res = engine.predict_batch(batch)
    assert len(batch_res) == 2
