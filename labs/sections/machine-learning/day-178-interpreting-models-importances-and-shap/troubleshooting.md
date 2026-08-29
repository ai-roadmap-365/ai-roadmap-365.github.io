# Troubleshooting Model Explanations

## 1. Exponential Complexity in Exact Shapley Computation
Exact Shapley values require evaluating $2^D$ feature subsets. For $D > 12$, use TreeSHAP (for trees) or KernelSHAP with Monte Carlo sampling.

## 2. Permutation Importance Correlation Distortion
When features $x_1$ and $x_2$ are highly correlated ($r > 0.9$), permuting $x_1$ creates impossible synthetic data points (e.g. Height=7ft, Weight=50lbs), distorting importance. Cluster correlated features before permuting.
