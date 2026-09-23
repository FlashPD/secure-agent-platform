# Current trust boundary

This increment is a local, trusted Python simulation. It executes two fixed
operations over synthetic state. No model-authored code, shell, network calls,
containers, HTTP API, or browser UI participate in a replay.

Trusted inputs are the fixture contract, resource metadata/ACLs, policy code,
selected experiment profile, operator review, and grader predicates. Document
bodies and action proposals are untrusted. Pydantic rejects unknown authority
fields and invalid tool arguments before replay starts.

The defended profile enforces actor permissions and per-task scope. Reading a
confidential document marks the episode confidential. Subsequent internal writes
require review; shared writes are denied. Shared writes without confidential reads
also require review. Baseline/prompt-only profiles deliberately disable these
business checks inside a synthetic episode. No prompt/model ablation is measured yet.

SQLite `BEGIN IMMEDIATE` serializes policy checks and effect application. Resource
metadata is loaded from the episode, and approval hashes bind its full snapshot.
Effect, approval consumption, idempotency output, and audit share one transaction.
Committed retries return their original result; changing an execution key's
arguments raises a conflict. Audit is append-only by convention, not tamper-proof.

`Store.review()` and `Store.approval()` are trusted operator library functions.
They have no authentication and must never become model tools. Operator/worker
credential separation and API authentication are future work. A nonce prevents
review replay; it does not establish reviewer identity.

The current grader detects exact synthetic canaries in final responses and ticket
title/body text. It does not detect paraphrases or encoded leakage. The demo has
one cross-project attack, so it cannot establish broad attack coverage or an ASR.

Not implemented: hostile-code containment, model context/output/time budgets,
durable worker leases/fencing, web security, hosted multi-tenancy, or a live model
integration. Do not expose this package as a remote service.
