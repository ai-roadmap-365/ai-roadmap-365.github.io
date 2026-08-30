# Security notes — Day 362

## What this lab does and does not touch

- **No network.** The subject is README text and a project description. Nothing is fetched, and no test opens a socket.
- **Nothing is executed.** The checker reads documentation and compares it against recorded facts. It never runs a documented command, which is deliberate — see the extension exercise for the trade-off.
- **No credentials.** No API key, token or account.
- **No writes outside this directory.** Only `__pycache__/`, `.pytest_cache/` and, if you create it, `.venv/`.
- **No `sudo`, no global installs.**

## Documentation is a disclosure surface

Worth stating plainly, because documentation rarely gets a security review of its own. Four things leak through READMEs routinely:

- **Example configurations with real values.** A hostname, a bucket name, an internal service address. Use placeholders that are obviously placeholders — `example.com`, `<your-api-key>` — rather than a real value with a character changed.
- **Architecture sections naming internal systems.** Useful to a reader and useful to someone mapping your infrastructure. Describe the shape without the inventory.
- **Troubleshooting sections quoting real errors.** A pasted stack trace or error response can carry a token, a path, a user identifier or an internal hostname. Redact before pasting.
- **Screenshots and terminal recordings.** These capture whatever was on screen, including environment variables in a shell prompt and other windows. `asciinema` records text, which at least makes the content greppable before publishing.

The recurring pattern: documentation is written quickly and reviewed for clarity rather than for content. Give it the same read you would give a log line.

## A demo published against real data publishes that data

If the demo corpus is real support tickets, real customer documents or a real inbox, then recording the demo distributes them. Use a fixture corpus you own and can publish. This is the same argument as Day 328 — data multiplies, and a recording is another copy nobody tracks.

## Why this checker does not execute anything

Running the documented commands would catch more drift, and it would also mean a documentation gate that executes arbitrary strings extracted from a Markdown file. In this lab that is safe because the fixtures are fixed. In a real pipeline running commands parsed out of a document is a code-execution path, and it needs the same care as any other: a sandbox, no credentials, and no network.

The extension exercise asks you to build it and measure the false-failure rate, which is the honest way to decide whether it belongs in a pipeline.

## Reversing everything this lab did

```bash
rm -rf __pycache__ .pytest_cache .venv
```

Nothing else was created, and nothing outside this directory was modified.
