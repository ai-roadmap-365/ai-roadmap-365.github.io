import hashlib
from dataclasses import dataclass
from typing import Dict, Optional

@dataclass
class ModelVersionMetadata:
    model_name: str
    version: str
    sha256_hash: str
    stage: str
    git_commit: str
    metrics: Dict[str, float]

class ModelRegistry:
    def __init__(self):
        self._models: Dict[str, Dict[str, ModelVersionMetadata]] = {}

    @staticmethod
    def compute_sha256(file_bytes: bytes) -> str:
        return hashlib.sha256(file_bytes).hexdigest()

    def register_model(
        self, model_name: str, version: str, artifact_bytes: bytes,
        git_commit: str, metrics: Dict[str, float]
    ) -> ModelVersionMetadata:
        if model_name not in self._models:
            self._models[model_name] = {}

        if version in self._models[model_name]:
            raise ValueError(f"Version {version} already exists for model {model_name}")

        sha256 = self.compute_sha256(artifact_bytes)
        meta = ModelVersionMetadata(
            model_name=model_name,
            version=version,
            sha256_hash=sha256,
            stage="STAGING",
            git_commit=git_commit,
            metrics=metrics
        )
        self._models[model_name][version] = meta
        return meta

    def transition_stage(self, model_name: str, version: str, new_stage: str) -> ModelVersionMetadata:
        valid_stages = {"STAGING", "PRODUCTION", "ARCHIVED", "REJECTED"}
        if new_stage not in valid_stages:
            raise ValueError(f"Invalid stage: {new_stage}")

        if model_name not in self._models or version not in self._models[model_name]:
            raise KeyError(f"Model {model_name}:{version} not found")

        if new_stage == "PRODUCTION":
            for v, meta in self._models[model_name].items():
                if meta.stage == "PRODUCTION" and v != version:
                    meta.stage = "ARCHIVED"

        meta = self._models[model_name][version]
        meta.stage = new_stage
        return meta

    def get_production_model(self, model_name: str) -> Optional[ModelVersionMetadata]:
        if model_name not in self._models:
            return None
        for meta in self._models[model_name].values():
            if meta.stage == "PRODUCTION":
                return meta
        return None

def run_registry_demo():
    registry = ModelRegistry()
    dummy_bytes_v1 = b"MODEL_WEIGHTS_V1_BIN_BLOB"
    dummy_bytes_v2 = b"MODEL_WEIGHTS_V2_BIN_BLOB"

    m1 = registry.register_model("fraud_detector", "1.0.0", dummy_bytes_v1, "a1b2c3", {"pr_auc": 0.82})
    m2 = registry.register_model("fraud_detector", "1.1.0", dummy_bytes_v2, "d4e5f6", {"pr_auc": 0.86})

    registry.transition_stage("fraud_detector", "1.0.0", "PRODUCTION")
    registry.transition_stage("fraud_detector", "1.1.0", "PRODUCTION")

    prod = registry.get_production_model("fraud_detector")
    print(f"Registry Demo: Active Production Version = {prod.version if prod else None}")
    return registry, prod

if __name__ == "__main__":
    run_registry_demo()
