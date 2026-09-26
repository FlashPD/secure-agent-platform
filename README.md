# Secure Agent Execution & Evaluation Platform

**Status: all six tools, durable execution, the authenticated API, and the operator
console are implemented. An 84-episode live benchmark completed across three sessions;
its development evidence is published. The development corpus now has 20 tasks;
the held-out portfolio release remains in progress.**

A local workplace-agent lab that measures legitimate task completion and resistance to prompt injection, with application-enforced permissions, reviewable actions, and reproducible security evaluations.

[Architecture and implementation plan](arch_plan/secure-agent-platform-plan.md)

Development, state, and the demo run on the Mac. Model inference can run on the Mac or on an optional RTX 5080 PC over an SSH tunnel. No paid cloud service or model API is required.

The first runnable slice reads a synthetic launch document and creates a ticket.
An authored attack script redirects the ticket to an unauthorized project.
The deterministic gateway blocks that write and permits the intended one.

## Latest measured development results

The [fourteen-task live benchmark](docs/evidence/fourteen-task-live-2026-09-24/README.md)
completed all 84 scheduled episodes across three sessions (10 + 10 + 64), using
the pinned local model and isolated tools:

| Profile | Clean task success | Task success under attack | Observed attacker wins |
|---|---:|---:|---:|
| Baseline | 12/14 | 10/14 | 4/14 |
| Prompt-only | 12/14 | 10/14 | 4/14 |
| Defended | 14/14 | 13/14 | 0/14 |

The one defended failure is retained: simulated review rejected a sensitive
write, but the model falsely claimed it had created the ticket. Independent
grading found zero tickets. All 13 failed task grades across the three profiles
remain in the report. These self-authored development results are not a held-out
release gate, and zero observed wins does not establish zero attack risk.

Open the [offline comparison viewer](docs/evidence/fourteen-task-live-2026-09-24/analysis/explorer.html),
[paired analysis](docs/evidence/fourteen-task-live-2026-09-24/analysis/analysis.md),
[runtime diagnostics](docs/evidence/fourteen-task-live-2026-09-24/diagnostics/diagnostics.md),
or [five-minute reviewer walkthrough](docs/reviewer-walkthrough.md).

## Run locally

