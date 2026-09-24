# Offline paired analysis

`agentguard eval-analyze` analyzes one completed ten-task development-suite run.
It works with existing replay or live bundles, without starting Docker or the model:

```sh
uv run --locked agentguard eval-analyze artifacts/suites/<run-id> \
  --output artifacts/analyses/<run-id>
```

The output directory must be new and outside the input evidence directory. The
command exports `analysis.md`, `analysis.json`, `explorer.html`, the exact analyzer
and viewer source, and checksums. Input checksums and experiment provenance accompany the analysis.
The original evidence is never rewritten. Default bootstrap settings are 5,000
resamples with seed 42; `--resamples` and `--seed` record explicit alternatives.

Open `explorer.html` in a browser for a standalone comparison of any task's clean
or attacked episodes under two profiles. It shows original task text, tool
proposals, decisions, simulated reviews, final model claims, and independent
state grades. All assets are embedded; the viewer makes no network requests.
Untrusted text is assigned through DOM `textContent`; embedded JSON escapes HTML
delimiters. A content security policy permits only the exact bundled script and
style. This static artifact has no execution or approval controls and does not
replace the planned authenticated application UI.

## Evidence contract

The analyzer checks every file listed in the input checksum manifest, rejects
paths escaping the evidence directory, and requires checksummed reports, manifests,
incremental episode records, source snapshots, and model-call records. Report
and manifest/episode snapshots must agree; fixture and source hashes must match
the manifest. These checks detect accidental alteration and inconsistent bundles.
They do not authenticate an operator who can replace files and their hashes.

Each scheduled episode must have exactly one result with the same episode ID,
task, profile, and input type. The current schema requires one clean and one
attacked episode per task and profile. Missing results, duplicates, altered
identities, invalid grades, or success attributed to an unfinished episode make
the analysis unusable. The CLI exits nonzero and writes no analysis. A killed
benchmark still needs recovery/report reconstruction; this command does not
invent missing grades or resume inference. Multi-payload/repetition suites will
need a new observation schema before they can use this analyzer.

All counts are recalculated from episode observations, independently of the
report's summary counts. Failed, cancelled, budget-exhausted, and approval-waiting
episodes remain in the denominator. An observed attacker win remains a win even
if the episode later fails. Each unfinished attacked episode without an observed
win also counts toward the conservative worst-case bound, exactly once.

## Comparisons

Every pair of profiles receives:

- Clean utility, attacked utility, and observed attack-success differences,
  expressed as treatment minus reference.
- Conditional observed attack success on the common set of tasks that both
  profiles solved cleanly. Included and excluded task IDs are exported. With no
  common clean successes, the rate is undefined (`null`), never zero.
- Descriptive 95% paired percentile bootstrap intervals for fresh inference.
  Each draw resamples task IDs with replacement, keeping clean/attacked results
  and every profile together. Shared draws preserve pairing across treatments.

Absolute rates include raw numerators and denominators. Reports also retain
status counts, unresolved attacks, simulated review counts, generated tokens,
model calls, observed episode timing, and per-episode failure labels. Labels such
as missing required ticket content, unauthorized effects, and task failure with a
denial can overlap. They describe observations and do not establish causes or
automatically classify a final response as a false completion claim.

## Interpretation limits

Ten self-authored development tasks, one payload and one trial each, are too
limited for a release-security claim. Task bootstrap intervals describe variation
in these fixtures. They do not estimate uncertainty over new attack families or
repeat sampling from the model. A degenerate interval, including `[0, 0]` for no
observed attack wins, does not establish zero population risk. Exact canary
matching still misses encoded or paraphrased disclosures.

Replay receives counts and paired differences for checking contracts, but no
bootstrap intervals or model-behavior claims. Runtime observations include host
load and container overhead; the analyzer does not isolate policy latency,
inference latency, human review time, or whole-machine memory. No release gate is
implemented by this command. Its successful exit means the analysis is usable,
not that the model meets the architecture's utility or security objectives.
