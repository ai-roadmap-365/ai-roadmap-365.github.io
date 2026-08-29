# Security Considerations for Model Diagnostics

## 1. Data Integrity and Synthetic Probing
When evaluating diagnostics with synthetic feature probes, ensure no confidential training rows are exposed in diagnostic log files.

## 2. Leakage in Learning Curve Cross-Validation
Always ensure preprocessing transformers are cloned inside cross-validation splits during learning curve computation to avoid optimistic validation curve artifacts.
