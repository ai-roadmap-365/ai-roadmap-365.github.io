import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import List

class EmbeddingBagClassifier(nn.Module):
    def __init__(self, vocab_size: int, embed_dim: int, num_classes: int):
        super().__init__()
        self.embedding_bag = nn.EmbeddingBag(vocab_size, embed_dim, mode="mean")
        self.fc = nn.Linear(embed_dim, num_classes)

    def forward(self, text_indices: torch.Tensor, offsets: torch.Tensor = None) -> torch.Tensor:
        if offsets is None:
            # 2D tensor (Batch, Seq_Len)
            doc_embeds = self.embedding_bag(text_indices)
        else:
            doc_embeds = self.embedding_bag(text_indices, offsets)
        return self.fc(doc_embeds)

class TextCNN(nn.Module):
    def __init__(self, vocab_size: int, embed_dim: int, num_classes: int,
                 num_filters: int = 16, filter_sizes: List[int] = [2, 3]):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=0)
        self.convs = nn.ModuleList([
            nn.Conv1d(in_channels=embed_dim, out_channels=num_filters, kernel_size=k)
            for k in filter_sizes
        ])
        self.fc = nn.Linear(num_filters * len(filter_sizes), num_classes)

    def forward(self, text_indices: torch.Tensor) -> torch.Tensor:
        # text_indices: (Batch, Seq_Len)
        embeds = self.embedding(text_indices).permute(0, 2, 1) # (Batch, embed_dim, Seq_Len)
        pooled_outputs = []
        for conv in self.convs:
            c = F.relu(conv(embeds))
            p = F.max_pool1d(c, kernel_size=c.size(2)).squeeze(2)
            pooled_outputs.append(p)
        
        doc_features = torch.cat(pooled_outputs, dim=1)
        return self.fc(doc_features)

def run_classification_demo():
    torch.manual_seed(42)
    eb_model = EmbeddingBagClassifier(vocab_size=50, embed_dim=8, num_classes=2)
    cnn_model = TextCNN(vocab_size=50, embed_dim=8, num_classes=2, num_filters=4, filter_sizes=[2, 3])

    inputs = torch.randint(1, 50, (2, 6)) # Batch=2, Len=6
    eb_logits = eb_model(inputs)
    cnn_logits = cnn_model(inputs)

    print(f"Classification Demo: EB Shape = {eb_logits.shape}, CNN Shape = {cnn_logits.shape}")
    return eb_logits, cnn_logits

if __name__ == "__main__":
    run_classification_demo()
