"""Eight synthetic documents, each reproducing a real failure mode.

Two are deliberately named to look like formats that do not exist, so a
pipeline that dispatches on the extension gets them wrong.
"""

from __future__ import annotations

from process import Document

PROSE = (
    "Retrieval quality depends on the text that reaches the index. "
    "A document that extracts badly cannot be rescued by a better model. "
    "Clean text is the input every later stage assumes it already has. "
)


def build_corpus() -> list[Document]:
    return [
        # Plain prose. The easy majority; should stay cheap.
        Document("doc-01.txt", (PROSE * 3).encode("utf-8")),
        # Born-digital PDF: has a font resource and a real text layer.
        Document("doc-02.pdf", b"%PDF-1.7 /Font\n" + (PROSE * 3).encode("utf-8")),
        # A scan: PDF header, no font resource, no text layer. Extraction
        # returns a few stray characters rather than raising.
        Document("doc-03.scan", b"%PDF-1.4\n" + b"\x00" * 900 + b"scanned page 1 of 40"),
        # Mojibake: decodes, but almost nothing is a letter.
        Document("doc-04.bin", ("=?#" * 200).encode("utf-8")),
        # HTML where most of the bytes are navigation and boilerplate.
        Document(
            "doc-05.html",
            (
                "<html><head><title>t</title></head><body>"
                "<nav><ul><li>Home</li><li>Docs</li><li>Pricing</li></ul></nav>"
                f"<main><p>{PROSE}</p></main>"
                "<footer><p>Cookie notice</p></footer></body></html>"
            ).encode("utf-8"),
        ),
        # Pathological: the extractor never returns within any sane budget.
        Document("doc-06.slow", b"SLOW:" + b"x" * 100),
        # Unknown format: undecodable bytes with no recognised signature.
        Document("doc-07.xyz", bytes([0xFF, 0xFE, 0x00, 0x01] * 50)),
        # A second normal PDF, so the summary is not dominated by failures.
        Document("doc-08.pdf", b"%PDF-1.7 /Font\n" + (PROSE * 2).encode("utf-8")),
    ]
