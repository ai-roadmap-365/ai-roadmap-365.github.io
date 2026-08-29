# Security and Privacy Notes for Day 163

- **Model Serialisation Security:** Random Forest models contain dozens to hundreds of tree structures. Persist with safe serialization formats (`treelite` or validated ONNX) rather than untrusted `pickle` files.
- **CPU Parallelism:** Bagged trees train independently (`embarrassingly parallel`) across CPU cores without network communication.
