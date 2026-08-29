# Troubleshooting Fairness Audits

## 1. Tradeoffs under the Impossibility Theorem
When base rates $P(Y=1|A=a)$ differ between demographic groups, you cannot satisfy Equalized Odds and Predictive Parity simultaneously. Engage legal and compliance teams to select the appropriate metric for your domain.

## 2. Small Sample Subgroups
Fairness metrics evaluated on small demographic subsets ($N < 50$) have high statistical variance. Use bootstrap confidence intervals to evaluate fairness differences.
