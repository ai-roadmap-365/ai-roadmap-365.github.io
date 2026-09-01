# Week 33 Project: Fine-Tuned Transformer

## Overview
Fine-tune a lightweight pretrained Transformer model (such as `distilbert-base-uncased` or `prajjwal1/bert-tiny`) on a domain-specific text classification task using the Hugging Face Transformers ecosystem and PyTorch. Evaluate the model rigorously across Accuracy, Precision, Recall, and Macro-F1 metrics, compare against classical baselines, and report results with complete honesty and ablation transparency.

## Objectives
- Load and prepare a domain text classification dataset (e.g. customer sentiment, product inquiry routing, or topic categorization).
- Implement tokenization with `AutoTokenizer` and dynamic batch padding via `DataCollatorWithPadding`.
- Configure `AutoModelForSequenceClassification` with a custom classification head.
- Set up optimization using `TrainingArguments` with AdamW decoupled weight decay, learning rate warmup, and early stopping.
- Compute evaluation metrics (Accuracy, Precision, Recall, Macro-F1) on held-out test data.
- Benchmark inference latency and export the model to ONNX Runtime format.

## Architecture
```
Raw Text Stream -> AutoTokenizer (BPE/WordPiece) -> Dynamic DataCollator
                        |
                        v
Pretrained Transformer Encoder Backbone (DistilBERT / MiniLM)
                        |
                        v
Layer-wise Learning Rate Decay (LLRD) + Pre-LN Residual Streams
                        |
                        v
Dense Classification Head -> Softmax -> Predictions (Accuracy & F1)
```

## Implementation Steps
1. **Data Ingestion & Cleaning:** Load dataset splits (train, validation, test) and inspect label balance.
2. **Tokenization Pipeline:** Map texts through the tokenizer with truncation and max length bounds.
3. **Model Initialization:** Instantiate `AutoModelForSequenceClassification` with the appropriate number of target class labels.
4. **Trainer Configuration:** Set learning rate ($2\times 10^{-5}$ to $5\times 10^{-5}$), batch size, warmup steps, and evaluation strategy.
5. **Training Execution:** Execute `trainer.train()`, monitor evaluation loss, and track early stopping.
6. **Evaluation & Reporting:** Compute final test metrics and analyze false positive / false negative failure modes.

## Expected output
```
[Week 33 Capstone Project: Fine-Tuned Transformer]
Loading Model: distilbert-base-uncased (66M parameters)
Dataset: 5,000 Training Samples, 1,000 Validation Samples, 1,000 Test Samples
Training Execution (3 Epochs):
  Epoch 1: Train Loss: 0.3842, Val Loss: 0.2910, Val F1: 0.884
  Epoch 2: Train Loss: 0.2105, Val Loss: 0.2450, Val F1: 0.912
  Epoch 3: Train Loss: 0.1280, Val Loss: 0.2390, Val F1: 0.925 (Best Checkpoint)
Final Test Evaluation:
  Accuracy: 92.4%
  Precision: 92.8%
  Recall: 91.9%
  Macro-F1: 92.3%
Inference Latency Benchmark (CPU): 3.2 ms per sequence [VERIFIED]
```

## Validation
- Confirm test set Macro-F1 meets or exceeds the $90.0\%$ target baseline.
- Verify dynamic batch collation operates without tensor shape mismatches.
- Ensure training evaluation loss decreases monotonically before early stopping.
- Verify error analysis documents at least 5 false-positive and false-negative edge cases.

## Deliverables
- `fine_tune_transformer.py`: Full fine-tuning and evaluation script.
- `model_report.md`: Detailed performance report comparing baseline vs transformer fine-tuning.
- `metrics.json`: Exported validation and test evaluation metrics.
