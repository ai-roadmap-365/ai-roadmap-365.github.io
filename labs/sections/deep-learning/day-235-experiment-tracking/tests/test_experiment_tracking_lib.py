import pytest
import os
import json
from examples.experiment_tracking_lib import ExperimentLogger, CheckpointManager

def test_experiment_logger(tmp_path):
    log_dir = str(tmp_path / "runs")
    logger = ExperimentLogger("test_run", log_dir=log_dir, config={"lr": 1e-4})
    logger.log_step(1, 1, {"loss": 0.5})
    logger.log_eval(1, {"val_acc": 0.9})

    assert os.path.exists(logger.log_path)
    with open(logger.log_path, "r", encoding="utf-8") as f:
        lines = [json.loads(line) for line in f]
    
    assert len(lines) == 3
    assert lines[0]["event"] == "init"
    assert lines[1]["loss"] == 0.5
    assert lines[2]["val_acc"] == 0.9

def test_checkpoint_manager_retention(tmp_path):
    save_dir = str(tmp_path / "ckpts")
    mgr = CheckpointManager(save_dir=save_dir, max_to_keep=2)
    
    mgr.save_checkpoint(1, 0.50, {"step": 1})
    mgr.save_checkpoint(2, 0.30, {"step": 2})
    active = mgr.save_checkpoint(3, 0.20, {"step": 3})

    assert len(active) == 2
    # Best 2: loss 0.20 (epoch 3) and loss 0.30 (epoch 2)
    assert any("epoch_3" in p for p in active)
    assert any("epoch_2" in p for p in active)
