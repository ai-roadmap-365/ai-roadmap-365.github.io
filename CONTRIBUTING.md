# Contributing

Thank you for reading this. The most valuable contribution to this project is
not a pull request — it is **telling me where the course is wrong**.

## The single most useful thing you can do

Run a lab. If its output does not match what the lesson says it will, open an
issue with:

- the day number,
- the command you ran,
- what you expected (quote the line from the lesson),
- what you actually got (paste it),
- your OS and `python3 --version`.

Every captured output in this course came from a real run on one machine on
one day. That is the standard the course holds itself to — and it is exactly
why your machine disagreeing with it is worth knowing about. A lesson that
quotes a number nobody can reproduce is a lesson with a bug.

## What makes a good issue

| Kind | What to include |
| --- | --- |
| **A lab does not run** | Day number, exact command, full error, OS, Python version |
| **Output does not match** | Both texts, side by side |
| **A fact looks wrong** | The claim, and the source you think contradicts it |
| **Something is unclear** | Which paragraph, and what you thought it meant |
| **A link is broken** | Where it is, and where it should go |

"A fact looks wrong" is genuinely welcome, including on history and dates. If
a claim cannot be verified, the right fix is to remove it, and I would rather
hear it from you than leave it standing.

## What makes a good pull request

Small and specific. A typo, a broken link, a clearer sentence, a lab fix for
an OS I could not test on — all straightforward to review and merge.

Before opening one:

```bash
npm install
npm run verify:all      # all 24 gates must pass
```

If you touched a lab, run its own tests too:

```bash
cd labs/sections/<section>/day-<nnn>-<slug>
bash tests/run_tests.sh   # must print "N checks, 0 failure(s)" and exit 0
```

### Rules the validators enforce, so you find out early

- **No placeholder text.** A dozen markers ("coming soon", "to be added", and
  similar) fail the build wherever they appear.
- **No invented output.** Anything shown as captured must come from a real
  run. If you cannot run it, say so in the prose rather than approximating.
- **No fabricated sources, versions or prices.** Cite what you checked, and
  link it in that day's `sources.yml`.
- **Alt text on every diagram**, matching `visuals.yml` exactly, with no `]`
  in it — a closing bracket ends markdown image syntax and breaks the image.
- **Relative links inside the repository.** Only the blog column is absolute,
  and it is generated from configuration.

### Writing a whole day

Please open an issue first so we can agree the scope — a day is a substantial
piece of work (a lesson of several thousand words, two diagrams, a lab with a
real test harness, captured output, and an instructor solution). The contract
is in `scripts/lib/contracts.mjs`; the quality standard is
`context/quality-bar.md`; the reference implementation is Day 001.

## Style

- Second person, present tense, plain words. Define every term at first use.
- Prefer a worked example over an assertion, and a measurement over an
  adjective.
- When the evidence contradicts the common wisdom, say so and show the
  measurement. Several lessons in this course exist in their current form
  because a test disagreed with the textbook.

## Code of conduct

By participating you agree to the [Code of Conduct](CODE_OF_CONDUCT.md).

## Licence

Contributions are accepted under the repository's licences: MIT for code,
CC BY-NC-SA 4.0 for course content. See [LICENSE](LICENSE).
