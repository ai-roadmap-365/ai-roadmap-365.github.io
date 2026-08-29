# Requirements

`requirements.txt` pins the exact versions this lab was written and run
against on 2026-08-20. Everything else it uses — `http.server`,
`urllib.request`, `hashlib`, `json`, `threading`, `dataclasses`, `datetime`
— is in the Python standard library. That is deliberate: the client code
this lab tests needs no third-party HTTP library at all.

Install into a lab-local virtual environment so the pins cannot collide
with anything else on your machine:

```bash
cd labs/sections/math-statistics-and-data/day-134-finding-data-open-datasets-and-apis
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
```

Only that install step needs the network. Everything after it runs
offline: the mock API in `mock_server.py` binds `127.0.0.1` on an
ephemeral port, so the tests exercise real HTTP without reaching anyone
else's machine.

## Why pandas is here at all

`fixtures.py` builds the two `unemployment_rate` series as `pandas.Series`
so Exercise 1's dtype-and-range check is the same kind of check you would
run on a real DataFrame column, not a hand-rolled substitute. `requests`
is not a dependency of this lab; the lesson describes it from its own
documentation and says plainly that it was not installed for this lab's
runs.

## If a pin will not install

Any recent pandas 2.2+ and pytest 7+ will almost certainly run this lab
unchanged — nothing here depends on a pandas 3.0-specific behaviour.
