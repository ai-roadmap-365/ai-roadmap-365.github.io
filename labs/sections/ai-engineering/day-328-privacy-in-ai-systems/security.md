# Security notes — Day 328

## What this lab does and does not touch

- **No network.** Nothing leaves the machine — the correct property for a lab about personal data. No test opens a socket.
- **No credentials.** No API key, token or account.
- **No writes outside this directory.** Only `__pycache__/`, `.pytest_cache/` and, if you create it, `.venv/`.
- **No `sudo`, no global installs.**
- **No real personal data.** Every identifier in the fixtures is synthetic and invalid by construction: `example.com` is reserved by RFC 2606, `192.0.2.0/24` is the TEST-NET-1 range reserved by RFC 5737 for documentation, and the card number fails the Luhn check so it cannot correspond to a real card.

## The salt is a secret

`pseudonym` takes a salt with a default value so the lab is reproducible. In production that default would be a serious weakness.

The value spaces here are small. There are roughly ten billion possible national identifiers of the form used in the fixture, and far fewer plausible phone numbers in any one country. An attacker with an unsalted token can hash the entire space and build a reverse lookup — the pseudonym becomes the identifier again, at the cost of an afternoon of compute.

A salt defeats that precomputation, which means:

- **Store it apart from the data it protects.** A salt in the same database as the pseudonyms protects nothing against whoever reads that database.
- **Rotating it is expensive.** Every existing pseudonym changes, so historical records stop linking. Choose it deliberately.
- **It is not a password hash.** For pseudonymisation you want speed and stability; for credentials you want a slow, memory-hard function such as Argon2. Do not confuse the two use cases.

## What this lab deliberately does not claim

**Pseudonymised is not anonymised.** The output is still personal data under the GDPR and comparable regimes, because the mapping remains reconstructible by someone holding the salt. Describing a pseudonymised dataset as anonymous is a category error with legal consequences.

**Pattern detection is not complete.** These detectors catch structured identifiers. They do not catch a person's name in free text, an unusual job title, or a combination of ordinary attributes that identifies one individual — Sweeney's result. Extension exercise 3 measures that gap rather than assuming it away.

**Embeddings are in scope.** Inversion attacks recover meaningful content from vectors, so a vector index derived from personal data is itself a store of personal data and inherits the same deletion obligations.

## Reversing everything this lab did

```bash
rm -rf __pycache__ .pytest_cache .venv
```

Nothing else was created, and nothing outside this directory was modified.
