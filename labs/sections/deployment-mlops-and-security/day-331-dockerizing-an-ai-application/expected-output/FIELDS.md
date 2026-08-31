# Reading the image plan

## The plan line

    image  21128 MB   one pull   845.1s   rollout to 20 nodes  16902.0s

| Part | Meaning |
| --- | --- |
| `image N MB` | The size of the **final** stage plus anything carried into it. Earlier stages are discarded. |
| `one pull` | How long a single node waits, at 200 Mbps. |
| `rollout to N nodes` | The pull paid once per node. This is where image size is actually felt. |

A 21 GB image is not "a bit slow to deploy". At twenty nodes it is four and a
half hours of pulling.

## The findings

| Rule | What it means | Typical saving |
| --- | --- | --- |
| `build-tooling-shipped` | Compilers and headers reached the final image. | 0.3–4 GB |
| `weights-baked-in` | Model weights are inside the image. | often the largest single item |
| `fat-base` | The final stage uses the full Python base rather than slim. | ~295 MB |

Each carries `saves_mb`, so the findings are ordered by what removing them
would actually buy rather than by how bad they sound.

## The comparison table

    multi-stage       21128 ->  18053 MB  (3075 MB, 1.17x)
    mount the weights 18053 ->   4553 MB  (13500 MB, 3.97x)
    both              21128 ->   4553 MB  (16575 MB, 4.64x)

Read the middle line against the first. **The multi-stage build — the
optimisation every Docker tutorial teaches — is the smaller of the two wins
here.** Moving the weights out of the image saves four times as much.

That is not an argument against multi-stage builds. It is an argument against
stopping there, which is what most guidance does, because most guidance was
written for web applications where there are no weights.

## The three component purposes

| Purpose | Meaning | May it be dropped from the final image? |
| --- | --- | --- |
| `BUILD` | Needed to produce artefacts, never at run time. | Yes — that is what a builder stage is for. |
| `RUNTIME` | The running process needs it. | No. |
| `DATA` | Weights and assets. Needed at run time. | Not dropped — **relocated** to a volume or object store. |

The distinction between `BUILD` and `RUNTIME` is what makes multi-stage
possible. The distinction between `RUNTIME` and `DATA` is what makes the bigger
saving possible, and it is the one people do not draw.

Note that `cuda-devel` is `BUILD` and `cuda-runtime` is `RUNTIME`. Confusing
them is the most common way to produce either a broken image or a needlessly
enormous one.
