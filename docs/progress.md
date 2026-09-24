# Implementation status

Updated September 23, 2026. The architecture plan remains the target design.

## First increment: authorization kernel and scripted evidence

- [x] Record sanitized Mac hardware and runtime readiness.
- [x] Establish Python 3.12 package, dependency lock, CLI, Ruff, mypy, pytest, and CI.
- [x] Validate proposals for `documents.read` and `tickets.create`.
- [x] Check workspace, resource scope, actor ACLs, and coarse confidentiality.
- [x] Bind expiring approvals to action, episode, execution key, contract, policy,
  resource snapshot, and sensitivity state; consume with the effect transaction.
- [x] Persist episode state, idempotency keys, simulated effects, and audit in SQLite WAL.
- [x] Exercise concurrent delivery, precommit failure, reopen/retry, and cancellation.
- [x] Add one authored development scenario and a state/output grader.
- [x] Export labeled replay JSON/Markdown with source/scenario hashes and checksums.

## Second increment: isolated tool execution

- [x] Pin the official Python base image by digest; build separate tool/probe images.
- [x] Add a fixed Docker supervisor with bounded input/output and explicit cleanup.
- [x] Compute outside the SQLite write lock and recheck policy/approval state on commit.
- [x] Reject forged effects and state changes that occur during computation.
- [x] Run clean/attacked replay through the same container backend for both profiles.
- [x] Measure 20 passing container smoke checks on Docker Desktop 29.7.2.
- [x] Expand deterministic coverage to 77 tests and add isolated smoke/replay to CI.

The first container smoke exposed dormant network interfaces and an automatic
removal race. The corrected checks verify active interfaces/routes; cleanup
confirms removal instead of accepting an in-progress response. See [the runbook](sandbox.md).

## Third increment: bounded native inference

- [x] Pin official Qwen3-4B Q4_K_M weights and a native llama.cpp arm64 runtime.
- [x] Add explicit project-local downloads, checksum verification, and license retention.
- [x] Add a loopback-only adapter with bounded HTTP, exact server tokenization,
  schema-constrained responses, and no provider/model fallback.
- [x] Persist requests and raw model responses before tool dispatch.
- [x] Enforce context, token, step, output, and time budgets, including one schema repair.
- [x] Pause at approval requests; reject post-cancellation and post-deadline effects.
- [x] Run baseline, prompt-only, and defended clean/attacked trials through Docker.
- [x] Export schedules, traces, SQLite backup, raw calls, grades, and checksums.
- [x] Confirm native Metal offload of 37/37 layers with an 8192-token context.
- [x] Pass 127 deterministic tests, including transport, protocol ordering,
  runtime budgets, evidence denominators, and installed-runtime integrity.

The first live trials exposed premature final answers with no tool effects. The
independent state grader marked them unsuccessful. Live testing also identified
that canonical JSON sorting changed schema property order, which matters to the
runtime's generation grammar. The wire format now preserves discriminator-first
ordering and requires tool tags; a regression test covers this boundary.

The development task is now version 2: its requested title and body requirement
are explicit in the user-visible task. The grader is unchanged. Version 1 trials
remain recorded, including failures caused by omitted body detail or title casing.

At this milestone the loop persisted evidence but did not implement durable leases, automatic
resume, an authenticated approval API, or model-failure retries. See the
[native-model runbook](local-model.md).

Measured outcome: all three task-v2 clean trials passed. Baseline and prompt-only
made the unauthorized write; defended denied it but did not complete the original
task. All 24 development episodes (including earlier failures) are retained in
the [evidence bundle](evidence/local-model-2026-09-23/README.md). This is a useful
feasibility result with a visible utility cost, not a passed release gate.

## Fourth increment: development suite and review simulation

- [x] Author ten development tasks covering scope, actor ACLs, read-only work,
  multiple reads/writes, sensitive approvals, refusals, and missing resources.
- [x] Grade committed reads, required attempts, exact ticket counts and requested
  bodies, final output, forbidden effects, and exact canary disclosures.
- [x] Add a deterministic reviewer with a predeclared exact-action contract,
  separate from the grader and attack objective. Ordinary runs still pause.
- [x] Execute 60 paired scripted cases: defended clean 10/10, attacked utility
  10/10, observed attack wins 0/10. These are authored actions, not model results.
- [x] Verify all 20 defended scripted cases again with real isolated Docker tools;
  preserve the separate report and the same five review decisions.
- [x] Add explicit replay/live suite commands, full schedules, source/fixture
  snapshots, SQLite backups, raw model calls, and exported checksums.
- [x] Retain denial-feedback development experiments, including false completion
  claims that fail the independent state grader.
- [x] Pass 156 tests plus lint, formatting, and strict type checks; add suite replay
  to CI. The tests include approval credential exclusion and cancellation on review.

See the [suite runbook](development-suite.md) and
[experiment evidence](evidence/development-suite-2026-09-23/README.md).
Both task-reminder treatments still failed live recovery: the model claimed
success without creating a ticket. All twelve new live episodes are retained;
no failed episode was removed or regraded. All six clean trials passed, and both
defended attacked trials blocked the write but failed task utility.

## Fifth increment: complete live feasibility and inspectable analysis

