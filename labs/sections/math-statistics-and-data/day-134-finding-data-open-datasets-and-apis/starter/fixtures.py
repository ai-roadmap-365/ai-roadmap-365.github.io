"""Fixture data for Day 134's exercises. Not itself an exercise -- read
alongside ``00_brief.md`` when the tests reference these names.

``DICTIONARY_A`` and ``DICTIONARY_B`` are two data dictionaries (codebooks)
for two fictional sources that both publish a column called
``unemployment_rate``. The columns below are built so that a naive check
-- same dtype, overlapping range -- passes on both, and only the
dictionaries' prose reveals that they are not the same measurement. That
gap is the lesson's opening failure story, made into fixtures.
"""

from __future__ import annotations

import pandas as pd

DICTIONARY_A: dict = {
    "name": "national-labour-force-survey",
    "fields": {
        "unemployment_rate": {
            "definition": (
                "share of the labour force not employed, actively seeking "
                "work in the last 4 weeks, and available to start within 2 weeks"
            ),
            "unit": "percent",
        }
    },
    "expected_regions": ["north", "south", "east", "west"],
}

DICTIONARY_B: dict = {
    "name": "administrative-benefit-claims-index",
    "fields": {
        "unemployment_rate": {
            "definition": (
                "share of the working-age population not currently employed, "
                "counted regardless of whether they are searching for work"
            ),
            "unit": "percent",
        }
    },
    "expected_regions": ["north", "south", "east", "west"],
}


def unemployment_series_a() -> "pd.Series":
    """From the labour-force-survey definition: job seekers only."""
    return pd.Series([4.1, 4.3, 4.0, 4.4, 5.2, 4.8], name="unemployment_rate")


def unemployment_series_b() -> "pd.Series":
    """From the administrative-claims definition: everyone not employed.

    Same dtype as series A, and its range (4.9-5.6) overlaps series A's
    range (4.0-5.2) -- the naive dtype-and-range check has nothing to flag.
    """
    return pd.Series([5.0, 5.4, 4.9, 5.6, 5.1, 5.3], name="unemployment_rate")


GOOD_SOURCE_METADATA: dict = {
    "granularity": "monthly, per region",
    "coverage": "national, 4 regions",
    "licence": "CC-BY-4.0",
    "dictionary": DICTIONARY_A,
    "update_cadence": "monthly, published on the 15th",
    "known_issues": ["one region was backfilled quarterly before 2020"],
}

DEFICIENT_SOURCE_METADATA: dict = {
    "granularity": "monthly",
    # coverage, licence, dictionary, update_cadence and known_issues all absent
}

NATIONAL_DATASET_KEYS: set = {"north", "south", "east"}
"""What a dataset that claims national coverage actually delivers here --
missing 'west', the gap Exercise 8 detects."""
