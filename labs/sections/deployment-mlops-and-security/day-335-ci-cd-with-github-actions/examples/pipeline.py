"""Reason about a CI pipeline before you push and wait eleven minutes to find out.

Offline and standard-library only. No runner, no GitHub, no network. The input
is a described workflow -- jobs, what each needs, how long it takes, how often
it fails -- and the questions worth asking are answerable from that.

Three of them:

  how long   the critical path, not the sum. Independent jobs run in parallel.
  how safe   which jobs can reach a secret, and whether a fork can trigger them
  how useful a gate that never fails is not a gate

The third is the one that decays quietly. A test job that has not failed in six
months is either protecting nothing or being ignored, and the pipeline gets
slower every quarter as people add stages nobody has ever seen go red.

Nothing here runs your tests. It reasons about the SHAPE of a pipeline, which
is the part you can get wrong for months without noticing.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Trigger(str, Enum):
    PUSH = "push"                          # a branch in your own repository
    PULL_REQUEST = "pull_request"          # read-only token, no secrets by default
    PR_TARGET = "pull_request_target"      # runs with SECRETS against fork code
    SCHEDULE = "schedule"
    MANUAL = "workflow_dispatch"


@dataclass
class Job:
    name: str
    needs: list[str] = field(default_factory=list)
    minutes: float = 1.0
    uses_secrets: bool = False
    caches: list[str] = field(default_factory=list)
    fails_per_100: float = 0.0     # how often this job catches something


@dataclass
class Workflow:
    name: str
    triggers: list[Trigger]
    jobs: dict[str, Job]


def missing_needs(wf: Workflow) -> list[str]:
    """Dependencies naming a job the workflow does not define."""
    return sorted(
        f"{name} needs '{dep}', which no job defines"
        for name, job in wf.jobs.items()
        for dep in job.needs
        if dep not in wf.jobs
    )


def find_cycle(wf: Workflow) -> list[str]:
    """One dependency cycle if any exists, normalised so it is stable."""
    def walk(node: str, path: list[str]) -> list[str] | None:
        if node in path:
            cycle = path[path.index(node):]
            return list(min(tuple(cycle[i:] + cycle[:i]) for i in range(len(cycle))))
        for dep in wf.jobs[node].needs if node in wf.jobs else []:
            found = walk(dep, path + [node])
            if found:
                return found
        return None

    for name in sorted(wf.jobs):
        found = walk(name, [])
        if found:
            return found
    return []


def finish_times(wf: Workflow) -> dict[str, float]:
    """When each job finishes, assuming unlimited parallel runners.

    A job starts as soon as everything it needs has finished, so its finish
    time is the latest of its dependencies plus its own duration.
    """
    if find_cycle(wf):
        raise ValueError(f"dependency cycle: {' -> '.join(find_cycle(wf))}")
    times: dict[str, float] = {}
    remaining = dict(wf.jobs)
    while remaining:
        ready = [n for n, j in remaining.items()
                 if all(d in times or d not in wf.jobs for d in j.needs)]
        if not ready:
            raise ValueError("no job can start; check the dependency graph")
        for name in sorted(ready):
            job = remaining.pop(name)
            start = max((times[d] for d in job.needs if d in times), default=0.0)
            times[name] = round(start + job.minutes, 2)
    return times


def critical_path(wf: Workflow) -> tuple[list[str], float]:
    """The longest chain of dependent jobs, and how long it takes.

    This is what a pipeline actually costs in wall-clock time. Summing the job
    durations overstates it, sometimes by a lot, because independent jobs run
    at the same time.
    """
    times = finish_times(wf)
    if not times:
        return [], 0.0
    end = max(times, key=lambda n: (times[n], n))
    chain = [end]
    while wf.jobs[chain[-1]].needs:
        deps = [d for d in wf.jobs[chain[-1]].needs if d in times]
        if not deps:
            break
        chain.append(max(deps, key=lambda d: (times[d], d)))
    return list(reversed(chain)), round(times[end], 2)


def total_minutes(wf: Workflow) -> float:
    """Runner minutes consumed. What you are billed for, and not what you wait."""
    return round(sum(j.minutes for j in wf.jobs.values()), 2)


@dataclass(frozen=True)
class Finding:
    rule: str
    job: str
    message: str


def review(wf: Workflow) -> list[Finding]:
    """Everything wrong with this pipeline's shape."""
    out: list[Finding] = []

    for msg in missing_needs(wf):
        out.append(Finding("undefined-need", msg.split()[0], msg))

    cycle = find_cycle(wf)
    if cycle:
        out.append(
            Finding("dependency-cycle", cycle[0],
                    f"cycle: {' -> '.join(cycle + [cycle[0]])}; no job in it can run")
        )
        return out

    # pull_request_target runs with repository secrets against code from a fork.
    if Trigger.PR_TARGET in wf.triggers:
        for name, job in sorted(wf.jobs.items()):
            if job.uses_secrets:
                out.append(
                    Finding("secrets-exposed-to-forks", name,
                            "pull_request_target runs with repository secrets against code the "
                            "fork controls; a pull request can exfiltrate them")
                )

    # A gate that has never failed is not protecting anything you can point to.
    for name, job in sorted(wf.jobs.items()):
        if job.fails_per_100 == 0.0 and job.minutes > 0:
            out.append(
                Finding("gate-never-fires", name,
                        f"has never failed; it costs {job.minutes} min per run and there is no "
                        "evidence it catches anything")
            )

    # A slow job with no cache is the cheapest thing to fix.
    for name, job in sorted(wf.jobs.items()):
        if job.minutes >= 3.0 and not job.caches:
            out.append(
                Finding("no-cache", name,
                        f"takes {job.minutes} min with nothing cached; a dependency cache is "
                        "usually the single largest saving available")
            )
    return out


def without(wf: Workflow, job_name: str) -> Workflow:
    """The same workflow with one job removed, and dependants re-pointed.

    Removing a job must not orphan the jobs that needed it -- they inherit its
    dependencies, which is what actually happens when you delete a stage.
    """
    if job_name not in wf.jobs:
        raise KeyError(job_name)
    inherited = wf.jobs[job_name].needs
    jobs = {}
    for name, job in wf.jobs.items():
        if name == job_name:
            continue
        needs = [d for d in job.needs if d != job_name]
        if job_name in job.needs:
            needs += [d for d in inherited if d not in needs]
        jobs[name] = Job(job.name, needs, job.minutes, job.uses_secrets,
                         list(job.caches), job.fails_per_100)
    return Workflow(wf.name, list(wf.triggers), jobs)


def savings_from_removing(wf: Workflow, job_name: str) -> dict[str, float]:
    """What deleting one job buys in wall-clock and in runner minutes."""
    before_path, before_wall = critical_path(wf)
    after = without(wf, job_name)
    _, after_wall = critical_path(after)
    return {
        "wall_before": before_wall,
        "wall_after": after_wall,
        "wall_saved": round(before_wall - after_wall, 2),
        "minutes_saved": round(total_minutes(wf) - total_minutes(after), 2),
        "on_critical_path": job_name in before_path,
    }
