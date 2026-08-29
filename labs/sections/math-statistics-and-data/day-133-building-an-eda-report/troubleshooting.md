# Troubleshooting

## `pytest: command not found`, or the harness exits before any check

You have not created the lab's virtual environment, or you are calling
bare `pytest` rather than the one in `.venv`.

```bash
cd labs/sections/math-statistics-and-data/day-133-building-an-eda-report
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
bash tests/run_tests.sh
```

The harness looks for `.venv/bin/pytest` first, then anything on your
PATH. To point it at an interpreter of your own:

```bash
PYTEST=/path/to/pytest bash tests/run_tests.sh
```

## `E   ImportError while loading conftest` or `ModuleNotFoundError: No module named 'report'`

You ran pytest from the wrong directory, or with an import mode that does
not put the test file's own directory on `sys.path`. Run from the lab
directory and name the directory, not the file:

```bash
.venv/bin/pytest starter          # correct
.venv/bin/pytest starter/test_report.py   # also fine
cd starter && pytest .            # also fine
```

## `import file mismatch` and a collection error

You ran `pytest examples starter` in one command. `starter/test_report.py`
and `examples/test_report.py` have the same module name, and pytest
collects test modules by dotted name, so the second import collides with
the first. Run them as two commands:

```bash
.venv/bin/pytest starter -q
.venv/bin/pytest examples -q
```

Section 5 of the harness runs the combined form deliberately and asserts
it fails, so this is a documented behaviour rather than a surprise.

## A window tries to open, or `RuntimeError: main thread is not in main loop`

Something imported `matplotlib.pyplot` before `matplotlib.use("Agg")`
ran. The backend can only be set before the first `pyplot` import.
`conftest.py` sets it on its second and third lines for exactly this
reason. If you added an import above it, move yours below. If you are
running the generator outside pytest, `report.py` sets `Agg` itself at
import — but only if `report` is the first thing that imports `pyplot`.

Belt and braces:

```bash
MPLBACKEND=Agg .venv/bin/pytest starter -q
```

## `version mismatch` in section 1 of the harness

The harness compares every installed version against
`requirements/requirements.txt` and reports any difference. This is a
real check, not a formality: `report.SAFE_PALETTE` is
`seaborn.color_palette("colorblind")` frozen as it stands in seaborn
0.13.2, and exercise 9 compares against it exactly.

If you cannot install the pins, the nine exercises will very likely still
pass on any matplotlib 3.x, pandas 2.2+ and NumPy 2.x.
`expected-output/FIELDS.md` records exactly which captured numbers are
version-sensitive.

## Exercise 6 fails on the figure bytes

Exercise 6 asserts that two renders of the same input produce identical
PNG bytes. That comparison is between **two runs in the same session on
the same machine**, and it should hold. If it does not, the usual cause is
that something non-deterministic crept into a `draw` function — a
`random` call without a seed, a dictionary iterated in a different order,
or a colour picked from a set.

What this assertion never claims is that your PNG bytes match the bytes
on some other machine. They legitimately may not: matplotlib rasterises
text through FreeType, and a different FreeType build or a different set
of installed fonts produces different pixels from identical code. The
byte-identity that the lesson leans on is the **Markdown**, which contains
no rendered glyphs at all.

## Exercise 3 passes but the numbers look identical

If the West's percentage is the same for `monthly_sales()` and
`perturbed()`, you rendered the same frame twice. `build_report(frame)`
and `render(directory, frame)` both take the frame, and they must be the
same one:

```python
changed = data.perturbed()
markdown = analysis.build_report(changed).render(directory, changed)   # both `changed`
```

Passing `monthly_sales()` to one and `perturbed()` to the other produces a
document whose figures and prose disagree — which is, with some irony,
precisely the failure the exercise exists to prevent.

## `ReportError` when you did not expect one

That is usually the generator doing its job. The three messages:

| Message contains | What it means |
| --- | --- |
| `no stated question` | The candidate's `question` is `None` or blank |
| `has a question but no way to answer it` | `draw` or `analyse` is `None` |
| `label, not a claim` | The caption has no number and no comparative word |

The third is the one that surprises people. `"revenue by region"` is a
label. `"revenue fell 12% in the West"` is a claim. The check cannot tell
whether the claim is true — only that one was made.

## The lab left something behind

It should not, and section 7 of the harness checks. If you find a stray
directory, it is almost certainly from a manual render you did yourself
rather than from the tests:

```bash
find . -path ./.venv -prune -o -type d -name '__pycache__' -print -exec rm -rf -- {} +
rm -rf .pytest_cache out
```

## Windows

Use WSL2 and follow the Linux instructions. Native Windows works for the
Python parts if you substitute `.venv\Scripts\python.exe` and
`.venv\Scripts\pytest.exe`, but `tests/run_tests.sh` is a bash script and
needs Git Bash or WSL; it will not run in `cmd.exe` or PowerShell.
