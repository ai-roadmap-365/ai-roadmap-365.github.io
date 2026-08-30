# Troubleshooting: Day 239 - How Large Language Models Are Trained

## Common Issues
1. **Shingle size k too large for short texts:**
   - Cause: Choosing $k=5$ on text with only 4 words.
   - Fix: Fall back to individual words if word count $< k$.
