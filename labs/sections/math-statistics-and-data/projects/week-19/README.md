# Week 19 project — Exploratory Analysis Report

This week was **Data Visualization**: why we visualize at all and how the
Cleveland–McGill ranking orders the encodings a reader can actually decode,
the matplotlib object model, seaborn's estimators, distributions,
relationships, time series, chart honesty, and finally the report as an
argument rather than a gallery.

Day 133 handed you a report generator and walked you through the method on a
dataset the course had already chosen. This project takes the dataset away.
You find a real one, state the question it will answer, and produce a
narrated exploratory analysis of it. The charts are the easy half. What
makes this project worth more than the day is that **every figure has to
survive a challenge you write yourself**: what question does this answer,
what does this view hide, what would it look like if the opposite were true,
and what did you check to rule that out. A learner who can answer those four
questions for five figures has understood Week 19. A learner who produced
twenty beautiful figures and cannot answer them has not, and the report will
show it.

**Environment:** pandas 3.0.5, matplotlib 3.11.1, seaborn 0.13.2, NumPy
2.5.2 and pyarrow 25.0.1 are what this course ran on. scipy, scikit-learn,
statsmodels, polars and plotly are not available — every check you make is
code you wrote yourself, exactly as on Days 127–133. Matplotlib must run
headless: call `matplotlib.use("Agg")` before importing `pyplot`, never call
`plt.show()`, and close each figure with `plt.close()` so a full report run
does not leak dozens of open figures.

## What you are building

A report that a code run produces, not a document you typed:

```
eda/
  load.py         # reads the pinned input, applies the Week 18 contracts
  quality.py      # missingness, duplicates, what cleaning changed
  palette.py      # the colourblind-safe palette and the check that verifies it
  figures.py      # one function per figure, each returning a Figure object
  stats.py        # your own interval / standard-error helpers
  render.py       # writes REPORT.md from measured values, never from literals
run_report.py     # entry point: load -> quality -> figures -> render
data/
  raw/<your-file>.csv        # the dataset you found, untouched
figures/
  fig-01-*.png ... fig-05-*.png
REPORT.md
manifest.json
```

`REPORT.md` is generated. Every number that appears in its prose is
formatted from a value the code computed in the same run that drew the
figures, so a prose sentence and the chart beside it cannot disagree. That
is the Day 126 discipline applied to writing: if you find yourself typing a
number into `render.py` as a literal, you have introduced the exact drift
the requirement exists to prevent.

Each function in `figures.py` returns a matplotlib `Figure`, which means you
can assert on it — axis labels, tick locations, the number of artists, the
y-axis lower limit — before it is ever saved (Day 128: a chart is an object
graph you can inspect, not an image you have to eyeball).

## Requirements

- **A real dataset you did not create.** Public open data is ideal. It needs
  enough structure to support at least one distribution, one relationship
  between two variables, and one grouped comparison; a time dimension as
  well is strongly preferred, because Day 131's failure modes only bite when
  there is a time axis. State its **provenance and licence** in `REPORT.md` —
  where it came from, when you downloaded it, what you are permitted to do
  with it. A dataset whose licence you cannot establish is a dataset you
  should not build a report on.
- **A stated question, and the decision it would inform.** Write both in the
  first section of `REPORT.md`, before any figure exists. An exploratory
  analysis with no question is a gallery; the question is what makes it
  possible for a figure to be judged relevant or irrelevant at all. "What
  drives X?" is not a question, it is a topic. "Did the change in Y at date
  D coincide with a change in X, and by how much?" is a question, and the
  decision it informs might be whether to keep doing Y.
- **At least five figures, each with its own question and a claim-bearing
  caption** (Day 133). The caption must contain something a reader could
  disagree with. "Monthly totals by region" is a restatement of the axes and
  earns nothing. "Region B's decline began two months before the policy
  change, so the policy cannot be its cause" is a claim — it can be argued
  with, which is what makes it worth writing.
