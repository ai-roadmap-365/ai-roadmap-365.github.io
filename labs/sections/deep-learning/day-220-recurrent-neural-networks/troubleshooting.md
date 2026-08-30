# Troubleshooting: Day 220 - Recurrent Neural Networks

## Common Issues
1. **Hidden state tensor dimension mismatch:**
   - Cause: Passing unbatched vectors to `W_xh` or `W_hh`.
   - Fix: Ensure `h_t` has shape `(batch_size, hidden_dim)`.
