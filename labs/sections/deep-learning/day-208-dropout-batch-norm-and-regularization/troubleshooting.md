# Troubleshooting: Day 208 - Dropout, Batch Norm, and Regularization

## Common Issues
1. **Validation accuracy drops drastically:**
   - Cause: Forgetting to call `model.eval()` before validation loop.
   - Fix: Always wrap validation code in `model.eval()` and `with torch.no_grad():`.
