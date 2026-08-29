# Troubleshooting Learning Curves

## 1. Flat Learning Curves
If validation score does not increase as training size increases, the model has hit a High Bias ceiling. Increasing dataset size will not improve performance; add features or increase model capacity.

## 2. Inverted Learning Curves (Train Score Below Validation)
Can occur when heavy regularization (e.g. Dropout, large L2 weight decay) is applied during training but disabled during validation evaluation.
