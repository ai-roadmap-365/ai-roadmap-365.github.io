"""The green suite. Every one of these tests passes on the buggy catalog.py.

That is the point of the lab, so do not "improve" this file until the very
last exercise. Read it and ask, for each test, which line of catalog.py it
never reaches. The two bugs live on exactly those lines.
"""

import catalog


def test_find_known_model() -> None:
    model = catalog.find_model("small")
    assert model is not None
    assert model.context_tokens == 8_000


def test_find_unknown_model_returns_none() -> None:
    assert catalog.find_model("enormous") is None


def test_describe_known_model() -> None:
    assert catalog.describe("small") == "small: 8,000 token context"


def test_describe_large_model() -> None:
    assert catalog.describe("large") == "large: 200,000 token context"


def test_estimate_cost_of_one_million_tokens() -> None:
    assert catalog.estimate_cost("medium", 1_000_000) == 3.0


def test_estimate_cost_rejects_unknown_model() -> None:
    try:
        catalog.estimate_cost("enormous", 1_000)
    except KeyError:
        return
    raise AssertionError("expected a KeyError for an unknown model")


def test_split_cost_divides_evenly() -> None:
    assert catalog.split_cost("medium", 1_000_000, 2) == 1.5


def test_price_line() -> None:
    assert catalog.price_line("large") == "large: $15.00 per million tokens"
