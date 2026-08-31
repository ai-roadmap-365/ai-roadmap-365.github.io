# Week 50 Capstone Project: AI Security Review Platform

## Project Overview
Build an end-to-end production AI Security Review Platform in Python. This comprehensive system unifies all Section 08 security disciplines:
1. **Threat Modeling & DREAD Scoring:** Systematic vulnerability decomposition across STRIDE and OWASP Top 10 for LLMs.
2. **Prompt Defense Firewall:** Heuristic jailbreak detection, XML delimiter escaping, and session canary token injection.
3. **Zero-Knowledge PII Token Vault:** In-memory entity de-identification with reversible detokenization and GDPR key erasure.
4. **Model Supply Chain Security:** SafeTensors verification, SHA256 checksumming, and CycloneDX-AI bill of materials (AIBOM) generation.
5. **Automated Adversarial Red Teaming:** Multi-turn probe execution and Attack Success Rate (ASR) quantification.

## Architecture

```text
[Client Request Ingress]
           │
           ▼
[AI Security Gateway Proxy]
  ├── Heuristic Prompt Firewall (Jailbreak Scanner)
  ├── Zero-Knowledge PII Token Vault (SSN/Email Sanitizer)
  └── Context Enclosure (XML Escaping + Canary Token)
           │
           ▼
[Hardened Serving Layer (SafeTensors + ModelScan AST)]
           │
           ▼
[Egress Inspection (Canary Monitor + Detokenizer)]
           │
           ▼
[Executive Security Audit Engine & ASR Evaluator]
```

## File Structure
- `starter/ai_security_review.py`: Starter implementation skeleton
- `examples/ai_security_review.py`: Verified reference implementation
- `tests/test_ai_security_review.py`: Test suite
- `expected-output/`: Captured execution logs
- `requirements/requirements.txt`: Project dependencies

## How to run
```bash
python3 examples/ai_security_review.py
```

## Expected output
```text
AI Security Review Platform Ready.
```

## Validation
Run test runner:
```bash
bash tests/run_tests.sh
```

## Verification Checklist
- [x] Correct STRIDE and DREAD risk calculations
- [x] In-memory PII sanitization and reversible detokenization
- [x] Prompt injection heuristic blocking and XML tag escaping
- [x] Outbound canary token exfiltration dropping
- [x] SafeTensors supply chain verification and AIBOM generation
- [x] Automated red teaming test execution achieving 0.0% ASR
- [x] Passing all 5 comprehensive unit tests
