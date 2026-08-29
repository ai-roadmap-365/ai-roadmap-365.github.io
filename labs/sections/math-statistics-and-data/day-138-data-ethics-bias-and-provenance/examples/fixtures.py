"""Fixture data for the Day 138 lab. All of it is invented for teaching.

There is no real dataset anywhere in this lab, and that is deliberate. A
lesson about who is missing from a dataset should not be taught by taking
a dataset about real people whose consent nobody in this room obtained,
and a synthetic population has a property no real one has: its true
composition is known exactly, so "the sample under-represents group B by a
factor of ten" is a checkable fact rather than an estimate.

Every name here is invented. Every number is chosen to make a mechanism
visible.
"""

from __future__ import annotations

from typing import Any

# ---------------------------------------------------------------------------
# Exercise 2 -- the reference population the sample claims to describe
# ---------------------------------------------------------------------------

#: What the published statistical abstract says the population looks like.
#: This is the "reference distribution" the coverage check needs: without
#: one, a sample's composition cannot be judged at all, only described.
REFERENCE_SHARES: dict[str, float] = {
    "north": 0.40,
    "south": 0.35,
    "east": 0.15,
    "west": 0.10,
}

#: What the survey actually collected. The west is reached at a tenth of
#: the rate the reference population says it should be -- the survey ran by
#: telephone during working hours, and the west's shift patterns are
#: different. Every other region is close to its reference share.
SURVEY_COUNTS: dict[str, int] = {
    "north": 4_200,
    "south": 3_700,
    "east": 1_600,
    "west": 100,
}

# ---------------------------------------------------------------------------
# Exercise 8 -- datasheets, complete and incomplete
# ---------------------------------------------------------------------------

#: A dataset shipped the way most datasets are shipped: a file, a title,
#: and a vague sense that somebody official produced it. Seven of the eleven
#: required provenance fields are absent, one is present but empty, and one
#: is present but null. Each of those is a different way of not answering.
INCOMPLETE_DATASHEET: dict[str, Any] = {
    "collector": "Regional Statistics Office",
    "collection_period": "2025",
    "purpose": "",
    "population_definition": None,
    "licence": "CC-BY-4.0",
}

#: The same dataset, documented. Nothing here is harder to produce than the
#: file itself; it is simply written down at the time rather than
#: reconstructed from memory two years later by somebody who was not there.
COMPLETE_DATASHEET: dict[str, Any] = {
    "collector": "Regional Statistics Office, Household Surveys Unit",
    "collection_period": "2025-01-06/2025-12-19",
    "purpose": (
        "Quarterly regional labour-force estimates for internal planning; "
        "not designed for small-area or sub-annual estimates"
    ),
    "population_definition": (
        "Residents aged 16 and over in private households in the four "
        "administrative regions"
    ),
    "sampling_frame": (
        "Landline and mobile telephone numbers on the national directory, "
        "called between 09:00 and 17:00 on weekdays"
    ),
    "inclusion_criteria": [
        "aged 16 or over on the first day of the reference week",
        "resident in a private household",
        "answered and consented to the full interview",
    ],
    "exclusion_criteria": [
        "communal establishments (halls of residence, care homes, barracks)",
        "households with no telephone number on the directory",
        "partial interviews terminated before the employment block",
    ],
    "known_gaps": [
        "the west region is reached at roughly a tenth of its population "
        "share because daytime calling misses its dominant shift pattern",
        "no coverage of communal establishments at all",
    ],
    "licence": "CC-BY-4.0",
    "version": "3.1.0",
    "changelog": [
        "3.0.0 first public release",
        "3.1.0 corrected regional weights for the east; no change to raw responses",
    ],
}

#: The eleven required fields, restated here so a learner can see the target
#: without opening ``ethics.py``. Kept in the same order as
#: ``ethics.DATASHEET_REQUIRED_FIELDS``.
EXPECTED_MISSING_FROM_INCOMPLETE: list[str] = [
    "purpose",
    "population_definition",
    "sampling_frame",
    "inclusion_criteria",
    "exclusion_criteria",
    "known_gaps",
    "version",
    "changelog",
]

# ---------------------------------------------------------------------------
# Named proxies, for the exercise that asks you to say what you are actually
# measuring. Each pair is (the proxy in the data, the thing it stands in for).
# ---------------------------------------------------------------------------

PROXY_PAIRS: tuple[tuple[str, str], ...] = (
    ("arrests recorded", "offences committed"),
    ("clicks", "interest"),
    ("diagnosis codes billed", "disease present"),
    ("prior spending on care", "need for care"),
    ("hours logged in the tracker", "work done"),
)
