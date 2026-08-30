"""Document processing with format dispatch, budgets and a quality gate.

Offline and standard-library only. The documents are synthetic, but each one
reproduces a real failure mode: a scan with no text layer, mojibake, a
pathological file that never returns, and an unknown format.

The pipeline has three outcomes rather than two. `accepted` goes downstream,
`dead` failed outright, and `flagged` produced text that scored badly -- still
indexed, because partial text usually beats none, but recorded for review. That
third outcome is what keeps the gate honest: a binary decision either discards
recoverable documents or silently admits garbage.
"""

from __future__ import annotations

import time
import multiprocessing as mp
from dataclasses import dataclass, field
from typing import Callable

# Cheap thresholds. None is conclusive alone; together they separate "fine"
# from "catastrophic", and catastrophic is what must not reach the index.
MIN_YIELD = 0.10  # extracted chars per source byte
MIN_ALPHA = 0.55  # proportion of characters that are letters
MAX_WORD_LEN = 12.0  # mean word length; runaway means spaces were lost


class UnknownFormat(RuntimeError):
    """Detection could not identify the document."""


@dataclass(frozen=True)
class Document:
    name: str
    data: bytes


@dataclass
class Scores:
    text_yield: float
    alpha_ratio: float
    mean_word_len: float

    def reasons(self) -> list[str]:
        """Why this text looks wrong. Empty means it looks fine."""
        out: list[str] = []
        if self.text_yield < MIN_YIELD:
            out.append("low text yield")
        if self.alpha_ratio < MIN_ALPHA:
            out.append("low alphabetic ratio")
        if self.mean_word_len > MAX_WORD_LEN:
            out.append("implausible word length")
        return out


@dataclass
class Result:
    name: str
    outcome: str  # accepted | flagged | dead
    text: str = ""
    scores: Scores | None = None
    detail: str = ""


@dataclass
class Report:
    results: list[Result] = field(default_factory=list)

    def count(self, outcome: str) -> int:
        return sum(1 for r in self.results if r.outcome == outcome)

    def summary(self) -> str:
        return (
            f"summary: accepted={self.count('accepted')} "
            f"flagged={self.count('flagged')} dead={self.count('dead')}"
        )


# ------------------------------------------------------------------- detect


def detect(doc: Document) -> str:
    """Identify the format from leading bytes, never from the extension.

    The extension lies: a `.pdf` may be a scan, a `.txt` may be UTF-16. Two of
    the demo documents are named to look like formats that do not exist,
    precisely so a pipeline that trusts the name gets them wrong.
    """
    # TASK 1: identify the format from doc.data's leading bytes.
    # Return one of: "pdf", "pdf-scan", "office", "html", "pathological",
    # "text", "unknown". A %PDF- header with no b"/Font" anywhere is a scan.
    # b"SLOW:" marks the pathological document. Bytes that will not decode as
    # UTF-8 are "unknown". Never look at doc.name.
    raise NotImplementedError("implement detect")

# ------------------------------------------------------------------ extract


def extract_text(doc: Document) -> str:
    return doc.data.decode("utf-8", errors="replace")


def extract_pdf(doc: Document) -> str:
    """Stand-in for a born-digital PDF with a real text layer."""
    body = doc.data.split(b"\n", 1)[1] if b"\n" in doc.data else b""
    return body.decode("utf-8", errors="replace")


def extract_pdf_scan(doc: Document) -> str:
    """A scan has no text layer, so a direct extractor recovers almost nothing.

    It does NOT raise. That is the whole problem: it returns a short string that
    would enter the index silently without a quality gate.
    """
    return "".join(chr(c) for c in doc.data[-24:] if 32 <= c < 127)


def extract_html(doc: Document) -> str:
    """Crudely strip tags. Real extraction would isolate the main content."""
    text = doc.data.decode("utf-8", errors="replace")
    out, depth = [], 0
    for ch in text:
        if ch == "<":
            depth += 1
        elif ch == ">":
            depth = max(0, depth - 1)
        elif depth == 0:
            out.append(ch)
    return " ".join("".join(out).split())


