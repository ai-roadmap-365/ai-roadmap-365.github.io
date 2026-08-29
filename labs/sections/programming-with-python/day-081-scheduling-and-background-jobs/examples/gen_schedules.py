"""Generate schedule files for cron, launchd and systemd — and install nothing.

This script writes text files into a directory you name. That is all it does.
It never runs ``crontab``, never runs ``launchctl``, never runs ``systemctl``,
and never touches anything under your home directory unless you point
``--out`` there yourself. The install commands are *printed* so you can read
them; running them is your decision, made deliberately, on a machine you
intend to schedule something on.

One schedule definition produces all three formats, which is the point: the
cron five-field expression, the launchd ``StartCalendarInterval`` dictionary
and the systemd ``OnCalendar`` string all say the same thing in three
dialects, and seeing them side by side is the fastest way to learn any of them.

    python3 examples/gen_schedules.py --out examples/schedules \\
        --hour 2 --minute 30 --project-dir /opt/reports
"""

from __future__ import annotations

import argparse
import datetime as dt
from dataclasses import dataclass
from pathlib import Path
from xml.sax.saxutils import escape

from cronexpr import parse

WEEKDAY_NAMES = ("Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat")
SYSTEMD_DAYS = ("Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat")


@dataclass(frozen=True)
class JobSchedule:
    """One schedule, expressible in three dialects."""

    label: str
    minute: int
    hour: int
    days_of_week: tuple[int, ...] = ()  # empty means every day; 0 = Sunday
    project_dir: str = "/opt/reports"
    python: str = "/usr/bin/python3"
    script: str = "job.py"
    log_dir: str = "/var/log/reports"
    timezone: str = "UTC"

    # ---- the command every dialect runs -------------------------------

    @property
    def command(self) -> str:
        return f"{self.python} {self.project_dir}/{self.script} --output-dir {self.project_dir}/out"

    @property
    def argv(self) -> tuple[str, ...]:
        return (
            self.python,
            f"{self.project_dir}/{self.script}",
            "--output-dir",
            f"{self.project_dir}/out",
        )

    # ---- cron ---------------------------------------------------------

    @property
    def cron_expression(self) -> str:
        dow = ",".join(str(d) for d in self.days_of_week) if self.days_of_week else "*"
        return f"{self.minute} {self.hour} * * {dow}"

    def cron_line(self) -> str:
        """The crontab entry, with the environment a cron job does NOT inherit."""
        stdout = f"{self.log_dir}/{self.label}.log"
        return "\n".join(
            [
                "# Generated schedule. Read it, then decide whether to install it.",
                "# Install with:  crontab -l > my.cron ; cat this-file >> my.cron ; crontab my.cron",
                "# List with:     crontab -l          Edit with:  crontab -e",
                "#",
                "# cron gives a job almost no environment: a short PATH, no shell",
                "# profile, HOME set but nothing sourced, and the home directory as",
                "# the working directory. Everything the job needs is therefore set",
                "# here, explicitly, rather than assumed.",
                "SHELL=/bin/sh",
                "PATH=/usr/local/bin:/usr/bin:/bin",
                f"TZ={self.timezone}",
                "MAILTO=",
                "",
                "# min hour day-of-month month day-of-week  command",
                f"{self.cron_expression} cd {self.project_dir} && {self.command} "
                f">> {stdout} 2>&1",
                "",
            ]
        )

    # ---- launchd (macOS) ----------------------------------------------

    def launchd_plist(self) -> str:
        args = "\n".join(f"      <string>{escape(a)}</string>" for a in self.argv)
        weekday_entries = ""
        if self.days_of_week:
            weekday_entries = "\n".join(
                "    <dict>\n"
                f"      <key>Weekday</key><integer>{day}</integer>\n"
                f"      <key>Hour</key><integer>{self.hour}</integer>\n"
                f"      <key>Minute</key><integer>{self.minute}</integer>\n"
                "    </dict>"
                for day in self.days_of_week
            )
            calendar = f"  <key>StartCalendarInterval</key>\n  <array>\n{weekday_entries}\n  </array>"
        else:
            calendar = (
                "  <key>StartCalendarInterval</key>\n"
                "  <dict>\n"
                f"    <key>Hour</key><integer>{self.hour}</integer>\n"
                f"    <key>Minute</key><integer>{self.minute}</integer>\n"
                "  </dict>"
            )
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <!-- Label: the unique name launchd knows this job by. Reverse-DNS by
       convention, and the file should be named after it. -->
  <key>Label</key>
  <string>{escape(self.label)}</string>

  <!-- ProgramArguments: argv, one element per array entry. NOT a shell
       command line: there is no shell here, so no globbing, no pipes, and
       no quoting rules to get wrong. -->
  <key>ProgramArguments</key>
  <array>
{args}
  </array>

{calendar}

  <!-- RunAtLoad false: loading the job should not immediately run it.
       Setting this true is a common surprise during installation. -->
  <key>RunAtLoad</key>
  <false/>

  <!-- launchd starts the job with a minimal environment, exactly like cron.
       Anything the job needs must be stated. -->
  <key>WorkingDirectory</key>
  <string>{escape(self.project_dir)}</string>
  <key>EnvironmentVariables</key>
  <dict>
    <key>PATH</key><string>/usr/local/bin:/usr/bin:/bin</string>
    <key>TZ</key><string>{escape(self.timezone)}</string>
  </dict>

  <!-- Where output goes. Without these, stdout and stderr are discarded and
       a failing job leaves no trace at all. -->
  <key>StandardOutPath</key>
  <string>{escape(self.log_dir)}/{escape(self.label)}.out.log</string>
  <key>StandardErrorPath</key>
  <string>{escape(self.log_dir)}/{escape(self.label)}.err.log</string>
