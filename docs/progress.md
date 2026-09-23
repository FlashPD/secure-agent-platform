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

## Next increment: finish Phase 0 feasibility

1. Pin a native llama.cpp build and Qwen3-4B artifact/license/checksum. Keep
   downloads explicit and capture backend, chat template, sampling, and context.
2. Add a bounded loop and local adapter; persist raw model responses before
   executing proposals. Measure one useful clean task and its attacked counterpart.
3. Expand to ten diverse development tasks with separate grader predicates.
4. Record latency, peak memory, failure counts, and model/schema compatibility.

**Phase 0 has not passed:** real isolated tools now run, but there are no live model
trials yet. No held-out suite has been authored or frozen.

## Later milestones

The remaining work follows the architecture plan: durable queue/leases/fencing;
all six tools; authenticated API and operator/worker credential separation;
approval UI and execution timeline; paired live evaluation and uncertainty;
recovery/isolation checks; frozen held-out benchmark; portfolio recording and release.

Do not treat the current effect transaction as proof of worker fencing, the trusted
`review()` library call as an authenticated approval endpoint, or authored replay
recovery as evidence that a model can recover after a denied call.
