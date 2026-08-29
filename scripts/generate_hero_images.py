#!/usr/bin/env python3
"""Draw the per-day hero image — the first image on the lesson page.

Why a raster and not an SVG: this file is what LinkedIn, X and Slack show when
somebody shares the day's blog link. Those crawlers read the `og:image` tag and
they do not render SVG, so the hero has to be a PNG at 1200x630.

Why it is also the page's first image: the owner shares the blog URL, and the
first image is what gets picked up. Keeping one image for both jobs means the
thumbnail can never disagree with the page.

Everything on the card comes from the day's own lesson.yml and the curriculum:
the day number, the title, the promise, the course. Nothing is invented here.

Usage:
    python3 scripts/generate_hero_images.py            # every authored day
    python3 scripts/generate_hero_images.py --day 85
"""

from __future__ import annotations

import argparse
import math
import re
import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:  # pragma: no cover - the message is the whole point
    sys.exit(
        "Pillow is required to draw the hero images.\n"
        "    python3 -m venv .venv && .venv/bin/pip install pillow\n"
        "Then re-run with that interpreter."
    )

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "public" / "social"
W, H = 1200, 630

# One colour and one motif per course, so a year of thumbnails reads as a set
# and a reader can tell which course a day belongs to at a glance.
COURSE_STYLE = {
    "computing-foundations": ("#38bdf8", "chip"),
    "programming-with-python": ("#818cf8", "code"),
    "math-statistics-and-data": ("#f472b6", "axes"),
    "machine-learning": ("#4ade80", "scatter"),
    "deep-learning": ("#fbbf24", "network"),
    "llms-and-generative-ai": ("#a78bfa", "tokens"),
    "ai-engineering": ("#22d3ee", "pipeline"),
    "deployment-mlops-and-security": ("#fb7185", "shield"),
    "capstone": ("#facc15", "flag"),
}

FONT_CANDIDATES = {
    "bold": [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ],
    "regular": [
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ],
}


def font(kind: str, size: int):
    for candidate in FONT_CANDIDATES[kind]:
        if Path(candidate).exists():
            try:
                return ImageFont.truetype(candidate, size)
            except OSError:
                continue
    return ImageFont.load_default()


def hex_rgb(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4))  # type: ignore[return-value]


def mix(a: tuple[int, int, int], b: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))  # type: ignore[return-value]


def wrap(draw, text: str, fnt, max_width: int, max_lines: int) -> list[str]:
    """Wrap to at most max_lines, and if it does not fit, end it deliberately.

    A thumbnail that stops mid-clause ("...updates lost and") reads as broken
    rather than abbreviated, so an over-long string is cut back to its last
    whole word and given an ellipsis.
    """
    words, lines, current, truncated = text.split(), [], "", False
    for i, word in enumerate(words):
        trial = f"{current} {word}".strip()
        if draw.textlength(trial, font=fnt) <= max_width:
            current = trial
            continue
        lines.append(current)
        current = word
        if len(lines) == max_lines:
            truncated = i < len(words) - 1
            current = ""
            break
    if current and len(lines) < max_lines:
        lines.append(current)
    elif current:
        truncated = True
    if truncated and lines:
        last = lines[-1]
        while last and draw.textlength(last + "…", font=fnt) > max_width:
            last = last.rsplit(" ", 1)[0] if " " in last else last[:-1]
        lines[-1] = last.rstrip(" ,;:—-") + "…"
    return lines


