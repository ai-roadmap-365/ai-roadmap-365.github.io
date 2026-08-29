"""The datasets for Day 137 -- "Features That Do Not Cheat".

Every generator here is seeded and returns exactly the same rows on every
machine, so every number this lab asserts is reproducible rather than
sampled. Nothing is downloaded; nothing touches the network.

Six generators, one per experiment:

* `signups`          -- a conversion table carrying one planted target leak
* `pricing`          -- a heavy-tailed feature for the scaling experiment
* `city_signups`     -- 40 city codes for the target-encoding experiment
* `sensor_log`       -- a time-ordered table whose rule changes by regime
* `paint_orders`     -- unordered colours for the ordinal-encoding trap
* `credit_lines`     -- spend and income that only separate as a ratio
* `tickets`          -- short documents for the bag-of-words experiment

Read the docstrings before the code: each one states what the honest
signal is and, where a leak is planted, exactly where it was planted.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

SEED = 137


def _sigmoid(z: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-z))


def signups(n: int = 400, seed: int = SEED) -> pd.DataFrame:
    """A conversion table with three honest features and one planted leak.

    Honest: `visits`, `minutes_on_site`, `discount_pct`. The label
    `converted` is drawn from a logistic model of those three, so the
    honest signal is real but far from perfect.

    Planted leak: `days_to_first_invoice`. An invoice only exists once a
    visitor has converted, so the column is a positive number for every
    converted row and the sentinel -1 for every unconverted one. At
    prediction time -- before the visitor has decided -- this column
    cannot exist at all. It is the outcome, wearing a different name.
    """
    rng = np.random.default_rng(seed)
    visits = rng.integers(1, 30, n)
    minutes = rng.gamma(2.0, 6.0, n)
    discount = rng.choice([0, 5, 10, 20], n)
    logit = -2.4 + 0.08 * visits + 0.045 * minutes + 0.035 * discount
    converted = (rng.random(n) < _sigmoid(logit)).astype(int)
    days = np.where(converted == 1, rng.integers(1, 15, n), -1)
    return pd.DataFrame(
        {
            "visits": visits.astype(float),
            "minutes_on_site": minutes,
            "discount_pct": discount.astype(float),
            "days_to_first_invoice": days.astype(float),
            "converted": converted,
        }
    )


def pricing(n: int = 500, seed: int = SEED + 1) -> pd.DataFrame:
    """A two-feature table whose first feature is heavy-tailed.

    `order_value` is lognormal, so a handful of rows sit two orders of
    magnitude above the median. A scaler fitted on all the data sees
    those rows wherever they fall; a scaler fitted on the training half
    only sees the ones that landed in training. That difference is the
    whole point of the scaling experiment, and it is why the feature is
    heavy-tailed rather than Gaussian: with a well-behaved feature the
    two scalers agree to three decimals and there is nothing to see.
    """
    rng = np.random.default_rng(seed)
    order_value = rng.lognormal(mean=3.0, sigma=1.4, size=n)
    tenure_days = rng.gamma(3.0, 90.0, size=n)
    logit = -1.1 + 0.55 * np.log(order_value) - 0.004 * tenure_days
    renewed = (rng.random(n) < _sigmoid(logit)).astype(int)
    return pd.DataFrame(
        {
            "order_value": order_value,
            "tenure_days": tenure_days,
            "renewed": renewed,
        }
    )


def panel_readings(
    n: int = 600,
    n_panels: int = 120,
    missing_rate: float = 0.60,
    seed: int = SEED + 7,
) -> pd.DataFrame:
    """Readings with a lot of gaps, grouped into small panels.

    Each solar panel has its own characteristic output, and `reading` is
    that output plus noise. `fault` depends on the reading. Sixty per
    cent of the readings are missing, and with 120 panels over 600 rows
    a panel holds five rows on average -- so a group mean fitted on a
    small training set is often estimated from one row, or from none.

    That is what makes group-mean imputation the sharpest available
    demonstration of a statistic fitted before the split. Impute over the
    whole table and a test row's gap is filled from the observed readings
    of its own panel, including the ones sitting in the test set.
    """
    rng = np.random.default_rng(seed)
    panel = rng.integers(0, n_panels, n)
    panel_output = rng.normal(0.0, 2.0, n_panels)
    reading = panel_output[panel] + rng.normal(0.0, 0.5, n)
    fault = (rng.random(n) < _sigmoid(1.2 * reading)).astype(int)
    observed = rng.random(n) >= missing_rate
    return pd.DataFrame(
        {
            "panel": pd.Series([f"P{p:03d}" for p in panel], dtype="str"),
            "reading": np.where(observed, reading, np.nan),
            "fault": fault,
        }
    )


def city_signups(n: int = 600, n_cities: int = 40, seed: int = SEED + 2) -> pd.DataFrame:
    """High-cardinality categories for the target-encoding experiment.

    40 city codes over 600 rows is 15 rows per city on average, which is
    exactly the regime where a per-category mean of the target is mostly
    noise. The cities do carry a small real effect, so an honest encoding
    is not useless -- it is just far less impressive than the naive one
    pretends.
    """
    rng = np.random.default_rng(seed)
    city = rng.integers(0, n_cities, n)
    city_effect = rng.normal(0.0, 0.35, n_cities)
    visits = rng.integers(1, 20, n)
    logit = -0.3 + 0.05 * (visits - 10) + city_effect[city]
    converted = (rng.random(n) < _sigmoid(logit)).astype(int)
    return pd.DataFrame(
        {
            "city": pd.Series([f"C{c:02d}" for c in city], dtype="str"),
            "visits": visits.astype(float),
            "converted": converted,
        }
    )


#: Alarm rate per calibration batch, in batch order. A batch is a period
#: of time, and the rate changes when the hardware is recalibrated.
BATCH_ALARM_RATE = [0.85, 0.15, 0.88, 0.12, 0.90, 0.10]


def sensor_log(per_batch: int = 60, seed: int = SEED + 3) -> pd.DataFrame:
    """A time-ordered table whose batches are periods of time.

    Rows come back in time order. `batch` is the calibration batch the
    sensor was running under, so a batch is not scattered through the
    table -- it occupies one contiguous stretch of it. The alarm rate
    changes sharply from batch to batch (a recalibration, a firmware
    change, a new supplier), while `reading` carries a mild, stable
    effect that holds across all of them.

    That combination is what a random split hides. Split at random and
    every batch has rows in training, so the model learns each batch's
    alarm rate from rows recorded at the same time as the ones it is
    scored on -- information from after the prediction moment. Split by
    time and the last batch is one the model has never seen, which is the
    situation every deployed model is actually in.
    """
    rng = np.random.default_rng(seed)
    frames = []
    for batch, rate in enumerate(BATCH_ALARM_RATE):
        reading = rng.normal(50.0, 6.0, per_batch)
        humidity = rng.normal(40.0, 9.0, per_batch)
        logit = np.log(rate / (1 - rate)) + 0.05 * (reading - 50.0)
        alarm = (rng.random(per_batch) < _sigmoid(logit)).astype(int)
        frames.append(
            pd.DataFrame(
                {
                    "batch": pd.Series([f"B{batch}"] * per_batch, dtype="str"),
                    "reading": reading,
                    "humidity": humidity,
                    "alarm": alarm,
                }
            )
        )
    out = pd.concat(frames, ignore_index=True)
    out.insert(0, "t", np.arange(len(out), dtype=int))
    return out


PAINT_COLOURS = ["amber", "cobalt", "ivory", "olive", "rose", "slate"]

#: The true return rate per colour, in the same order as PAINT_COLOURS.
#: Deliberately NOT monotone in the list position: ivory (code 2) is the
#: worst and cobalt (code 1) the best, so any model that can only move
#: monotonically with the code is guaranteed to be wrong somewhere.
PAINT_RETURN_RATE = [0.20, 0.08, 0.72, 0.15, 0.62, 0.25]


def paint_orders(per_colour: int = 200, seed: int = SEED + 4) -> pd.DataFrame:
    """Unordered categories with a deliberately non-monotone outcome.

    Colour names have no order. Alphabetical position is not a quantity,
    which is exactly why an ordinal code invites a model to interpolate
    between categories that have no midpoint.
    """
    rng = np.random.default_rng(seed)
    colours: list[str] = []
    returned: list[int] = []
    for name, rate in zip(PAINT_COLOURS, PAINT_RETURN_RATE):
        colours.extend([name] * per_colour)
        returned.extend((rng.random(per_colour) < rate).astype(int).tolist())
    return pd.DataFrame(
        {
            "colour": pd.Series(colours, dtype="str"),
            "returned": np.array(returned, dtype=int),
        }
    )


def credit_lines(n: int = 500, seed: int = SEED + 5) -> pd.DataFrame:
    """Spend and income whose marginals overlap but whose ratio does not.

    Income is drawn from the same distribution for both classes. Spend is
    income times a ratio drawn per class, and the two ratio bands do not
    overlap. So neither column separates the classes on its own, while
    `spend / income` separates them completely. This is an interaction in
    the plainest possible form.
    """
    rng = np.random.default_rng(seed)
    label = (rng.random(n) < 0.5).astype(int)
    income = rng.uniform(30_000, 140_000, n)
    ratio = np.where(label == 1, rng.uniform(0.52, 0.68, n), rng.uniform(0.32, 0.48, n))
    spend = income * ratio
    return pd.DataFrame(
        {
            "income": income,
            "spend": spend,
            "stressed": label,
        }
    )


#: The corpus vocabulary and each word's pull towards "urgent". No word
#: is decisive: the largest effect only doubles a word's odds of turning
#: up, so a document is classified by the whole bag or not at all.
TICKET_WORDS = [
    "outage", "refund", "broken", "charged", "cancel", "waiting",
    "thanks", "question", "hello", "curious", "manual", "hours",
    "order", "account", "team", "please", "about", "with", "the", "and",
]
TICKET_EFFECT = [
    0.40, 0.34, 0.38, 0.30, 0.36, 0.26,
    -0.40, -0.32, -0.36, -0.28, -0.34, -0.24,
    0.06, -0.05, 0.04, -0.03, 0.02, -0.02, 0.01, -0.01,
]


def tickets(n: int = 300, seed: int = SEED + 6) -> pd.DataFrame:
    """Short support tickets, each a bag of lower-case words.

    Every document draws its words from one shared pool; the label only
    tilts the odds. Twelve words carry a real but modest pull and eight
    carry essentially none, so no single word settles a document and the
    classifier has to add evidence up.

    On top of that sits a long tail of reference codes, each appearing in
    only a handful of documents corpus-wide. Those are the words that
    make the choice of vocabulary consequential: a code that turns up
    three times and happens to land twice on an urgent ticket looks like
    a strong feature to anything that scores words against the label.
    """
    rng = np.random.default_rng(seed)
    effect = np.array(TICKET_EFFECT, dtype=float)
    rows: list[str] = []
    labels: list[int] = []
    for _ in range(n):
        urgent = int(rng.random() < 0.5)
        sign = 1.0 if urgent else -1.0
        weights = np.exp(sign * effect)
        weights = weights / weights.sum()
        length = int(rng.integers(8, 15))
        words = rng.choice(TICKET_WORDS, size=length, replace=True, p=weights).tolist()
        if rng.random() < 0.35:
            words.append(f"ref{int(rng.integers(0, 80)):02d}")
        rows.append(" ".join(words))
        labels.append(urgent)
    return pd.DataFrame(
        {
            "text": pd.Series(rows, dtype="str"),
            "urgent": np.array(labels, dtype=int),
        }
    )
