"""Grouped by UX property, so a failure names what the user would feel.

Run with: bash tests/run_tests.sh
"""

from __future__ import annotations

import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
LAB = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(LAB, "examples"))

from stream_ux import (  # noqa: E402
    State,
    StreamFailed,
    is_terminal,
    perceived_wait,
    render_stream,
    token_source,
)

TOKENS = ["The ", "refund ", "window ", "is ", "thirty ", "days."]


# ------------------------------------------------------- the state machine


def test_healthy_run_reaches_done():
    t = render_stream(TOKENS)
    assert t.final.state is State.DONE
    assert t.final.text == "".join(TOKENS)


def test_states_occur_in_a_legal_order():
    states = render_stream(TOKENS).states()
    assert states[0] is State.IDLE
    assert State.WAITING in states
    assert states.index(State.WAITING) < states.index(State.STREAMING)
    assert is_terminal(states[-1])


def test_no_frames_follow_a_terminal_state():
    for kwargs in ({}, {"fail_at": 3}, {"cancel_at": 2}):
        t = render_stream(TOKENS, **kwargs)
        terminal = [i for i, f in enumerate(t.frames) if is_terminal(f.state)]
        assert terminal == [len(t.frames) - 1], "a terminal state must end the run"


# ------------------------------------------------------ perceived latency


def test_streaming_is_perceived_as_faster_than_blocking():
    # Same content, same total work. The difference is entirely when the user
    # first has something to read.
    streaming = render_stream(TOKENS, latency_ticks=3)
    blocking = render_stream(TOKENS, latency_ticks=9)
    assert perceived_wait(streaming) < perceived_wait(blocking)


def test_time_to_first_token_ignores_the_waiting_frames():
    t = render_stream(TOKENS, latency_ticks=5)
    assert t.time_to_first_token() == 6  # 5 waiting frames, then the first token


def test_perceived_wait_is_not_total_duration():
    t = render_stream(TOKENS, latency_ticks=2)
    assert perceived_wait(t) < t.final.tick


def test_a_run_that_never_emits_has_no_first_token():
    t = render_stream([], latency_ticks=2)
    assert t.time_to_first_token() is None
    # With nothing ever shown, the whole run is perceived wait.
    assert perceived_wait(t) == t.final.tick


# ----------------------------------------------------- incremental output


def test_text_only_grows_during_streaming():
    t = render_stream(TOKENS)
    lengths = [len(f.text) for f in t.frames if f.state is State.STREAMING]
    assert lengths == sorted(lengths)
    assert len(set(lengths)) == len(lengths), "each frame should add something"


def test_waiting_frames_show_nothing():
    t = render_stream(TOKENS, latency_ticks=4)
    assert all(f.text == "" for f in t.frames if f.state is State.WAITING)


# --------------------------------------------------------- partial output


def test_a_failed_stream_keeps_what_arrived_by_default():
    t = render_stream(TOKENS, fail_at=3)
    assert t.final.state is State.ERROR
    assert t.final.text == "The refund window "
    assert "upstream closed" in t.final.note


def test_discarding_partial_output_loses_what_the_user_read():
    kept = render_stream(TOKENS, fail_at=3)
    discarded = render_stream(TOKENS, fail_at=3, keep_partial_on_error=False)
    assert discarded.final.text == ""
    assert len(kept.final.text) > 0
    # Both failed at the same point; only one wasted the user's reading.
    assert kept.final.tick == discarded.final.tick


def test_failure_before_any_token_leaves_nothing_to_keep():
    t = render_stream(TOKENS, fail_at=0)
    assert t.final.state is State.ERROR
    assert t.final.text == ""
    assert t.time_to_first_token() is None


# --------------------------------------------------------- cancellation


def test_cancellation_stops_early_and_keeps_the_partial_text():
    t = render_stream(TOKENS, cancel_at=2)
    assert t.final.state is State.CANCELLED
    assert t.final.text == "The refund "
    assert t.final.tick < render_stream(TOKENS).final.tick


def test_cancellation_is_not_an_error():
    t = render_stream(TOKENS, cancel_at=2)
    assert t.final.state is not State.ERROR
    assert t.final.note == "stopped by user"


# --------------------------------------------------------- the source


def test_token_source_raises_at_the_configured_point():
    gen = token_source(TOKENS, fail_at=2)
    assert next(gen) == "The "
    assert next(gen) == "refund "
    with pytest.raises(StreamFailed):
        next(gen)


def test_token_source_completes_when_it_does_not_fail():
    assert list(token_source(TOKENS)) == TOKENS