def motif(draw, kind: str, accent: tuple[int, int, int]) -> None:
    """Geometry that says something about the course, drawn from its own palette."""
    cx, cy = 985, 330
    faint = mix(accent, (11, 18, 32), 0.55)

    if kind == "chip":
        draw.rounded_rectangle([cx - 78, cy - 78, cx + 78, cy + 78], 16, outline=accent, width=6)
        draw.rounded_rectangle([cx - 36, cy - 36, cx + 36, cy + 36], 8, fill=faint)
        for offset in (-50, -18, 18, 50):
            draw.line([cx + offset, cy - 78, cx + offset, cy - 104], fill=accent, width=6)
            draw.line([cx + offset, cy + 78, cx + offset, cy + 104], fill=accent, width=6)
            draw.line([cx - 78, cy + offset, cx - 104, cy + offset], fill=accent, width=6)
            draw.line([cx + 78, cy + offset, cx + 104, cy + offset], fill=accent, width=6)
    elif kind == "code":
        draw.line([cx - 34, cy - 56, cx - 92, cy, cx - 34, cy + 56], fill=accent, width=11, joint="curve")
        draw.line([cx + 34, cy - 56, cx + 92, cy, cx + 34, cy + 56], fill=accent, width=11, joint="curve")
        draw.line([cx - 10, cy + 68, cx + 10, cy - 68], fill=faint, width=10)
    elif kind == "axes":
        draw.line([cx - 90, cy + 78, cx + 100, cy + 78], fill=accent, width=6)
        draw.line([cx - 90, cy + 78, cx - 90, cy - 90], fill=accent, width=6)
        points = [(cx - 90 + i * 6, cy + 66 - (i * 6) ** 1.32 / 26) for i in range(31)]
        draw.line(points, fill=accent, width=7, joint="curve")
    elif kind == "scatter":
        draw.line([cx - 90, cy + 78, cx + 100, cy + 78], fill=faint, width=5)
        draw.line([cx - 90, cy + 78, cx - 90, cy - 90], fill=faint, width=5)
        for dx, dy in ((-58, 34), (-24, 6), (12, -22), (46, -50), (-40, -6), (28, 18), (68, -68)):
            draw.ellipse([cx + dx - 10, cy + dy - 10, cx + dx + 10, cy + dy + 10], fill=accent)
        draw.line([cx - 78, cy + 50, cx + 88, cy - 72], fill=faint, width=5)
    elif kind == "network":
        left = [(cx - 78, cy + d) for d in (-66, 0, 66)]
        mid = [(cx, cy + d) for d in (-34, 34)]
        right = (cx + 78, cy)
        for a in left:
            for b in mid:
                draw.line([a, b], fill=faint, width=3)
        for b in mid:
            draw.line([b, right], fill=faint, width=3)
        for x, y in left + mid + [right]:
            draw.ellipse([x - 13, y - 13, x + 13, y + 13], fill=accent)
    elif kind == "tokens":
        for i in range(4):
            x = cx - 96 + i * 50
            shade = mix((11, 18, 32), accent, 0.35 + i * 0.2)
            draw.rounded_rectangle([x, cy - 20, x + 40, cy + 20], 9, fill=shade)
        for i in range(0, 190, 18):
            draw.line([cx - 96 + i, cy + 46, cx - 84 + i, cy + 46], fill=faint, width=4)
    elif kind == "pipeline":
        for dx in (-78, 0, 78):
            draw.rounded_rectangle(
                [cx + dx - 28, cy - 28, cx + dx + 28, cy + 28], 10, outline=accent, width=6
            )
        draw.line([cx - 46, cy, cx - 30, cy], fill=accent, width=6)
        draw.line([cx + 30, cy, cx + 46, cy], fill=accent, width=6)
    elif kind == "shield":
        draw.polygon(
            [
                (cx, cy - 88),
                (cx + 76, cy - 54),
                (cx + 76, cy + 14),
                (cx, cy + 96),
                (cx - 76, cy + 14),
                (cx - 76, cy - 54),
            ],
            outline=accent,
            width=6,
        )
        draw.line([cx - 30, cy + 6, cx - 6, cy + 32, cx + 36, cy - 26], fill=accent, width=11, joint="curve")
    else:  # flag
        draw.line([cx - 54, cy + 88, cx - 54, cy - 78], fill=accent, width=7)
        draw.polygon(
            [(cx - 54, cy - 78), (cx + 64, cy - 78), (cx + 42, cy - 38), (cx + 64, cy + 2), (cx - 54, cy + 2)],
            outline=accent,
            width=6,
        )


