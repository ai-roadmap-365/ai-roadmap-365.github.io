# Troubleshooting: Day 241 - The Model Landscape: Claude, GPT, Gemini, Llama

## Common Issues
1. **Pricing calculation mismatch:**
   - Cause: Input tokens multiplied by output rates.
   - Fix: Use separate pricing variables `in_rate` and `out_rate`.
