# Week 17 project — A/B Test Analyzer

This week was **Probability and Statistics**: probability rules, random
variables and distributions, Bayes' theorem, descriptive statistics and
Simpson's paradox, sampling and the bootstrap, and finally hypothesis tests,
confidence intervals, permutation tests, power, multiple comparisons and
peeking — closing with one worked experiment on Day 119.

Day 119 walked you through *one* experiment the course handed you, with two
datasets already prepared. This project is different in the one way that
matters: you build a **reusable analyzer**, and then you build your own
**simulator** to generate experiments to feed it — including experiments
where you, and only you, know the true effect. That is the whole point. When
you generate the data yourself, you can check whether your own tool gets the
right answer, because you already know what the right answer is. Run your
analyzer against a hundred simulated experiments with no true effect, and if
it declares "significant" close to 5% of the time, you have not just built a
statistics tool — you have **verified your own instrument**. Nothing in Day
119 asked you to do that. This project does, and it is the part that turns a
calculation into science.

**Environment constraint:** scipy, pandas, statsmodels and matplotlib are
**not** available in this environment. NumPy and Pillow are, along with the
standard library's `statistics`, `math` (its `erf` function gives you normal
tail probabilities), `csv` and `random`. Every test you use is one you wrote
yourself, exactly as on Days 117–119 — there is no `scipy.stats.ttest_ind` to
fall back on here.

## What you are building

Two separate command-line tools that never share code by accident:

1. **A simulator** that generates a fake experiment with a *known* ground
   truth, and writes it to a CSV.
2. **An analyzer** that takes a CSV and a pre-registered plan, and produces a
   verdict — with no knowledge of how the CSV was generated.

```
python simulate.py --n 4000 --base-rate 0.12 --effect 0.02 --noise 0.0 \
  --segments region:3 --seed 7 --out data/exp001.csv --truth data/exp001.truth.json

python analyze.py data/exp001.csv --plan plans/exp001.plan.json --out results/exp001/
```

The analyzer must not import anything from the simulator, must not read the
`.truth.json` file, and must not accept a CSV without a plan. If your
analyzer can see the answer, it is not being tested — it is being told.

## Requirements

- **Your own simulator**, configurable in sample size, base rate or mean,
  effect size, noise, and segment structure (at least one categorical segment
  column, e.g. `region` with 3+ levels). It must be able to generate a
  **zero-effect** experiment (the null is literally true) and a
  **known-nonzero-effect** experiment, selected by a flag, not by chance.
  Every simulated row is independent — the most common way to sabotage this
  requirement is reusing one random seed across what are supposed to be
  independent runs (see Troubleshooting).
- **The analyzer as a separate, reusable component.** It is a CLI that takes
  a CSV and a plan file as inputs and does not contain the answer anywhere in
  its source. If you find yourself hard-coding "the effect is 0.02" into
  `analyze.py`, stop — that defeats the entire exercise.
- **A pre-registered plan, as an input file, not a comment.** A JSON or YAML
  file the analyzer reads that states: the primary metric, α, the intended
  traffic split (e.g. 50/50), the sample size you calculated from your own
  power analysis, and the stopping rule (fixed horizon, or a named
  sequential rule). **The tool must refuse to run and exit non-zero if no
  plan is given or the plan is missing a required field.** This is not
  optional politeness — it is the mechanism that makes pre-registration real
  rather than decorative.
- **A sample-ratio mismatch (SRM) check that can halt the analysis.** Compare
  the observed split against the planned split with a chi-squared or exact
  goodness-of-fit test, computed **once**, over the final assigned counts. If
  it fails at a conservative threshold (a common choice is α = 0.001,
  stricter than your experiment's own α, because you want few false alarms
  here but any real failure caught), the tool must stop before computing any
  effect estimate and say why. Randomisation you cannot trust makes
  everything downstream meaningless.
- **The test plus a confidence interval on the difference, and the effect
  size in its own units — never a bare p-value.** For a proportion metric,
  report the difference in rates with its CI in percentage points (or
  relative lift, stated as such); for a continuous metric, report the
  difference in means with its CI in the metric's own units.
- **A permutation test as a second opinion** (Day 118). Report both p-values
  side by side. When they disagree by more than a small stated margin,
  explain why in the output — do not silently prefer one.
- **A bootstrap interval** (Day 117) on the difference, reported alongside
  the analytic interval, with a note on how closely they agree and, if they
  diverge, why you think so.
- **At least one guardrail metric** (e.g. latency, error rate, unsubscribe
  rate) that can **veto** an otherwise-positive verdict — a guardrail
  breach must change the final verdict, not just appear in a side table.