- **A self-challenge for every figure**, in the report, immediately after the
  figure: **what this view hides**, and **what you checked**. This is the
  requirement the project is built around. Some concrete forms it takes:
  - A bar chart of group means hides the shape of each group. Day 130 showed
    two samples with identical five-number summaries where one was bimodal —
    a boxplot cannot see modality and neither can a bar of means. Plot the
    distributions and say whether they are unimodal.
  - A trailing average hides the present. Day 131: a trailing mean lags by
    roughly half its window, so a 30-day trailing line is describing where
    the series was about 15 days ago. State your window and its lag.
  - A scatter with a fitted line hides whether the relationship is actually
    linear. Look at the residuals, or bin the x-axis and compare the group
    means across bins, and say what you found.
  - A time series hides what your sampling interval destroyed. Day 131's
    aliasing example manufactured a twenty-day cycle out of a four-day
    signal purely through the sampling rate. If you resampled or aggregated
    to a coarser interval, say what frequency you can no longer see.
- **Honest scales throughout, with the lie factor computed for at least one
  chart.** Tufte's lie factor is the size of the effect shown in the graphic
  divided by the size of the effect in the data; an honest chart sits at
  about 1. Pick the chart where a truncated baseline was most tempting —
  where the real difference is small and the full-scale version looks flat —
  compute the lie factor for the truncated version and for the version you
  shipped, and put both numbers in the report. If you deliberately break a
  rule (a truncated axis on a series where zero is genuinely meaningless,
  such as a temperature or a pH), **disclose it in that figure's caption**
  along with the reason (Day 132). A disclosed rule-break is a judgment
  call; an undisclosed one is the lie factor doing its work unannounced.
- **A colourblind-safe palette, verified by your own check.** Do not assert
  that a palette is safe because a library named it so. Reuse the Day 127
  simulation: transform your palette's colours into deuteranopic space and
  measure the perceptual separation that survives. Day 127's measured
  example is the standard to beat — a red/green pair kept only about 6% of
  its separation under that simulation, while the colourblind-safe pair kept
  essentially all of it. Report your own numbers for your own palette, and
  state the threshold you decided was acceptable before you measured.
- **Uncertainty stated in the prose, not only drawn.** Wherever the report
  states an estimate — a group mean, a rate, a difference between groups —
  give an interval or a standard error alongside it in the sentence (Days
  117 and 118). An error bar in a figure that never appears in the text is
  an ornament. Where you cannot compute an interval honestly — a single
  observation, a census rather than a sample, a quantity whose sampling
  process you do not know — say so explicitly rather than omitting the
  question. "No interval is available here because these are all the records
  that exist, not a sample from a larger population" is a complete and
  correct answer.
- **Data quality reported before analysis** (Week 18). Before the first
  figure: how many rows and columns, what fraction of each column is
  missing and whether the missingness looks structured or scattered, how
  many duplicate rows on your key, what you cleaned, and **what that
  cleaning changed** — not just that you did it. If you dropped rows,
  report how many and whether the dropped ones differ systematically from
  the kept ones on some other column, because a figure drawn after a
  selective drop is a figure about a population you have quietly redefined.
- **Reproducible generation** (Day 126). `run_report.py` reads a pinned
  input file, computes every value, draws every figure, and writes
  `REPORT.md` and `manifest.json` in one pass. Run it twice on the same
  input and the two `REPORT.md` files must be identical. Record in
  `manifest.json` the input file's hash, the package versions you ran, every
  seed you set, and a hash of the generated report.
- **A section of what you looked at and found nothing in.** List the
  relationships you checked that turned out flat, the splits that made no
  difference, the seasonal effect that was not there. Without this section
  the next reader repeats every dead end you already walked down, and the
  report silently overstates its own hit rate by hiding its misses.
- **`REPORT.md` as the deliverable**, with the figures embedded as images
  and referenced by number in the text, plus the code in `eda/` that
  generated it. A report delivered as a notebook with the charts inline and
  no way to regenerate it does not meet this requirement.

## Steps

1. Find the dataset. Confirm you can state its provenance and licence before
   you spend any time on it, and confirm it has the structure the first
   requirement asks for.
2. Write the question and the decision it informs, into `REPORT.md`'s first
   section, before drawing anything. If you cannot write the decision, the
   question is not yet a question.
3. Load the data and run the quality pass — missingness, duplicates, dtypes,
   the Week 18 inspection battery. Write the data-quality section now, while
   "before" still exists.
4. Build `palette.py` and its check first, before any figure, so every figure
   you draw is drawn in a palette you have already verified. Building it
   afterwards means recolouring five finished figures.
