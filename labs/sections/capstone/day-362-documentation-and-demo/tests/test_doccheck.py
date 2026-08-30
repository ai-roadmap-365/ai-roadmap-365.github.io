"""Grouped by check, plus extraction tests for the two regexes that got it wrong.

Run with: bash tests/run_tests.sh
"""

from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LAB = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(LAB, "examples"))

from doccheck import (  # noqa: E402
    Level,
    Project,
    claimed_outputs,
    commands_in,
    review,
    sections_in,
)
from fixtures import DRIFTED_README, GOOD_README, PROJECT  # noqa: E402


def names(readme, project=PROJECT):
    return review(readme, project).names()


# ------------------------------------------------------------- extraction


def test_only_shell_tagged_blocks_are_read_as_commands():
    # The bug this lab had first: an untagged block is OUTPUT, and reading it
    # back as a command made the checker report its own examples as unknown.
    readme = "```bash\nmake run\n```\n\nmake run ->\n\n```\nlistening\n```\n"
    assert commands_in(readme) == ["make run"]


def test_comments_and_prompts_are_stripped_from_commands():
    readme = "```bash\n# set it up\n$ make install\n```\n"
    assert commands_in(readme) == ["make install"]


def test_claimed_output_is_matched_to_one_command_not_the_whole_document():
    # With re.S a dot matches newlines, and the command group swallowed
    # everything above the first block.
    got = claimed_outputs(GOOD_README)
    assert set(got) == {"make run", "make test"}
    assert got["make test"] == "12 passed in 0.4s"


def test_sections_are_read_in_order():
    heads = sections_in(GOOD_README)
    assert heads[0] == "Support Assistant"
    assert "Limitations" in heads


# ----------------------------------------------------------- the good case


def test_a_current_readme_passes_cleanly():
    report = review(GOOD_README, PROJECT)
    assert report.ok
    assert report.names() == set()
    assert report.summary() == "PASS fail=0 warn=0"


# ------------------------------------------------- each check on its own


def test_missing_sections_fail():
    readme = GOOD_README.replace("## Limitations", "## Notes")
    assert "sections" in names(readme)


def test_a_renamed_command_is_caught():
    # The drift that matters: the README still says the old name, and nothing
    # else in the project notices.
    readme = GOOD_README.replace("make run\n```", "make serve\n```", 1)
    report = review(readme, PROJECT)
    issue = next(i for i in report.issues if i.check == "commands")
    assert issue.level is Level.FAIL
    assert "make serve" in issue.detail


def test_an_undocumented_command_only_warns():
    project = Project(
        commands=PROJECT.commands + ("make deploy",),
        captured_outputs=PROJECT.captured_outputs,
        known_limitations=PROJECT.known_limitations,
    )
    issue = next(i for i in review(GOOD_README, project).issues
                 if i.check == "undocumented_commands")
    assert issue.level is Level.WARN
    assert "make deploy" in issue.detail
    # A warning does not fail the review.
    assert review(GOOD_README, project).ok


def test_a_changed_output_is_caught():
    readme = GOOD_README.replace("listening on 127.0.0.1:8080", "listening on 0.0.0.0:9000")
    issue = next(i for i in review(readme, PROJECT).issues if i.check == "outputs")
    assert issue.level is Level.FAIL
    assert "differs from captured" in issue.detail


def test_an_output_with_nothing_captured_is_caught():
    readme = GOOD_README + "\nmake lint ->\n\n```\nall clean\n```\n"
    issue = next(i for i in review(readme, PROJECT).issues if i.check == "outputs")
    assert issue.level is Level.FAIL
    assert "no captured output" in issue.detail


def test_placeholder_text_fails():
    readme = GOOD_README.replace("English only.", "To be written")
    assert "placeholders" in names(readme)


def test_a_known_limitation_left_unstated_fails():
    readme = GOOD_README.replace("English only. ", "")
    issue = next(i for i in review(readme, PROJECT).issues if i.check == "limitations")
    assert issue.level is Level.FAIL
    assert "English only" in issue.detail


def test_recording_no_limitations_warns():
    project = Project(commands=PROJECT.commands, captured_outputs=PROJECT.captured_outputs)
    issue = next(i for i in review(GOOD_README, project).issues if i.check == "limitations")
    assert issue.level is Level.WARN


# ------------------------------------------------------------ the drift


def test_the_drifted_readme_fails_on_five_checks():
    report = review(DRIFTED_README, PROJECT)
    assert not report.ok
    assert report.summary() == "FAIL fail=5 warn=1"


def test_the_drifted_readme_names_what_broke():
    assert names(DRIFTED_README) == {
        "sections",
        "commands",
        "undocumented_commands",
        "outputs",
        "placeholders",
        "limitations",
    }


def test_a_warning_alone_does_not_fail_the_review():
    readme = GOOD_README.replace("```bash\nmake test\n```", "")
    report = review(readme, PROJECT)
    assert "undocumented_commands" in report.names()
    assert report.ok
