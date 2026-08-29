# A Report That Argues — the nine exercises

You are not writing an analysis today. You are writing the **checks that
decide whether an analysis is fit to be read**, and you are wiring them
into a generator that refuses to build a report that fails them.

Four files sit in this directory:

| File | What it is |
| --- | --- |
| `data.py` | The dataset. Deterministic: `numpy.random.default_rng(133)`, so every number below is the same on your machine as on the machine this lab was written on |
| `report.py` | The generator: `Candidate`, `Report`, `Estimate`, and the six checks. Read this first |
| `analysis.py` | The twelve candidate figures exploration produced, and `build_report`, which filters them down to five |
| `test_report.py` | Your nine exercises. Each one currently calls `pytest.skip` |

Replace each `pytest.skip(...)` with real assertions, and delete the skip
line. Run `pytest starter -v` as often as you like. Never run
`pytest examples starter` in one command — both directories hold a module
named `test_report.py` and pytest aborts collection on the clash. Run the
two directories as two separate commands.

Every directory fixture is a real temporary directory that is deleted the
moment the test finishes. When you are done, no image and no Markdown file
exists anywhere outside this repository's checkout.

---

## Exercise 1 — a figure must have a question

`Report.add_panel` raises `ReportError` on a `Candidate` whose `question`
is `None` or blank. Prove both, prove that the refused figure is not
half-admitted (`report.panels` is still empty), and then prove the same
candidate is accepted once it has a question.

This is the day's thesis compiled into an exception. A figure whose
question you cannot state is a figure that does not belong in the report,
and the generator will not let you add one by accident.

## Exercise 2 — the caption carries the claim

`carries_claim` demands a number, a percent sign, or a comparative word.
Show it rejects `"revenue by region"` and accepts a caption with a figure
in it, and show `add_panel` refusing a `Finding` whose caption is only a
label.

Then prove **both** honest limits of the heuristic. It passes
`"revenue doubled in every region"` even on data where revenue halved —
it cannot read the data, so it cannot judge truth. And it refuses
`"revenue tripled in all four regions"`, which is a real claim written
with a word that is simply not on the list. The check buys you exactly
one thing: it makes the *absence* of a claim impossible to ship by
accident.

## Exercise 3 — the numbers in the prose come from the data

`data.perturbed()` returns the same frame with one input changed. Render
the report from both frames and prove the sentence about the West's
change moved with the data. If a number is the same in both documents, it
was typed rather than computed, and it will be wrong the first time the
data is refreshed.

## Exercise 4 — every figure is referenced

`orphan_figures` compares the PNG files on disk against the image links in
the Markdown. Prove the generated report has none, then copy one figure to
a new name and prove the check finds it. An orphan is either a figure you
meant to discuss and forgot, or a leftover from a previous run.

## Exercise 5 — uncertainty is stated, not implied

Days 117 and 118 put the interval in the error bar. This exercise puts it
in the sentence. Prove every one of the five panels reports an `Estimate`,
that four of them carry a 95% interval and one carries an explicit note
saying why no interval is available, and that a bare point estimate is
caught by `missing_uncertainty`.

## Exercise 6 — reproducibility

Day 126's idempotence, applied to prose. Render the same input twice into
two directories and prove the Markdown is byte-identical — and that each
figure's PNG bytes are identical too, on this machine and this run. Then
prove that changing the input changes the document, and that nothing in
the output is a clock reading. Provenance here is a hash of the data, not
a timestamp of the run, which is exactly why two runs agree.

## Exercise 7 — ordering for the reader

Prove the conclusion appears before the evidence, and the caveats before
the provenance. Then prove something stronger: each panel's caption
appears verbatim as its numbered line in the conclusion. The conclusion is
not a separate summary that can drift; it *is* the list of captions.

## Exercise 8 — the "so what" filter

Twelve candidate figures went in. Prove that five survive and seven do
not, that fewer than half survive at all, that no discarded slug reaches
the Markdown and no file was written for one — and that every discarded
candidate's one-line reason **is** in the report, under "what we looked at
and found nothing in". Deleting the chart and keeping the sentence is the
whole move.

## Exercise 9 — the accessibility contract

Days 127 and 132 as a build check. Prove all five surviving figures pass
`accessibility_problems` — colourblind-safe palette, both axes labelled —
and that `draw_inaccessible` (red against green, no axis labels) fails
with exactly four named problems.
