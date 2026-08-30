# Security notes — Day 329

## What this lab does and does not touch

- **No network.** Everything is in-process. No test opens a socket.
- **No credentials.** No API key, token or account.
- **No writes outside this directory.** Only `__pycache__/`, `.pytest_cache/` and, if you create it, `.venv/`.
- **No `sudo`, no global installs.**
- **No real personal data.** The single identifier in the fixtures uses `example.com`, a domain reserved by RFC 2606.

## An auditor is a security control, and it needs its own evidence

The checks here encode three properties that are security or privacy properties rather than functional ones:

- **`redaction_before_indexing`** — identifiers inside embeddings can only be removed by re-embedding, so this ordering determines whether a future incident is a config change or a corpus rebuild.
- **`shared_budget`** — a paid stage with separate accounting is a path the spend cap does not bound, which is how unbounded consumption gets in.
- **`erasure_is_complete`** — a deletion that reaches some stores and not others leaves a system able to answer from content someone had a right to have removed.

The important design decision is the `BrokenAssistant`. A checker that has never failed anything provides no assurance: it may be correct, or it may be checking nothing. Planting known defects and asserting that the audit finds **exactly** those — no fewer, and no more — is what makes the auditor's own passing result meaningful.

That is worth generalising. Any test that guards a security property should have a companion proving it fails when the property is violated, or it is decoration.

## What this lab does not do

It does not sandbox anything, and it audits an in-process object rather than a running service. A real conformance harness would run against a deployed system, which brings authentication, rate limits and test-data handling with it — all of which are out of scope here and none of which change the checks themselves.

## Reversing everything this lab did

```bash
rm -rf __pycache__ .pytest_cache .venv
```

Nothing else was created, and nothing outside this directory was modified.
