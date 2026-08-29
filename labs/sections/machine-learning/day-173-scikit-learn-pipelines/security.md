# Security and Privacy Notes for Day 173

- **Pickle / Joblib Serialization Security:** Loading untrusted `.pkl` or `.joblib` pipeline files allows arbitrary remote code execution. Only deserialize pipeline artifacts from cryptographically signed, authenticated artifact repositories.
- **Local Sandbox:** All pipelines execute locally on CPU.
