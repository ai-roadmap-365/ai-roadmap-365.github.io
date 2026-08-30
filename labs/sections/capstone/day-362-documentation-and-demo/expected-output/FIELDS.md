# Reading the documentation check

## An issue line

      FAIL  outputs: make run (differs from captured)

| Part | Meaning |
| --- | --- |
| level | `OK`, `WARN` or `FAIL`. Only `FAIL` makes the review fail. |
| check | Which of the six checks. |
| detail | What was found, naming the specific command, section or limitation. |

## The verdict

      => FAIL fail=5 warn=1

`PASS` requires zero `FAIL` findings. Warnings are reported and do not block.

## Warn versus fail, and why the line is there

| Finding | Level | Why |
| --- | --- | --- |
| A documented command that does not exist | **FAIL** | Actively misleads. The reader pastes it and it breaks. |
| A provided command nobody documented | **WARN** | A gap. The reader simply never learns about it. |
| A claimed output that differs from reality | **FAIL** | The reader cannot tell success from failure. |
| No limitations recorded at all | **WARN** | Probably untrue, but it is a prompt rather than a defect. |

Blocking on incompleteness makes the gate annoying, and an annoying gate gets disabled — at which point it catches nothing at all.

## The six checks

| Check | Catches |
| --- | --- |
| `sections` | A missing answer to one of the six questions a reader has. |
| `commands` | A command that was renamed, so the README is confidently wrong. |
| `undocumented_commands` | Capability nobody wrote down. |
| `outputs` | An output that changed, so the reader cannot verify success. |
| `placeholders` | Writing that was never finished. |
| `limitations` | A constraint you know about and never stated. |
