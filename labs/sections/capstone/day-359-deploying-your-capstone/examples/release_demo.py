#!/usr/bin/env python3
"""Five deployments: one clean, four that stop at different gates."""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from release import Build, DeployBlocked, Deployment, Health, deploy, rollback


def run(label: str, build: Build, **kwargs) -> None:
    dep = Deployment(live_version="v1.0.0")
    print(f"--- {label} ---")
    try:
        deploy(dep, build, **kwargs)
    except DeployBlocked:
        pass
    for event in dep.events:
        print(event.line())
    print(f"  => {dep.summary()}")


def main() -> int:
    run("clean release", Build("v1.1.0"))
    run("tests failed", Build("v1.1.0", tests_passed=False))
    run("irreversible migration", Build("v1.1.0", migrations_reversible=False))
    run("starts but cannot serve", Build("v1.1.0"), health=Health(readiness=False))
    run("canary exceeds error budget", Build("v1.1.0"), error_rate=0.09)

    print("--- rollback after a bad promotion ---")
    dep = Deployment(live_version="v1.0.0")
    deploy(dep, Build("v1.1.0"))
    print(f"  promoted: {dep.summary()}")
    rollback(dep)
    print(f"  {dep.events[-1].line().strip()}")
    print(f"  => {dep.summary()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
