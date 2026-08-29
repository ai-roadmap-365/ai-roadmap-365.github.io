"""The generated schedule files say what they claim — and install nothing.

The last two tests are the ones that matter for safety: they read every file
in this lab and assert that no code path anywhere executes `crontab`,
`launchctl` or `systemctl`. The install commands exist only as text to be
read.
"""

from __future__ import annotations

import datetime as dt
import re
from pathlib import Path

from cronexpr import parse
from gen_schedules import JobSchedule, write_all

UTC = dt.timezone.utc
HERE = Path(__file__).resolve().parent
LAB = HERE.parent

DAILY = JobSchedule(label="com.example.dailyreport", minute=30, hour=2)
WEEKDAYS = JobSchedule(
    label="com.example.weekdayreport", minute=15, hour=6, days_of_week=(1, 2, 3, 4, 5)
)


def test_the_generated_cron_line_parses_to_the_intended_schedule():
    schedule = parse(DAILY.cron_expression)
    assert DAILY.cron_expression == "30 2 * * *"
    base = dt.datetime(2026, 7, 19, 0, 0, tzinfo=UTC)
    assert schedule.next_run_after(base) == dt.datetime(2026, 7, 19, 2, 30, tzinfo=UTC)
    assert schedule.next_run_after(
        dt.datetime(2026, 7, 19, 2, 30, tzinfo=UTC)
    ) == dt.datetime(2026, 7, 20, 2, 30, tzinfo=UTC)


def test_the_weekday_schedule_skips_the_weekend():
    schedule = parse(WEEKDAYS.cron_expression)
    assert WEEKDAYS.cron_expression == "15 6 * * 1,2,3,4,5"
    # 2026-07-17 is a Friday; the next run is Monday the 20th.
    assert schedule.next_run_after(
        dt.datetime(2026, 7, 17, 12, 0, tzinfo=UTC)
    ) == dt.datetime(2026, 7, 20, 6, 15, tzinfo=UTC)


def test_the_cron_file_sets_the_environment_cron_does_not_give_you():
    text = DAILY.cron_line()
    assert "PATH=/usr/local/bin:/usr/bin:/bin" in text
    assert "SHELL=/bin/sh" in text
    assert "TZ=UTC" in text
    assert f"cd {DAILY.project_dir}" in text  # cron starts in $HOME, not your project
    assert ">>" in text and "2>&1" in text  # output goes somewhere on purpose


def test_all_three_dialects_agree_on_the_same_moment():
    """One schedule definition, three syntaxes, 02:30 in every one of them."""
    plist = DAILY.launchd_plist()
    assert DAILY.cron_expression == "30 2 * * *"
    assert "<key>Hour</key><integer>2</integer>" in plist
    assert "<key>Minute</key><integer>30</integer>" in plist
    assert DAILY.on_calendar == "*-*-* 02:30:00"


def test_the_launchd_plist_declares_every_key_that_matters():
    plist = DAILY.launchd_plist()
    for required in (
        "Label",  # what launchd calls the job
        "ProgramArguments",  # argv, not a shell command line
        "StartCalendarInterval",  # when
        "RunAtLoad",  # loading must not mean running
        "StandardOutPath",  # otherwise output is discarded
        "StandardErrorPath",
        "EnvironmentVariables",  # launchd gives a minimal environment, like cron
    ):
        assert f"<key>{required}</key>" in plist, f"{required} missing from the plist"
    assert "<false/>" in plist  # RunAtLoad is false
    for argument in DAILY.argv:
        assert f"<string>{argument}</string>" in plist


def test_the_weekday_plist_has_one_calendar_entry_per_day():
    plist = WEEKDAYS.launchd_plist()
    assert plist.count("<key>Weekday</key>") == 5
    for day in (1, 2, 3, 4, 5):
        assert f"<key>Weekday</key><integer>{day}</integer>" in plist


def test_the_systemd_pair_splits_what_from_when():
    service = DAILY.systemd_service()
    timer = DAILY.systemd_timer()
    assert "Type=oneshot" in service
    assert "ExecStart=" in service
    assert "OnCalendar" not in service  # the service has no schedule of its own
    assert "OnCalendar=*-*-* 02:30:00" in timer
    assert "Persistent=true" in timer  # catch-up after downtime, which cron lacks
    assert "WantedBy=timers.target" in timer


def test_writing_the_files_produces_four_readable_artefacts(tmp_path):
    written = write_all(DAILY, tmp_path)
    assert sorted(p.suffix for p in written) == [".cron", ".plist", ".service", ".timer"]
    for path in written:
        assert path.read_text(encoding="utf-8").strip()


def test_the_committed_example_files_match_what_the_generator_produces():
    """The files in examples/schedules are generated, not hand-edited."""
    committed = LAB / "examples" / "schedules"
    assert (committed / "com.example.dailyreport.cron").read_text() == DAILY.cron_line()
    assert (committed / "com.example.dailyreport.plist").read_text() == DAILY.launchd_plist()
    assert (
        committed / "com.example.dailyreport.service"
    ).read_text() == DAILY.systemd_service()
    assert (committed / "com.example.dailyreport.timer").read_text() == DAILY.systemd_timer()


# --------------------------------------------------------------------------
# Safety: this lab installs nothing, anywhere, ever.
# --------------------------------------------------------------------------

INSTALLERS = re.compile(r"\b(crontab|launchctl|systemctl|launchd|at|batch)\b")
EXECUTION = re.compile(
    r"(subprocess\.(run|call|check_call|check_output|Popen)|os\.(system|exec|spawn)|"
    r"^\s*(crontab|launchctl|systemctl)\s)",
    re.MULTILINE,
)


def _source_files() -> list[Path]:
    files = []
    for pattern in ("*.py", "*.sh"):
        files.extend(sorted((LAB / "examples").glob(pattern)))
        files.extend(sorted((LAB / "starter").glob(pattern)))
        files.extend(sorted((LAB / "tests").glob(pattern)))
    return files


def test_no_file_in_this_lab_executes_a_scheduler_command():
    """The rule, enforced: install commands are printed, never run."""
    offenders = []
    for path in _source_files():
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if EXECUTION.search(line) and INSTALLERS.search(line):
                offenders.append(f"{path.name}:{number}: {line.strip()}")
    assert offenders == [], "a file appears to execute a scheduler command:\n" + "\n".join(
        offenders
    )


def test_the_generator_writes_only_where_it_is_told(tmp_path):
    """No default output path, no home directory, no surprises."""
    import gen_schedules

    before = sorted(tmp_path.iterdir())
    assert before == []
    gen_schedules.main(
        ["--out", str(tmp_path), "--hour", "3", "--minute", "5", "--label", "test.job"]
    )
    names = sorted(p.name for p in tmp_path.iterdir())
    assert names == [
        "test.job.cron",
        "test.job.plist",
        "test.job.service",
        "test.job.timer",
    ]
