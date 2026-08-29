# Troubleshooting: Day 188 - Recommender Systems

## Common Issues
1. **Gradient Overshoot:**
   - Cause: Using excessive learning rate with unstandardized rating scales.
   - Fix: Use `lr=0.01` and standard L2 regularization `reg=0.05`.