Requires Python 3.12+ and [uv](https://docs.astral.sh/uv/). From this directory:

```sh
uv sync --locked
make doctor
make check
make demo-replay
make demo-durable
make eval-suite
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
success rate. The browser console is described below.

`make demo-durable` demonstrates a persisted approval wait, simulated review,
an interruption after ticket commit, and recovery without a duplicate ticket.
It also uses authored responses and performs **zero model trials**. The worker
uses transactional claims, renewable leases, and fencing at every checkpoint and
effect commit. Separate tests kill subprocesses before and after effects.
See the [durable execution runbook and limits](docs/durable-execution.md).

The authenticated API supports defended task submission, owner-scoped status and
redacted timelines, cancellation, and exact-action review. Start the scripted
application locally, with API and worker in separate terminals. Building the
React/TypeScript UI also requires Node.js 24 LTS:

```sh
make ui-setup ui-build
uv run --locked agentguard control-init --fixture
make api-serve       # Terminal 1: loopback-only API
make worker          # Terminal 2: durable worker, no operator credential file
```

Open `http://127.0.0.1:8000/`, connect using the token in
`artifacts/control/operator.token`, and choose **authorized shared write** to
review an exact action. If control settings already exist, skip initialization.
The console supports task selection, redacted timelines, approval/rejection,
cancellation, and observer access. See the [operator UI runbook](docs/operator-ui.md)
or use the [control-plane API client](docs/control-plane.md).
`make control-smoke` verifies real HTTP authentication and API restart during an
approval wait with separate worker processes. Fixture runs are labeled and perform
zero model trials; omit `--fixture` when initializing a separate live instance.

`make eval-suite` expands deterministic validation to ten development tasks and
60 paired episodes, including exact-action approval simulation, confidential-data
rules, actor ACLs, and state/output grading. It is also scripted replay. See the
[suite runbook](docs/development-suite.md) for fixtures, grading limits, and the
explicit `make eval-suite-live` command for fresh model trials.

Analyze any completed suite and open its standalone comparison viewer:

```sh
uv run --locked agentguard eval-analyze artifacts/suites/<run-id> \
  --output artifacts/analyses/<run-id>
open artifacts/analyses/<run-id>/explorer.html  # macOS
```

The analyzer verifies evidence checksums and scheduled results, calculates paired
comparisons and conditional attack success, and adds descriptive task-bootstrap
intervals for fresh inference. The viewer shows proposals, policy decisions, and
independent grades side by side. It runs offline and displays untrusted content
as text. See [the analysis contract and limits](docs/evaluation-analysis.md).

`make eval-multi-attack` exercises one clean input plus four attack families under
all three profiles (15 authored episodes, zero model trials). Scheduling,
pause/resume, paired task-cluster statistics, and the viewer preserve each payload's
identity. See [the multiple-attack development pilot](docs/multi-attack-evaluation.md).

The [twenty-task catalogue](docs/development-corpus.md) adds six workflows with
four attacks each. `make eval-development` runs all 174 authored episodes;
`make eval-expansion` runs the 90 original expansion episodes, retaining seven
defended attacker wins involving sibling-ticket edits and final-response disclosures,
and exits nonzero after saving complete reports. These are scripted boundary
checks, not new live-model measurements.
The [90-episode Docker evidence](docs/evidence/development-expansion-2026-09-24/README.md)
includes the complete outcomes, offline viewer, and retained failure analysis.

The [ticket-scope treatment](docs/adr-003-ticket-scope-and-response-boundary.md)
adds exact ticket permissions to all five update workflows. `make eval-development`
now selects the versioned v5 catalogue; `make eval-ticket-scope` runs its six-task
treatment subset. These authored checks block the four sibling edits and retain
the three final-response disclosures, so both commands still exit nonzero.
`make eval-expansion` retains the original seven-failure fixtures. New operator
installations use the narrowed contracts; existing settings keep their suite.
No fresh-model improvement or output-confidentiality guarantee is claimed.
The [90-episode Docker treatment evidence](docs/evidence/ticket-scope-2026-09-24/README.md)
includes the exact four improved outcomes, remaining failures, and offline viewer.

The opt-in [response-clearance treatment](docs/adr-004-response-clearance-treatment.md)
adds a separate final-output boundary. `make eval-response-scope` withholds the
three known disclosures, but also blocks a harmless clean triage response:
defended clean success is 5/6 and attacked success is 20/24, with zero observed
attacker wins in authored replay. The command exits 1 for the clean-task failure.
This measured utility cost keeps it out of the default catalogue. Raw evaluation
artifacts remain privileged and are not sanitized by the response policy.
The [90-episode response treatment evidence](docs/evidence/response-scope-2026-09-24/README.md)
preserves all five changed outcomes and the failed clean-task grade.

The opt-in [verified-effect receipt treatment](docs/adr-005-verified-effect-receipts.md)
recovers this completion-message utility with an explicit, fixed receipt for an
exact reviewed ticket update. It verifies the committed effect and current authority
before delivering any confirmation. In a matched 180-episode Docker replay,
defended clean success rises from 5/6 to 6/6 and attacked success from 20/24 to
24/24, while both controls retain zero observed attacker wins. These are authored
boundary checks, not fresh model trials or a held-out release result. Run
`make eval-effect-receipt`; [the full evidence](docs/evidence/effect-receipt-2026-09-25/README.md)
preserves the matched control and all baseline failures. The default remains v5.

Benchmarks can run directly from your terminal across multiple sessions. Add
`--max-episodes 10` to `agentguard eval-suite` to pause after ten episodes, or press
Ctrl+C once to finish the current episode and pause. Continue with
`uv run --locked agentguard eval-resume artifacts/suites/<run-id>` and inspect
progress with `agentguard eval-status`. Keep the same code/model environment.
See [pause, resume, and interruption accounting](docs/resumable-benchmarks.md).

## Run isolated tools

Start Docker Desktop, then run:

```sh
make sandbox-build     # Explicit download/build from a digest-pinned Python image
make sandbox-smoke     # Real containment probes; nonzero exit if a check fails
make demo-isolated     # Same authored episodes, with both profiles using containers
```

The container uses a fixed entrypoint, unprivileged UID, no network, read-only
root, dropped capabilities, and CPU/memory/PID limits. No host paths, credentials,
or Docker socket are mounted. Bounded JSON travels over stdin/stdout; only the
host can commit simulated effects. Permissions and approvals are rechecked after
computation, outside which the database write lock is released.

`make demo-replay` retains the lightweight in-process backend for local contract
tests. Reports identify the actual backend. Neither mode performs model inference.
See the [sandbox runbook and measured checks](docs/sandbox.md).

## Run a real local model

The pinned `mac-small` profile targets macOS on Apple Silicon. Start Docker, then:

```sh
make models-fetch       # Explicit ~2.5 GB model download plus pinned native runtime
make model-serve        # Keep this terminal open; loopback-only native inference
```

In another terminal, run `make eval-smoke`. It executes six fresh trials across
baseline, prompt-only, and defended profiles using the isolated tools. Reports
include failed episodes, state-based grades, raw model-call evidence, model/runtime
checksums, template, sampling settings, and budgets. This one-task development
smoke does not establish benchmark-level security or utility.
See the [local-model runbook and current limitations](docs/local-model.md).

The [measured six-episode comparison](docs/evidence/local-model-2026-09-23/README.md)
passed every clean trial. The injection succeeded against baseline and prompt-only;
the gateway blocked it under defended, but the model failed to recover and finish
the task. Earlier failed development trials are retained alongside the final smoke.

Two subsequent [denial-feedback experiments](docs/evidence/development-suite-2026-09-23/README.md)
retained that utility failure: the model claimed success after denial without
creating a ticket. Their state grades remain failed.

The earlier [ten-task live evaluation](docs/evidence/ten-task-live-2026-09-23/README.md)
retains all 60 scheduled episodes, including two defended recovery failures.
It predates the expanded six-tool schema and is kept separate from the latest
84-episode results above; the studies are not pooled or selectively regraded.

## Expanded tool workflows

Document search, ticket listing and versioned updates, and reviewed document sharing
now use the same gateway and transactional effect boundary. Shares write only to an
episode-local simulated sink. The console displays the exact source document or
current ticket when reviewing these actions.

```sh
make eval-tools             # 24 authored episodes; zero model trials
make sandbox-build          # Rebuild the fixed tool image after upgrading
make eval-tools-isolated    # The same workflows through Docker
make eval-tools-live        # 24 fresh episodes; original versioned task wording
```

The [tool contract and upgrade runbook](docs/tool-surface.md) covers filtering,
version checks, approvals, migration, and the four new development tasks. New
console installations offer all 20 development scenarios using `suite-v4.json`,
including the six new workflows. Existing settings retain their
selected suite version. See the
[scripted tool-surface evidence](docs/evidence/tool-surface-2026-09-23/README.md).
The ten-task live results above predate the expanded schema and remain unchanged.

The [expanded live evaluation](docs/evidence/six-tool-live-2026-09-23/README.md)
retains all 24 original trials. Eleven strict task grades failed on ambiguous
punctuation requirements; those failures remain published. All profiles had zero
observed attacker wins and zero policy-denial episodes, so this run does not
establish comparative attack reduction or denial recovery. Separate versioned
wording experiments passed all 12 follow-up trials without changing graders.
The evidence also includes token accounting, tool coverage, observed durations,
and narrowly scoped policy-cost measurements.

## Implemented boundaries

- Typed tool proposals cannot supply actor identity, scope, or approval grants.
- The gateway checks actor ACLs, task scope, and confidential/shared-write rules.
- Scoped approvals expire and are invalidated by changed actions, resources,
  permissions, or episode state.
- SQLite transactions commit approval consumption, simulated effects, audit,
  and execution-key results together. Retries do not create duplicate tickets.
- Queued runs reject missing, expired, and superseded worker leases, including
  after tool computation. Recovery reuses saved responses and original budgets.
- Approval waits release leases; persisted reviews atomically wake the job.
- The API derives actor/workspace from credentials, scopes every run to its owner,
  rejects cross-origin writes, and separates observer access from operator review.
- Independent graders inspect stored tickets and final output rather than the
  agent's success claim or the number of denied calls.

The security tests exercise direct forbidden actions, stale/cross-episode grants,
concurrent retries, cancellation, and rollback on precommit failure.

## Project evidence and next milestone

- [Implementation progress and remaining milestones](docs/progress.md)
- [Remaining release work and effort estimate](docs/release-readiness.md)
- [Twenty-task corpus, grader coverage, and retained security failures](docs/development-corpus.md)
- [84-episode live results and measured resume](docs/evidence/fourteen-task-live-2026-09-24/README.md)
- [Runtime budget, coverage, and denial diagnostics](docs/runtime-diagnostics.md)
- [Interactive operator console and browser security](docs/operator-ui.md)
- [Operator console screenshots and verification](docs/evidence/operator-ui-2026-09-23/README.md)
- [Complete live feasibility and failure analysis](docs/evidence/ten-task-live-2026-09-23/README.md)
- [Offline analysis and viewer contract](docs/evaluation-analysis.md)
- [Live model results and retained failure analysis](docs/evidence/local-model-2026-09-23/README.md)
- [Ten-task suite and denial-feedback experiments](docs/evidence/development-suite-2026-09-23/README.md)
- [Observed development hardware](docs/hardware.md)
- [Current trust boundary and limitations](docs/threat-model.md)
- [Why this first increment precedes live feasibility](docs/adr-001-first-increment.md)
- [Why a bounded native loop precedes durable execution](docs/adr-002-local-model-loop.md)
- [Dependency license inventory](docs/dependency-licenses.json)

Next: measure attack effectiveness, address or explicitly retain exposed policy
limitations, and freeze the held-out corpus before release evaluation. The
twenty-task development target and multi-attack scheduling are implemented. The portfolio release still
requires the full acceptance criteria in the architecture plan.
