# Security Considerations - Day 288
1. **Tool Execution Sandboxing:** The calculator tool uses restricted evaluation scopes (`__builtins__: None`) to prevent arbitrary code execution vulnerabilities.
2. **Loop Exhaustion Protection:** Strict maximum step boundaries ($K \le 10$) prevent denial-of-service and runaway token consumption.
