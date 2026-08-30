import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Tuple

class BiLSTMAttentionSentiment(nn.Module):
    def __init__(self, vocab_size: int, embed_dim: int, hidden_dim: int, num_classes: int = 2):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=0)
        self.lstm = nn.LSTM(embed_dim, hidden_dim, batch_first=True, bidirectional=True)
        self.attn_proj = nn.Linear(hidden_dim * 2, hidden_dim)
        self.attn_vec = nn.Linear(hidden_dim, 1, bias=False)
        self.classifier = nn.Sequential(
            nn.Dropout(0.5),
            nn.Linear(hidden_dim * 2, num_classes)
        )

    def forward(self, x: torch.Tensor, mask: torch.Tensor = None) -> Tuple[torch.Tensor, torch.Tensor]:
        embeds = self.embedding(x)
        h_seq, _ = self.lstm(embeds)
        u = torch.tanh(self.attn_proj(h_seq))
        scores = self.attn_vec(u).squeeze(2)

        if mask is not None:
            scores = scores.masked_fill(mask == 0, -1e9)

        attn_weights = F.softmax(scores, dim=1)
        doc_vec = torch.bmm(attn_weights.unsqueeze(1), h_seq).squeeze(1)
        logits = self.classifier(doc_vec)
        return logits, attn_weights

    def explain_tokens(self, x: torch.Tensor, target_class: int = 1) -> Tuple[torch.Tensor, torch.Tensor]:
        self.eval()
        embeds = self.embedding(x).detach().requires_grad_(True)
        h_seq, _ = self.lstm(embeds)
        u = torch.tanh(self.attn_proj(h_seq))
        scores = self.attn_vec(u).squeeze(2)
        attn_weights = F.softmax(scores, dim=1)
        doc_vec = torch.bmm(attn_weights.unsqueeze(1), h_seq).squeeze(1)
        logits = self.classifier(doc_vec)

        score = logits[0, target_class]
        score.backward()

        saliency = (embeds.grad[0] * embeds[0]).sum(dim=1).detach()
        return saliency, attn_weights[0]

def run_sentiment_demo():
    torch.manual_seed(42)
    model = BiLSTMAttentionSentiment(vocab_size=50, embed_dim=8, hidden_dim=4, num_classes=2)
    x = torch.randint(1, 50, (2, 5))
    logits, weights = model(x)
    saliency, _ = model.explain_tokens(x[:1], target_class=1)

    print(f"Sentiment Demo: Logits Shape = {logits.shape}, Saliency Shape = {saliency.shape}")
    return logits, saliency

if __name__ == "__main__":
    run_sentiment_demo()
