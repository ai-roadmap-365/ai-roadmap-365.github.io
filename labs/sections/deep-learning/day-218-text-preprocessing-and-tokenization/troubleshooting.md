# Troubleshooting: Day 218 - Text Preprocessing and Tokenization

## Common Issues
1. **Unseen character produces key error:**
   - Cause: Missing `<unk>` fallback in vocabulary lookup.
   - Fix: Use `vocab.get(token, vocab["<unk>"])`.
