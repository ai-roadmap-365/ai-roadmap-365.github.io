import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Optional

class BERTMaskedLM(nn.Module):
    def __init__(self, vocab_size: int = 1000, d_model: int = 32,
                 num_layers: int = 2, num_heads: int = 4):
        super().__init__()
        self.token_embeddings = nn.Embedding(vocab_size, d_model, padding_idx=0)
        self.pos_embeddings = nn.Embedding(128, d_model)
        self.norm = nn.LayerNorm(d_model)

        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model, nhead=num_heads, dim_feedforward=4 * d_model,
            activation="gelu", batch_first=True, norm_first=True
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)

        self.mlm_dense = nn.Linear(d_model, d_model)
        self.mlm_norm = nn.LayerNorm(d_model)
        self.mlm_decoder = nn.Linear(d_model, vocab_size, bias=False)

        # Weight tying
        self.mlm_decoder.weight = self.token_embeddings.weight

    def forward(self, input_ids: torch.Tensor,
                attention_mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        seq_len = input_ids.size(1)
        positions = torch.arange(seq_len, device=input_ids.device).unsqueeze(0)

        x = self.token_embeddings(input_ids) + self.pos_embeddings(positions)
        x = self.norm(x)

        h = self.transformer(x, src_key_padding_mask=attention_mask)
        h_mlm = F.gelu(self.mlm_dense(h))
        h_mlm = self.mlm_norm(h_mlm)
        logits = self.mlm_decoder(h_mlm)
        return logits

def run_bert_demo():
    torch.manual_seed(42)
    model = BERTMaskedLM(vocab_size=100, d_model=16, num_layers=2, num_heads=2)
    input_ids = torch.randint(1, 100, (2, 8))
    logits = model(input_ids)

    print(f"BERT Demo: Logits Shape = {logits.shape}")
    return logits

if __name__ == "__main__":
    run_bert_demo()
