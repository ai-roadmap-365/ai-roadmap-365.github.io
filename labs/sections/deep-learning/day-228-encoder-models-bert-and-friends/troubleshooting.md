# Troubleshooting: Day 228 - Encoder Models: BERT and Friends

## Common Issues
1. **Dimension mismatch in decoder:**
   - Cause: Output projection shape does not match `(d_model, vocab_size)`.
   - Fix: Use `nn.Linear(d_model, vocab_size, bias=False)`.
