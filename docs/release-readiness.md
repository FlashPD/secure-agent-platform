# Remaining work for a portfolio release

Updated September 28, 2026. **The first 400-trial evaluation is complete. Its
behavioral gate is FAIL.** No episodes remain in that session. The current
priority is improving utility before release.

## Completed platform and evaluation work

The six tools, deterministic authorization, scoped approvals, transactional
effects, durable worker, authenticated API, and React console are implemented.
The twenty-task development corpus, forty decision-template holdouts, four attacks
per holdout, frozen protocol, and resumable 400-trial execution are complete.
All outcomes, paired analysis, exposure accounting, and
[failure analysis](evidence/release-v1-2026-09-27/README.md) are retained.

The subsequent [32-trial checklist study](evidence/utility-checklist-2026-09-27/README.md)
is also complete. Its treatment improved formatting but failed its selection
rule and was not promoted. Earlier estimates that still counted corpus authoring
and the first full evaluation as future work are superseded.

## Current path to a useful release

| Step | Done when |
|---|---|
| Stronger model / utility pilot | The eight-trial guard study is complete but rejected (0/4 to 1/4 exact success, one guarded timeout); finish PC setup and validate a useful configuration |
| Broader development | A selected configuration succeeds across the wider known workflows, including exact outputs, committed effects, and denial recovery; retain regressions and failures |
| New release study | Declare and freeze the selected configuration and evaluation scope before inference; use independently authored tasks for an untouched holdout claim |
| Release gate | Account for every scheduled trial; meet the frozen utility, attack, completion, and invariant requirements without changing denominators or graders |
| Portfolio package | Update the case study/system card, verify clean-checkout reproduction, record the five-minute walkthrough, and publish the actual gate result |

Both [model screens](model-utility-pilot.md) stopped without selecting a candidate.
The [completion-guard pilot](completion-guard.md) recovered omitted actions but
failed selection; incorrect decisions and a final-response timeout remain.
[Windows/RTX 5080 setup](pc-inference.md) is prepared for the next session.
The small pilot is a selection step, not a replacement for the release evaluation.
The forty evaluated templates are now exposed and cannot become untouched again.

## Why the first gate failed

Defended clean task success was **5/40**, below the frozen **32/40** requirement.
There were two noncompleted defended trials versus one baseline trial, and two
unresolved attacked trials versus zero. Observed attacker wins were 0/160 versus
104/160; the unresolved attacks remain in worst-case bounds. Security counts do
not compensate for failed utility. The failure review identifies incorrect
choices, exact-format mismatches, omitted effects, and repeated denied proposals.

The checklist achieved only 4/8 clean and 3/8 attacked successes against
requirements of 7/8 and 6/8, with one unresolved timeout. Another full evaluation
should wait for measured improvement on development inputs.

## Remaining acceptance limits

These remain open even after utility improves:

- A release-scale prompt-only ablation to separate prompt and gateway contributions.
- A host-wide public-network audit after setup; container network denial alone
  does not establish this.
- Bounded artifact storage, additional live mid-episode recovery/cancellation and
  orphan-container cleanup measurements, and broader telemetry/step timing.
- Stronger operator/worker OS process separation; HTTP credential separation
  exists but is not equivalent.
- Structured-generation coverage for the search nonblank regex; host validation
  enforces it, but the pinned runtime grammar does not.
- An independent clean-checkout reproduction and final recording. The Git evidence
  extract omits the full SQLite state required for independent state regrading.

The [system card](system-card.md) and
[frozen limitations](../evaluations/release-limitations-v1.json) define the scope.
A failed behavioral gate can support an explicitly experimental portfolio case
study, but the current user-selected priority is improved utility before release.
Optional RTX 5080 support, multi-seed repeats, external AgentDojo integration,
hosted deployment, and dashboards are outside the shortest release path.

Docker is unnecessary for reading results, offline regrading, or fixture demos.
Start Docker Desktop for isolated tools; fresh inference additionally needs the
pinned native model server. Preserve the original release freeze and all failures.
