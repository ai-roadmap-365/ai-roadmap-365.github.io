# Security notes — Day 324

## What this lab does and does not touch

- **No network.** The corpus is eight synthetic in-memory documents. No test opens a socket, and `requires_network` is `false`.
- **No credentials.** No API key, token or account anywhere.
- **No writes outside this directory.** Only `__pycache__/`, `.pytest_cache/` and, if you create it, `.venv/` — all inside this lab and all removable with the documented cleanup.
- **No `sudo`, no global installs.**
- **Child processes are cleaned up.** Extraction runs in a `multiprocessing` child marked `daemon=True` and is explicitly terminated on timeout, then joined. No worker outlives the run.

## Why extraction runs in a child process, and why that matters beyond this lab

The budget in this lab exists to stop a synthetic sleep. In production the same mechanism is a genuine security control:

- **Document parsers are a real attack surface.** They are typically complex C libraries consuming fully untrusted input, and they have a long history of memory-safety vulnerabilities. Decompression bombs, deeply nested structures and malformed cross-reference tables are all used in practice.
- **A process boundary is what makes a limit enforceable.** A thread cannot be killed, so a cooperative timeout only works on code that cooperates — which excludes exactly the inputs you are defending against. An earlier version of this lab used a thread pool and the 30-second sleep blocked the whole run.
- **In production, add a memory ceiling too** (`resource.setrlimit` in the child), and prefer a sandbox where one is available. Extension exercise 3 covers the memory half.
- **Never let a parser fetch remote resources** referenced by the document. That turns document processing into a server-side request forgery primitive.

## Privacy

Extraction is the point where document contents become plain, greppable text — so it is the right stage for redaction, and the stage where sending content to a third-party OCR or document-intelligence API becomes a data-residency decision rather than a technical one. This lab sends nothing anywhere.

## Reversing everything this lab did

```bash
rm -rf __pycache__ .pytest_cache .venv
```

Nothing else was created, and nothing outside this directory was modified.
