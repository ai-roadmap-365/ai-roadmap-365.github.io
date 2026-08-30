# Troubleshooting: Day 236 - Quantization and Distillation

## Common Issues
1. **KL divergence returning negative loss:**
   - Cause: Passing raw student logits to `KLDivLoss` instead of `F.log_softmax()`.
   - Fix: Use `F.log_softmax(student_logits / tau)`.
