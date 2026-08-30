import torch
import torch.nn as nn
from typing import Tuple

class CustomLSTMCell(nn.Module):
    def __init__(self, input_dim: int, hidden_dim: int):
        super().__init__()
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        # Fused gate linear projection: 4 * hidden_dim
        self.gates = nn.Linear(input_dim + hidden_dim, 4 * hidden_dim)
        # Initialize forget gate bias to 1.0
        with torch.no_grad():
            self.gates.bias[0:hidden_dim].fill_(1.0)

    def forward(self, x_t: torch.Tensor, states: Tuple[torch.Tensor, torch.Tensor]) -> Tuple[torch.Tensor, torch.Tensor]:
        h_prev, c_prev = states
        combined = torch.cat([x_t, h_prev], dim=1)
        gate_outputs = self.gates(combined)

        f_t, i_t, c_cand, o_t = torch.chunk(gate_outputs, 4, dim=1)
        
        f_t = torch.sigmoid(f_t)
        i_t = torch.sigmoid(i_t)
        c_cand = torch.tanh(c_cand)
        o_t = torch.sigmoid(o_t)

        c_t = f_t * c_prev + i_t * c_cand
        h_t = o_t * torch.tanh(c_t)
        return h_t, c_t

class CustomGRUCell(nn.Module):
    def __init__(self, input_dim: int, hidden_dim: int):
        super().__init__()
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.gate_rz = nn.Linear(input_dim + hidden_dim, 2 * hidden_dim)
        self.gate_cand = nn.Linear(input_dim + hidden_dim, hidden_dim)

    def forward(self, x_t: torch.Tensor, h_prev: torch.Tensor) -> torch.Tensor:
        combined = torch.cat([x_t, h_prev], dim=1)
        r_z = self.gate_rz(combined)
        r_t, z_t = torch.chunk(r_z, 2, dim=1)
        
        r_t = torch.sigmoid(r_t)
        z_t = torch.sigmoid(z_t)

        combined_cand = torch.cat([x_t, r_t * h_prev], dim=1)
        h_cand = torch.tanh(self.gate_cand(combined_cand))

        h_t = (1 - z_t) * h_prev + z_t * h_cand
        return h_t

def run_lstm_gru_demo():
    torch.manual_seed(42)
    lstm_cell = CustomLSTMCell(input_dim=8, hidden_dim=16)
    gru_cell = CustomGRUCell(input_dim=8, hidden_dim=16)

    x = torch.randn(4, 8)
    h0 = torch.zeros(4, 16)
    c0 = torch.zeros(4, 16)

    h_lstm, c_lstm = lstm_cell(x, (h0, c0))
    h_gru = gru_cell(x, h0)

    print(f"LSTM/GRU Demo: LSTM h Shape = {h_lstm.shape}, GRU h Shape = {h_gru.shape}")
    return h_lstm, c_lstm, h_gru

if __name__ == "__main__":
    run_lstm_gru_demo()
