import pytest
from examples.saving_and_versioning_models_lib import ModelRegistry

def test_register_and_hashing():
    reg = ModelRegistry()
    raw = b"BINARY_BYTES_12345"
    meta = reg.register_model("risk_model", "1.0.0", raw, "git_sha_1", {"roc_auc": 0.90})

    assert meta.stage == "STAGING"
    assert len(meta.sha256_hash) == 64
    assert meta.version == "1.0.0"

    with pytest.raises(ValueError):
        reg.register_model("risk_model", "1.0.0", raw, "git_sha_1", {"roc_auc": 0.90})

def test_stage_promotion_and_archival():
    reg = ModelRegistry()
    reg.register_model("risk_model", "1.0.0", b"V1", "sha1", {"auc": 0.80})
    reg.register_model("risk_model", "1.1.0", b"V2", "sha2", {"auc": 0.85})

    reg.transition_stage("risk_model", "1.0.0", "PRODUCTION")
    assert reg.get_production_model("risk_model").version == "1.0.0"

    # Promoting 1.1.0 must archive 1.0.0 automatically
    reg.transition_stage("risk_model", "1.1.0", "PRODUCTION")
    assert reg.get_production_model("risk_model").version == "1.1.0"
    assert reg._models["risk_model"]["1.0.0"].stage == "ARCHIVED"