def extract_pathological(doc: Document) -> str:
    """Never returns within any sane budget. The harness must stop it."""
    time.sleep(30)
    return "unreachable"


EXTRACTORS: dict[str, Callable[[Document], str]] = {
    "text": extract_text,
    "pdf": extract_pdf,
    "pdf-scan": extract_pdf_scan,
    "html": extract_html,
    "pathological": extract_pathological,
}


# -------------------------------------------------------------------- score


def score(doc: Document, text: str) -> Scores:
    """Four cheap signals over the extracted text.

    Empty output is a common case, not an edge case, so every ratio guards its
    denominator.
    """
    # TASK 2: compute the three signals.
    #   text_yield    len(text) / len(doc.data), capped at 1.0 -- a RATIO, so a
    #                 short document is not confused with a failed extraction
    #   alpha_ratio   letters / non-space characters (letters only, not every
    #                 non-space character)
    #   mean_word_len mean length of text.split()
    # Empty output is a common case: guard every denominator.
    raise NotImplementedError("implement score")

# ------------------------------------------------------------------ process


def _extract_worker(fmt: str, doc: Document, out: "mp.Queue") -> None:
    """Run one extractor in a child process and post the result back."""
    try:
        out.put(("ok", EXTRACTORS[fmt](doc)))
    except Exception as exc:  # noqa: BLE001 - any parser failure is a dead letter
        out.put(("err", type(exc).__name__))


def extract_with_budget(fmt: str, doc: Document, budget_s: float) -> tuple[str, str]:
    """Run an extractor under a hard deadline. Returns (status, payload).

    The budget is enforced by the HARNESS, not by the extractor. A parser stuck
    in a tight loop cannot be interrupted cooperatively, and a thread cannot be
    killed at all -- an earlier version of this lab used a thread pool and the
    30-second sleep blocked the whole run anyway, because the pool's shutdown
    waits for its workers. A child process can genuinely be terminated, which
    is why production extraction belongs in one.
    """
    queue: "mp.Queue" = mp.Queue()
    child = mp.Process(target=_extract_worker, args=(fmt, doc, queue), daemon=True)
    child.start()
    child.join(timeout=budget_s)

    if child.is_alive():
        child.terminate()
        child.join(timeout=1.0)
        return ("timeout", f"timeout after {budget_s:.2f}s")

    try:
        status, payload = queue.get_nowait()
    except Exception:  # noqa: BLE001 - child died without posting
        return ("error", "ExtractorCrashed")
    return (status, payload)


def process_one(doc: Document, *, budget_s: float = 2.0) -> Result:
    """Detect, dispatch under a budget, score, then gate."""
    # TASK 3: detect, dispatch under a budget, score, then gate.
    #   - a format with no registered extractor is a normal "dead" outcome
    #     with detail f"no extractor for format '{fmt}'", not an exception
    #   - run the extractor via extract_with_budget(fmt, doc, budget_s); a
    #     non-"ok" status is a "dead" Result carrying the returned payload
    #   - score the text; if scores.reasons() is non-empty the outcome is
    #     "flagged" (still carrying the text, detail = the first reason)
    #   - otherwise "accepted"
    raise NotImplementedError("implement process_one")

def process_all(docs: list[Document], *, budget_s: float = 2.0) -> Report:
    return Report(results=[process_one(d, budget_s=budget_s) for d in docs])


def format_line(r: Result) -> str:
    if r.scores is None:
        return f"{r.name:<15} {r.outcome:<10} {r.detail}"
    s = r.scores
    line = (
        f"{r.name:<15} {r.outcome:<10} "
        f"yield={s.text_yield:.2f} alpha={s.alpha_ratio:.2f} words={s.mean_word_len:.1f}"
    )
    return f"{line}   {r.detail}" if r.detail else line
