# Security and Privacy Notes for Day 164

- **Gradient Leakage in Collaborative Boosting:** In distributed gradient boosting, raw gradient vectors `r_i = y_i - p_i` expose individual label values `y_i`. Apply differential privacy noise to gradients before federated sharing.
- **Local Execution:** Sequential boosting loops execute deterministically on CPU.
