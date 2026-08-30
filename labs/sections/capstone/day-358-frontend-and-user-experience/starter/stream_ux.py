"""The state machine behind a streaming AI interface.

Offline, standard-library only, and deterministic -- time is a logical clock, so
the measurements are exact rather than "about right" on a busy laptop.

An AI interface is not a form that submits and returns. It is a long-running,
interruptible, partially-failing operation shown to someone who is waiting, and
almost everything that makes it feel good or bad lives in the state machine
rather than in the styling:

  IDLE -> WAITING -> STREAMING -> DONE
                  \\-> ERROR
                  \\-> CANCELLED

Three properties decide whether it feels responsive:

  time to first token   what the user experiences as "did it hear me"
  incremental delivery  partial text is visible while more arrives
  cancellability        a wrong answer can be stopped without waiting

The last one is the one prototypes skip, and the one users reach for most.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Iterator


class State(str, Enum):
    IDLE = "idle"
    WAITING = "waiting"
    STREAMING = "streaming"
    DONE = "done"
    ERROR = "error"
    CANCELLED = "cancelled"


class StreamFailed(RuntimeError):
    """The upstream stream broke partway through."""


@dataclass
class Frame:
    """One observable moment, as a UI would render it."""

    tick: int
    state: State
    text: str
    note: str = ""

    def line(self) -> str:
        shown = self.text if len(self.text) <= 34 else self.text[:31] + "..."
        base = f"t={self.tick:<3} {self.state.value:<9} {shown!r}"
        return f"{base}  {self.note}" if self.note else base


@dataclass
class Transcript:
    frames: list[Frame] = field(default_factory=list)

    @property
    def final(self) -> Frame:
        return self.frames[-1]

    def time_to_first_token(self) -> int | None:
        """Ticks until the user saw ANY output. None if they never did."""
        for frame in self.frames:
            if frame.state is State.STREAMING and frame.text:
                return frame.tick
        return None

    def states(self) -> list[State]:
        return [f.state for f in self.frames]

    def summary(self) -> str:
        ttft = self.time_to_first_token()
        return (
            f"{self.final.state.value} after {self.final.tick} ticks, "
            f"ttft={ttft if ttft is not None else 'never'}, "
            f"{len(self.final.text)} chars"
        )


def token_source(tokens: list[str], *, fail_at: int | None = None) -> Iterator[str]:
    """Yield tokens, optionally breaking partway through.

    A stream that fails after emitting real content is the interesting case:
    the user has already read something, so discarding it is a worse outcome
    than keeping it and saying the answer is incomplete.
    """
    for index, token in enumerate(tokens):
        if fail_at is not None and index == fail_at:
            raise StreamFailed(f"upstream closed after {index} tokens")
        yield token


def render_stream(
    tokens: list[str],
    *,
    latency_ticks: int = 3,
    fail_at: int | None = None,
    cancel_at: int | None = None,
    keep_partial_on_error: bool = True,
) -> Transcript:
    """Drive the state machine and record every frame a UI would show.

    `latency_ticks` is the wait before the first token -- the part the user
    experiences as the system not having heard them.
    """
    # TASK 1: drive the state machine, appending one Frame per observable
    # moment.
    #   - start at tick 0 with State.IDLE and empty text
    #   - emit `latency_ticks` WAITING frames with empty text; an unchanged
    #     screen is indistinguishable from a broken one
    #   - for each token: advance the tick, APPEND to the accumulated text, and
    #     emit a STREAMING frame (text only ever grows, and every frame differs)
    #   - StopIteration -> a DONE frame
    #   - StreamFailed  -> an ERROR frame keeping the text so far, unless
    #     keep_partial_on_error is False. The user already read it.
    #   - after `cancel_at` tokens -> a CANCELLED frame keeping the text, with
    #     note "stopped by user". Not an error: they stopped it deliberately.
    #   - a terminal frame ENDS the run. Return immediately, or a late token
    #     appends to a response the user already stopped.
    raise NotImplementedError("implement render_stream")

def perceived_wait(transcript: Transcript) -> int:
    """Ticks the user spent with nothing to read.

    This is the number that correlates with how slow an interface feels, and it
    is NOT the total duration. A response that streams for forty ticks after a
    three-tick wait feels faster than one that appears complete after ten.
    """
    # TASK 2: ticks the user spent with nothing to read.
    # That is the time to first token when there is one, and the WHOLE run when
    # there is not. It is not the total duration, and confusing the two is the
    # most common mistake in this area.
    raise NotImplementedError("implement perceived_wait")

def is_terminal(state: State) -> bool:
    return state in (State.DONE, State.ERROR, State.CANCELLED)
