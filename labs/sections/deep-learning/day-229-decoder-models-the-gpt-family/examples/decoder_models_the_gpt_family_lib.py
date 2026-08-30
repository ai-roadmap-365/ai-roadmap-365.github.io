import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Optional

class GPTDecoderLayer(nn.Module):
    def __init__(self, d_model: int, num_heads: int):
        super().__init__()
        self.norm1 = nn.LayerNorm(d_model)
        self.self_attn = nn.MultiheadAttention(d_model, num_heads, batch_first=True)
        self.norm2 = nn.LayerNorm(d_model)
        self.ffn = nn.Sequential(
            nn.Linear(d_model, 4 * d_model),
            nn.GELU(),
            nn.Linear(4 * d_model, d_model)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        seq_len = x.size(1)
        causal_mask = nn.Transformer.generate_square_subsequent_mask(seq_len).to(x.device)
        
        normed = self.norm1(x)
        attn_out, _ = self.self_attn(normed, normed, normed, attn_mask=causal_mask, is_causal=True)
        x = x + attn_out
        x = x + self.ffn(self.norm2(x))
        return x

class MiniatureGPT(nn.Module):
    def __init__(self, vocab_size: int = 200, d_model: int = 32,
                 num_layers: int = 2, num_heads: int = 2):
        super().__init__()
        self.token_embeddings = nn.Embedding(vocab_size, d_model)
        self.pos_embeddings = nn.Embedding(128, d_model)
        self.layers = nn.ModuleList([
            GPTDecoderLayer(d_model, num_heads) for _ in range(num_layers)
        ])
        self.final_norm = nn.LayerNorm(d_model)
        self.lm_head = nn.Linear(d_model, vocab_size, bias=False)
        self.lm_head.weight = self.token_embeddings.weight

    def forward(self, input_ids: torch.Tensor) -> torch.Tensor:
        seq_len = input_ids.size(1)
        pos = torch.arange(seq_len, device=input_ids.device).unsqueeze(0)
        x = self.token_embeddings(input_ids) + self.pos_embeddings(pos)

        for layer in self.layers:
            x = layer(x)

        x = self.final_norm(x)
        logits = self.lm_head(x)
        return logits

    @torch.no_grad()
    def generate(self, prompt_ids: torch.Tensor, max_new_tokens: int = 5,
                 temperature: float = 1.0) -> torch.Tensor:
        current_ids = prompt_ids
        for _ in range(max_new_tokens):
            logits = self.forward(current_ids)[:, -1, :]
            logits = logits / temperature
            probs = F.softmax(logits, dim=-1)
            next_token = torch.multinomial(probs, num_samples=1)
            current_ids = torch.cat([current_ids, next_token], dim=1)
        return current_ids

def run_gpt_demo():
    torch.manual_seed(42)
    model = MiniatureGPT(vocab_size=100, d_model=16, num_layers=2, num_heads=2)
    prompt = torch.randint(1, 100, (1, 4))
    gen = model.generate(prompt, max_new_tokens=4, temperature=0.8)

    print(f"GPT Demo: Prompt Len = {prompt.size(1)}, Generated Len = {gen.size(1)}")
    return gen

if __name__ == "__main__":
    run_gpt_demo()
