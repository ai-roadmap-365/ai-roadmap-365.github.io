# Troubleshooting: Day 224 - A Sentiment Analysis Project

## Common Issues
1. **Backward pass error in explain_tokens:**
   - Cause: Target class score was detached before calling backward.
   - Fix: Keep computation graph intact when computing `logits[0, target_class].backward()`.
