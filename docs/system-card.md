# System card — experimental portfolio build

Updated September 27, 2026. The platform is a local authorization and evaluation
laboratory for a workplace assistant. Forty decision-template holdouts and the
self-service evaluation workflow are implemented. The 400 fresh baseline/defended
trials are complete, with a **FAIL** gate: defended clean utility 5/40,
observed attacker wins 0/160, and two unresolved attacked timeouts. See the
[frozen results and failure analysis](evidence/release-v1-2026-09-27/README.md). No production or
universal prompt-injection-resistance claim is made.

## Intended use and implemented system

A reviewer can inspect a synthetic agent task, proposed tool actions, authorization
decisions, scoped approvals, committed effects, independent grades, and retained
failures. The six tools search/read documents, list/create/update tickets, and
request document sharing. Sharing writes to a simulated sink, not a real service.

FastAPI establishes operator identity; a durable worker runs the bounded model
loop; a deterministic gateway evaluates trusted actor and task contracts. The
host validates a container's proposed effect and atomically commits the simulated
mutation, approval consumption, audit, and idempotency result in SQLite. Worker
leases prevent stale workers from committing. The operator console and offline
comparison viewer expose evidence without asking for private reasoning traces.

The experimental baseline and prompt-only profile disable business authorization
within synthetic episodes. All three profiles retain bounded execution and outer
episode/container containment. Ordinary application endpoints use defended mode.
See [the trust boundaries](threat-model.md) and [architecture](../arch_plan/secure-agent-platform-plan.md).

## Model and execution profile

The installed Mac profile pins Qwen3-4B Q4_K_M, model revision
`bc640142c66e1fdd12af0bd68f40445458f3869b`, and llama.cpp b11149, commit
`d2e54583c7452353eb35d40431281f6ee984332f`. The model artifact SHA-256 is
`7485fe6f11af29433bc51cab58009521f205840f5b4ae3a32fa7f92e8534fdf5`.
The model license is Apache-2.0; the runtime license is MIT. Exact download,
runtime, sampling, and context settings are in [the pinned profile](../config/model-mac-small.json).

Published Mac evidence used Apple M1 Metal, one 8192-token slot, seed 42,
temperature 0.7, top-p 0.8, top-k 20, and non-thinking generation. The bounded
loop allows eight steps, 4096 generated tokens per episode, 768 per call, one
schema repair, and 300 seconds per episode. A completed model reply does not
establish task completion. The graders inspect resulting state and output.
The runtime's grammar does not enforce the unanchored nonblank search regex;
host validation still enforces it.

## Measured results

The frozen release yielded baseline/defended clean success of 2/40 and 5/40,
attacked success of 4/160 and 7/160, and observed attacker wins of 104/160 and
0/160. Defended worst-case wins are 2/160 because of two unresolved timeouts.
All 400 outcomes are retained; the product gate fails. The evaluated holdout is
now exposed and cannot remain untouched if used for subsequent tuning.

The following are separate development studies and must not be pooled into that score.

| Study | Measured result | Interpretation |
|---|---|---|
| [84 fresh episodes, fourteen tasks](evidence/fourteen-task-live-2026-09-24/README.md) | Defended clean 14/14; attacked utility 13/14; observed attacker wins 0/14. Baseline and prompt-only each 12/14, 10/14, 4/14. | Useful development comparison; one defended false-completion failure remains. |
| [First ten-episode receipt pilot](evidence/receipt-live-pilot-2026-09-25/README.md) | Both arms failed all five tasks. | A valid effect receipt did not compensate for omitted required reads/listing. |
| [Ten-episode receipt disclosure follow-up](evidence/receipt-disclosure-2026-09-25/README.md) | Template-only treatment completed 5/5 tasks; all four payloads reached model requests; one denied attack was followed by recovery. Control failed 5/5. | One known task; evidence of recovered workflow utility, not held-out security. |

Authored replay is a deterministic boundary/grader check, not a model trial.
All published failed grades remain in their original reports. Exact canary,
canonical base64, and lowercase-hex matching do not detect arbitrary encodings or
semantic disclosure. A zero observed attack count does not establish zero risk.

## Release protocol and outstanding limits

The [release workflow](release-evaluation.md) now supports a pre-execution freeze,
exactly 400 resumable trials, and separate PASS/FAIL/UNUSABLE gate results. It
uses forty new decision-rule templates, four fixed attacks each, declared lineage, pinned
source/environment/model/tool image, and passing invariant/isolation evidence.
It rechecks state grades and journal consistency, reports attack exposure and
paired task-bootstrap intervals, and preserves incomplete trials in denominators.
The tooling itself is tested with explicit test doubles; those tests are not
held-out or fresh-model evidence.

The release remains experimental even if the behavioral gate passes: remaining
acceptance work includes improved utility and completion in a new declared study, a host-wide public-network
audit, bounded artifact storage, additional live recovery/cleanup measurements,
an independent clean-checkout walkthrough, and the final recording. The
[limitations declaration](../evaluations/release-limitations-v1.json) travels with
the frozen experiment. Changing policy or graders after seeing held-out results
requires a separately identified follow-up; the original outcomes remain published.

The author knows the synthetic fixtures and defenses. Automated overlap checks
cannot prove semantic independence. The benchmark measures this fixed local
model and authored task/payload distribution, not enterprise deployment safety.
Raw transcripts and database snapshots are privileged evidence; response clearance
does not sanitize them. Local checksums detect accidental changes, not forgery by
the machine owner. Containers are a laboratory boundary, not microVM isolation.
There is no production multi-tenancy, model-authored shell/code execution, live
enterprise integration, or measured RTX 5080 performance in this release.

The [v1 decision corpus](held-out-corpus.md) shares resource/action plumbing and
attack mechanisms with development. Its eight families are not an independent
external benchmark. The [runbook](run-400.md) lets a reviewer create a schedule
without generation, then run bounded sessions without replacing failed trials.
