import pytest
import torch
from examples.lstms_and_grus_lib import CustomLSTMCell, CustomGRUCell

def test_lstm_cell_dimensions():
    torch.manual_seed(42)
    cell = CustomLSTMCell(input_dim=10, hidden_dim=20)
    x = torch.randn(2, 10)
    h0 = torch.zeros(2, 20)
    c0 = torch.zeros(2, 20)

    h1, c1 = cell(x, (h0, c0))
    assert h1.shape == (2, 20)
    assert c1.shape == (2, 20)

def test_gru_cell_dimensions():
    torch.manual_seed(42)
    cell = CustomGRUCell(input_dim=10, hidden_dim=20)
    x = torch.randn(3, 10)
    h0 = torch.zeros(3, 20)

    h1 = cell(x, h0)
    assert h1.shape == (3, 20)
