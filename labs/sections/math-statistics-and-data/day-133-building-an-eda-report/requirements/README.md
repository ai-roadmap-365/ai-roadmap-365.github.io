# Requirements

`requirements.txt` pins the exact versions this lab was written and run
against on 2026-08-20. Everything else it uses — `hashlib`, `re`,
`shutil`, `tempfile`, `dataclasses`, `pathlib` — is in the Python
standard library.

Install into a lab-local virtual environment so the pins cannot collide
with anything else on your machine:

```bash
cd labs/sections/math-statistics-and-data/day-133-building-an-eda-report
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
```

Only that install step needs the network. Everything after it runs
offline: the lab reads no URL, opens no socket, and needs no API key.

## Why the pins are exact

Section 1 of `tests/run_tests.sh` compares every installed version against
this file and fails on a mismatch. That is deliberate. Two of this lab's
measured facts are version-sensitive:

- the colourblind-safe palette in `report.SAFE_PALETTE` is
  `seaborn.color_palette("colorblind")` as it stands in seaborn 0.13.2,
  frozen to hex so the accessibility check has an exact set to compare
  against;
- the byte-identity of the rendered PNGs in exercise 6 is a property of
  one matplotlib build with one font stack. It is asserted only across two
  runs on the same machine, which is where the guarantee actually holds.

`seaborn` is pinned because `SAFE_PALETTE` came from it, even though the
lab's own drawing code calls matplotlib directly.

## If a pin will not install

Any recent matplotlib 3.x, pandas 2.2+ or NumPy 2.x will almost certainly
run the lab. The version check in section 1 of the harness will complain;
the nine exercises should still pass. If they do not, `expected-output/FIELDS.md`
records exactly which captured values are version-sensitive and which are
exact everywhere.
