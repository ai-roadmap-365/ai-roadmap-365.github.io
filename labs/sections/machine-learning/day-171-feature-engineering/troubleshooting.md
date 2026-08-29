# Troubleshooting Guide for Day 171

## Common Issues

### 1. Data Leakage in Group Aggregations
- **Symptom:** Validation scores are unrealistically high because test target averages were included in group statistics.
- **Cause:** Calculating `df.groupby('user_id')['amount'].transform('mean')` on the combined train+test DataFrame.
- **Fix:** Always calculate group statistics on training splits only and map onto test splits with fallback global statistics for unseen groups.

### 2. Cyclical Boundary Discontinuity
- **Symptom:** Model predicts abrupt discontinuous shifts between 23:59 and 00:01.
- **Cause:** Using raw linear integers (`0 to 23`) for hours. The algorithm treats 23 and 0 as maximum distance (23 units apart).
- **Fix:** Use 2D Sine and Cosine coordinate encoding `(sin(2 pi t / 24), cos(2 pi t / 24))`.
