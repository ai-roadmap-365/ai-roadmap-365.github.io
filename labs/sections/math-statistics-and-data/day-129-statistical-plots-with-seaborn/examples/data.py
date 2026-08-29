"""The tables every exercise in this lab is built from.

Nothing here is randomised or loaded from a file -- every table is a small
literal so a reader can check every asserted number by eye against the
source. Two tables carry the whole lab:

`team_scores` -- exercises 2, 3, 4, 7 and 9. Four teams, four observations
each. Team B's four scores are 90, 88, 92, 10 -- three of the four highest
scores in the entire dataset, dragged down by one bad observation to a
group mean (70.0) lower than team A's (79.0), whose four scores are all
unremarkable and close together. This is the lab's through-line: a bar
chart of the mean tells you B did worse than A. A strip chart of the same
four points each shows the opposite story.

`wide_revenue` / its melted form `long_revenue` -- exercises 1, 5 and 6.
One row per region in wide form (a `q1`..`q4` column each); one row per
region-quarter observation in long form, produced with the exact `melt`
call Day 124 taught.
"""

from __future__ import annotations

import pandas as pd

# --------------------------------------------------------------------------
# `team_scores` -- the barplot trap. Four teams, four observations each.
#
# Team A: 78, 82, 80, 76 -- mean 79.0, all four values close together.
# Team B: 90, 88, 92, 10 -- mean 70.0, but three of four are the highest
#          individual scores in the whole table; one outlier (10) drags
#          the mean below team A's despite B's typical performance being
#          the best in the dataset.
# Team C: 65, 70, 68, 67 -- mean 67.5.
# Team D: 55, 60, 58, 57 -- mean 57.5.
# --------------------------------------------------------------------------


def build_team_scores() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "team": ["A", "A", "A", "A", "B", "B", "B", "B", "C", "C", "C", "C", "D", "D", "D", "D"],
            "score": [78, 82, 80, 76, 90, 88, 92, 10, 65, 70, 68, 67, 55, 60, 58, 57],
        }
    )


# --------------------------------------------------------------------------
# `wide_revenue` -- exercises 1, 5 and 6. One row per region, one column
# per quarter. `melt` (Day 124) turns this into `long_revenue`: one row
# per (region, quarter) observation, which is what lets `hue="region"`
# and `col="region"` work at all.
# --------------------------------------------------------------------------


def build_wide_revenue() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "region": ["North", "South", "East", "West", "Central"],
            "q1": [120, 95, 110, 130, 88],
            "q2": [125, 98, 108, 128, 90],
            "q3": [130, 101, 115, 135, 95],
            "q4": [128, 105, 118, 140, 97],
        }
    )


def build_long_revenue() -> pd.DataFrame:
    return build_wide_revenue().melt(id_vars="region", var_name="quarter", value_name="revenue")
