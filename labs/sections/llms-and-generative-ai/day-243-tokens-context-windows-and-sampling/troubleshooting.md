# Troubleshooting: Day 243 - Tokens, Context Windows, and Sampling

## Common Issues
1. **NaN in Softmax after Top-p:**
   - Cause: Masking out all tokens because cumulative probability condition was inverted.
   - Fix: Ensure `sorted_indices_to_remove[0] = False` to always keep the top token.
