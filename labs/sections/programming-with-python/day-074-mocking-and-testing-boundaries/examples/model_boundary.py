"""A language model behind an injected boundary — the same pattern, one step on.

A model call is not a pure function. It is slow, it costs money per call, and
it returns something different every time even with the same input. You cannot
assert on its text in a unit test, and you should stop trying.

What you CAN test, deterministically and for free, is everything on your side
of the boundary:

  * `build_prompt`  — did you put the right numbers in the right places?
  * `parse_verdict` — do you survive the shapes the model actually returns?
  * `classify_day`  — do you retry the right number of times, and fail cleanly?

So the model arrives as an argument: any object with `complete(prompt) -> str`.
In production that object wraps a real API client. In tests it is four lines of
scripted text. Judging whether the model's answers are any *good* is a separate
job with a separate name — an evaluation suite — and it is not a unit test.
"""

from __future__ import annotations

from dataclasses import dataclass

from report_v2 import DailyReport

LABELS = ("cold", "mild", "warm", "hot")


class ModelError(Exception):
    """Any refusal that belongs to the model-calling layer."""


class ModelUnavailable(ModelError):
    """The model could not be reached or refused to answer. Retryable."""


class MalformedResponse(ModelError):
    """The model answered, but not in the shape this program can use."""


@dataclass(frozen=True)
class Verdict:
    label: str
    confidence: float
    note: str


PROMPT_TEMPLATE = """\
Classify one day of weather station data.
Answer with exactly three lines: label, confidence, note.
The label must be one of: {labels}.

station: {station}
date: {day}
readings: {count}
minimum: {minimum:.1f}
maximum: {maximum:.1f}
mean: {mean:.1f}"""


def build_prompt(report: DailyReport) -> str:
    """Turn a report into the exact text sent to the model. Pure and testable."""
    return PROMPT_TEMPLATE.format(
        labels=", ".join(LABELS),
        station=report.station,
        day=report.day.isoformat(),
        count=report.count,
        minimum=report.minimum,
        maximum=report.maximum,
        mean=report.mean,
    )


def parse_verdict(raw: str) -> Verdict:
    """Parse the model's reply, refusing anything this program cannot use.

    Deliberately forgiving about whitespace, capitalisation and the chatty
    preamble models like to add; deliberately strict about the label and the
    confidence, because those two are the ones that go on to do damage.
    """
    fields: dict[str, str] = {}
    for line in raw.splitlines():
        key, sep, value = line.partition(":")
        if sep:
            fields[key.strip().lower()] = value.strip()

    missing = [k for k in ("label", "confidence", "note") if k not in fields]
    if missing:
        raise MalformedResponse(f"missing field(s): {', '.join(missing)}")

    label = fields["label"].lower()
    if label not in LABELS:
        raise MalformedResponse(f"label {label!r} is not one of {', '.join(LABELS)}")

    try:
        confidence = float(fields["confidence"])
    except ValueError as exc:
        raise MalformedResponse(f"confidence {fields['confidence']!r} is not a number") from exc
    if not 0.0 <= confidence <= 1.0:
        raise MalformedResponse(f"confidence {confidence} is outside 0.0-1.0")

    return Verdict(label=label, confidence=confidence, note=fields["note"])


def classify_day(
    report: DailyReport,
    *,
    model,
    attempts: int = 2,
    sleep=lambda seconds: None,
) -> Verdict:
    """Ask the model to classify a day, retrying a malformed or missing answer.

    `model` is any object with `complete(prompt) -> str`. That one parameter is
    the whole boundary: the network, the cost, and the non-determinism all live
    on the other side of it.
    """
    prompt = build_prompt(report)
    last_reason = ""
    for attempt in range(1, attempts + 1):
        try:
            return parse_verdict(model.complete(prompt))
        except (ModelUnavailable, MalformedResponse) as exc:
            last_reason = f"{type(exc).__name__}: {exc}"
            if attempt < attempts:
                sleep(float(attempt))
    raise ModelError(f"no usable answer after {attempts} attempts — last was {last_reason}")