- **Segment analysis that reports rather than concludes.** Break the result
  down by your segment column and print each segment's estimate — clearly
  labelled as exploratory, uncorrected, and not a basis for a decision on its
  own. Detect and flag explicitly when a segment's effect sign is opposite
  the pooled effect's sign (a Simpson's-paradox-shaped reversal, Day 116).
- **The calibration study — the heart of this project.** Using your own
  simulator, run the full analyzer over many (200+) independently seeded
  zero-effect experiments and report the observed false-positive rate
  against the nominal α. Then run it over many independently seeded
  known-nonzero-effect experiments (same effect size each time) and report
  the observed power against the power you predicted in your plan's sample
  size calculation. This is what separates an analysis tool from an analysis
  toy: you are not just running a test, you are checking whether the test
  behaves the way the theory says it should.
- **A demonstration of peeking's cost**, using your own simulator: run many
  zero-effect experiments twice each — once analyzed only at the pre-declared
  fixed horizon, once analyzed by checking after every batch of new data and
  stopping the instant p < α — and report the false-positive rate for each
  policy.
- **A plain-language verdict**: one paragraph a colleague could act on,
  stating the estimate, its interval, and explicitly what value the interval
  would have needed to exclude for the decision to flip. Include an
  **"inconclusive"** outcome as a legitimate, first-class result — not a
  failure state and not silently rounded to "no effect."
- **`NOTES.md`** recording: your measured false-positive rate and how close
  it landed to your nominal α; your measured power against your predicted
  power; one specific experiment where your analyzer's verdict was wrong
  given the ground truth you set, and your best explanation of why; and the
  hardest bug you hit while building this.

## Steps

1. Build the simulator first, for the zero-effect case only, and print
   summary statistics by hand before writing any analysis code. You need to
   trust the data generator before you trust anything built on top of it.
2. Write the pre-registered plan format and the refuse-to-run check. Get the
   analyzer to reject a missing or incomplete plan before it does anything
   else.
3. Add the SRM check on a clean 50/50 simulated split (it should pass) and on
   a deliberately skewed split you construct by hand (it should halt).
4. Implement the primary test and its confidence interval for the zero-effect
   case, and confirm the p-value distribution looks uniform-ish across a
   handful of runs before trusting a single one.
5. Add the known-nonzero-effect mode to the simulator, and confirm the
   analyzer detects it at a sample size that matches your power calculation.
6. Add the permutation test and the bootstrap interval, and compare all three
   (analytic, permutation, bootstrap) on the same simulated dataset before
   moving on.
7. Add the guardrail metric and confirm it can flip a verdict from positive
   to inconclusive or negative when you deliberately break it in the
   simulator.
8. Add segment generation to the simulator and the segment breakdown to the
   analyzer. Deliberately construct one dataset with a sign reversal between
   a segment and the pooled result, and confirm your flag fires on it.
9. Run the calibration study last, once every other piece works on individual
   runs — it is many repeated calls to a tool you already trust in isolation.
10. Run the peeking demonstration, reusing the calibration harness with a
    different stopping policy.

## Expected output

- Running the analyzer with no `--plan` flag, or a plan missing a required
  field → a non-zero exit code and a clear message naming the missing field,
  and no analysis performed.
- The SRM check on a clean 50/50 simulated split → passes, analysis proceeds.
- The SRM check on a split you construct by hand to be skewed (e.g. 60/40 on
  thousands of rows) → halts, and the output says why, before any effect
  estimate is printed.
- On a well-behaved metric (a proportion or a roughly-normal continuous
  metric with a reasonably large sample), the analytic and bootstrap
  intervals should agree closely — overlapping substantially, with centers
  close together. The exact bounds depend on your simulated data and are not
  specified here.
- The permutation and analytic p-values should agree closely when your
  metric is well-behaved (roughly symmetric, no extreme outliers) and can
  diverge more when it is not — both outcomes are expected depending on what
  you simulate; the point is that you can say which case you are in and why.
- Over 200+ independently seeded zero-effect experiments, the observed
  false-positive rate should land near your nominal α — but not exactly on
  it. With 200 trials at α = 0.05 the standard error on that rate is about 1.5
  percentage points, so a 95% band runs roughly 0.020 to 0.080 — a measured
  rate of 0.035 or 0.065 is a correct result, not an error to chase. Work that
  band out for your own trial count rather than borrowing this one: it is the
  same standard-error calculation from Day 117, applied to your own measurement
  of your own tool. State your measured rate and your trial count together,
  because neither means anything alone.
