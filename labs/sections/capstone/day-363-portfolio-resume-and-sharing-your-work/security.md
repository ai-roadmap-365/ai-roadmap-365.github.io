# Security notes — Day 363

## What this lab does and does not touch

- **No network.** Evidence links are judged from the string rather than fetched. No test opens a socket.
- **No credentials.** No API key, token or account.
- **No writes outside this directory.** Only `__pycache__/`, `.pytest_cache/` and, if you create it, `.venv/`.
- **No `sudo`, no global installs.**
- **The example claims are fictional**, and the URLs use `example.com`, a domain reserved by RFC 2606.

## A portfolio is a permanent public disclosure

This is the security point of the day, and it is easy to skip past because a portfolio does not feel like infrastructure.

Once published, it is copied, cached, indexed and forked. Deleting it later removes your copy and none of the others. Four things leak this way routinely:

- **Secrets in repository history.** Making a private repository public exposes every commit, not just the current tree. A key removed six months ago is still there. Run `gitleaks` or `trufflehog` over the **history** before flipping visibility, not after.
- **Screenshots.** They capture whatever was on screen — a token in a shell prompt, an internal hostname in a browser tab, another window. Crop deliberately and look at what remains.
- **Demo recordings.** Same problem, over a longer window. A terminal recording that captures text rather than pixels at least lets you read it before publishing.
- **Real data in a demo corpus.** Publishing the demo publishes the corpus. Use fixtures you own.

## Work you may not be free to publish

Work done for an employer is frequently not yours to release, and the constraint is contractual rather than technical. Two routes that keep you on the right side of it:

- **Describe without publishing.** A claim can be specific, measured and attributed without the artefact being public. The evidence check will grade it weak, and that is the correct outcome — the reader genuinely cannot verify it, and pretending otherwise helps nobody.
- **Rebuild it on your own time**, on public data, as a comparable thing you can publish.

What not to do is publish it anyway and hope. That decision is discoverable, permanent, and says something about you that no portfolio recovers from.

## A hosted demo is an exposed endpoint

If you host a live demo, it is a public service with everything that implies: it can be scraped, abused and made expensive. If it calls a paid API, put a hard cap on it — Day 327's exercise — or ship a recording instead, which costs nothing and cannot be abused.

## Reversing everything this lab did

```bash
rm -rf __pycache__ .pytest_cache .venv
```

Nothing else was created, and nothing outside this directory was modified.
