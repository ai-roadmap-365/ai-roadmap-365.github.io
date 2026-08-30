# Troubleshooting: Day 223 - Text Classification with Embeddings

## Common Issues
1. **Dimension error in Conv1d:**
   - Cause: Passing `(Batch, Seq_Len, Dim)` instead of `(Batch, Dim, Seq_Len)`.
   - Fix: Use `.permute(0, 2, 1)`.
