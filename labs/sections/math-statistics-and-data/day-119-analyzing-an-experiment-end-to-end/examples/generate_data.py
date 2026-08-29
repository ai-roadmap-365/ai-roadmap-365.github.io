"""Generate `../data/exp_a.csv` and `../data/exp_b.csv` from the parameters in
`dataset.py`. Deterministic: run it twice, get byte-identical files.

    python3 generate_data.py

Every row gets a user_id, a group, a segment, the primary metric
(`converted`), a guardrail metric (`latency_ms`) and a secondary continuous
metric (`time_on_page_sec`). Rows are written in a shuffled "arrival order"
-- not grouped by arm -- because exercise 8 walks the file in order to
simulate watching the experiment run live.
"""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np

import dataset as D

HERE = Path(__file__).parent
DATA_DIR = HERE.parent / "data"


def _draw_group(
    rng: np.random.Generator,
    segments: tuple,
    latency_control: tuple[float, float],
    latency_treatment: tuple[float, float],
    user_id_start: int,
) -> list[dict]:
    rows: list[dict] = []
    uid = user_id_start
    for entry in segments:
        if len(entry) == 4:
            segment, n_control, n_treatment, control_rate = entry
            treatment_rate = control_rate + D.A_TRUE_LIFT_PP
        else:
            segment, n_control, n_treatment, control_rate, treatment_rate = entry

        for group, n, rate, latency_params in (
            ("control", n_control, control_rate, latency_control),
            ("treatment", n_treatment, treatment_rate, latency_treatment),
        ):
            converted = rng.random(n) < rate
            latency = rng.normal(latency_params[0], latency_params[1], size=n)
            time_on_page = rng.lognormal(D.TIME_ON_PAGE_MU, D.TIME_ON_PAGE_SIGMA, size=n)
            is_outlier = rng.random(n) < D.OUTLIER_FRACTION
            n_outliers = int(is_outlier.sum())
            if n_outliers:
                time_on_page[is_outlier] = rng.uniform(
                    D.OUTLIER_RANGE_SEC[0], D.OUTLIER_RANGE_SEC[1], size=n_outliers
                )
            for i in range(n):
                rows.append(
                    {
                        "user_id": uid,
                        "group": group,
                        "segment": segment,
                        "converted": int(converted[i]),
                        "latency_ms": round(float(latency[i]), 2),
                        "time_on_page_sec": round(float(time_on_page[i]), 2),
                    }
                )
                uid += 1
    return rows


def generate_a() -> list[dict]:
    rng = np.random.default_rng(D.SEED_A)
    return _draw_group(rng, D.A_SEGMENTS, D.A_LATENCY_CONTROL, D.A_LATENCY_TREATMENT, 1)


def generate_b() -> list[dict]:
    rng = np.random.default_rng(D.SEED_B)
    return _draw_group(rng, D.B_SEGMENTS, D.B_LATENCY_CONTROL, D.B_LATENCY_TREATMENT, 1)


def write_csv(rows: list[dict], path: Path, shuffle_seed: int) -> None:
    rng = np.random.default_rng(shuffle_seed)
    order = rng.permutation(len(rows))
    shuffled = [rows[i] for i in order]
    fieldnames = ["user_id", "group", "segment", "converted", "latency_ms", "time_on_page_sec"]
    with path.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(shuffled)


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    rows_a = generate_a()
    rows_b = generate_b()
    # exp_a's arrival order is fixed at shuffle seed 2 deliberately, not seed
    # 1: it is the order that gives exercise 8's peeking walk a p-value path
    # that dips in and out of significance before settling -- exactly the
    # instability a fixed sample size protects you from. Seed 1 (and most
    # other seeds) happens to look significant from the very first checkpoint
    # on this same underlying data, which is a fine outcome but a much
    # weaker lesson. The underlying rows and their true group labels are
    # identical either way; only the order they "arrive" in changes.
    write_csv(rows_a, DATA_DIR / "exp_a.csv", shuffle_seed=2)
    write_csv(rows_b, DATA_DIR / "exp_b.csv", shuffle_seed=D.SEED_B + 1)
    print(f"wrote {len(rows_a)} rows to {DATA_DIR / 'exp_a.csv'}")
    print(f"wrote {len(rows_b)} rows to {DATA_DIR / 'exp_b.csv'}")


if __name__ == "__main__":
    main()
