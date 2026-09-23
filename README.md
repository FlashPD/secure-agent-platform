# Secure Agent Execution & Evaluation Platform

**Status: first implementation increment; live model and container feasibility pending.**

A local workplace-agent lab that measures legitimate task completion and resistance to prompt injection, with application-enforced permissions, reviewable actions, and reproducible security evaluations.

[Architecture and implementation plan](arch_plan/secure-agent-platform-plan.md)

Development, state, and the demo run on the Mac. Model inference can run on the Mac or on an optional RTX 5080 PC over an SSH tunnel. No paid cloud service or model API is required.

The first runnable slice reads a synthetic launch document and creates a ticket.
An authored attack script redirects the ticket to an unauthorized project.
The deterministic gateway blocks that write and permits the intended one.

## Run locally

Requires Python 3.12+ and [uv](https://docs.astral.sh/uv/). From this directory:

```sh
uv sync --locked
make doctor
make check
make demo-replay
```

If uv is not installed, bootstrap it inside the repository with an available
Python 3.12 (on this Mac: `/opt/homebrew/bin/python3.12`):

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install uv==0.12.18
make setup
```

The Makefile also finds uv in `.venv/bin`. Dependency installation needs network
access; the installed replay and tests need no model, credentials, or services.

`make demo-replay` creates a new directory under `artifacts/replays/` with four
episodes, a SQLite database, JSON and Markdown reports, and report checksums.
Each run compares clean and attacked inputs under baseline and defended profiles.
The baseline deliberately disables business authorization inside its synthetic
episode. Authored recovery attempts the intended project after the redirected write.

**This is scripted replay, not fresh inference or a recording of a model run.**
It exercises contracts and graders; its results are not a measured model attack
success rate. Tools currently run as fixed trusted Python operations. Container
isolation, the model adapter, API, worker leases, and UI remain to be implemented.

## Implemented boundaries

- Typed tool proposals cannot supply actor identity, scope, or approval grants.
- The gateway checks actor ACLs, task scope, and confidential/shared-write rules.
- Scoped approvals expire and are invalidated by changed actions, resources,
  permissions, or episode state.
- SQLite transactions commit approval consumption, simulated effects, audit,
  and execution-key results together. Retries do not create duplicate tickets.
- Independent graders inspect stored tickets and final output rather than the
  agent's success claim or the number of denied calls.

The security tests exercise direct forbidden actions, stale/cross-episode grants,
concurrent retries, cancellation, and rollback on precommit failure.

## Project evidence and next milestone

- [Implementation progress and remaining milestones](docs/progress.md)
- [Observed development hardware](docs/hardware.md)
- [Current trust boundary and limitations](docs/threat-model.md)
- [Why this first increment precedes live feasibility](docs/adr-001-first-increment.md)
- [Dependency license inventory](docs/dependency-licenses.json)

Next: pin a native local model and runtime, measure one real clean/attacked
workflow, validate an isolated tool, and expand to ten development tasks. The
portfolio release requires live paired results and the full acceptance criteria
in the architecture plan; those outcomes have not been measured yet.
