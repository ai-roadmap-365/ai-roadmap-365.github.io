# What in these captures is exact, and what is not

Everything in `expected-output/` was captured from a real run on the
authoring machine on 2026-08-20: macOS 26.5.2 (Apple Silicon, arm64),
Python 3.14.0, matplotlib 3.11.1, seaborn 0.13.2, pandas 3.0.5, NumPy
2.5.2, pytest 9.1.1, bash 3.2.57, through a lab-local `.venv` built by
the setup commands in `metadata.yml`. Nothing was typed by hand.

Nothing in this lab is randomly sampled at run time. Every generator
takes a fixed seed, so a second run on this machine reproduces these
files byte for byte. What follows is about running them *somewhere else*.

## Exact everywhere — identical on any machine, any platform

These come from arithmetic on fixed inputs and from matplotlib
transforms that are pure geometry. A different operating system,
processor or screen cannot change them.

| Value | Capture | Why it is exact |
| --- | --- | --- |
| Lie factor `1.0000`, zero-baseline bar pair | 01 | Matplotlib autoscales a bar chart from zero, so the drawn ratio is the data ratio |
| Drawn height ratio `3.0000` on `ylim=(99, 103)` | 01, 02 | `(102-99)/(100-99)` in axes fractions; a fixed transform of fixed numbers |
| Lie factor `2.9412` for the truncated pair | 01, 02 | `3.0 / 1.02` |
| Line lie factor `1.0000` on every baseline | 02 | A linear axis is affine; the recovered change is the true change |
| Data correlation `-0.001034` | 03 | NumPy's Philox/PCG64 generators are specified to be reproducible across platforms for a given seed |
| Drawn correlation equal to the data correlation | 03 | Correlation is invariant under affine transforms — this is algebra, not a measurement |
| Inverted-axis correlation `-0.913234` | 03 | An exact sign flip of `+0.913234` |
| Slopes `-0.7305` and `+0.7045` | 04 | Least squares on a fixed array |
| Mode counts `1` (Sturges) and `2` (Freedman-Diaconis) | 05 | Both rules are deterministic functions of the fixed sample |
| Bin counts `10` and `14` | 05 | As above |
| Drawn area ratio `4.00` (area) and `16.00` (radius) | 06 | `scatter`'s `s` is stored in points squared and read straight back |
| Flat 2D bar ratio `2.000` | 07 | The control case; a linear transform of `2.0` |
| Luminance gaps `0.0996` and `0.5505` | 08 | The WCAG relative-luminance formula on fixed hex colours |
| All four caption-contract verdicts | 09 | Pure string and limit logic |
| Test counts: 42 reference tests, 22 starter skips, 59 harness checks | test-run | Fixed by the files themselves |

## Version-specific — a different matplotlib may move these

| Value | Capture | What could change it |
| --- | --- | --- |
| Tracking gaps `0.4938`, `0.2261`, `0.0147`, `0.0046` | 03 | These depend on matplotlib's autoscale margins and on where `twinx` places the second Axes. The *ordering* — separated is large, widened is under 0.05, and both correlated and uncorrelated pairs reach the same small value — is what the lesson claims and is robust. The fourth decimal place is not. |
| 3D drawn ratios `2.341` and `4.204` | 07 | These depend on matplotlib's perspective projection at `focal_length=0.2`, its default `view_init` elevation and azimuth, and the axis limits set in `bar3d_projected_areas`. `Axes3D`'s projection internals have changed across matplotlib releases before. The reference test pins `2.341` to `±0.02`, which is a version claim, not a universal one. The claim that *survives* any camera is the one the script states: under perspective the drawn size of a bar depends on where it stands. |
| Luminance gap `0.1970` for seaborn's palette | 08 | Reads the first two colours of seaborn 0.13.2's `colorblind` palette. Those hex values are a library constant, so a future seaborn could change them. The assertion is only that this gap exceeds the red/green one, which is the claim being made. |
| Autoscaled top limit `107.1` | 09 | Matplotlib's default bar-chart margin. It appears in the printed `ylim` only, and no assertion depends on it. |
| `platform` line in the harness banner | test-run | Reports the machine it ran on. Expected to differ. |
| `pytest` timing lines (`2.12s` and similar) | pytest-*, test-run | Wall-clock. Never asserted on. |

## Deliberately selected, and therefore disclosed

Two of this lab's datasets were not the first thing tried. Both
selections are the same act the lab spends a day warning about, so both
are disclosed here and in the source docstrings.

- **`uncorrelated_pair`, seed 416.** Chosen by scanning seeds 1-599 for
  the smallest absolute correlation, to get a clean demonstration series.
  The claim being demonstrated — that scaling cannot change a drawn
  correlation — holds for every seed; the seed only makes the printed
  number tidy.
- **`bimodal_sample`, seed 21 at separation 0.85 and spread 0.95.**
  Chosen by scanning a grid of separations, spreads, sample sizes and
  seeds for a case where Sturges' rule and the Freedman-Diaconis rule
  genuinely disagree. **Most parameter settings do not disagree.** The
  claim is that the disagreement is *possible* with two citable rules,
  not that it is typical. Any stronger reading of exercise 5 than that
  is not supported by what was run here.

## What was not run

No BI tool — Tableau, Power BI, Looker Studio — was installed or executed
anywhere in this lab or its lesson. Everything said about their default
behaviour comes from their published documentation and is marked as such
in the lesson. No output from any of them is reproduced here.
