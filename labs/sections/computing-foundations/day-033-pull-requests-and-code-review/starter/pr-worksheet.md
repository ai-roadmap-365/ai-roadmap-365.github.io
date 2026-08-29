# Pull-request worksheet — Day 033

Fill this in for the change you made in the hands-on exercise. It is the same
thing you would type into the description box of a real pull request. Keep it
when you are done — a clear description you can point to is worth more than any
advice about writing one.

---

## 1. Pull-request description

Write it exactly as you would on a hosting platform.

**Title** (one line, imperative, under ~60 characters):

> _e.g. "Add greeting line to course notes"_

**Description** (what the change does and, crucially, *why*):

> _2–4 sentences. What did you change? Why was it needed? What problem does it
> solve or what does it add?_

**How I verified it** (tests, manual checks, the diff you read):

> _e.g. "Ran the script; git diff main..feature shows only the intended line;
> the merge produced a clean merge commit with no conflicts."_

---

## 2. What the diff shows

Paste the output of `git diff main..feature` (or list the files and the exact
lines it touched):

```text
_paste git diff main..feature here_
```

Files touched: _______________________________________________

Lines added / removed: ________________________________________

---

## 3. Merge strategy

Which strategy did you use to bring `feature` into `main`?

- [ ] Merge commit (`git merge --no-ff`)
- [ ] Squash and merge (`git merge --squash`)
- [ ] Rebase and merge

**Why this strategy fit this change** (2–3 sentences):

> _e.g. "I used a merge commit so the review-and-revise history — the original
> commit plus the 'addressed feedback' commit — stays visible in main." OR
> "I squashed because the two 'wip' commits were noise and I wanted one tidy,
> revertible commit on main."_

---

## 4. Reflection (optional but recommended)

In one or two sentences: what would a reviewer most likely comment on if this
were a real pull request, and how would you respond?

> _______________________________________________________________
