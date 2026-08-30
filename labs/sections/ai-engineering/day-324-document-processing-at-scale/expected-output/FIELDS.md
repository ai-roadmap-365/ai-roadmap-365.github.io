# What each column in the run output means

    doc-01.txt      accepted   yield=1.00 alpha=0.98 words=4.8

| Column | Meaning |
| --- | --- |
| name | The document. Two are deliberately named for formats that do not exist (`.scan`, `.slow`) so a pipeline that dispatches on the extension gets them wrong. |
| outcome | `accepted`, `flagged` or `dead`. Three outcomes, not two — see below. |
| `yield` | Extracted characters per source byte, capped at 1.0. A ratio, so a genuinely short document is not confused with a failed extraction of a long one. |
| `alpha` | Proportion of non-space characters that are letters. Mojibake and OCR noise score near zero. |
| `words` | Mean word length. Natural prose sits near 4-6; a page whose spaces were lost scores in the hundreds. |
| detail | For a flagged document, the first failing signal. For a dead one, why it died. |

## The three outcomes

- **accepted** — scored cleanly, goes to the index.
- **flagged** — produced text that scored badly. Still indexed, because partial text usually beats none, but recorded so it can be re-routed to a costlier extractor.
- **dead** — failed outright: a timeout, a crash, or a format with no registered extractor.

A binary accept-or-reject cannot express the middle case, and the middle case is where scans and encoding failures live.
