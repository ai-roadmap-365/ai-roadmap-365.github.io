# Security and Privacy Notes for Day 170

- **Privacy Inversion in Target Encoding:** High-cardinality target encodings on small rare categories ($n_c = 1$) can reveal exact individual target labels. Enforce minimum sample thresholds ($n_c \ge 5$) or additive differential privacy noise.
- **Local Sandbox:** All scalers and encoders run locally on CPU.
