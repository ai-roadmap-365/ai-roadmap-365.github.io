# Security notes — Week 52 project

## What this project does and does not touch

- **No network.** The input is a declared delivery — a list of requirements and the evidence offered for each. Nothing is fetched and no command in the fixture is executed.
- **No credentials.** No API key, token or account.
- **No writes outside this directory.** Only `__pycache__/`, `.pytest_cache/` and, if you create it, `.venv/`.
- **No `sudo`, no global installs.**
- **The example delivery is fictional**, and its URLs use `example.com`, a domain reserved by RFC 2606.

## The gate does not run the commands, and that is on purpose

`Kind.COMMAND` records that a command exists and was run on a date. This module never executes it.

That is a deliberate limitation rather than an oversight. A delivery manifest is a document, frequently written by somebody else, and a tool that executed arbitrary strings out of one would be a straightforward code-execution vector — a hostile manifest becomes a hostile shell. If you extend this to actually run the commands, run them in a sandbox, on an allowlist, and never on a manifest you did not write.

The consequence is that the gate checks whether the evidence is *of a checkable kind*, not whether the check passes. A human still has to run it. That is the correct division: the tool catches the requirement nobody produced evidence for, which is the failure that actually happens.

## The two requirements in the fixture that are security requirements

**A hard spend cap.** Missing in the demo, and missing in most real deliveries, because there is no document it naturally lives in. An agent with a retry loop and no cap is the most common expensive accident in this field.

**No secrets in repository history.** Stale in the demo — verified 78 days and an unknown number of commits ago. This is the one whose failures are permanent: making a repository public exposes every commit, so a key removed months ago is still there. Re-run `gitleaks` over the history immediately before flipping visibility, not after.

## A delivery manifest is a map of what is not finished

Once it lists "no spend cap" and "security review is only a document", it is an accurate description of where your system is weak. Keep it in the private repository, or fix the gaps before publishing it.

## Reversing everything this project did

```bash
rm -rf __pycache__ .pytest_cache .venv
```

Nothing else was created, and nothing outside this directory was modified.
