# Troubleshooting — Day 358

## `perceived_wait` equals the total duration on every run

You are returning `transcript.final.tick` unconditionally. It should be the time to first token whenever there is one, and only fall back to the final tick when nothing was ever shown. Those are different quantities, and conflating them makes streaming look no better than blocking.

## The blocking run does not look worse than the streaming one

You are comparing total duration. Compare `perceived_wait`, or `time_to_first_token`. In the reference run both deliver 47 characters and the difference is 4 ticks against 12.

## `test_no_frames_follow_a_terminal_state` fails

Your loop appends the terminal frame and keeps going. Return immediately after appending `done`, `error` or `cancelled`. This is the bug that lets a late token append to a response the user already stopped — a stop button that does not stop.

## The error case loses text that should be kept

You are clearing the accumulated text when the stream raises. Keep it unless `keep_partial_on_error` is `False`. The user has already read it; the failure does not un-read it.

## `test_text_only_grows_during_streaming` fails on duplicate lengths

Every streaming frame must add something. If two consecutive frames have the same length you are re-emitting the buffer rather than appending a token — usually a frame appended before the token is added rather than after.

## `time_to_first_token` returns a waiting tick

It must find the first frame that is `STREAMING` **and** has non-empty text. A waiting frame has empty text by construction, so checking the state alone is not enough if you ever emit an empty streaming frame.

## Cancellation is reported as an error

`cancel_at` should produce `State.CANCELLED` with the note `"stopped by user"`, keeping the partial text. Reporting it as an error tells the user something broke when they were the one who stopped it.

## A run with no tokens behaves strangely

`render_stream([])` is a legitimate case: the stream completes without ever emitting. `time_to_first_token` should return `None`, and `perceived_wait` should then be the whole run — the user waited for the entire duration and saw nothing.

## `NotImplementedError` on most tests

Expected. The starter stubs `render_stream` and `perceived_wait` — see `expected-output/starter-run.txt`, which also names the two tests that pass without them.