5. Draw figure 1 and write its question, its caption and its self-challenge
   in the same sitting. Do not draw figure 2 until figure 1's challenge is
   written — the challenge is what tells you whether the figure was worth
   drawing, and writing all five challenges at the end turns them into
   paperwork.
6. Repeat for figures 2 through 5, choosing encodings by the Cleveland–McGill
   ranking rather than by what looks interesting: position on a common scale
   beats length, which beats angle and area. If you are tempted by a bubble
   chart, remember Day 127 — encoding a value in a circle's **radius**
   squares every ratio, so a value twice as large draws four times the ink.
7. Compute the lie factor for your most tempting-to-truncate chart, in both
   the truncated and the shipped version, and write both numbers into the
   report.
8. Add the interval or standard error to every estimate in the prose, and the
   explicit note wherever one cannot be computed.
9. Write the "looked at, found nothing" section from your working notes.
10. Discard at least one figure, and record in the report why you discarded
    it. A report where nothing was cut is usually a report where nothing was
    judged.
11. Move every number in the prose into `render.py` as a formatted computed
    value, then run `run_report.py` twice from clean and confirm the two
    generated `REPORT.md` files are byte-identical.
12. Read the finished report as a reader who disagrees with your conclusion,
    and check that the report already answers them. Where it does not, that
    is your last figure or your last paragraph.

## Expected output

- Two consecutive runs of `run_report.py` on the same pinned input produce
  `REPORT.md` files that are identical byte for byte, and manifests with the
  same report hash.
- Every figure in `figures/` is referenced by number somewhere in
  `REPORT.md`, and every figure reference in `REPORT.md` resolves to a file
  that exists — no orphans in either direction. This is checkable by script
  and you should check it by script.
- Each of the five figures carries three things in the report: the question
  it answers, a caption making a claim a reader could dispute, and a
  self-challenge naming what the view hides and what you checked.
- Your colourblind check runs and reports a number for every pair of colours
  in your palette, and every pair clears the threshold you set before
  measuring. Report the retained-separation figure for your own palette
  rather than expecting it to match the 6% / near-100% contrast Day 127
  measured for its red/green and colourblind-safe pairs — those are that
  simulation's numbers for those specific colours.
- The lie factor is stated for at least one chart in both its truncated and
  its shipped form, and the shipped form's figure is close to 1. Any figure
  that deliberately departs from that says so in its own caption.
- The data-quality section reports, for the specific dataset you chose, the
  row and column counts, per-column missingness, duplicate count on your
  key, and for each cleaning action a before-and-after measurement. Where
  these depend on your dataset, report your own measured figures — this
  project is graded on the discipline of measuring, not on any particular
  value.
- Every estimate in the prose carries an interval or a standard error, or an
  explicit sentence saying why one is not available.
- At least one discarded figure is named, with the reason it was discarded.
- The "looked at, found nothing" section is non-empty and specific enough
  that a reader could avoid repeating one of those checks.
- The conclusion states something a reader could act on or argue with, and
  names what evidence would change it.

Where a figure's content depends on the dataset you chose, the expectation
above is about the **shape** of the result — a number reported with an
interval, a distribution shown alongside a mean, two runs producing the same
bytes — not about a specific value. There is no target number for your
dataset because nobody else has your dataset.

## Validation

- [ ] The dataset is genuinely external, with provenance and licence stated
      in `REPORT.md`.
- [ ] The question and the decision it informs appear before the first
      figure.
- [ ] At least five figures, each with its own stated question.
- [ ] Every caption makes a claim a reader could disagree with, rather than
      restating the axes.
- [ ] Every figure has a self-challenge naming what it hides and what was
      checked — including a distribution check behind any chart of means, a
      stated lag behind any trailing average, and a linearity check behind
      any fitted line.
- [ ] The lie factor is computed and reported for at least one chart, in
      both its truncated and its shipped form.
- [ ] Any deliberate rule-break (truncated baseline, dual axis, non-linear
      scale) is disclosed in that figure's caption with its reason.
- [ ] The palette passes a colourblind check the learner wrote and ran, with
      numbers reported and a threshold stated in advance.
- [ ] Every estimate in the prose carries an interval or standard error, or
      an explicit note that none is available and why.
- [ ] Data quality — missingness, duplicates, cleaning and what it changed —
      is reported before the first analytical figure.
