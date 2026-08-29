"""The small synthetic dataset this lab's worked study is built on.

The study needs a source that is messy in *specific, nameable* ways, because
the point of the worked study is to show a damage report with real numbers in
it. So the frame is generated from a fixed seed with four deliberate defects:

  1. inconsistent casing and stray whitespace in `station_type`;
  2. eight duplicated `reading_id` values (the same reading delivered twice);
  3. six readings where the sensor emitted its fault sentinel, -1.0;
  4. five readings where `pm25_ug_m3` is simply blank.

Underneath the mess there is one real effect: roadside stations record higher
PM2.5 than park stations. The generator plants a true mean difference of
6.0 ug/m3 (roadside 18.0, park 12.0, both with a standard deviation of 5.0),
so the study has something honest to find, and the confirmation half has a
real chance of confirming it.

`observations.csv` in this directory is the saved output of
`generate_frame()`. It is committed so that the study has a genuine file on
disk with a genuine checksum, which is what the provenance gate checks.
`test_reference.py` asserts the committed file still matches the generator
byte for byte, so the two can never drift apart silently.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).parent.resolve()
SOURCE_CSV = HERE / "data" / "observations.csv"

DATASET_SEED = 140

ROADSIDE_STATIONS = ("ST-01", "ST-02", "ST-03", "ST-04")
PARK_STATIONS = ("ST-05", "ST-06", "ST-07", "ST-08")

ROADSIDE_MEAN = 18.0
PARK_MEAN = 12.0
PM25_SD = 5.0
TRUE_DIFFERENCE = ROADSIDE_MEAN - PARK_MEAN

READINGS_PER_STATION = 32
N_DUPLICATED = 8
N_SENTINEL = 6
N_BLANK = 5

FAULT_SENTINEL = -1.0

# The four casing variants the field units actually emit. Exactly one of them
# is the value the study wants; the other three are the same thing wearing a
# different coat, which is what the cleaning step measures.
CASINGS = ("roadside", "Roadside", "ROADSIDE", " roadside ")
PARK_CASINGS = ("park", "Park", "PARK", " park ")

ALPHA = 0.05


def generate_frame(seed: int = DATASET_SEED) -> pd.DataFrame:
    """Build the raw observation frame, defects and all, deterministically."""
    rng = np.random.default_rng(seed)

    stations = list(ROADSIDE_STATIONS) + list(PARK_STATIONS)
    rows = []
    for station in stations:
        roadside = station in ROADSIDE_STATIONS
        mean = ROADSIDE_MEAN if roadside else PARK_MEAN
        casings = CASINGS if roadside else PARK_CASINGS
        for day in range(READINGS_PER_STATION):
            rows.append(
                {
                    "station_id": station,
                    "captured_at": f"2026-06-{day + 1:02d}",
                    "station_type": casings[rng.integers(0, len(casings))],
                    "pm25_ug_m3": round(float(rng.normal(mean, PM25_SD)), 2),
                    "humidity_pct": round(float(rng.uniform(40.0, 90.0)), 1),
                    "temp_c": round(float(rng.uniform(15.0, 30.0)), 1),
                }
            )

    frame = pd.DataFrame(rows)
    # A stable id assigned in capture order, before any defect is introduced.
    frame.insert(0, "reading_id", [f"R{i + 1:04d}" for i in range(len(frame))])

    # Defect 3 and 4: the sensor fault sentinel, and outright blanks. Both are
    # chosen from disjoint index pools so a single row never carries two.
    damaged = rng.choice(frame.index, size=N_SENTINEL + N_BLANK, replace=False)
    sentinel_rows = damaged[:N_SENTINEL]
    blank_rows = damaged[N_SENTINEL:]
    frame.loc[sentinel_rows, "pm25_ug_m3"] = FAULT_SENTINEL
    frame.loc[blank_rows, "pm25_ug_m3"] = np.nan

    # Defect 2: eight readings delivered twice. The duplicate is byte-identical
    # to its original, which is exactly why a naive ingest never notices. The
    # rows are drawn from the undamaged pool so that each defect stays
    # separable in the damage report -- a duplicated blank would be two
    # defects on one row and would blur the before/after counts.
    undamaged = frame.index.difference(pd.Index(damaged))
    repeated = rng.choice(undamaged, size=N_DUPLICATED, replace=False)
    frame = pd.concat([frame, frame.loc[repeated]], ignore_index=True)

    # Delivery order is not capture order. Shuffle so nothing downstream can
    # accidentally depend on the rows arriving sorted.
    order = rng.permutation(len(frame))
    frame = frame.iloc[order].reset_index(drop=True)
    return frame


def write_source_csv(path: Path | None = None, seed: int = DATASET_SEED) -> Path:
    """Write the generated frame to CSV exactly as the committed file was."""
    target = Path(path) if path is not None else SOURCE_CSV
    target.parent.mkdir(parents=True, exist_ok=True)
    generate_frame(seed).to_csv(target, index=False, lineterminator="\n")
    return target


def load_source_csv(path: Path | None = None) -> pd.DataFrame:
    """Read the committed CSV the way an ingest step would: everything as
    text first, so nothing is silently coerced before the contract runs."""
    source = Path(path) if path is not None else SOURCE_CSV
    return pd.read_csv(source, dtype=str, keep_default_na=False)
