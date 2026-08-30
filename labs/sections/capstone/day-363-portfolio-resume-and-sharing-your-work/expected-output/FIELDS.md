# Reading the claim assessment

## An assessment line

      WEAK    Reduced answer latency to 840ms.
              measurement without a baseline; does not say who did it

| Part | Meaning |
| --- | --- |
| grade | `STRONG`, `WEAK` or `VAGUE`. |
| claim | The sentence, truncated for display. |
| reasons | Every property that is missing, so the fix is obvious. Absent on a strong claim. |

## The three grades

| Grade | Meaning |
| --- | --- |
| `STRONG` | All four properties present — measured, with a baseline, attributed, and linked to something openable. |
| `WEAK` | Something is missing, and it is fixable by adding words. |
| `VAGUE` | Vague wording **and** no measurement. The weakest kind: it sounds like a result and contains none. |

The distinction between `WEAK` and `VAGUE` is about what it costs to fix. A missing baseline is a sentence away. A claim with nothing measured needs you to go and measure something.

## The four properties

| Property | Failure it prevents |
| --- | --- |
| measurement | An adjective standing where a figure should be. |
| baseline | A number that describes the present rather than a change. |
| attribution | A reader unable to tell what you did from what the team did. |
| evidence | A link only the author can open. |

## The hint lines

    Reduced answer latency to 840ms.    add the value it started from, what you personally did

A grade says something is wrong. A hint says what to add. The second is the one you can act on, which is why the report produces both.