- [ ] `REPORT.md` is generated by code from a pinned input, with no numbers
      typed as literals in the prose.
- [ ] Two runs produce byte-identical reports, with the manifest recording
      input hash, versions, seeds and report hash.
- [ ] Every figure is referenced in the text, and every reference resolves —
      no orphans.
- [ ] A "looked at, found nothing" section exists and is specific.
- [ ] At least one discarded figure is named with its reason.
- [ ] The conclusion is actionable or arguable, and names what would change
      it.

## Troubleshooting

- The report reads like a gallery — pretty figures, no thread? The question
  was written after the charts, or never. Go back to step 2: state the
  question and the decision it informs, then ask of each existing figure
  whether it moves that question forward. The ones that do not are your
  discards, and cutting them makes the report stronger, not shorter.
- Captions that describe the axes ("sales by month", "age versus income")?
  A caption that nobody could disagree with carries no information the
  figure did not already carry. Rewrite each as a sentence with a verb and a
  claim, then check that you could imagine a colleague pushing back on it.
  If you cannot imagine the pushback, it is still a label.
- A bar chart of group means where the bars differ but the groups overlap
  almost entirely? A mean is a single number standing in for a whole shape.
  Day 130's pair of samples had identical five-number summaries with one of
  them bimodal — the summary could not see it and neither can your bar.
  Plot the distributions, and if either group is bimodal, say so in the
  self-challenge: a mean between two modes describes a value that few
  members of the group actually have.
- Someone read your trailing-average line as "where we are now"? A trailing
  mean lags its series by roughly half its window (Day 131), so a 30-day
  trailing average is a statement about roughly two weeks ago. Label the
  line with its window, state the lag in the caption, and if the report's
  conclusion depends on the current level, show the raw series underneath
  the smoothed one rather than the smoothed line alone.
- Two series on a dual axis that look like they track each other? You can
  make almost any two series appear correlated by choosing the two scales
  that align them, which is exactly why Day 132 treated dual axes as a
  rhetorical device rather than a chart type. If you want to claim the
  series move together, show it directly — index both to a common baseline
  and use one axis, or plot one against the other as a scatter — and state
  the association with an interval. If you keep the dual axis, disclose in
  the caption that the vertical alignment of the two series is a choice you
  made, not a finding.
- Your bar chart's baseline does not start at zero? Bar length is the
  encoding, so a truncated baseline multiplies the apparent difference —
  that is the lie factor rising above 1 by construction. Either start bars
  at zero, or switch to an encoding where zero is not implied (a dot plot on
  a truncated scale is honest in a way a truncated bar is not, because a dot
  encodes position, not length).
- Your palette "is colourblind-safe" because a library said so, and your own
  check fails it? Trust your check and change the palette. This is the
  Day 127 measurement in miniature: a red/green pair that looks maximally
  distinct to you retained only about 6% of its separation under the
  deuteranopia simulation, and the reader it fails cannot tell you it failed.
  Also make sure colour is never the only encoding for something the reader
  must distinguish — pair it with a marker shape, a line style, or a direct
  label.
- Numbers in your prose disagree with the figure beside them? They were
  typed as literals and the data changed underneath them. Every number in
  `REPORT.md` must be formatted from the same computed value the figure was
  drawn from, in the same run (Day 126). One place where this bites late: a
  number that was correct when you wrote it, and stayed in the file through
  three data refreshes.
- The "reproducible" report differs between two runs, and nothing in your
  code is random? Check your seaborn calls. Seaborn's default error bar is a
  **bootstrap**, which resamples — so `sns.barplot` or `sns.lineplot` with
  default settings draws a slightly different interval every run, and your
  byte-identical check fails on figures you never thought were stochastic
  (Day 129). Fix it by seeding (`seed=`) or by choosing a deterministic error
  bar such as a standard error or a percentile interval, and record the
  choice in the manifest either way.
- Your conclusion goes further than the data can carry it — an association
  described as a cause, a pattern in one year projected forward, a
  difference between two groups explained by a mechanism you did not
  measure? The honest move is not to soften the wording until it means
  nothing. State the claim, state what would settle it (the experiment, the
  extra variable, the additional year of data), and say which of those you
  could actually get. A report that names the study it cannot run is more
  useful than one that hedges its way out of saying anything.
