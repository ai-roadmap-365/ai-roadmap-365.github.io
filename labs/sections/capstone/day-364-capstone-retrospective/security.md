# Security notes — Day 364

## What this lab does and does not touch

- **No network.** The input is a recorded list of tasks and incidents. Nothing is fetched.
- **No credentials.** No API key, token or account.
- **No writes outside this directory.** Only `__pycache__/`, `.pytest_cache/` and, if you create it, `.venv/`.
- **No `sudo`, no global installs.**
- **The example record is fictional.** The task names and incidents are representative of a capstone rather than drawn from any real project.

## A retrospective is a document about incidents

That is the security point of the day, and it is easy to miss because a retrospective feels like process rather than infrastructure.

The findings you are producing describe, in order: what your system got wrong, which controls were missing, and how long the gap stayed open. That is a useful document for you and a useful document for somebody attacking the system. Three consequences worth holding:

- **Describe the incident, do not reproduce it.** "Answers cited nothing after an index rebuild" is a finding. Pasting the offending answer, the prompt that produced it, or the document it should have cited puts user content into a file that may be published.
- **A recorded incident may contain personal data.** If a user reported it, their report may quote their own query. Summarise it; do not carry it forward verbatim into a public write-up.
- **An unfixed finding is a disclosed weakness.** "A per-request cap would have caught it" says plainly that there is currently no per-request cap. If the retrospective is going to be public — in a portfolio, say — either fix the gap first or describe it at a level that does not amount to instructions.

## Blamelessness is a data-quality control, not only a kindness

A review that names individuals produces defensive accounts, and defensive accounts are inaccurate ones. If the record you are analysing was gathered in an environment where an honest answer carries a cost, the estimates and incident reports in it are already distorted and no amount of arithmetic recovers them. This matters for a team retrospective more than a solo one, and it is worth stating before the numbers are collected rather than after.

## Reversing everything this lab did

```bash
rm -rf __pycache__ .pytest_cache .venv
```

Nothing else was created, and nothing outside this directory was modified.
