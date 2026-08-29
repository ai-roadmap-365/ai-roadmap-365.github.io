"""The same suite, run against the fixed catalogue.

The first eight tests are character for character the ones in
starter/test_catalog.py, and that is the point: fixing both type errors
changed no observable behaviour on any path a test walks. They were green
before and are green after.

The ninth test is new. It asks the question the old suite never asked — what
does describe() do with a name that is not in the catalogue? — and it is the
test you would only think to write after a checker pointed at that line.
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


def test_describe_unknown_model_no_longer_crashes() -> None:
    assert catalog.describe("enormous") == "enormous: unknown model"
