# Exercise 6 — compare the two approaches

You have now tested the same behaviour twice. Fill this in from your own two
files, in sentences rather than single words. Count things; do not estimate.

## 1. Count what each approach cost

| Question | `starter/test_report_v1.py` (patch) | `starter/test_report_v2.py` (fakes) |
| --- | --- | --- |
| Lines in the test file (`wc -l`) | | |
| Number of `patch(...)` calls | | |
| Number of string targets you had to get exactly right | | |
| Number of pytest fixtures used (`tmp_path`, …) | | |
| Wall-clock time of the file (`pytest --durations=0`) | | |
| Things that must be undone when a test ends | | |

## 2. Answer these in one or two sentences each

**a.** Which file would still pass if somebody changed
`from sensor_service import fetch_readings` to `import sensor_service` at the
top of the module under test, and why?

**b.** Which file would still pass if the report gained a fifth line? Which
would still pass if `write_daily_report` started writing the file before
fetching the readings?

**c.** Your patch test names a module and an attribute in a string. Nothing
checks that string until the test runs. Name one refactor that would silently
turn that test into a test of nothing, and say what you would notice.

**d.** In exercise 5d you asserted on `client.calls`. That is an assertion about
an interaction, not about a result. Say why it is defensible here, and name one
assertion about interactions that you deliberately did NOT write because it
would break on a harmless refactor.

**e.** `report_v2.build_report` takes six parameters where `write_daily_report`
took two. That is a real cost. Argue either side: is the extra signature worth
it for this program, and what size of program would change your answer?

## 3. The design rule you would give a colleague

Write one sentence, in your own words, that tells someone when to reach for
`patch` and when to move the boundary instead. Then write the single sentence
you would put in a code review comment when you see a test with four patches
in it.

## 4. What you could not remove

Some boundaries cannot be injected — name at least one in this lab, say why,
and say what you would do about it instead.
