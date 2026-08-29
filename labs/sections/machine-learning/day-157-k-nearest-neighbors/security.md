# Security and Privacy Notes for Day 157

- **Data Retention in Memory:** KNN is an instance-based model that retains the entire training dataset in memory at inference time. In privacy-sensitive applications, querying the model or extracting its nearest neighbors can expose raw user data.
- **Local Sandbox:** Lab runs entirely in offline memory with no network communication.
