# Troubleshooting: Day 191 - Building Datasets and Labeling

## Common Issues
1. **Division by Zero in Cohen Kappa:**
   - Cause: All samples belong to a single class making p_e == 1.0.
   - Fix: Return 1.0 early if p_e is close to 1.0.
