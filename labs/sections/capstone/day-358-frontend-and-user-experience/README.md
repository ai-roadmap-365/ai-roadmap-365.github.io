# Lab — Day 358: Frontend and User Experience

## Lesson
<!-- generated-links:start — do not edit by hand; regenerate with `npm run update:links` -->
- **Lesson title:** Frontend and User Experience
- **Day number:** 358 of 365
- **Lesson article:** https://ai-roadmap-365.github.io/day-358-frontend-and-user-experience
- **Lab files:** everything you need is in [this directory](./) — follow “How to run” below.
- **Browse the course locally:** from the repository root, this lab also appears in the course website at `/labs/day-358-frontend-and-user-experience` when the site is running.
<!-- generated-links:end -->

## Purpose

Implement the state machine behind a streaming AI interface, then measure what each design decision costs the person waiting.

Everything runs offline on a logical clock — one tick per observable moment — so the measurements are exact and can be asserted on, which a wall-clock version could not.

## Learning objectives

- Model a response as five observable states and enforce that terminal states are terminal.
- Measure time to first token and perceived wait, and distinguish both from total duration.
- Keep partial output when a stream breaks.
- Treat cancellation as its own ending rather than an error.
- Show that text only grows during streaming and every frame differs from the last.

## Prerequisites

- Day 357, "Milestone Review and Course Correction" — this is Week 52, and you are shipping the capstone you audited.
- Comfortable with Python generators, dataclasses and enums.

## Supported operating systems

macOS, Linux and Windows (via WSL or PowerShell). Nothing is platform-specific.

## Hardware requirements

Any machine running Python 3.10 or newer. No GPU. The suite completes in hundredths of a second.

## Required software

- Python 3.10 or newer.
- `pytest` 7 or newer.

## Free and open-source options

Every dependency is free and open source: Python is PSF-licensed, `pytest` is MIT-licensed. No account, no API key, no network — the token stream is simulated so the state machine is testable. The lesson discusses server-sent events, HTMX, the Vercel AI SDK, Streamlit and Gradio as the real options.

## Installation

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements/requirements.txt
```

Removing `.venv` fully reverses the installation.

## File structure

```text
starter/stream_ux.py         your work: render_stream, perceived_wait
examples/stream_ux.py        reference implementation
examples/stream_ux_demo.py   the same answer rendered five ways
tests/test_stream_ux.py      grouped by UX property
tests/run_tests.sh           suite entry point
expected-output/             real captured output and measured values
requirements/                pinned dependency
```

## How to run

```bash
python3 examples/stream_ux_demo.py   # five renderings of one answer
bash tests/run_tests.sh              # run the suite
```

To work on the exercise, edit `starter/stream_ux.py`, then copy it over the reference:

```bash
cp starter/stream_ux.py examples/stream_ux.py
bash tests/run_tests.sh
```

Keep a copy of the reference first if you want to compare.

## What the commands do

`python3 examples/stream_ux_demo.py` renders the same eight-token answer five ways — healthy streaming with every frame shown, a blocking equivalent, a stream that fails midway with the partial kept, the same failure with it discarded, and a user cancellation — reporting the ending, total ticks, time to first token, characters retained and perceived wait for each.

`bash tests/run_tests.sh` runs `pytest` over sixteen tests grouped by property: the state machine, perceived latency, incremental output, partial output, cancellation and the token source.

## Expected output

```text
--- streaming, healthy ---
t=0   idle      ''
t=1   waiting   ''  awaiting first token
t=4   streaming 'The '
t=12  done      'The refund window is thirty day...'
done after 12 ticks, ttft=4, 47 chars  perceived_wait=4
--- blocking (no partial output) ---
done after 20 ticks, ttft=12, 47 chars  perceived_wait=12
--- stream fails midway, partial kept ---
error after 8 ticks, ttft=4, 21 chars  perceived_wait=4
--- stream fails midway, partial discarded ---
error after 8 ticks, ttft=4, 0 chars  perceived_wait=4
--- cancelled by user ---
cancelled after 7 ticks, ttft=4, 18 chars  perceived_wait=4
```

(The healthy run prints every frame; only the first and last are shown here.) `expected-output/FIELDS.md` explains each field.

## Validation steps

1. `bash tests/run_tests.sh` reports `16 passed`.
2. Compare the first two summaries: identical content, perceived wait of 4 against 12.
3. Compare the two failure runs: identical timing, and one keeps 21 characters while the other keeps none.
4. Confirm no frame follows a terminal state. If one does, a cancelled response can still gain text.

## Tests

Sixteen tests in six groups:

- **the state machine** — a healthy run reaches `done`, states occur in a legal order, and no frame follows a terminal state.
- **perceived latency** — streaming beats blocking on perceived wait, `ttft` ignores the waiting frames, perceived wait is not total duration, and a run that never emits has no first token.
- **incremental output** — text only grows and every frame differs; waiting frames show nothing.
- **partial output** — a failure keeps what arrived by default, discarding loses the user's reading, and a failure before any token has nothing to keep.
- **cancellation** — stops early, keeps the partial text, and is not an error.
- **the source** — raises where configured, completes otherwise.

## Cleanup

```bash
rm -rf __pycache__ .pytest_cache
rm -rf .venv
```

Both are safe to remove and fully reversible.

## Troubleshooting

See `troubleshooting.md`.

## Security notes

See `security.md`. In short: no network, no credentials — and the lesson covers why incremental rendering makes output escaping easier to get wrong.

## Extension exercises

1. **Reconnection.** Add a resume attempt after a failure, keeping text across both attempts, and test the failed-resume case as well as the successful one.
2. **Structured streaming.** Stream JSON and render only complete top-level fields, then measure how much later the first useful render happens than with prose.
3. **A stall detector.** Add a state for "streaming but nothing has arrived recently", which is a different problem from waiting and usually needs a different message.

## Navigation

- [Lesson](../../../../content/sections/capstone/day-358-frontend-and-user-experience/README.md)
- Previous: Day 357 — Milestone Review and Course Correction
- Next: Day 359 — Deploying Your Capstone
