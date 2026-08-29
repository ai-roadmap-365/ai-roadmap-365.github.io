# Security Considerations in Model Interpretability

## 1. Model Inversion and Reconstruction
Detailed local explanations (like exact SHAP feature attributions) can be exploited by adversaries to reconstruct confidential training features or reverse-engineer proprietary decision logic.

## 2. Explanation Manipulation and Scaffolding
Adversaries can design scaffolding wrappers that display benign SHAP attributions while the underlying model uses biased or forbidden demographic proxy features. Always audit models end-to-end.
