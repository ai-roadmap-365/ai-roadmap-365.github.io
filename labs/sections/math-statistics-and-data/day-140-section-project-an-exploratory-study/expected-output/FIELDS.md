# What is exact, what is sampled, and what is machine-dependent

Captured on 2026-08-20 from a real run on the authoring machine (macOS
26.5.2, Apple Silicon, arm64, Python 3.14.0, NumPy 2.5.2, pandas 3.0.5,
matplotlib 3.11.1, pytest 9.1.1), through a lab-local `.venv` created by the
documented setup commands. Every number below came from that run; none is
invented.

## Exact everywhere, on any correct implementation

These are fixed by the seeded generator and by arithmetic, not by sampling.
They are the same on any machine that installs the pinned versions.

- The raw delivery is **264 rows**; **245** survive cleaning; **19** are
  removed (7.20% of the delivery).
- The four damage-report measurements: distinct `station_type` values
  8 -> 2; rows 264 -> 256; fault-sentinel rows 6 -> 0; blank-PM2.5 rows
  5 -> 0.
- **8** rows violate the declared grain on arrival, and **0** after cleaning.
- The exploration/confirmation split is **122 / 123** readings.
- The research log records **4** exploration looks, so the reported
  comparison count is **4**.
- The measured difference on the confirmation half is **5.50 ug/m3**, with a
  95% interval of **3.80 to 7.21**, on n=60 roadside and n=63 park readings.
  The generator plants a true difference of **6.00**, which falls inside that
  interval.
- The two-sided z critical value for a 95% interval, computed by bisecting
  `phi`: **1.959964** (to six decimal places).
- The worked study writes exactly **11 files**; the harness runs exactly
  **8 gates**.
- The final line of a passing `run_tests.sh`: `81 checks, 0 failure(s).`
- `pytest examples` reports **54 passed**; `pytest starter` on an untouched
  checkout reports **1 passed, 32 skipped**; a fully solved `starter/`
  reports **33 passed**.

## Digests: exact for text, expected to differ for the figures

`worked-study-manifest.txt` lists a SHA-256 for every file the study
generates. They are not all equally portable, and the distinction matters
because gate 8 compares them.

- The **text digests** (`CLEANING.md`, `FIGURES.json`, `INGEST.json`,
  `QUESTION.md`, `REPORT.md`, `RESEARCH_LOG.md`, `SOURCE.json`,
  `data/observations.csv`) are byte-stable for a given pandas and NumPy
  version. `data/observations.csv` hashes to
  `8323f91e...1157a4e` here; `SOURCE.json` embeds that hash, so if the CSV
  digest ever moves, `SOURCE.json`'s moves with it.
- The **two PNG digests are machine-dependent** and are the one thing in
  this lab expected to differ on another computer. Matplotlib rasterises
  text with the fonts it finds, and a different font file, FreeType build or
  matplotlib version produces different bytes for a visually identical
  chart. **Nothing in the harness asserts a PNG digest against a stored
  literal.** What is asserted is the property that matters: two builds *on
  the same machine* produce identical bytes, checked by rebuilding and
  comparing rather than by looking a value up.

## Reproducibility, and exactly what it does and does not claim

`08-reproducibility.txt` shows every generated file identical across two
independent builds, figures included. That was measured, not assumed, and it
holds because `study.py` reads no clock, seeds every draw, wraps its report
with `textwrap.fill` rather than by hand, and saves PNGs with
`metadata={"Software": None}` so the matplotlib-version tag is not written
into the file.

The claim is **same machine, same pinned versions, same seeds, identical
bytes**. It is not a claim that the figures hash the same on your machine as
on the authoring one; see above.

## Paths sanitised in the captured output

The example scripts build their studies in a temporary directory, so their
real output contains a path like
`/var/folders/.../T/tmpXXXXXXXX/study` on macOS or `/tmp/tmpXXXXXXXX/study`
on Linux. Those have been replaced with `<tmp>` in the captured files. One
consequence worth flagging: in `09-whole-harness.txt`, the
`FileNotFoundError` line is truncated to 44 characters by the script before
printing, so on a real run it reads as a truncated real path with a trailing
`...`, not as `<tmp>/nowhere`. Everything else in that file is verbatim.

## Machine-dependent, described but not asserted on

- The `platform` line in section 1 of `run_tests.sh`'s output reads
  `macOS-26.5.2-arm64-arm-64bit-Mach-O` here and will read differently on
  Linux or Windows/WSL. Nothing in the harness checks its content, only that
  the four installed versions match `requirements.txt`.
- Every wall-clock figure (`54 passed in 0.90s` and similar) is hardware
  dependent. No test asserts on a timing anywhere in this lab.
- The scratch directory `run_tests.sh` creates with `mktemp -d` has a
  different name every run and is removed by an `EXIT` trap.

## Nothing here is sampled

Unusually for this section, there is no tolerance anywhere in this lab. Every
figure is either fixed arithmetic or fixed by a seed, so every assertion is
an equality. The one statistical statement — that the planted 6.00 difference
falls inside the measured 95% interval — is checked as a fact about this
seed's interval, not as a coverage rate over repeated samples.
