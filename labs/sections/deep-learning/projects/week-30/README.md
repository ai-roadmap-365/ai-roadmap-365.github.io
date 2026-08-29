# Week 30 Project: Fashion-MNIST Classifier

## Project overview
In this project, you will engineer a complete, industrial-grade PyTorch deep learning training and evaluation pipeline to classify 70,000 apparel items across 10 classes in the Fashion-MNIST benchmark. You will integrate all concepts from Week 30: custom `Dataset` and `DataLoader` pipelines, multi-layer `nn.Module` architecture with Batch Normalization and Dropout, AdamW optimization with decoupled weight decay, Linear Warmup with Cosine Annealing learning rate schedules, gradient norm clipping, and an automated `EarlyStopping` controller with atomic checkpointing.

## Objectives
- Ingest and normalize the Fashion-MNIST dataset (`70,000` 28x28 grayscale images across 10 clothing categories: T-shirt/top, Trouser, Pullover, Dress, Coat, Sandal, Shirt, Sneaker, Bag, Ankle boot).
- Implement a deep regularized classifier (`FashionClassifierNet`) utilizing `nn.Linear`, `nn.BatchNorm1d`, `nn.ReLU`, and `nn.Dropout`.
- Implement `AdamW` optimizer paired with a custom `WarmupCosineScheduler` or `OneCycleLR` policy.
- Build a modular `PyTorchTrainer` harness with automatic validation evaluation, gradient norm clipping, and early stopping.
- Achieve >= 88.0% test accuracy on the held-out Fashion-MNIST test partition while maintaining full reproducibility with deterministic seeding.

## Architecture
```
[28x28 Grayscale Image]
       │
       ▼
[Flatten: 784-D Vector]
       │
       ▼
[Linear: 784 -> 512] ──► [BatchNorm1d(512)] ──► [ReLU] ──► [Dropout(0.3)]
       │
       ▼
[Linear: 512 -> 256] ──► [BatchNorm1d(256)] ──► [ReLU] ──► [Dropout(0.2)]
       │
       ▼
[Linear: 256 -> 128] ──► [BatchNorm1d(128)] ──► [ReLU] ──► [Dropout(0.1)]
       │
       ▼
[Linear: 128 -> 10] ──► [CrossEntropyLoss / Logits] ──► [Apparel Category 0-9]
```

## Implementation guidelines
1. **Determinism:** Seed `random`, `numpy`, and `torch` using `seed_everything(seed=42)`.
2. **Data Pipeline:** Create train (`50,000`), validation (`10,000`), and test (`10,000`) `DataLoader` instances with `batch_size = 64` and `num_workers = 2`.
3. **Optimization Setup:** Configure `AdamW(lr=1e-3, weight_decay=1e-4)` and dynamic gradient clipping `clip_grad_norm_(max_norm=1.0)`.
4. **Learning Rate Schedule:** Apply a 5-epoch linear warmup followed by half-period cosine decay over 30 total epochs.
5. **Early Stopping:** Configure `EarlyStopping(patience=5, min_delta=1e-3)` tracking validation loss, saving the best checkpoint to `best_fashion_model.pt`.
6. **Evaluation Mode:** Always evaluate validation and test metrics inside `model.eval()` and `with torch.no_grad():`.

## Deliverables
- Complete Python training pipeline `fashion_mnist_classifier.py`.
- Saved checkpoint artifact `best_fashion_model.pt` containing `model_state_dict`, `optimizer_state_dict`, `config`, and validation metrics.
- Comprehensive evaluation report including accuracy per apparel class, confusion matrix analysis, and training vs validation loss curves.
