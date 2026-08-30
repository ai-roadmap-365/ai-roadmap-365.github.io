# Troubleshooting: Day 230 - Hugging Face Transformers in Practice

## Common Issues
1. **Pad token id confusion:**
   - Cause: Using default pad token 0 when model expects different id.
   - Fix: Use `tokenizer.pad_token_id`.