</dict>
</plist>
"""

    # ---- systemd (Linux) ----------------------------------------------

    @property
    def on_calendar(self) -> str:
        if self.days_of_week:
            days = ",".join(SYSTEMD_DAYS[d] for d in self.days_of_week)
            return f"{days} *-*-* {self.hour:02d}:{self.minute:02d}:00"
        return f"*-*-* {self.hour:02d}:{self.minute:02d}:00"

    def systemd_service(self) -> str:
        exec_start = " ".join(self.argv)
        return f"""# {self.label}.service — WHAT to run. It has no schedule of its own.
# Check the file with:   systemd-analyze verify {self.label}.service
# Run it once by hand:   systemctl --user start {self.label}.service
[Unit]
Description=Daily station report
# The timer will not start the job before the network is up.
After=network-online.target

[Service]
# oneshot: this is a task that finishes, not a daemon that stays up.
# systemd counts the unit as active until the process exits.
Type=oneshot
WorkingDirectory={self.project_dir}
Environment=PATH=/usr/local/bin:/usr/bin:/bin
Environment=TZ={self.timezone}
ExecStart={exec_start}
# A hard ceiling, enforced by systemd rather than by the job itself.
TimeoutStartSec=600
# Everything the job prints goes to the journal, tagged with this identifier:
#   journalctl --user -u {self.label}.service -n 50
StandardOutput=journal
StandardError=journal
SyslogIdentifier={self.label}
"""

    def systemd_timer(self) -> str:
        return f"""# {self.label}.timer — WHEN to run it. Pairs with {self.label}.service.
# Install (user scope, no root):
#   cp {self.label}.service {self.label}.timer ~/.config/systemd/user/
#   systemctl --user daemon-reload
#   systemctl --user enable --now {self.label}.timer
# Inspect:  systemctl --user list-timers
[Unit]
Description=Run the daily station report

[Timer]
OnCalendar={self.on_calendar}
# Persistent: if the machine was off at the scheduled moment, run once as
# soon as it comes back. This is the catch-up behaviour cron does not have.
Persistent=true
# Spread load: start somewhere in the first minute rather than exactly on
# the second, so a fleet of machines does not stampede one server.
RandomizedDelaySec=60
AccuracySec=1s
Unit={self.label}.service

[Install]
WantedBy=timers.target
"""

    # ---- the human-readable summary ------------------------------------

    def summary(self) -> str:
        schedule = parse(self.cron_expression)
        base = dt.datetime(2026, 7, 19, 0, 0, tzinfo=dt.timezone.utc)
        upcoming = []
        cursor = base
        for _ in range(3):
            cursor = schedule.next_run_after(cursor)
            upcoming.append(cursor.strftime("%Y-%m-%d %H:%M"))
        return "\n".join(
            [
                f"label          : {self.label}",
                f"cron           : {self.cron_expression}",
                f"launchd        : StartCalendarInterval Hour={self.hour} Minute={self.minute}",
                f"systemd        : OnCalendar={self.on_calendar}",
                f"reads as       : {schedule.describe()}",
                f"next three (from {base:%Y-%m-%d %H:%M} UTC): " + ", ".join(upcoming),
            ]
        )


def write_all(schedule: JobSchedule, out_dir: Path) -> list[Path]:
    """Write the four schedule files. Returns the paths written."""
    out_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for name, text in (
        (f"{schedule.label}.cron", schedule.cron_line()),
        (f"{schedule.label}.plist", schedule.launchd_plist()),
        (f"{schedule.label}.service", schedule.systemd_service()),
        (f"{schedule.label}.timer", schedule.systemd_timer()),
    ):
        path = out_dir / name
        path.write_text(text, encoding="utf-8")
        written.append(path)
    return written


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="gen_schedules.py",
        description=(
            "Write cron, launchd and systemd schedule files for one job. "
            "Installs nothing; prints the install commands so you can decide."
        ),
    )
    parser.add_argument("--out", type=Path, required=True, help="directory to write into")
    parser.add_argument("--label", default="com.example.dailyreport")
    parser.add_argument("--hour", type=int, default=2)
    parser.add_argument("--minute", type=int, default=30)
    parser.add_argument(
        "--weekday",
        type=int,
        action="append",
        default=None,
        help="0=Sunday .. 6=Saturday; repeat for several. Omit for every day.",
    )
    parser.add_argument("--project-dir", default="/opt/reports")
    parser.add_argument("--python", default="/usr/bin/python3")
    parser.add_argument("--log-dir", default="/var/log/reports")
    parser.add_argument("--timezone", default="UTC")
    args = parser.parse_args(argv)

    schedule = JobSchedule(
        label=args.label,
        minute=args.minute,
        hour=args.hour,
        days_of_week=tuple(args.weekday or ()),
        project_dir=args.project_dir,
        python=args.python,
        log_dir=args.log_dir,
        timezone=args.timezone,
    )
    written = write_all(schedule, args.out)
    print(schedule.summary())
    print()
    print("written:")
    for path in written:
        print(f"  {path}")
    print()
    print("NOTHING was installed. To install, you would run — deliberately, yourself:")
    print("  cron    : crontab -l > my.cron && cat "
          f"{args.out}/{schedule.label}.cron >> my.cron && crontab my.cron")
    print("  launchd : cp "
          f"{args.out}/{schedule.label}.plist ~/Library/LaunchAgents/ && "
          f"launchctl load ~/Library/LaunchAgents/{schedule.label}.plist")
    print("  systemd : cp "
          f"{args.out}/{schedule.label}.{{service,timer}} ~/.config/systemd/user/ && "
          f"systemctl --user daemon-reload && systemctl --user enable --now {schedule.label}.timer")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
