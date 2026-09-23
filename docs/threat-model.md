# Current trust boundary

This increment executes two fixed operations over synthetic state. The local
replay uses trusted Python; the isolated replay sends bounded JSON to a fixed
container entrypoint. Neither mode accepts model-authored code or shell commands.
There is no model integration, HTTP API, or browser UI yet.

Trusted inputs are the fixture contract, resource metadata/ACLs, policy code,
selected experiment profile, operator review, and grader predicates. Document
bodies and action proposals are untrusted. Pydantic rejects unknown authority
fields and invalid tool arguments before replay starts.

The defended profile enforces actor permissions and per-task scope. Reading a
confidential document marks the episode confidential. Subsequent internal writes
require review; shared writes are denied. Shared writes without confidential reads
also require review. Baseline/prompt-only profiles deliberately disable these
business checks inside a synthetic episode. No prompt/model ablation is measured yet.

SQLite `BEGIN IMMEDIATE` serializes preparation and effect application separately.
Computation runs between transactions, without holding the write lock. Resource
metadata is loaded from the episode, and approval hashes bind its full snapshot.
After computation, the host validates the returned effect and rechecks current
policy, cancellation, approval expiry/consumption, and the full state hash.
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

The container backend uses no host mounts or network, a read-only root filesystem,
unprivileged UID, dropped capabilities, no-new-privileges, default seccomp, and
bounded resources. A separate diagnostic image probes these restrictions. Tool
stdout/stderr and stdin writes are bounded by size and wall time. The supervisor
explicitly removes a timed-out container; killing the Docker CLI alone is not
sufficient. Failure to confirm cleanup raises a typed error. If the supervisor
itself crashes, orphan reconciliation is still pending; this is distinct from
the tested tool-process timeout path.

No microVM-grade isolation or resistance to kernel/container-engine exploits is
claimed. A malicious operator, compromised host, and modified trusted images are
outside this lab's boundary. Docker's configured engine/context is trusted.

Not implemented: model context/output/time budgets,
durable worker leases/fencing, web security, hosted multi-tenancy, or a live model
integration. Do not expose this package as a remote service.
