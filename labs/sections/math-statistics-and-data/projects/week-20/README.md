# Week 20 — Section Project: Full Exploratory Study

This is not a week's exercise. **This is the section project for the whole of
Course 03 — Math, Statistics, and Data, Days 99 to 140** — and it is the last
thing you do before Day 141 opens Course 04 and machine learning begins. Six
weeks are folded into one deliverable: vectors and matrices, derivatives and
gradients, probability and inference, pandas end to end, visualization, and
finally the practice of working with data that somebody else collected for
their own reasons.

Every weekly project so far took one week's technique and stretched it. This
one takes forty-two days of technique and asks whether you can run a study
with it — choose a dataset, pose three questions, answer the ones that can be
answered, say plainly which one cannot, and hand over something a stranger can
regenerate from scratch. Budget for it accordingly: this is roughly
**eighteen to twenty-five hours of work**, and it is meant to be spread over
one to two weeks rather than compressed into a weekend. Most of the earlier
projects in this section landed between four and ten hours. This is the
capstone, and the difference in scale is deliberate.

**Environment:** pandas 3.0.5, matplotlib 3.11.1, seaborn 0.13.2, NumPy 2.5.2
and pyarrow 25.0.1 are what this course ran on. scipy, scikit-learn,
statsmodels and polars are not available, so every interval, every standard
error and every test statistic in your study is code you wrote — which is
exactly what Weeks 17 and 18 spent thirteen days preparing you to do.
Matplotlib must run headless: call `matplotlib.use("Agg")` before importing
`pyplot`, never call `plt.show()`, and close each figure with `plt.close()`.

## What you are building

One study directory, reproducible from a pinned input, whose deliverable is
`STUDY.md`:

```
study/
  data/
    raw/            # the pinned input, or the fetch code if the licence forbids shipping it
    interim/        # confirmation set held out here, untouched until the end
  src/
    ingest.py       # source -> DataFrame at one stated grain, with the contract
    contracts.py    # the Week 18 assertions: grain, dtypes, ranges, uniqueness
    clean.py        # named, idempotent cleaning steps that record what they changed
    features.py     # derived columns, each with a leakage note
    stats.py        # your own interval, standard-error and resampling helpers
    figures.py      # one function per figure, each returning a Figure
    render.py       # writes STUDY.md from measured values, never from literals
  run_study.py      # entry point: ingest -> contract -> clean -> features -> stats -> figures -> render
  figures/          # fig-01-*.png onward
  STUDY.md          # the deliverable, generated
  RESEARCH_LOG.md   # dated, append-only: what you looked at and in what order
  DAMAGE_REPORT.md  # what cleaning changed, and what it cost
  manifest.json     # input hash, versions, seeds, comparison count, output hash
```

If you prefer to work in a notebook, you may — Day 139's rules apply in full,
and a notebook is judged by whether **restart-and-run-all** produces the whole
study from nothing. A notebook that only runs in the order you happened to
execute cells is not a study; it is a transcript of one session that no longer
exists.

`STUDY.md` is generated. Every number in its prose is formatted from a value
computed in the same run that drew the figures. This is the Day 126
discipline applied to writing, and the reason for it is not neatness: a study
whose prose numbers are typed by hand is a study whose prose will eventually
disagree with its own figures, and you will not be there when a reader
notices.

## Requirements

- **A dataset you chose and can justify** (Day 134). `STUDY.md` states where
  it came from, who collected it and why, the licence and what it permits,
  the date and method of retrieval, and a checksum of the exact file you
  analysed. Include a data dictionary — every column you use, its meaning,
  its units, and its permitted values. If the licence forbids redistribution,
  say so explicitly and ship the **fetch code** instead of the data, so the
  study is still reproducible by someone who accepts the source's terms. A
  dataset whose licence you cannot establish is a dataset you should not
  build a study on.

- **Three questions, written before you analyse anything** (Days 119, 136).
  Each one gets the decision it would inform, written beside it. At least one
  must be answerable from the data you have; **at least one must turn out not
  to be**. Discovering that a question cannot be settled by your data is a
  result, not a failure — it is arguably the most useful thing a study
  produces, because it stops the next person spending a month on it. Say so
  in the study, name what specifically is missing (the variable you do not
  have, the comparison group that does not exist, the time period that was
  never recorded), and say what data would settle it.

- **Ingestion with a stated grain and a contract** (Days 126, 135). Write, in
  one sentence, what one row means — "one reading per sensor per hour", "one
  loan application per applicant per submission". Then encode it: assertions
  on uniqueness at that grain, on dtypes, on value ranges, on the join
  cardinality of anything you merge (`validate=` on every `merge`, as on Day
  124). The contract runs on every execution and fails loudly. A grain you
  cannot state in a sentence is a grain you do not have, and every groupby
  and every join downstream inherits the confusion.

