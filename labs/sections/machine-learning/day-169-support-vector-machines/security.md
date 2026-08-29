# Security and Privacy Notes for Day 169

- **Privacy Vulnerability in Dual SVMs:** The fitted dual model stores the raw feature vectors of all support vectors in memory (`model.support_vectors_`). If deployed client-side, proprietary training records could be extracted.
- **Local Sandbox:** All SVM solvers run locally on CPU.
