# Reading the build plan

## The plan summary

    cold build   0/6 layers cached  rebuild 76.0s
    after edit   2/6 layers cached  rebuild 76.0s

| Part | Meaning |
| --- | --- |
| `n/m layers cached` | How many layers were reused out of the total. |
| `rebuild Ns` | Wall-clock cost of the layers that must run. Cached layers cost nothing. |

The two lines are the whole argument. A cold build is the same either way; the
warm build is where ordering pays.

## The first miss

    first miss   line 3: COPY . .
                 reads changed file(s): src/app.py

The first layer that could not be reused, and why. Everything below it rebuilds
regardless of its own inputs, so this one line explains the entire cost.

## The reasons a layer is not reused

| Reason | Meaning |
| --- | --- |
| `no cache (cold build)` | Nothing to reuse; every layer runs. |
| `reads changed file(s): …` | This layer copies something that changed. It is the first miss. |
| `a previous layer changed` | This layer's own inputs are fine. It rebuilds anyway. |

The third is the rule people forget. A layer cannot be reused just because
nothing it touches has changed.

## The cost model

| Instruction | Seconds |
| --- | --- |
| `RUN` that installs dependencies | 75 |
| any other `RUN` | 8 |
| `COPY` / `ADD` | 1 |
| `FROM`, `WORKDIR`, `ENV`, `EXPOSE`, `USER`, `CMD`, … | 0 |

The absolute numbers are nominal. What matters is the **ratio**: an install is
about seventy-five times a copy, which is why an ordering mistake that
invalidates the install costs so much more than it looks like it should.

## The lint rules

| Rule | What it costs you |
| --- | --- |
| `copy-before-install` | Every source edit re-runs the install. Time. |
| `unpinned-base` | A rebuild months later gets a different image. Reproducibility. |
| `apt-cache-kept` | The package index ships inside the layer. Size, and see `security.md`. |
| `pip-cache-kept` | The wheel cache ships inside the layer. Size. |
| `runs-as-root` | The process runs as uid 0 in the container. Blast radius. |

`copy-before-install` is reported at the line of the **COPY**, not the install,
because the copy is the line you move.
