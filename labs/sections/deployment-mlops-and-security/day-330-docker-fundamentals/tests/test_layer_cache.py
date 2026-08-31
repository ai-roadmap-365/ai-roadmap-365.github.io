"""Grouped by what the cache model decides.

Run with: bash tests/run_tests.sh
"""

from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "examples"))

from layer_cache import (  # noqa: E402
    INSTALL_SECONDS,
    Instruction,
    digest,
    lint,
    parse,
    plan_build,
)

NAIVE = """\
FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "-m", "app"]
"""

ORDERED = """\
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src/ ./src/
USER 10001
CMD ["python", "-m", "app"]
"""


# ------------------------------------------------------------------- parsing


def test_comments_and_blank_lines_produce_no_layer():
    ins = parse("# a comment\n\nFROM python:3.12-slim\n\n# another\nWORKDIR /app\n")
    assert [i.verb for i in ins] == ["FROM", "WORKDIR"]


def test_line_numbers_are_the_real_ones():
    # The linter reports these, so an off-by-one sends people to the wrong line.
    ins = parse("# comment\n\nFROM python:3.12-slim\nWORKDIR /app\n")
    assert [i.line_no for i in ins] == [3, 4]


def test_a_backslash_continuation_is_one_instruction():
    ins = parse("RUN apt-get update \\\n && apt-get install -y curl \\\n && rm -rf /var/lib/apt/lists/*\n")
    assert len(ins) == 1
    assert "apt-get install" in ins[0].args and "rm -rf" in ins[0].args


def test_the_verb_is_uppercased_but_the_arguments_are_not():
    ins = parse("from python:3.12-slim AS Builder\n")
    assert ins[0].verb == "FROM"
    assert "Builder" in ins[0].args


# ---------------------------------------------------------------------- cost


def test_an_install_layer_costs_far_more_than_a_copy():
    run = Instruction(1, "RUN", "pip install -r requirements.txt")
    copy = Instruction(2, "COPY", "src/ ./src/")
    assert run.cost_seconds == INSTALL_SECONDS
    assert run.cost_seconds > copy.cost_seconds * 50


def test_metadata_instructions_are_free():
    for verb in ("FROM", "WORKDIR", "ENV", "EXPOSE", "USER", "CMD"):
        assert Instruction(1, verb, "x").cost_seconds == 0.0


def test_a_run_that_installs_nothing_is_cheap():
    assert Instruction(1, "RUN", "mkdir -p /app/data").cost_seconds < INSTALL_SECONDS


# ------------------------------------------------------------- copied paths


def test_the_last_token_is_the_destination_not_a_source():
    assert Instruction(1, "COPY", "requirements.txt .").copied_paths == ["requirements.txt"]
    assert Instruction(1, "COPY", "a.txt b.txt /dest/").copied_paths == ["a.txt", "b.txt"]


def test_flags_are_not_sources():
    assert Instruction(1, "COPY", "--from=builder /wheels /wheels").copied_paths == ["/wheels"]


def test_an_instruction_that_copies_nothing_has_no_sources():
    assert Instruction(1, "RUN", "pip install x").copied_paths == []


# --------------------------------------------------------------- cache rule


def test_a_cold_build_reuses_nothing():
    plan = plan_build(parse(ORDERED), cold=True)
    assert plan.rebuilt == plan.layers


def test_an_untouched_project_reuses_everything():
    plan = plan_build(parse(ORDERED), set())
    assert plan.rebuilt == []
    assert plan.seconds == 0.0


def test_copy_dot_makes_every_later_layer_depend_on_every_file():
    plan = plan_build(parse(NAIVE), {"src/app.py"})
    assert plan.first_miss.instruction.verb == "COPY"
    assert plan.seconds >= INSTALL_SECONDS  # the install re-runs


def test_copying_the_manifest_first_protects_the_install():
    plan = plan_build(parse(ORDERED), {"src/app.py"})
    assert plan.seconds < INSTALL_SECONDS
    assert not any(x.instruction.verb == "RUN" and not x.reused for x in plan.layers)


def test_everything_after_the_first_miss_also_misses():
    # THE rule. A later layer cannot be reused just because its own inputs
    # are unchanged.
    plan = plan_build(parse(ORDERED), {"requirements.txt"})
    idx = plan.layers.index(plan.first_miss)
    assert all(not x.reused for x in plan.layers[idx:])


def test_changing_the_manifest_does_re_run_the_install():
    plan = plan_build(parse(ORDERED), {"requirements.txt"})
    assert plan.seconds >= INSTALL_SECONDS


def test_a_change_to_a_file_nobody_copies_costs_nothing():
    assert plan_build(parse(ORDERED), {"README.md"}).seconds == 0.0


def test_the_cold_builds_cost_about_the_same():
    # The ordering trick is free: it buys warm-build speed, not cold.
    naive = plan_build(parse(NAIVE), cold=True).seconds
    ordered = plan_build(parse(ORDERED), cold=True).seconds
    assert abs(naive - ordered) < 5.0


# --------------------------------------------------------------------- lint


def test_copy_before_install_is_reported():
    rules = {f.rule for f in lint(parse(NAIVE))}
    assert "copy-before-install" in rules


def test_a_correctly_ordered_dockerfile_is_clean():
    assert lint(parse(ORDERED)) == []


def test_an_unpinned_base_image_is_reported():
    for ref in ("FROM python\n", "FROM python:latest\n"):
        assert "unpinned-base" in {f.rule for f in lint(parse(ref + "USER 1\n"))}


def test_a_pinned_base_image_is_not_reported():
    assert "unpinned-base" not in {f.rule for f in lint(parse("FROM python:3.12-slim\nUSER 1\n"))}


def test_apt_without_cleanup_in_the_same_layer_is_reported():
    df = "FROM debian:12\nRUN apt-get update && apt-get install -y curl\nUSER 1\n"
    assert "apt-cache-kept" in {f.rule for f in lint(parse(df))}


def test_apt_with_cleanup_in_the_same_layer_is_clean():
    df = ("FROM debian:12\n"
          "RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*\n"
          "USER 1\n")
    assert "apt-cache-kept" not in {f.rule for f in lint(parse(df))}


def test_a_missing_user_instruction_is_reported():
    assert "runs-as-root" in {f.rule for f in lint(parse("FROM python:3.12-slim\n"))}


def test_findings_carry_the_line_to_look_at():
    f = next(x for x in lint(parse(NAIVE)) if x.rule == "copy-before-install")
    assert f.line_no == 3


# ------------------------------------------------------------------- digest


def test_the_digest_ignores_comments_and_spacing():
    assert digest(ORDERED) == digest("# a note\n\n" + ORDERED)


def test_the_digest_changes_when_an_instruction_changes():
    assert digest(NAIVE) != digest(ORDERED)
