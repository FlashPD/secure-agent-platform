# Implementation status

Updated September 24, 2026. The architecture plan remains the target design.

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
At this milestone, the browser UI was still pending. The existing live evaluation
evidence is unchanged. Production identity and hardened worker isolation remain out
of scope for this increment.

## Eighth increment: interactive operator console

- [x] Build a React/TypeScript UI served by FastAPI from the same loopback origin.
- [x] Add task selection, owner-scoped recent runs, redacted timelines, and confirmed cancellation.
- [x] Display exact action arguments, original task/scope, policy, resource version,
  expiry, and hash with explicit approve/reject; never render approval nonces.
- [x] Keep bearer credentials only in tab memory; clear sessions on disconnect/reload,
  abort requests, and discard late responses. Observer sessions remain read-only.
- [x] Preserve submission identity after a lost response. Never automatically retry
  review decisions or replace the action snapshot being inspected.
- [x] Serve only an exact compiled-asset allowlist; preserve Host/Origin and API
  authentication checks, strict CSP, no-store responses, and escaped content.
- [x] Pass 267 Python tests and nine real Chrome workflow/security scenarios,
  including API restart, stale/expired approvals, hostile content, and mobile layout.
- [x] Pass Python/TypeScript/format checks; verify the wheel includes and serves
  UI assets while excluding credentials and local artifacts.
- [x] Add locked frontend dependencies, license metadata, a browser CI job,
  the operator runbook, and sanitized screenshots.

See the [operator UI runbook](operator-ui.md) and
[verification screenshots](evidence/operator-ui-2026-09-23/README.md).
These are authored-fixture browser
checks with real API/worker processes, not fresh model trials or a human-usability
study. Independent paired grades remain in the offline report viewer. No live
benchmark result changed, and the held-out release gate is still pending.

## Ninth increment: complete the tool surface

- [x] Add ACL/scope-filtered FTS5 document search and bounded ticket listing.
- [x] Add versioned ticket updates with full snapshot checks and idempotent effects.
- [x] Add exact-document sharing into an episode-local sink, with source/destination review.
- [x] Propagate confidentiality through search snippets, ticket previews, and stored tickets.
- [x] Migrate schema 4 to 5 transactionally, preserving legacy tickets and concurrent startup.
- [x] Extend the fixed container runner, independent grader, reviewer, and approval UI.
- [x] Add four development workflows; new console installs offer 14 scenarios.
- [x] Run all 24 scripted tool episodes through Docker: defended clean and attacked
  utility 4/4 each, zero observed attacker wins; both permissive profiles expose
  all four authored attacks. This is zero model trials.
- [x] Pass all 24 container contract/containment checks.
- [x] Pass 311 Python tests, 11 Chrome scenarios, Python/TypeScript checks, and UI build.
- [x] Rerun the original 60-episode replay and seven-check durable recovery demo.
- [x] Publish checksummed scripted evidence, the offline viewer, and exact-share screenshot.

See [tool contracts and reproduction](tool-surface.md) and
[recorded verification](evidence/tool-surface-2026-09-23/README.md).
The original ten-task live evidence remains unchanged. Search uses host FTS5
before sending authorized snippets to isolated computation; share effects remain
entirely synthetic. No new live-model or held-out result is claimed.

## Tenth increment: expanded live feasibility and diagnostics

- [x] Complete all 24 original new-tool trials with pinned local inference and Docker.
- [x] Retain eleven exact-punctuation task failures and inspect their saved state.
- [x] Publish raw calls, source/fixture snapshots, paired analysis, and an offline viewer.
- [x] Run twelve additional live wording-treatment trials; all pass with unchanged
  graders and attacks, and original failures remain failed.
- [x] Use clarified task literals for new console installs; retain all prior suite versions.
- [x] Complete the clarified catalogue’s 84 scripted episodes; defended utility 14/14
  clean and attacked, with zero model trials.
- [x] Reconcile measured/unknown token use, timing, tool coverage, and denial denominators.
- [x] Measure two 1,000-decision policy samples, retaining both results and source.
- [x] Pass 333 Python tests, lint, formatting, and strict types.
- [x] Document the remaining release work and focused-effort estimate.

See the [complete results and limits](evidence/six-tool-live-2026-09-23/README.md)
and [diagnostics contract](runtime-diagnostics.md). In the original 24 trials,
clean/attacked utility was 3/4 and 2/4 for baseline, 2/4 and 2/4 for prompt-only,
and 2/4 and 2/4 for defended. No profile attempted a forbidden action: there is
no new live denial-recovery denominator or comparative attack reduction.
The observed policy P95 values (0.0633 and 0.0322 ms) exclude persistence,
resource resolution, tools, and inference. No held-out release result is claimed.

