# Security and Privacy Notes for Day 155

- **Local Execution:** All code runs entirely in offline memory with zero outbound network calls.
- **Synthetic & Standard Datasets:** The lab uses `sklearn.datasets.load_breast_cancer` (a public de-identified dataset) and synthetic vectors.
- **Filesystem Safety:** The lab creates no persistent files outside its own directory.
