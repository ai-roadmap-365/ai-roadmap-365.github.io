# Troubleshooting: Day 194 - Serving a Model over an API

## Common Issues
1. **Dimension Mismatch in Forward Pass:**
   - Cause: Input feature length does not match weight vector length.
   - Fix: Align feature ordering with weight array dimensionality.