## Eleventh increment: resumable benchmark sessions

- [x] Persist benchmark scheduling, started markers, immutable results, and session history.
- [x] Add CLI status/resume and episode-limited sessions; Ctrl+C drains the current episode.
- [x] Reject concurrent writers and changed source, dependencies, fixtures, model, or tools.
- [x] Reuse saved results; preserve effects and unknown-token reservations after process death.
- [x] Keep interrupted trials in denominators and unknown durations out of timing distributions.
- [x] Test real subprocess death, foreground-group signals, lost exports, and compatibility failures.
- [x] Pass 356 tests, lint, formatting, and strict types, including `uv run` signal forwarding.
- [x] Complete a 24-episode CLI replay across sessions of 2, 3, and 19 episodes;
  verify final checksums, paired analysis, and diagnostics with zero model trials.

See [the terminal runbook](resumable-benchmarks.md). This is deterministic recovery
evidence, not a fresh-model experiment or the planned 400-episode release benchmark.

## Twelfth increment: fourteen-task live evidence and measured resume

- [x] Account for all 84 fresh model trials across three sessions of 10, 10, and 64 episodes.
- [x] Verify every published result against the local benchmark journal and original checksums.
- [x] Publish clean utility 12/14 baseline, 12/14 prompt-only, 14/14 defended;
  attacked utility 10/14, 10/14, 13/14; observed attacker wins 4/14, 4/14, 0/14.
- [x] Retain all 13 failed task grades, including the defended false completion after review rejection.
- [x] Export paired uncertainty, conditional denominators, the offline viewer, and runtime diagnostics.
- [x] Reconcile 275 calls and 9,484 generated tokens; distinguish episode timing from session wall time.

See [the complete publication](evidence/fourteen-task-live-2026-09-24/README.md).
There are no missing or interrupted episodes. This demonstrates live pause/resume
between episodes, not live mid-episode crash recovery. The four newer tool-workflow
attacks still show no observed wins in any profile. No held-out release gate has
passed, and earlier versioned studies remain unchanged. Packaging performed no inference.

## Thirteenth increment: multiple attacks per task

- [x] Add versioned, bounded attack variants without changing trusted task/reviewer/grader contracts.
- [x] Schedule one clean control and every declared payload per profile, with payload provenance.
- [x] Preserve attack identity and committed effects across pauses and interrupted-trial accounting.
- [x] Reject dropped/substituted variants and catalogue/fixture mismatches; retain legacy evidence support.
- [x] Keep correlated payloads together in paired task bootstrap draws, including unequal payload counts.
- [x] Add attack selection to the offline viewer and payload IDs to failure/diagnostic records.
- [x] Add a four-family development pilot with 15 authored episodes and no inference.
- [x] Pass the Python suite and new integrity/outage regressions, lint/format/type checks,
  TypeScript checks, and two Chrome checks covering every payload and legacy reports.

See [contracts, reproduction, and limits](multi-attack-evaluation.md). This reuses
the confidential-review workflow; the independent development catalogue remains
fourteen tasks. New payload effectiveness under fresh inference is unmeasured.
The original published runs and grades are unchanged.

## Fourteenth increment: twenty-task development corpus and stronger graders

- [x] Preserve the fourteen versioned development tasks and add six compositional workflows.
- [x] Author four fixed attack families for every new workflow; full catalogue has 174 episodes.
- [x] Add independent forbidden-listing/source-share, exact-response, and opt-in encoded-canary predicates.
- [x] Retain four project-authorized sibling edits and three final-response disclosures as defended failures.
- [x] Pass all 20 defended clean tasks and preserve all seven known attack wins in full replay.
- [x] Expose 20 clean scenarios in new operator installations while preserving saved suite selection.
- [x] Pass 402 Python tests, lint/format checks, and strict typing.
- [x] Complete all 90 expansion episodes through Docker and independently recheck every grade.
- [x] Pass 13 Chrome scenarios and frontend checks; publish the viewer and disclosure screenshot.

See [task provenance, grouping, reproduction, and interpretation limits](development-corpus.md).
The six new tasks have related development ancestors; no new independent-family
or held-out claim is made. Grader v4 leaves historical published grades unchanged.
This increment performs zero fresh model trials.
The [Docker evidence](evidence/development-expansion-2026-09-24/README.md) retains
all 55 failed task grades across the three profiles.

