# Reading the transcript

## A frame line

    t=5   streaming 'The refund '

| Part | Meaning |
| --- | --- |
| `t=` | Logical tick. One per observable moment, so the numbers are exact and assertable. |
| state | `idle`, `waiting`, `streaming`, `done`, `error` or `cancelled`. |
| text | Exactly what the interface would be showing at that moment. Truncated in the display, not in the data. |
| note | Present on waiting and on terminal frames — why it is waiting, or how it ended. |

## A summary line

    done after 12 ticks, ttft=4, 47 chars  perceived_wait=4

| Field | Meaning |
| --- | --- |
| ending | Which of the three terminal states was reached. |
| ticks | Total duration. **Not** what the user experiences. |
| `ttft` | Time to first token — the tick at which anything was first readable. `never` if nothing ever appeared. |
| chars | Length of the text the user is left with. Zero after a discarded partial. |
| `perceived_wait` | Time spent with nothing to read. Equals `ttft` when there is one, and the whole run when there is not. |

## The comparison to make

    streaming   done after 12 ticks, ttft=4,  perceived_wait=4
    blocking    done after 20 ticks, ttft=12, perceived_wait=12

Same content. The streaming run is better on both numbers here, but the one that matters is the second: even if total duration were identical, the user would wait a third as long with nothing to read.

    partial kept       error after 8 ticks, 21 chars
    partial discarded  error after 8 ticks,  0 chars

Identical failure, identical timing. One version also takes away what the user had already read.
