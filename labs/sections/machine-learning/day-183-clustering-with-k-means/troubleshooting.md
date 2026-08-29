# Troubleshooting: Day 183 - Clustering with k-means

## Common Issues
1. **Centroids Diverging / NaN Values:**
   - Cause: A cluster lost all assigned samples during the E-step, causing division by zero in mean calculation.
   - Solution: In the maximization step, check `if np.sum(mask) > 0:` before taking `np.mean`. If zero, reset the centroid to a random point.
