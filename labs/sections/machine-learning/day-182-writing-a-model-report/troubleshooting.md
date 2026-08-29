# Troubleshooting Model Reports

## 1. Empty Quantitative Slice Tables
A Model Card that omits subgroup slice metrics violates the Mitchell et al. (2019) standard. Always include quantitative performance broken down across at least two demographic/operational dimensions.

## 2. Inconsistent Versioning
Link the Model Card directly to the Git commit hash and Model Registry URI (e.g. MLflow/W&B Run ID) of the trained model artifact.
