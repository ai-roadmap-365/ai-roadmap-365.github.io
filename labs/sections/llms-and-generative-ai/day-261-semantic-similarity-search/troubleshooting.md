# Troubleshooting: Day 261 - Semantic Similarity Search

## Common Issues
1. **Dimension mismatch in np.dot:**
   - Cause: Query vector dimension does not match corpus matrix dimension.
   - Fix: Assert query_vec.shape[0] == self.dimension before dot products.
