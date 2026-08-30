import json
import os
from typing import Dict, Any, List, Optional

class ExperimentLogger:
    def __init__(self, run_id: str, log_dir: str = "./runs", config: Optional[Dict[str, Any]] = None):
        # TODO: Initialize experiment logger and log init event to JSONL
        pass

    def log_step(self, step: int, epoch: int, metrics: Dict[str, float]):
        # TODO: Append step metrics to JSONL file
        pass

class CheckpointManager:
    def __init__(self, save_dir: str = "./checkpoints", max_to_keep: int = 2):
        # TODO: Initialize checkpoint manager
        pass

    def save_checkpoint(self, epoch: int, val_loss: float, model_state: Dict[str, Any]) -> List[str]:
        # TODO: Save checkpoint and prune older checkpoints beyond max_to_keep
        pass
