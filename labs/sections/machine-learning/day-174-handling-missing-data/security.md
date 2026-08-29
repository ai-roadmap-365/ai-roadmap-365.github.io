# Security and Privacy Notes for Day 174

- **MNAR Missingness Signal Privacy:** In healthcare datasets, the fact that a diagnostic test is missing (`MissingIndicator = 1`) often leaks critical private information about patient health status. Ensure missing indicator features comply with HIPAA/GDPR anonymization.
- **Local Sandbox:** All imputation routines execute locally on CPU.
