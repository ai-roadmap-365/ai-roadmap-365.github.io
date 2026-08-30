import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import List, Tuple, Dict, Any

class SkipGramNegativeSampling(nn.Module):
    def __init__(self, vocab_size: int, embed_dim: int):
        super().__init__()
        self.target_embeddings = nn.Embedding(vocab_size, embed_dim)
        self.context_embeddings = nn.Embedding(vocab_size, embed_dim)
        # Initialize weights uniformly
        nn.init.uniform_(self.target_embeddings.weight, -0.5 / embed_dim, 0.5 / embed_dim)
        nn.init.uniform_(self.context_embeddings.weight, -0.5 / embed_dim, 0.5 / embed_dim)

    def forward(self, center_words: torch.Tensor, context_words: torch.Tensor,
                negative_words: torch.Tensor) -> torch.Tensor:
        # center_words: (B,)
        # context_words: (B,)
        # negative_words: (B, K)
        
        v_center = self.target_embeddings(center_words) # (B, d)
        u_context = self.context_embeddings(context_words) # (B, d)
        u_neg = self.context_embeddings(negative_words) # (B, K, d)

        # Positive score: log(sigmoid(v_center . u_context))
        pos_score = torch.sum(v_center * u_context, dim=1) # (B,)
        pos_loss = F.logsigmoid(pos_score)

        # Negative score: log(sigmoid(- v_center . u_neg))
        # (B, 1, d) x (B, d, K) -> (B, 1, K) -> (B, K)
        neg_score = torch.bmm(u_neg, v_center.unsqueeze(2)).squeeze(2) # (B, K)
        neg_loss = torch.sum(F.logsigmoid(-neg_score), dim=1) # (B,)

        total_loss = - (pos_loss + neg_loss).mean()
        return total_loss

def compute_cosine_similarity(v1: torch.Tensor, v2: torch.Tensor) -> float:
    return F.cosine_similarity(v1.unsqueeze(0), v2.unsqueeze(0)).item()

def run_embedding_demo():
    torch.manual_seed(42)
    model = SkipGramNegativeSampling(vocab_size=100, embed_dim=16)
    
    center = torch.tensor([4, 10])
    context = torch.tensor([5, 12])
    negatives = torch.tensor([
        [15, 22, 33, 44],
        [55, 66, 77, 88]
    ])

    loss = model(center, context, negatives)
    v1 = model.target_embeddings.weight[0]
    v2 = model.target_embeddings.weight[1]
    sim = compute_cosine_similarity(v1, v2)
    
    print(f"Embedding Demo: Loss = {loss.item():.4f}, Cosine Sim = {sim:.4f}")
    return model, loss.item(), sim

if __name__ == "__main__":
    run_embedding_demo()
