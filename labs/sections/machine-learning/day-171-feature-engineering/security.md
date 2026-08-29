# Security and Privacy Notes for Day 171

- **Differential Privacy in Group Statistics:** Small groups ($N < 5$) can leak private individual values through aggregate mean features. Enforce group size minimums ($N \ge 10$) or apply differential privacy noise.
- **Local Sandbox:** All feature engineering transformations execute locally on CPU.
