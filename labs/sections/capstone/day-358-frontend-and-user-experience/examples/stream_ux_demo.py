#!/usr/bin/env python3
"""Four runs of the same answer, showing what each UX decision costs."""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from stream_ux import perceived_wait, render_stream

TOKENS = ["The ", "refund ", "window ", "is ", "thirty ", "days ", "from ", "purchase."]


def show(label: str, transcript, *, frames: bool = False) -> None:
    print(f"--- {label} ---")
    if frames:
        for frame in transcript.frames:
            print(frame.line())
    print(f"{transcript.summary()}  perceived_wait={perceived_wait(transcript)}")


def main() -> int:
    show("streaming, healthy", render_stream(TOKENS), frames=True)
    show("blocking (no partial output)", render_stream(TOKENS, latency_ticks=11))
    show("stream fails midway, partial kept", render_stream(TOKENS, fail_at=4))
    show(
        "stream fails midway, partial discarded",
        render_stream(TOKENS, fail_at=4, keep_partial_on_error=False),
    )
    show("cancelled by user", render_stream(TOKENS, cancel_at=3))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
