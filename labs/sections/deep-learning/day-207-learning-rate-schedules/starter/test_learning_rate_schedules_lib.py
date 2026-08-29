import pytest
import torch
from examples.learning_rate_schedules_lib import create_warmup_cosine_scheduler

def test_warmup_cosine_scheduler_warmup_phase():
    w = torch.tensor([1.0], requires_grad=True)
    opt = torch.optim.SGD([w], lr=0.1)
    sched = create_warmup_cosine_scheduler(opt, warmup_steps=10, total_steps=100, min_lr_ratio=0.01)

    assert sched.get_last_lr()[0] == 0.0
    for _ in range(5):
        sched.step()
    # At step 5 (halfway through warmup), lr should be 0.05
    assert pytest.approx(sched.get_last_lr()[0], abs=1e-5) == 0.05

    for _ in range(5):
        sched.step()
    # At step 10 (end of warmup), lr should be peak 0.1
    assert pytest.approx(sched.get_last_lr()[0], abs=1e-5) == 0.1

def test_warmup_cosine_scheduler_final_decay():
    w = torch.tensor([1.0], requires_grad=True)
    opt = torch.optim.SGD([w], lr=0.1)
    sched = create_warmup_cosine_scheduler(opt, warmup_steps=10, total_steps=100, min_lr_ratio=0.01)

    for _ in range(100):
        sched.step()

    # At final step 100, lr should decay to min_lr_ratio * base_lr = 0.001
    assert pytest.approx(sched.get_last_lr()[0], abs=1e-5) == 0.001

def test_scheduler_state_dict_persistence():
    w1 = torch.tensor([1.0], requires_grad=True)
    opt1 = torch.optim.SGD([w1], lr=0.1)
    sched1 = create_warmup_cosine_scheduler(opt1, warmup_steps=20, total_steps=100)

    for _ in range(50):
        sched1.step()
    lr_at_50 = sched1.get_last_lr()[0]

    state = sched1.state_dict()

    w2 = torch.tensor([1.0], requires_grad=True)
    opt2 = torch.optim.SGD([w2], lr=0.1)
    sched2 = create_warmup_cosine_scheduler(opt2, warmup_steps=20, total_steps=100)
    sched2.load_state_dict(state)

    assert pytest.approx(sched2.get_last_lr()[0], abs=1e-5) == lr_at_50