- Over many independently seeded known-effect experiments at your chosen
  effect size, the observed power should land reasonably near what your
  sample-size calculation predicted — the exact figures depend on your
  chosen effect size, α, and sample size, so state your own inputs alongside
  your own measured power rather than expecting a fixed figure.
- The peeking demonstration's stop-at-first-significance false-positive rate
  should be clearly, substantially higher than the fixed-horizon rate on the
  same null simulations — often several times higher — though the exact
  multiple depends on how often you peek and how many batches you check.
- The final verdict for at least one run should read as a complete,
  actionable sentence — an estimate, an interval, and what would have
  changed the decision.
- At least one demonstrated "inconclusive" verdict, printed as such, not
  silently treated as "no effect."

## Validation

- [ ] The simulator and the analyzer are separate programs; the analyzer's
      source contains no hard-coded ground truth.
- [ ] The simulator can produce both a zero-effect and a known-nonzero-effect
      experiment, selected explicitly, each independently seeded.
- [ ] The analyzer refuses to run without a complete pre-registered plan,
      exiting non-zero with a clear message.
- [ ] The SRM check runs once over final counts, passes on a clean split, and
      halts the analysis on a skewed split before any effect estimate.
- [ ] The primary result reports a test statistic, a confidence interval on
      the difference, and the effect size in its own units — never a bare
      p-value alone.
- [ ] A permutation test runs alongside the analytic test, and the two
      p-values are compared with any disagreement explained.
- [ ] A bootstrap interval is reported alongside the analytic interval, with
      agreement or divergence discussed.
- [ ] At least one guardrail metric can veto a positive verdict, and this is
      demonstrated on a deliberately broken guardrail.
- [ ] Segment analysis is reported as exploratory and uncorrected, and a
      Simpson's-paradox-shaped sign reversal is detected and flagged when
      present.
- [ ] The calibration study runs 200+ independently seeded null experiments
      and reports the observed false-positive rate against nominal α, with
      the trial count stated.
- [ ] The calibration study also runs many independently seeded known-effect
      experiments and reports observed power against predicted power.
- [ ] The peeking demonstration shows a clearly elevated false-positive rate
      under stop-at-first-significance versus the fixed-horizon rule.
- [ ] At least one run produces a plain-language verdict naming what would
      have flipped the decision, and at least one run is honestly reported as
      inconclusive.
- [ ] `NOTES.md` records the measured false-positive rate, the measured
      power, one wrong verdict with an explanation, and the hardest bug.

## Troubleshooting

- False-positive rate suspiciously near 0% across your calibration runs?
  The same random seed is being reused across what are supposed to be
  independent simulated experiments, so they are not actually independent —
  check that each run in your calibration loop passes a distinct seed.
- False-positive rate near 50%? Your analyzer is peeking — checking
  significance repeatedly during data collection and stopping early — even
  in a run you intended to be a fixed-horizon calibration check. Audit where
  the stopping decision is made.
- Permutation and analytic p-values disagree noticeably on one metric? That
  is information, not a bug — it usually means the metric is skewed or has
  heavy tails, which violates the analytic test's assumptions but not the
  permutation test's. Say so in your output rather than treating one as
  wrong.
- Bootstrap interval is suspiciously narrow compared to the analytic one?
  You likely resampled within each group separately at the row level, or
  resampled the wrong unit (e.g. resampling individual events when the
  randomised unit was the user). Resample whole units, with replacement,
  respecting the group each unit belongs to.
- The SRM check fires on almost every run, even ones you built to be clean?
  It is probably being computed at every row as data streams in rather than
  once over the final assigned counts — a single clean split will drift
  above and below 50/50 many times along the way by chance alone. Compute it
  once, at the end.
- Segment analysis "finds" a significant effect in nearly every segment?
  Each segment is being tested at the full α with no correction for testing
  many segments at once — this is exactly the multiple-comparisons problem
  from Day 118. The requirement is to report segments as exploratory, not to
  correct them into a formal claim; make sure your output actually says so.
- Your power calculation disagrees sharply with your measured power? Check
  that the effect size is expressed in the same units in both places — a
  power calculation done in standardized units (like Cohen's d) will not
  match a simulator configured with a raw effect in percentage points unless
  you convert consistently.
- You are reporting an inconclusive result as if the experiment failed?
  Inconclusive is a legitimate outcome: it means the interval was too wide
  to rule out either "no effect" or "a meaningful effect," and the honest
  next step is more data or a different design — not a rewritten verdict
  that pretends to more certainty than the interval supports.
