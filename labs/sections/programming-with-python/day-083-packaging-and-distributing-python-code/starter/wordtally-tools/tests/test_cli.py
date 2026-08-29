"""Tests for the command-line half.

`main` is called directly with an argument list, exactly as Day 80 argued:
a `main(argv) -> int` is a plain function, so testing it needs no subprocess,
no shell, and no installed console script. The lab's harness separately checks
that the INSTALLED console script runs, which is the other half of the claim.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from wordtally.cli import build_parser, main

SAMPLE = "The cat sat on the mat. The mat was a cat's mat."


@pytest.fixture()
def sample_file(tmp_path: Path) -> Path:
    path = tmp_path / "sample.txt"
    path.write_text(SAMPLE, encoding="utf-8")
    return path


def test_parser_knows_both_subcommands() -> None:
    parser = build_parser()
    assert parser.parse_args(["count", "x.txt"]).command == "count"
    assert parser.parse_args(["top", "x.txt"]).n == 3


def test_count_prints_the_number_and_exits_zero(
    sample_file: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert main(["count", str(sample_file)]) == 0
    assert capsys.readouterr().out.strip() == "12"


def test_top_prints_ranked_words(
    sample_file: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert main(["top", str(sample_file), "-n", "2"]) == 0
    lines = capsys.readouterr().out.strip().splitlines()
    assert [line.split() for line in lines] == [["3", "mat"], ["1", "cat"]]


def test_a_missing_file_exits_two(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert main(["count", str(tmp_path / "nope.txt")]) == 2
    assert "cannot read" in capsys.readouterr().err


def test_a_non_positive_n_exits_two(
    sample_file: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert main(["top", str(sample_file), "-n", "0"]) == 2
    assert "must be positive" in capsys.readouterr().err


def test_stdin_is_read_when_the_path_is_a_dash(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    import io
    import sys

    monkeypatch.setattr(sys, "stdin", io.StringIO(SAMPLE))
    assert main(["count", "-"]) == 0
    assert capsys.readouterr().out.strip() == "12"
