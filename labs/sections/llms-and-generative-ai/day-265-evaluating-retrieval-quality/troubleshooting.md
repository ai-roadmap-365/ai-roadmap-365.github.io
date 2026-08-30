# Troubleshooting: Day 265 - Evaluating RAG with RAGAS and TruLens

## Common Issues
1. **Empty sentence arrays:**
   - Cause: Consecutive delimiters in text.
   - Fix: Filter out empty strings after regex splitting.
