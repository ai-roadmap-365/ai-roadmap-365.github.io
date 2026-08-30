# Troubleshooting: Day 229 - Decoder Models: The GPT Family

## Common Issues
1. **Causal mask device mismatch:**
   - Cause: Mask created on CPU while model runs on CUDA/MPS.
   - Fix: Use `causal_mask.to(x.device)`.
