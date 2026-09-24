# Remaining work for a portfolio release

The application, six tools, deterministic authorization tests, durable worker,
operator console, twenty-task development corpus, and development evidence are implemented. The release is still
experimental: the planned held-out corpus and product-quality gate do not exist.
Completing application features is distinct from validating agent behavior.

## Remaining milestones and estimate

One focused engineer-day is about six hours, including verification and writing.
These estimates are planning ranges, not a commitment or measured implementation
velocity. Model failures and corpus authoring are the main uncertainties.

| Work | Done when | Focused days |
|---|---|---:|
| Expanded live feasibility | All 24 original new-tool trials accounted for; budgets, failures, and denial outcomes published; wording follow-ups kept separate | Completed this increment |
| Corpus and split | 20 development and 40 held-out tasks, four attacks per held-out task, workflow-family separation, provenance, and freeze manifest | 4–6 |
| Release evaluation and gates | All 400 required episodes; multi-payload paired task-cluster intervals, ablation, comparison compatibility checks, explicit gate result | 2–3 |
| Reliability evidence | Remaining cancellation, artifact-quota, model-failure, orphan-container, telemetry, policy-latency, and public-network checks implemented or explicitly scoped with acceptance consequences | 2–3 |
| Portfolio packaging | Model/system card, architecture decisions, clean-checkout reproduction, sanitized evidence, five-minute recording, and final reviewer walkthrough | 1–2 |

With expanded live feasibility complete, the remaining estimate is approximately
**9–14 focused days (roughly 55–85 hours)**, or about **4–6 weeks at 15 hours/week**.
The estimate at the start of this increment was 10–16 days (60–100 hours).
Unattended inference adds elapsed time. A larger-model investigation or substantial changes
identified by development trials can extend the estimate. The first six-tool
run took 54 minutes for 24 episodes (mean about 135 seconds). A simple linear
projection gives about 15 hours for 400 episodes before setup/recovery; held-out
workflows and additional attacks may take longer. This is scheduling guidance,
not a throughput guarantee.

Resumable benchmark sessions are now implemented and covered by deterministic
crash/signal tests. The [84-episode live run](evidence/fourteen-task-live-2026-09-24/README.md)
also completed across three sessions without missing/interrupted trials; see
[the runbook](resumable-benchmarks.md). The estimate above
predates that increment and has not been re-estimated. A full held-out run remains pending.

The RTX 5080 inference profile, repeated multi-seed release trials, external
AgentDojo adapter, hosted deployment, and optional telemetry dashboards are not
on this critical path. Production multi-tenancy and hostile-host protection remain
outside the first-release goals. HTTP credential separation already exists;
stronger OS process separation must not be presented as implemented.

## Evidence that still needs to be collected

- Effective development attacks on the expanded tool workflows. The fresh
  [24-episode six-tool run](evidence/six-tool-live-2026-09-23/README.md) had no
  forbidden proposals in any profile, so denial recovery remains unmeasured on
  those workflows. In the subsequent 84-episode catalogue run, those four newer
  workflows again had zero observed attacker wins in every profile. Do not pool
  differently versioned runs into one score.
- Forty held-out tasks. The [twenty-task development target](development-corpus.md)
  is now met, with four attacks on each of the six added workflows. All twenty
  tasks are development assets with known related families. Do not relabel them
  as held-out. Freeze task
  families, payloads, budgets, grader predicates, and thresholds before release runs.
- Four fixed attack families for each held-out task; the current catalogue has
  fourteen one-payload tasks and six four-payload tasks. [Multiple-attack scheduling, resumable identities, and paired
  task-cluster analysis](multi-attack-evaluation.md) are now implemented and tested
  with a four-family development pilot and the six-workflow expansion. New live
  effectiveness is unmeasured. Tool-response insertion remains pending. Grader v4
  now supports explicitly declared canonical base64/hex canary matching; arbitrary
  encoding and semantic leakage remain outside that coverage.
- Treatment decisions for the seven exposed defended paths in expansion replay:
  four protected-sibling edits inside authorized projects and three final-response
  disclosures. These are authored counterexamples, not live attack rates. Resolve
  or explicitly retain these limits before freezing release policy and thresholds.
- Release gates that require compatible, complete evidence. Initial objectives
  from the architecture plan are clean utility at least 80%, defended clean-utility
  loss no greater than five percentage points, and lower observed attack success
  without more ungraded trials. A failed objective must remain visible and result
  in an experimental release, not an edited denominator.
- Structured-generation compatibility: the pinned runtime does not enforce the
  search query’s unanchored nonblank regex in its grammar. Host validation still
  enforces it. Test an equivalent supported constraint in a declared schema
  treatment before claiming full grammar coverage.
- False-block annotations, approval burden, state/task disruption, and infrastructure
  failure counts. A denied action alone is not evidence of complete protection.
- Fresh-model mid-episode crash recovery remains unmeasured. Safe pause/resume
  between episodes is now demonstrated by all 84 live trials completing across
  sessions of 10, 10, and 64. Process-death and signal-injection tests still use
  authored replay/model doubles; do not describe the live run as a crash experiment.
- A measured public-network audit after downloads, bounded artifact storage,
  cancellation during computation,
  and cleanup after supervisor interruption. Existing container network denial
  is not a host-wide traffic audit. Two 1,000-call policy microbenchmarks now
  satisfy the initial narrowly scoped latency measurement; broader step timing
  and telemetry remain incomplete.
- An independent clean-checkout walkthrough that verifies the published checksums
  and reproduces a small fresh benchmark. The full release must account for all
  400 required baseline/defended episodes, whether successful or not.

The original [architecture plan](../arch_plan/secure-agent-platform-plan.md)
remains the acceptance target. [Implementation progress](progress.md) and linked
versioned evidence distinguish completed work from these remaining objectives.
