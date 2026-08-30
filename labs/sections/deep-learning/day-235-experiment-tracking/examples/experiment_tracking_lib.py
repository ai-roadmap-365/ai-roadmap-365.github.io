import json
import os
from typing import Dict, Any, List, Optional

class ExperimentLogger:
    def __init__(self, run_id: str, log_dir: str = "./runs", config: Optional[Dict[str, Any]] = None):
        self.run_id = run_id
        self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)
        self.log_path = os.path.join(self.log_dir, f"{run_id}.jsonl")
        
        init_event = {
            "event": "init",
            "run_id": run_id,
            "config": config or {}
        }
        self._append(init_event)

    def _append(self, record: Dict[str, Any]):
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")

    def log_step(self, step: int, epoch: int, metrics: Dict[str, float]):
        record = {
            "event": "step",
            "step": step,
            "epoch": epoch,
            **metrics
        }
        self._append(record)

    def log_eval(self, epoch: int, metrics: Dict[str, float]):
        record = {
            "event": "eval",
            "epoch": epoch,
            **metrics
        }
        self._append(record)

class CheckpointManager:
    def __init__(self, save_dir: str = "./checkpoints", max_to_keep: int = 2):
        self.save_dir = save_dir
        self.max_to_keep = max_to_keep
        self.checkpoints: List[Dict[str, Any]] = []
        os.makedirs(self.save_dir, exist_ok=True)

    def save_checkpoint(self, epoch: int, val_loss: float, model_state: Dict[str, Any]) -> List[str]:
        ckpt_filename = f"model_epoch_{epoch}_loss_{val_loss:.3f}.json"
        ckpt_path = os.path.join(self.save_dir, ckpt_filename)
        
        with open(ckpt_path, "w", encoding="utf-8") as f:
            json.dump({"epoch": epoch, "val_loss": val_loss, "state": model_state}, f)

        self.checkpoints.append({"epoch": epoch, "val_loss": val_loss, "path": ckpt_path})
        # Sort by validation loss ascending (lower is better)
        self.checkpoints.sort(key=lambda x: x["val_loss"])

        # Prune if exceeding max_to_keep
        while len(self.checkpoints) > self.max_to_keep:
            to_remove = self.checkpoints.pop(-1)
            if os.path.exists(to_remove["path"]):
                os.remove(to_remove["path"])

        return [c["path"] for c in self.checkpoints]

def run_experiment_tracking_demo():
    logger = ExperimentLogger("demo-run-01", log_dir="./test_runs", config={"lr": 3e-4, "batch_size": 32})
    logger.log_step(1, 1, {"loss": 0.45})
    logger.log_eval(1, {"val_loss": 0.38, "val_acc": 0.88})

    manager = CheckpointManager(save_dir="./test_checkpoints", max_to_keep=2)
    manager.save_checkpoint(1, 0.38, {"w": [1.0, 2.0]})
    manager.save_checkpoint(2, 0.25, {"w": [1.1, 2.1]})
    active_ckpts = manager.save_checkpoint(3, 0.20, {"w": [1.2, 2.2]})

    print(f"Experiment Demo: Logged to {logger.log_path}, Active Checkpoints = {len(active_ckpts)}")
    return logger.log_path, active_ckpts

if __name__ == "__main__":
    run_experiment_tracking_demo()
