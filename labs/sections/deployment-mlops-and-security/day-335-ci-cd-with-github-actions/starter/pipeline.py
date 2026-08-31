"""STARTER -- implement each TASK below, then run the tests.

Every function that raises NotImplementedError is yours to write. The
imports, constants and data structures are given; the logic is not.
Run `bash tests/run_tests.sh` to see which tasks are still outstanding.

Reason about a CI pipeline before you push and wait eleven minutes to find out.

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
    PUSH = 'push'
    PULL_REQUEST = 'pull_request'
    PR_TARGET = 'pull_request_target'
    SCHEDULE = 'schedule'
    MANUAL = 'workflow_dispatch'

@dataclass
class Job:
    name: str
    needs: list[str] = field(default_factory=list)
    minutes: float = 1.0
    uses_secrets: bool = False
    caches: list[str] = field(default_factory=list)
    fails_per_100: float = 0.0

@dataclass
class Workflow:
    name: str
    triggers: list[Trigger]
    jobs: dict[str, Job]

def missing_needs(wf: Workflow) -> list[str]:
    """Dependencies naming a job the workflow does not define."""
    raise NotImplementedError('TASK 1: implement missing_needs. Dependencies naming a job the workflow does not define.')

def find_cycle(wf: Workflow) -> list[str]:
    """One dependency cycle if any exists, normalised so it is stable."""
    raise NotImplementedError('TASK 3: implement find_cycle. One dependency cycle if any exists, normalised so it is stable.')

def finish_times(wf: Workflow) -> dict[str, float]:
    """When each job finishes, assuming unlimited parallel runners.

    A job starts as soon as everything it needs has finished, so its finish
    time is the latest of its dependencies plus its own duration.
    """
    raise NotImplementedError('TASK 4: implement finish_times. When each job finishes, assuming unlimited parallel runners.')

def critical_path(wf: Workflow) -> tuple[list[str], float]:
    """The longest chain of dependent jobs, and how long it takes.

    This is what a pipeline actually costs in wall-clock time. Summing the job
    durations overstates it, sometimes by a lot, because independent jobs run
    at the same time.
    """
    raise NotImplementedError('TASK 5: implement critical_path. The longest chain of dependent jobs, and how long it takes.')

def total_minutes(wf: Workflow) -> float:
    """Runner minutes consumed. What you are billed for, and not what you wait."""
    raise NotImplementedError('TASK 6: implement total_minutes. Runner minutes consumed. What you are billed for, and not what you wait.')

@dataclass(frozen=True)
class Finding:
    rule: str
    job: str
    message: str

def review(wf: Workflow) -> list[Finding]:
    """Everything wrong with this pipeline's shape."""
    raise NotImplementedError("TASK 7: implement review. Everything wrong with this pipeline's shape.")

def without(wf: Workflow, job_name: str) -> Workflow:
    """The same workflow with one job removed, and dependants re-pointed.

    Removing a job must not orphan the jobs that needed it -- they inherit its
    dependencies, which is what actually happens when you delete a stage.
    """
    raise NotImplementedError('TASK 8: implement without. The same workflow with one job removed, and dependants re-pointed.')

def savings_from_removing(wf: Workflow, job_name: str) -> dict[str, float]:
    """What deleting one job buys in wall-clock and in runner minutes."""
    raise NotImplementedError('TASK 9: implement savings_from_removing. What deleting one job buys in wall-clock and in runner minutes.')
