# Week 28 Project: Section Project -- Deployed ML Service

## Project overview
Train, persist, register, serve, and monitor an enterprise-grade machine learning microservice:
1. **Model Pipeline:** Train a regularized customer churn classifier with stratified cross-validation and subgroup slice verification.
2. **Model Registry & Provenance:** Export weights with cryptographic SHA-256 hashing, semantic versioning (`v1.0.0`), and automated stage promotion (`PRODUCTION`).
3. **REST Serving API:** Host the model behind a low-latency FastAPI service with Pydantic request validation, batch endpoints, and automated circuit-breaker fallback heuristics.
4. **Production Observability:** Implement a real-time Population Stability Index (PSI) drift detector alerting on statistical feature distribution shifts.

## Objectives
- Train a regularized classification pipeline on customer behavioral features.
- Evaluate ROC-AUC and PR-AUC, asserting zero slice regression on key customer segments.
- Compute SHA-256 hash of binary model weights and register in a local provenance catalog.
- Host the model behind a low-latency FastAPI REST service with Pydantic validation.
- Implement real-time drift observability with Population Stability Index (PSI) monitoring.

## Architecture
```
Raw Customer Ingestion -> Train & Validate -> SHA-256 Model Registry -> FastAPI Microservice -> PSI Drift Monitor
```

## Implementation guidelines
1. **Training & Preprocessing:** Train a regularized classification pipeline with stratified cross-validation.
2. **Model Registry:** Store lineage metadata (Git commit SHA, training metrics, dataset hash, stage tag).
3. **FastAPI Serving:** Preload model on startup, validate inputs with Pydantic, and implement `/predict` and `/predict_batch`.
4. **Drift Observability:** Maintain reference quantile bins and trigger alerts when PSI >= 0.20.

## Expected output
```
[Deployed ML Service Verification Suite]
1. Model Training & Cross-Validation:
   - CV ROC-AUC: 0.912 ± 0.014
   - CV PR-AUC: 0.865 ± 0.018
2. Model Registry:
   - Exported model v1.0.0 (SHA-256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855)
   - Promoted to PRODUCTION stage
3. REST Service Benchmark:
   - /predict latency: 1.2 ms (p95)
   - /predict_batch (N=100) latency: 4.8 ms (p95)
4. PSI Drift Monitoring:
   - In-distribution payload: PSI = 0.024 [STABLE]
   - Perturbed drift payload: PSI = 0.318 [ALERT: SEVERE DRIFT]
```

## Validation
To validate your implementation:
1. Confirm that cross-validation achieves ROC-AUC >= 0.88.
2. Verify that SHA-256 cryptographic registration matches the model artifact.
3. Ensure FastAPI endpoints respond with HTTP 200 and schema-valid predictions.
4. Validate that PSI correctly flags synthetic distribution drift.

## Deliverables
- Complete Python training pipeline and model registry module.
- FastAPI service application with Pydantic schemas.
- PSI drift monitor test suite.
