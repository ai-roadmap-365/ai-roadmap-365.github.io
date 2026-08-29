# Security & Ethical Governance in Algorithmic Fairness

## 1. Protected Attribute Retention vs Privacy
Auditing fairness requires collecting demographic attributes (gender, race, age). Store sensitive attributes in encrypted, access-restricted vaults separate from general feature stores.

## 2. Proxy Feature Circumvention
Excluding protected features from training data does NOT prevent algorithmic bias because other features (e.g. zip codes, education, purchasing habits) act as strong redundant proxies.
