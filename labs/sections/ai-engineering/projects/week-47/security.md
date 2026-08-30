# Security notes — Week 47 project

## What this project does and does not touch

- **No network.** The corpus, the retrieval index and the model are all simulated in-process. No test opens a socket.
- **No credentials and no spend.** `requires_api_key` is `false`. Running the project costs nothing.
- **No writes outside this directory.** Only `__pycache__/`, `.pytest_cache/` and, if you create it, `.venv/`.
- **No `sudo`, no global installs.**
- **No real personal data.** The only identifiers in the fixture use `example.com`, a domain reserved by RFC 2606, and a phone number in the UK reserved-for-drama `07700 900xxx` range.

## The three controls this project assembles, and why each is a security property

**Redaction before indexing.** Ordering is the control. Redact after chunking and the identifiers are inside the embeddings, at which point removing them requires re-embedding the corpus — an expensive remediation that teams defer, which means the exposure persists. Doing it at the boundary makes the derived stores clean by construction.

**A spend cap checked before the call.** Unbounded spend is an availability and abuse risk, not just a budgeting one. Anything a user can trigger, an attacker can trigger repeatedly. Charging retrieval to the same ledger matters here: a system that caps generation but not retrieval has an uncapped path.

**Verified erasure across every store.** The index, the content hashes and the response cache each hold data derived from a document. A deletion that reaches two of three leaves the system able to answer from deleted content, and reports success while doing so. The read-back is what converts an intention into evidence.

Note the interaction the tests cover: clearing the content hash is part of the erasure, not housekeeping. Leave it and a later re-ingest sees the document as unchanged and never restores it — a deletion that quietly becomes permanent in a way nobody chose.

## What a real deployment would add

- **Tenant partitioning** in the index and the cache, so a cache key collision cannot serve one tenant's answer to another.
- **A sandbox for extraction**, since real parsers consume untrusted input.
- **Retention policies per store**, particularly for traces, which typically hold full prompts and are kept longest.
- **A salt held apart from the data**, since the pseudonyms here use a fixed default for reproducibility.

## Reversing everything this project did

```bash
rm -rf __pycache__ .pytest_cache .venv
```

Nothing else was created, and nothing outside this directory was modified.
