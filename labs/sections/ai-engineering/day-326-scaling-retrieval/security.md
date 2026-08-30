# Security notes — Day 326

## What this lab does and does not touch

- **No network.** Vectors are generated in-process from a seeded pseudo-random generator. No test opens a socket, and `requires_network` is `false`.
- **No credentials.** No API key, token or account anywhere.
- **No writes outside this directory.** Only `__pycache__/`, `.pytest_cache/` and, if you create it, `.venv/`.
- **No `sudo`, no global installs.**
- **No unbounded memory.** The corpus is 2,000 vectors of 32 dimensions — a few megabytes.

## What real approximate indexes raise, which this lab deliberately simulates

An ANN index is a shared data structure, and that creates problems a flat list does not have:

- **Multi-tenant leakage.** If tenants share an index, one tenant's vectors can sit inside a list another tenant's query probes. Filtering *after* retrieval is not sufficient: the candidate set was already computed across the boundary, and timing differences can be observable. Partition by tenant, or apply the filter during traversal rather than afterwards.
- **Deletion is not removal.** Graph indexes such as HNSW commonly tombstone a deleted vector rather than removing it, and the data remains in the structure until a compaction runs. For a right-to-erasure request that is not enough — the obligation is to delete, not to hide. Check what your index actually does rather than assuming, and confirm that compaction has run.
- **Rebuilds copy everything.** An index rebuild materialises a second full copy of the vectors, often on disk. That copy inherits the same access-control and retention obligations as the original, and is easy to forget.

## Privacy

Embeddings are derived from content and are not anonymous: inversion attacks can recover meaningful information about the source text from a vector. Treat an embedding store with the same care as the documents it was built from, not as a harmless numeric artefact.

## Reversing everything this lab did

```bash
rm -rf __pycache__ .pytest_cache .venv
```

Nothing else was created, and nothing outside this directory was modified.
