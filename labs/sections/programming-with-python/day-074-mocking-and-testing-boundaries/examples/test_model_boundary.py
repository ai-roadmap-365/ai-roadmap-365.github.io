"""Testing code that calls a language model, without calling a language model.

    pytest examples/test_model_boundary.py -q

Not one of these tests asserts that the model is clever, or correct, or good.
They assert that YOUR code puts the right numbers in the prompt, survives the
shapes the model actually returns, retries the right number of times, and fails
with a message a human can act on. All of that is deterministic, free, and
finishes in milliseconds.

Whether the model's answers are any good is a real question with a different
answer: an evaluation suite, run deliberately, against a dataset, reporting a
score rather than pass or fail. It is not a unit test and it does not belong in
this file.
"""

import datetime

import pytest
from fakes import RecordingSleep, ScriptedModel
from model_boundary import (
    MalformedResponse,
    ModelError,
    ModelUnavailable,
    Verdict,
    build_prompt,
    classify_day,
    parse_verdict,
)
from report_v2 import DailyReport

REPORT = DailyReport("ALPHA", datetime.date(2026, 4, 12), 24, 12.0, 22.0, 17.0)

GOOD_REPLY = "label: mild\nconfidence: 0.82\nnote: a calm spring day"


# --- the prompt you build ---------------------------------------------------


def test_the_prompt_contains_the_report_s_numbers():
    prompt = build_prompt(REPORT)
    assert "station: ALPHA" in prompt
    assert "date: 2026-04-12" in prompt
    assert "mean: 17.0" in prompt


def test_the_prompt_lists_the_labels_the_parser_will_accept():
    # If these two ever drift apart, every reply becomes malformed.
    assert "cold, mild, warm, hot" in build_prompt(REPORT)


# --- the replies you parse --------------------------------------------------


def test_a_well_formed_reply_parses():
    assert parse_verdict(GOOD_REPLY) == Verdict("mild", 0.82, "a calm spring day")


def test_a_chatty_reply_still_parses():
    # Models add preambles. Your parser meets the model where it is.
    assert parse_verdict("Sure! Here is the answer.\n" + GOOD_REPLY).label == "mild"


def test_capitals_and_stray_spaces_are_tolerated():
    assert parse_verdict("Label:  MILD \nConfidence: 0.5\nNote: x").label == "mild"


@pytest.mark.parametrize(
    "reply, expected_message",
    [
        # `match=` is a regular expression, so the parentheses are escaped.
        ("confidence: 0.9\nnote: x", r"missing field\(s\): label"),
        ("label: balmy\nconfidence: 0.9\nnote: x", "'balmy' is not one of"),
        ("label: mild\nconfidence: quite\nnote: x", "not a number"),
        ("label: mild\nconfidence: 1.4\nnote: x", "outside 0.0-1.0"),
    ],
)
def test_replies_this_program_cannot_use_are_refused(reply, expected_message):
    with pytest.raises(MalformedResponse, match=expected_message):
        parse_verdict(reply)


# --- the retries and failures you own ---------------------------------------


def test_one_good_reply_needs_one_call():
    model = ScriptedModel([GOOD_REPLY])
    assert classify_day(REPORT, model=model).label == "mild"
    assert len(model.prompts) == 1


def test_a_malformed_reply_is_retried():
    model = ScriptedModel(["I would rather not say.", GOOD_REPLY])
    assert classify_day(REPORT, model=model, attempts=2).confidence == 0.82
    assert len(model.prompts) == 2
    assert model.prompts[0] == model.prompts[1]  # the same prompt, resent


def test_an_unavailable_model_is_retried():
    model = ScriptedModel([ModelUnavailable("rate limited"), GOOD_REPLY])
    assert classify_day(REPORT, model=model, attempts=2).label == "mild"


def test_giving_up_says_what_the_last_failure_was():
    model = ScriptedModel(["nonsense", "still nonsense"])
    with pytest.raises(ModelError, match="MalformedResponse"):
        classify_day(REPORT, model=model, attempts=2)


def test_backoff_between_model_attempts_is_recorded_not_waited():
    waits = RecordingSleep()
    model = ScriptedModel(["nonsense", "nonsense", GOOD_REPLY])
    classify_day(REPORT, model=model, attempts=3, sleep=waits)
    assert waits.waits == [1.0, 2.0]
