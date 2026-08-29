# Security Considerations for Error Analysis

## 1. Targeted Adversarial Slices
Adversaries target unmonitored feature slices where model accuracy drops below 50% to execute evasion attacks. Always audit slice-based performance across rare inputs.

## 2. Privacy Leakage in Error Logs
When logging misclassified user inputs for manual human auditing, redact all PII (names, SSNs, credit card numbers) before writing to annotation databases.
