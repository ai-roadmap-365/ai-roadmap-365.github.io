# Troubleshooting Guide for Day 173

## Common Issues

### 1. `clone()` Fails on Custom Transformer
- **Symptom:** `TypeError: __init__() got an unexpected keyword argument` during `GridSearchCV`.
- **Cause:** Adding `*args` or `**kwargs` to `__init__` or modifying parameter names.
- **Fix:** Follow scikit-learn conventions: every argument in `__init__` must be an explicit keyword argument stored as `self.param_name = param_name` with identical spelling without modification.

### 2. Dimension Mismatch in `ColumnTransformer`
- **Symptom:** `ValueError: all the input array dimensions except for the concatenation axis must match exactly`.
- **Cause:** A branch transformer returned a 1D vector instead of a 2D matrix of shape `(N, D)`.
- **Fix:** Ensure all custom transformer `transform()` methods return 2D NumPy arrays `(N, D)`.