- **Cleaning with a damage report** (Days 121, 125, and Week 18's project).
  `DAMAGE_REPORT.md` records, for every cleaning step: what it changed, how
  many values it touched, and **what it did to the distributions** — the mean,
  the spread and the shape before and after. If you dropped rows, say how
  many and whether the dropped ones differ systematically from the kept ones
  on some other column, because every figure after a selective drop describes
  a population you quietly redefined. "The data was cleaned" is not a damage
  report; it is the absence of one.

- **An untouched confirmation set** (Day 136). Before you explore, split off a
  confirmation set and put it somewhere you will not casually read it. Explore
  on the rest. Every hypothesis you form, every subgroup you notice, every
  cut-off you choose, comes from the exploration set only. When your findings
  are final, you check them against the confirmation set **once**, and you
  report what happened — including a finding that does not survive. Alongside
  it: `RESEARCH_LOG.md`, dated and append-only, recording what you looked at
  and in what order, and a **comparison count** — how many distinct
  comparisons you actually made before arriving at a claim. Twenty
  comparisons at a 5% threshold produce roughly one apparently-significant
  result from pure noise (Day 119), so a claim without a comparison count is
  a claim a reader cannot weigh.

- **Statistics with the uncertainty stated in prose** (Days 117, 118). Every
  estimate in `STUDY.md` — a mean, a rate, a difference between groups — is
  written with an interval or a standard error in the same sentence, not only
  drawn as an error bar in a figure nobody quotes. Where an interval cannot
  be computed honestly (a census rather than a sample, a single observation, a
  sampling process you do not know), write that sentence explicitly instead
  of omitting the question. And **no causal language for observational data**:
  if you did not assign the treatment, you did not run an experiment, and
  "increases", "drives" and "leads to" are claims your design cannot support.
  State the association, state what would settle causation, and say whether
  that study is obtainable.

- **At least five figures** (Week 19), each carrying its own question and a
  claim-bearing caption — a sentence a reader could disagree with, not a
  restatement of the axes. The palette is colourblind-safe **by your own
  check**, not by a library's label: run the Day 127 deuteranopia simulation
  over your palette, report a number per colour pair, and state the threshold
  you set before you measured. Compute the lie factor for the chart where a
  truncated baseline was most tempting; the shipped version sits near 1, or
  the caption discloses the departure and the reason for it.

- **Reproducibility** (Days 126, 139). The whole study regenerates from the
  pinned input in one pass, **twice**, with the same result: byte-identical
  `STUDY.md`, identical figure content, identical manifest hashes. Seeds are
  set and recorded. If a notebook is part of the deliverable, it restarts and
  runs all, from a cleared kernel, without error and without touching the
  confirmation set more than once.

- **An ethics and limits section** (Day 138). Name the frame: whose question
  this is and what the answer would be used for. Name the proxies: every
  quantity you measured that stands in for the thing you actually care about,
  and how it could mislead. Name **who is missing from the data** — the people
  or cases the collection process never captured, and what that omission does
  to your conclusions. Name the features you excluded on ethical grounds and
  why. Then state plainly what the study cannot support: the decisions no
  reader should make on the strength of it.

- **Feature discipline** (Day 137). Every derived column carries a note saying
  what it is built from and when that information becomes available. A feature
  computed from something that happens after the outcome you are asking about
  is a leak, and a leak makes a weak answer look decisive. The tell is a
  relationship that is far cleaner than the domain makes plausible.

- **`STUDY.md` as the deliverable**, plus the code that generated it, the
  manifest and the research log. A finding presented without the code that
  produced it is an assertion.

## Steps

1. Choose the dataset. Confirm the licence, the provenance and the dictionary
   **before** you spend an evening on the data. Compute and record the
   checksum of the file you will analyse.
2. Write the three questions and their decisions into `STUDY.md`, and commit
   or timestamp that file, before you load anything. This ordering is the
   whole reason the questions are worth anything.
3. Write `ingest.py` and `contracts.py` together. State the grain in a
   sentence, then encode it. Do not proceed until the contract passes on the
   raw input, or fails for a reason you can explain.
4. Split the confirmation set now, before you have seen anything interesting.
   Record in the log how you split it, with what seed, and how large it is.
   Then leave it alone.
5. Run the quality pass and write `DAMAGE_REPORT.md` while "before" still
   exists. Every cleaning step is named, idempotent and measured.
6. Explore, on the exploration set only, logging as you go. Append to
   `RESEARCH_LOG.md` in the moment; a log reconstructed afterwards is
   fiction, and it will not contain the dead ends, which are the part with
   value.
7. Build your features, each with its leakage note. For every feature that
   makes a relationship look unusually clean, ask what it knows that it should
   not.
8. Answer question one. Write the estimate with its interval. Then question
   two, then question three — and when one of them cannot be answered, say so
   in the study rather than quietly substituting an easier question.
9. Draw the figures, writing each one's question and caption in the same
   sitting as the figure itself. Verify the palette before the first figure,
   not after the fifth.
10. Move every prose number into `render.py` as a formatted computed value.
11. Check your findings against the confirmation set. Once. Report the result
    whichever way it goes, and if a finding evaporates, keep the section that
    says it did.
12. Write the ethics and limits section, and the conclusion.
13. **Run Day 140's `check_study(path)` harness against your study directory.**
    Fix everything it names, then run it again until it reports nothing.
14. Regenerate the whole study twice from clean, confirm the two runs agree,
    and only then submit.

## Expected output

- **Day 140's harness passes.** Point `check_study(path)` at your study
  directory and it reports nothing missing and nothing unsupported. This is
  the first gate, not the last: run it early enough that what it names is
  still cheap to fix, and treat its output as a checklist you were given
  rather than a verdict you received.
- Two consecutive runs of `run_study.py` from a clean state produce a
  byte-identical `STUDY.md`, figures with identical content, and a manifest
  whose input hash, seeds and output hash match across both runs.
- The confirmation set was used **exactly once**, at the end, and the study
  says what happened when it was — including any finding that did not
  survive.
- Three questions appear in `STUDY.md` before any analysis, each with the
  decision it would inform, and **at least one is answered "the data cannot
  settle this"**, with the specific missing ingredient named and the study
  that would settle it described.
- Every estimate in the prose carries an interval or a standard error, or an
  explicit sentence saying why none is available.
- The comparison count is stated, and any claim near a threshold is discussed
  in the light of it.
- `DAMAGE_REPORT.md` gives, per cleaning step, a before-and-after measurement
  of the affected distribution, not just a description of the action.
- The grain is stated in one sentence and enforced by an assertion that runs
  on every execution.
- At least five figures, each referenced in the text, each with a question and
  a disputable caption; every figure reference resolves and no figure file is
  an orphan. The palette check reports a number for every colour pair against
  a threshold set in advance.
- The ethics section names the frame, the proxies, who is missing, and the
  decisions the study cannot support.
- The conclusion states something a reader could act on or argue with, and
  names what evidence would change it.

Where a result depends on the dataset you chose — the row count, the
missingness fractions, the width of an interval, the size of a difference,
the number of rows a cleaning step touched, the retained separation in your
palette check — the expectation above is about the **shape** of the result,
not a value. A mean reported with an interval. A distribution shown beside
any chart of means. Two runs producing the same bytes. A finding stated with
its comparison count. There is no target number for your study, because
nobody else has your dataset, and any number quoted here would be a number
invented for a dataset that does not exist.

## Validation

Day 140's `check_study(path)` harness is the first gate. Build the study, run
the harness against the directory, fix everything it names, run it again, and
only then work down the list below — the harness exists so that the mechanical
half of this list is answered before a marker ever sees the study, and so that
what remains is the half that needs a human.

- [ ] Day 140's harness runs against the study directory and reports nothing
      missing and nothing unsupported.
- [ ] Provenance, licence, retrieval date and method, checksum and data
      dictionary are all in `STUDY.md`; where the licence forbids
      redistribution, the fetch code ships instead of the data and the
      restriction is stated.
- [ ] Three questions, each with its decision, appear before any analysis.
- [ ] At least one question is answerable and at least one is honestly
      reported as unanswerable, with the missing ingredient named.
- [ ] The grain is stated in one sentence and enforced by a contract that runs
      every time; every merge carries `validate=`.
- [ ] `DAMAGE_REPORT.md` records what changed, how many values, and the effect
      on the distributions, per step.
- [ ] A confirmation set was split before exploration and consulted exactly
      once, at the end; the study reports the outcome either way.
- [ ] `RESEARCH_LOG.md` is dated, append-only, and includes the dead ends.
- [ ] The comparison count is recorded and used when discussing any claim near
      a threshold.
- [ ] Every estimate in the prose carries an interval or a standard error, or
      an explicit note that none is available and why.
- [ ] No causal language anywhere the design does not support it.
- [ ] Five or more figures, each with its question and a claim-bearing
      caption; every reference resolves and no figure is an orphan.
- [ ] The palette passes a colourblind check you wrote and ran, with a number
      per pair and a threshold stated in advance.
- [ ] The lie factor is computed for at least one chart; the shipped version
      is near 1 or its departure is disclosed in the caption with a reason.
- [ ] Every derived feature carries a note on what it is built from and when
      that information becomes available.
- [ ] The study regenerates from the pinned input twice with the same result;
      any notebook restarts and runs all cleanly.
- [ ] The ethics and limits section names the frame, the proxies, who is
      missing from the data, and what the study cannot support.
- [ ] `STUDY.md` contains no number typed as a literal.
- [ ] The conclusion is actionable or arguable and names what would change it.

## Troubleshooting

- **Your three questions are really one question asked three ways.** "Does
  price affect volume?", "Is volume higher when price is lower?", and "What is
  the relationship between price and volume?" are one question with three
  haircuts, and answering it once answers all three — which means two of your
  three answers cost you nothing and taught you nothing. The test is the
  decision column: if two questions would inform the same decision in the same
  direction, they are the same question. Replace one with something that
  probes a different part of the data, or a different mechanism, or a
  different time period.

- **You consulted the confirmation set during exploration.** It is now part
  of your exploration set, and it can no longer confirm anything (Day 136) —
  every pattern you found afterwards had the chance to be fitted to it. There
  is no repair that does not cost data. Either split a fresh confirmation set
  from what remains untouched and start the exploration phase again on the
  rest, or report the study honestly as exploratory throughout, with no
  confirmed findings. Both are acceptable; pretending the holdout survived is
  not.

- **A finding evaporated on the confirmation set.** This is the system
  working. You found a pattern in the exploration set, it did not reappear in
  data that had no chance to shape your hypothesis, and you now know something
  you could not have known otherwise. Report it as a finding that did not
  confirm, with the comparison count that puts it in context. The failure mode
  here is not the evaporation — it is going back to the exploration set to
  hunt for a variant that survives, which converts a clean negative into an
  unfalsifiable positive.

- **Your conclusion says "increases", "drives", "causes" or "leads to", and
  you did not assign the treatment.** Observational data supports association,
  not causation, and the fix is not to hedge until the sentence means nothing.
  State the association with its interval, name the confounders you can think
  of and whether you could measure them, name the experiment or natural
  experiment that would settle it, and say whether it is obtainable. A study
  that names the study it cannot run is more useful than one that hedges its
  way out of saying anything.

- **One answer looks far more decisive than the domain makes plausible.**
  Check the features for leakage (Day 137). A column computed from something
  that happens after the outcome — a status field updated at closure, a total
  that already contains the quantity you are predicting, a timestamp that only
  exists for completed cases — will make a relationship look clean in a way
  reality does not. Ask of every feature: at the moment the question is being
  asked, would this value actually be known? If not, remove it and re-run.

- **A chart of group means over a bimodal distribution.** A mean is one number
  standing in for a whole shape, and a mean that falls between two modes
  describes a value few members of the group actually have. Day 130 showed
  two samples with identical five-number summaries where one was bimodal —
  neither the boxplot nor the bar of means could see it. Plot the
  distributions, say whether each group is unimodal, and if one is not, say so
  beside the chart rather than in a footnote.

- **A trailing average read as the current level.** A trailing mean lags its
  series by roughly half its window (Day 131), so a 30-day trailing line is a
  statement about where the series was about two weeks ago. Label the line
  with its window, state the lag, and if the conclusion depends on the present
  level, show the raw series underneath the smoothed one.

- **The prose disagrees with the figure beside it.** The number was typed as a
  literal, and the data moved underneath it (Day 126). Every number in
  `STUDY.md` must be formatted from the same computed value that drew the
  figure, in the same run. This bites hardest late: a number that was correct
  when you wrote it and stayed in the file through three data refreshes.

- **The notebook only runs in the order you happened to use.** A cell defined
  a variable, you edited that cell, and the old value is still in the kernel
  holding everything together (Day 139). Restart the kernel and run all. If it
  fails, the failure is real and has been there for hours. Fix the ordering,
  move shared setup into the imported modules rather than into cells, and make
  restart-and-run-all part of how you finish every session, not a check you
  perform once at the end.

- **The study reports a "clean" dataset with no damage report.** Cleaning is
  lossy and every step is a decision someone downstream may disagree with
  (Week 18's project). If the study cannot say what changed, how many values
  it touched, and what happened to the distributions, then the cleaning is
  unreviewable — and unreviewable cleaning is where a study's most consequential
  choices hide. Rebuild the cleaning as named, idempotent steps that measure
  themselves, and let the report be a by-product of running them.

- **Two runs of a study with no randomness in it still differ.** Check
  seaborn: its default error bar is a bootstrap, so `sns.barplot` and
  `sns.lineplot` resample on every call and draw a slightly different interval
  each run (Day 129). Seed it, or choose a deterministic error bar such as a
  standard error or a percentile interval, and record the choice in the
  manifest. Dictionary iteration over a set, an unsorted `glob`, and a
  timestamp written into the output are the other three usual suspects.