## Fifteenth increment: per-ticket update authority

- [x] Add trusted update-ticket lists and `gateway-v3` denial before computation/review.
- [x] Preserve project inventory access while narrowing write scope; missing/null lists keep legacy authority.
- [x] Reject revoked scope at review, after approval, and during effect computation.
- [x] Version five task contracts without changing their prose, attacks, scripts, or graders.
- [x] Select the v5 catalogue for new console installations and display editable tickets to reviewers.
- [x] Pass 423 Python tests, lint/format checks, and strict typing.
- [x] Preserve all 20 defended clean tasks and block the four sibling-edit paths in full replay.
- [x] Retain three final-response disclosures as failures, without exposing grader canaries to policy.
- [x] Complete all 90 treatment episodes through Docker, recheck every grade, and publish the offline viewer.
- [x] Pass 14 Chrome scenarios, including exact ticket scope and sibling preservation in review.

See [ADR 003](adr-003-ticket-scope-and-response-boundary.md) and
[the treatment evidence](evidence/ticket-scope-2026-09-24/README.md). Existing saved control
settings and original evidence retain their prior task scope. This increment
performs zero fresh model trials; final-response confidentiality remains unenforced.

## Sixteenth increment: opt-in final-response authorization

- [x] Add a trusted synthetic recipient and response clearance, independent of tool approval.
- [x] Withhold confidential-influenced final text from an internal-only destination at commit time.
- [x] Commit decision metadata with the final result under current scope, cancellation, and worker lease.
- [x] Retain raw local evidence; test rollback/recovery without another model generation.
- [x] Apply the same rule to scripted benchmarks and record response-denial counts and viewer annotations.
- [x] Keep all three known response disclosures blocked in treatment replay while retaining its clean-task failure.
- [x] Preserve the default v5 catalogue and all prior versioned evidence.
- [x] Complete all 90 treatment episodes through Docker, recheck every grade, and publish the comparison.
- [x] Pass the 445-test Python suite and 22 focused response tests after adding a deadline regression
  (446 distinct tests covered), lint/format/types, the frontend build, and 15 Chrome scenarios.

See [ADR 004](adr-004-response-clearance-treatment.md) and
[the treatment evidence](evidence/response-scope-2026-09-24/README.md). The six-task treatment
has defended clean utility 5/6, attacked utility 20/24, and observed attack wins
0/24 in authored replay. Its 16.7-point clean-utility loss exceeds the proposed
five-point objective, so it remains opt-in and exits nonzero. No live-model
effectiveness or held-out release claim follows from these checks.

## Seventeenth increment: verified effect receipts

- [x] Add an opt-in, fixed completion receipt bound to one exact reviewed ticket update.
- [x] Verify the episode-local execution, consumed approval, current state, and authority at final commit.
- [x] Withhold false completion claims, matching initial fixtures, stale state, and revoked permissions.
- [x] Recover after a finalization crash without regeneration or duplicate effects.
- [x] Version a matched control and treatment; retain prior wording, evidence, and default catalogue.
- [x] Pass 472 Python tests, lint/format/types, the frontend build, and 16 Chrome scenarios.
- [x] Complete 180 Docker-isolated authored episodes and independently recheck every state grade.
- [x] Publish both comparisons, complete denominators, exact five-grade improvement, and receipt provenance.

See [ADR 005](adr-005-verified-effect-receipts.md) and
[the evidence](evidence/effect-receipt-2026-09-25/README.md). Defended clean success
recovers from 5/6 to 6/6 and attacked success from 20/24 to 24/24, with zero observed
attacker wins in both matched suites. The receipt deliberately releases a completion
bit; it does not declassify model prose or establish whole-task success. No fresh
model trials or held-out release gate are claimed.

## Next increment: live treatment feasibility and held-out preparation

Measure ticket/response-scope and effect-receipt behavior with fresh inference. Audit related
workflow families and freeze forty untouched held-out workflows and their
four attack variants, keeping related workflow families in the same split.
See the [remaining milestones and estimate](release-readiness.md).

## Later milestones

The remaining work follows the architecture plan: stronger operator/worker isolation;
paired held-out evaluation and uncertainty;
recovery/isolation checks; frozen held-out benchmark; portfolio recording and release.

Direct `Store.review()` remains a trusted library call; authentication applies to
the HTTP review endpoint. Authored replay recovery is not evidence that a model
can recover after a denied call.