def draw_day(day: dict, out_path: Path, challenge: str, site: str) -> None:
    accent_hex, motif_kind = COURSE_STYLE.get(day["section"], COURSE_STYLE["computing-foundations"])
    accent = hex_rgb(accent_hex)
    top, bottom = hex_rgb("#0b1220"), hex_rgb("#131f38")

    img = Image.new("RGB", (W, H), top)
    draw = ImageDraw.Draw(img)

    # Diagonal gradient, then a faint grid: the same visual language as the site.
    for y in range(H):
        draw.line([(0, y), (W, y)], fill=mix(top, bottom, y / H))
    grid = mix(top, (255, 255, 255), 0.055)
    for x in range(0, W, 48):
        draw.line([(x, 0), (x, H)], fill=grid)
    for y in range(0, H, 48):
        draw.line([(0, y), (W, y)], fill=grid)

    # The accent rule across the top, fading along the course's own colour.
    for x in range(W):
        draw.line([(x, 0), (x, 8)], fill=mix(accent, hex_rgb("#a855f7"), x / W))

    f_badge = font("bold", 26)
    f_eyebrow = font("bold", 21)
    f_title = font("bold", 58)
    f_title_sm = font("bold", 46)
    f_sub = font("regular", 25)
    f_meta = font("bold", 20)
    f_foot = font("regular", 19)

    # DAY N / 365 — the thing the owner wants unmissable in a feed.
    badge = "365 DAYS" if day["dayId"] == "cover" else f"DAY {day['number']} / 365"
    bw = draw.textlength(badge, font=f_badge)
    draw.rounded_rectangle([72, 74, 72 + bw + 44, 74 + 52], 26, fill=mix(top, accent, 0.22))
    draw.text((94, 100), badge, font=f_badge, fill=accent, anchor="lm")

    draw.text((72 + bw + 68, 100), challenge.upper(), font=f_eyebrow, fill=(100, 116, 139), anchor="lm")

    title_font = f_title if len(day["title"]) <= 34 else f_title_sm
    lines = wrap(draw, day["title"], title_font, 800, 3)
    y = 208
    for line in lines:
        draw.text((72, y), line, font=title_font, fill=(248, 250, 252))
        y += title_font.size + 12

    promise = re.sub(r"^After this lesson you will be able to ", "", day.get("promise", ""))
    promise = re.split(r"[;.]", promise)[0].strip()
    if promise:
        promise = promise[0].upper() + promise[1:]
        for line in wrap(draw, promise, f_sub, 780, 2):
            draw.text((72, y + 8), line, font=f_sub, fill=(148, 163, 184))
            y += f_sub.size + 8

    # Course pill and the promise that every day carries a runnable lab.
    pill_y = 470
    course = day["course_title"]
    cw = draw.textlength(course, font=f_meta)
    draw.rounded_rectangle([72, pill_y, 72 + cw + 44, pill_y + 42], 21, fill=hex_rgb("#1e293b"))
    draw.text((94, pill_y + 21), course, font=f_meta, fill=accent, anchor="lm")

    lab = "hands-on lab included"
    lw = draw.textlength(lab, font=f_meta)
    lx = 72 + cw + 60
    draw.rounded_rectangle([lx, pill_y, lx + lw + 44, pill_y + 42], 21, fill=hex_rgb("#1e293b"))
    draw.text((lx + 22, pill_y + 21), lab, font=f_meta, fill=hex_rgb("#86efac"), anchor="lm")

    draw.text((72, 556), site.replace("https://", ""), font=f_meta, fill=hex_rgb("#7dd3fc"))
    draw.text(
        (72, 586),
        # This image is the LinkedIn preview card, so it follows the same
        # rule as the post text: no open-source framing here.
        "One lesson and one runnable lab, every day. Free and no prerequisites.",
        font=f_foot,
        fill=(100, 116, 139),
    )

    motif(draw, motif_kind, accent)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path, "PNG", optimize=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--day", type=int)
    parser.add_argument("--manifest", default="dist/social-manifest.json")
    args = parser.parse_args()

    import json

    manifest_path = REPO / args.manifest
    if not manifest_path.exists():
        sys.exit(
            f"{args.manifest} not found. Run `npm run generate:social` first — it writes the "
            "manifest this script draws from."
        )
    data = json.loads(manifest_path.read_text())
    days = [d for d in data["days"] if args.day is None or d["number"] == args.day]
    if not days:
        sys.exit(f"No authored day matches --day {args.day}.")

    for day in days:
        draw_day(day, OUT / f"{day['dayId']}.png", data["challenge"], data["site"])

    # The site-wide cover: what a shared link to the homepage, a course page or
    # the search page previews as. Drawn from the same template so the whole
    # site shares one visual identity.
    if args.day is None:
        cover = {
            "number": 365,
            "dayId": "cover",
            "title": "365 Days of AI Mastery",
            "section": "llms-and-generative-ai",
            "course_title": "Nine standalone courses",
            "promise": (
                "A complete, self-paced path from how a computer actually works "
                "to shipping production AI systems"
            ),
        }
        draw_day(cover, OUT / "cover.png", data["challenge"], data["site"])

    print(f"✓ hero images: {len(days)} day(s) + cover written to {OUT.relative_to(REPO)}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
