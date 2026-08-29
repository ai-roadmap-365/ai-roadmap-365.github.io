# Your brief — build the acceptance harness

Course 03 taught a dozen separable skills. A study is what happens when they
have to hold each other up, and the thing that breaks is never a single skill.
It is the seams: a clean dataset with an unstated question, a beautiful chart
of a leaked feature, a confident conclusion drawn from an exploration that
examined forty things. Every component correct, the study worthless.

You are building the checker that finds those seams. `check_study(path)` reads
a study directory and returns a verdict: eight gates, each passing or carrying
findings that name exactly what is missing.

## What you are given

| File | What it is |
| --- | --- |
| `dataset.py` | The synthetic source frame, with four deliberate defects and one real planted effect. Complete — do not edit. |
| `study.py` | The worked miniature study: question, provenance, ingestion, cleaning, split, figures, estimate, report, manifest. Complete — do not edit. |
| `fixtures.py` | Deliberately broken copies of that study, one defect at a time. Complete — do not edit. |
| `acceptance.py` | **Your work.** The verdict types, the file readers and the four Markdown parsers are given. The nine exercises are yours. |
| `test_starter.py` | Your running score. |

Build the worked study yourself first, so you can read what you are grading:

```bash
.venv/bin/python3 -c "
import sys; sys.path.insert(0, 'starter')
import fixtures, pathlib
print(fixtures.worked_study(pathlib.Path('/tmp/day140-look')))
"
```

Read `QUESTION.md`, `SOURCE.json`, `INGEST.json`, `CLEANING.md`,
`RESEARCH_LOG.md`, `FIGURES.json`, `REPORT.md` and `MANIFEST.json`. Ten
minutes there will save you an hour in the exercises. Delete the directory
afterwards.

## The nine exercises

Each one lives in `acceptance.py` with a docstring stating exactly what it
must accept and reject. Check yourself after each:

```bash
.venv/bin/pytest starter -q
```

1. **`gate_question_recorded`** — fail a study whose question file is missing
   or empty, naming it.
2. **`gate_provenance_complete`** — fail a source record lacking a URL,
   retrieval date or checksum, and name which. Recompute the checksum.
3. **`gate_grain_asserted`** — fail an ingestion with no row-grain assertion;
   pass one that states a grain and records that it was verified.
4. **`gate_damage_report_quantified`** — fail a cleaning step documented
   without a before/after measurement. A changelog is not a damage report.
5. **`gate_confirmation_untouched`** — detect a study whose confirmation split
   was used during exploration, by checking the research log's ordering
   against the split's first use.
6. **`gate_uncertainty_reported`** — fail a reported estimate with no
   interval, and name the sentence.
7. **`gate_figures_documented`** — fail an unlabelled figure, pass a
   documented one, and catch a figure file no record mentions.
8. **`gate_outputs_reproducible`** — detect a study whose output changed
   between runs, by recomputing every manifest digest.
9. **`check_study`** — run all eight, never stopping at the first failure, and
   return the verdict.

## Three rules the tests enforce

**Every finding names something.** "Provenance incomplete" is useless at 23:00
the night before a deadline. "SOURCE.json is missing: checksum_sha256" is a
task. Exercise 6 goes further and quotes the sentence, because on a
twelve-page report the filename is a re-read and the sentence is a fix.

**A failing gate always carries at least one finding.** `_failed` raises if you
try to fail a gate silently.

**Collect, do not stop.** Three missing fields give three findings; three
broken gates give three failed gates. A verdict is a task list.

## The one that will take longest

Exercise 5. The study that peeked at its confirmation set and the study that
did not produce **byte-identical** reports, figures and intervals — the test
`test_confirmation_gate_reads_only_the_log` proves it. The peek exists in the
research log's ordering and nowhere else. If your gate reads `REPORT.md`, it
cannot possibly work.

## When you are done

```bash
.venv/bin/pytest starter -q       # 33 passed
bash tests/run_tests.sh           # the full harness
```

Then point it at something of your own.
