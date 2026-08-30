# Troubleshooting: Day 214 - Data Augmentation

## Common Issues
1. **Target loss NaN with MixUp:**
   - Cause: Passing scalar integer labels to CrossEntropyLoss with soft target vectors.
   - Fix: Use soft target CrossEntropyLoss or `torch.sum(-target * log_softmax(logits))`.
