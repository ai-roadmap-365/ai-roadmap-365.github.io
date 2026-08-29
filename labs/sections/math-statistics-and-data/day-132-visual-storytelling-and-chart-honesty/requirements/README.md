# Requirements

`requirements.txt` pins the exact versions this lab was executed against
on 2026-08-20. They are pins, not minimums: the captured numbers in
`expected-output/` came from these versions, and `tests/run_tests.sh`
checks each installed version against this file so a mismatch is reported
rather than silently producing different figures.

```
matplotlib==3.11.1
seaborn==0.13.2
pandas==3.0.5
numpy==2.5.2
pytest==9.1.1
```

Install them into a lab-local virtual environment:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
```

That one `pip install` is the only step that touches the network.
Everything afterwards runs offline.

`seaborn` is used in exactly one place — reading the first two colours of
its `colorblind` palette in exercise 8 — and `pandas` in exactly one,
attaching real weekly dates to the cherry-picked-window series in
exercise 4. Both are genuinely executed here; neither is decorative.

matplotlib runs on the `Agg` backend, which needs no display server and
no GUI toolkit. Nothing in this lab opens a window and nothing calls
`plt.show()`, so it works identically over SSH, in a container and in
continuous integration.