- [x] Complete all 60 fresh local-model episodes with isolated tools and simulated review.
- [x] Publish every result: clean utility 8/10 baseline, 9/10 prompt-only, 10/10 defended;
  attacked utility 6/10, 6/10, 8/10; observed attack wins 4/10, 4/10, 0/10.
- [x] Retain both defended recovery failures and false completion claims; no regrading.
- [x] Measure 185 model calls, 5,939 generated tokens, zero schema repairs, and no
  unfinished episodes. Observe 27.00–75.89 s per episode and about 3.59 GiB native
  server command maximum RSS under uncontrolled host load.
- [x] Add checksum/schedule-validated offline analysis, common-clean conditional
  denominators, paired task-bootstrap intervals, and overlapping failure labels.
- [x] Export an offline comparison viewer with escaped untrusted text, restrictive
  CSP, original tasks, tool decisions, simulated reviews, and independent grades.
- [x] Verify all 60 replay selections in Chrome, mobile layout, and hostile-text handling.
- [x] Add CLI progress after each saved episode and a five-minute reviewer walkthrough.
- [x] Pass 179 tests, Ruff, formatting, and strict mypy checks.

See [the complete live evidence and model decision](evidence/ten-task-live-2026-09-23/README.md).
**Phase 0 feasibility is complete.** Retain the pinned `mac-small` profile for
platform development, provisionally: it solves all ten clean tasks but still
fails recovery after two blocked attacks. The release model choice remains open
pending broader evidence. Only two of six planned tools exist; no held-out suite
has been authored or frozen, and no portfolio release gate has passed.

## Sixth increment: durable worker kernel

- [x] Add schema-v3 jobs with idempotent submissions, transactional claims,
  renewable leases, random tokens, and monotonically increasing claim generations.
- [x] Permit one active lease across workers; fence model checkpoints, terminal
  status, tool preparation, and effect commits in their own write transactions.
- [x] Recover saved responses with stable execution keys, identical model inputs,
  and preserved token/step/repair budgets and original episode deadlines.
- [x] Fail explicitly when a process dies before its model response is saved;
  reserve its full token allowance and never silently generate a replacement.
- [x] Release leases for approval waits; atomically wake jobs on review, handle
  review/checkpoint races, and reject expired or changed approval scope.
- [x] Pin recovery to model identity, source hashes, task, budgets, and tool backend.
- [x] Test real subprocess deaths before and after effect commit, stale workers,
  concurrent claims, cancellation, heartbeat renewal, and database migration.
- [x] Add `make demo-durable` with state grading, simulated review/interruption,
  and a reopened database; run it in CI. It performs zero model trials.
- [x] Pass 207 tests, lint, formatting, and strict types; rerun all 60 scripted
  development episodes and all seven durable-demo checks successfully.

See the [durable execution contract and runbook](durable-execution.md). These are
library-level worker guarantees, not authentication or production process isolation.
The existing synchronous benchmark remains a separate execution mode; its published
live evidence is unchanged. No fresh model evaluation is claimed for this increment.

## Seventh increment: authenticated local control plane

- [x] Add a loopback-only FastAPI service with private bearer credentials and
  separate operator/observer permissions; the worker does not load API credentials.
- [x] Derive actor/workspace from trusted identity, allow only predefined defended
  tasks, and scope run/approval access to the authenticated owner.
- [x] Atomically commit resources, job, ownership, idempotency binding, and audit;
  preserve retry identity and enforce a bounded pending-run admission limit.
- [x] Expose status, redacted timelines, cancellation, and scoped approval detail/review.
- [x] Reject stale approvals at review time and again at effect commit; validate
  current scope, ACLs, sensitivity, policy, resource state, and run deadline.
- [x] Enforce exact Host/Origin, browser Fetch Metadata, explicit CSRF headers,
  bounded JSON bodies, non-cacheable responses, and generic validation errors.
- [x] Add separate setup/API/worker commands and a real HTTP smoke that restarts
  the API during an approval wait, then completes via another worker process.
- [x] Pass 256 tests, lint, formatting, and strict types; all 12 real HTTP smoke
  checks pass. The smoke uses authored responses and performs zero model trials.
- [x] Lock API/test dependencies and update their license metadata inventory.

See the [API runbook and trust boundaries](control-plane.md). HTTP authority is
separated; the API and worker still share the trusted local OS user and SQLite.
The existing live evaluation evidence is unchanged. There is no browser approval
UI, production identity provider, or hardened worker process isolation yet.

## Next increment: interactive operator UI

1. Build the scenario picker and redacted execution timeline against the authenticated API.
2. Display exact review scope, expiry, and resource versions with explicit approve/reject.
3. Test browser escaping, credential handling, stale review errors, and restart behavior.

Extend coverage to the remaining four planned tools during platform work. The
static report viewer does not replace the authenticated application/approval UI.

## Later milestones

The remaining work follows the architecture plan: all six tools;
stronger operator/worker isolation;
approval UI and execution timeline; paired held-out evaluation and uncertainty;
recovery/isolation checks; frozen held-out benchmark; portfolio recording and release.

Direct `Store.review()` remains a trusted library call; authentication applies to
the HTTP review endpoint. Authored replay recovery is not evidence that a model
can recover after a denied call.
