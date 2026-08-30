# Security notes — Day 365

## What this lab does and does not touch

- **No network.** The input is a written plan. Nothing is fetched.
- **No credentials.** No API key, token or account.
- **No writes outside this directory.** Only `__pycache__/`, `.pytest_cache/` and, if you create it, `.venv/`.
- **No `sudo`, no global installs.**
- **The example plan is fictional**, and deliberately typical rather than drawn from anyone's real commitments.

## Keeping the habits when nobody is grading you

This is the last day, and the security point of it is not about this lab. It is that the practices from the past year survive only if they are cheap enough to keep doing without a course telling you to.

Four that are worth the minutes, in rough order of how often skipping them causes real harm:

- **Secret scanning before anything goes public.** Making a repository public exposes every commit, not just the current tree. `gitleaks` over the history takes seconds and is the single highest-value habit on this list.
- **A spend cap on anything that calls a paid API.** Day 327's per-request cap and Day 360's budget alarm. An agent with a retry loop and no cap is the most common expensive accident in this field, and it happens to careful people.
- **Untrusted input stays untrusted.** Day 361's review. Retrieved documents, tool output and user text are data, never instructions, and that does not stop being true because the project is small.
- **A dependency you did not read is a dependency you trusted.** Pin versions, and look at what a new package actually pulls in before it is in your lock file.

If you keep one, keep the first. It is the one whose failures are permanent.

## A learning plan is a personal document

If you publish yours — some people do, and it is a reasonable way to stay accountable — it states your available hours, what you are weak at, and what you are working on. That is unremarkable on its own and worth a moment's thought if your plan names an employer's systems, an unfixed weakness in something you run, or hours that contradict what you have told somebody.

Nothing here needs paranoia. It needs the same read-before-publishing pass as anything else that leaves your machine.

## Reversing everything this lab did

```bash
rm -rf __pycache__ .pytest_cache .venv
```

Nothing else was created, and nothing outside this directory was modified.
