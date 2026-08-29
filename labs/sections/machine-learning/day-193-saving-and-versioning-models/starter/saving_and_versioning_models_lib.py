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
        # TODO: Compute SHA-256 hexadecimal digest
        pass

    def register_model(self, model_name: str, version: str, artifact_bytes: bytes,
                       git_commit: str, metrics: Dict[str, float]) -> ModelVersionMetadata:
        # TODO: Register model with SHA-256 and initial STAGING stage
        pass

    def transition_stage(self, model_name: str, version: str, new_stage: str) -> ModelVersionMetadata:
        # TODO: Update stage; if PRODUCTION, archive existing production versions
        pass

    def get_production_model(self, model_name: str) -> Optional[ModelVersionMetadata]:
        # TODO: Return currently active PRODUCTION model
        pass
