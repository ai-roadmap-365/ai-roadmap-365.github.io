# Troubleshooting: Day 269 - RAG over PDFs and Messy Documents

## Common Issues
1. **Zero scores on BM25:**
   - Cause: Query tokens do not match document tokens.
   - Fix: Normalize text using regex word extraction and lowercasing.
