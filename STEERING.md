# STEERING — Liner Hanger Engineering Skill

**Decision date:** 2026-11-14  
**Status:** Approved development objective and task order; engineering models **not yet complete or validated**.  
**Primary execution environment:** Codex operating in existing checkout `C:\dev\liner-hanger-project`, repository `smbabalola/liner-hanger-project`.  
**Implementation target:** `skills/liner-hanger-rca/` — **the skill itself**, not a parallel application or isolated repository demo.

## One objective

**Build a portable, self-contained Liner Hanger Skill that can independently calculate and verify a planned Baker Hughes liner-hanger job, and later compare actual rig surface records against that validated plan to investigate possible failure mechanisms.**

A future coding assistant must be able to install **only this skill package** and generate a UI using its documented callable interfaces, schemas, examples, workflow specification and tests. UI implementation is deferred until the engineering modules and portable skill integration are ready.

**Success means working, benchmarked physics modules and repeatable skill-only workflows, not simply a TODO, a diagram, a plausible report, or 219 passing pre-existing tests.**

## Current execution checkpoint — 2026-11-14

**Development stage tracker:** `LH-CALC-00` baseline audit **accepted**; `LH-CALC-01` **accepted at limited software/analytical scope** after user independently ran the full Windows regression at commit `15c9dec`: **273 passed in 10.67 s**. **2 of 9 milestones accepted (~22%)**. This percentage describes accepted development gates, **not** finished physics, well-specific accuracy, operational approval, or engineer certification.

**Active stage:** `LH-CALC-02` torque-and-drag — **IN PROGRESS, initial straight-section solver committed (4/7 development checkpoints = 57%)**. `scripts/torque_drag_straight.py`, `scripts/run_torque_drag.py`, synthetic example, tests and skill-local validation notes now exist. A fixed, independently hand-derivable 60° straight-section force/torque benchmark and sensitivity/negative tests are encoded; **their complete Python regression is not yet confirmed**, and neither full multi-section/dogleg physics nor professional engineering review has passed. **Overall accepted-stage progress stays 2/9 (~22%)**. A user-run Windows regression gave **308 passed, 1 failed** (15.50 s): invalid inclination −1 was correctly rejected by the upstream planned-section intake but a torque-and-drag test expected a torque-and-drag exception. The **test boundary only** was corrected in commit `e601a1b`, and an extra negative test was added. No physical calculation or survey safety gate was weakened. **The correction has not yet been regressed**; next expected total **310 tests**, and stage completion remains blocked until actual passing output. Afterward pursue sourced multi-section/depth propagation and benchmarked curvature treatment. No UI implementation, false OEM ratings or field-operating recommendations.

**Evidence blockers:** No readable authorized KHRM-299510 original calculation inputs and outputs were verified in the initial source audit; do not invent field data. Professional/OEM validation of stage-1 primitives remains outstanding. Automated GitHub Actions was committed but **a successful run has not yet been confirmed**; user-run Windows test evidence is confirmed.

### Mandatory maintenance of steering and TODO

- **`STEERING.md`** records stable objectives, technical architecture, stage priority and **current accepted-stage checkpoint**. Update this checkpoint whenever a stage is accepted or the approved technical direction changes, without turning this file into a verbose per-commit diary.
- **`TODO.md`** records each active task, implementation and validation evidence, blockers, changed paths, commit IDs, **stage-level percent and programme-level percent** after substantive progress.
- Progress counts **accepted gates / 9**, reported separately from partially completed checkpoints. A passing test verifies software, not independently approved field-engineering output. No advancing a task checkbox on predicted results or unauthenticated equipment ratings.
- Before reporting completion, keep `STEERING.md`, `TODO.md` and the skill-local technical references consistent; supersede outdated status prose instead of allowing multiple contradictory 'latest' snapshots.

## Execution order — one task at a time, bounded repeat loop

**P0 — Baseline and source audit.** Confirm checkout HEAD and clean working tree; run the pre-change full test suite, record counts, audit existing BHA, equipment-spec, planned/observed comparison, CSV and evidence modules. Review permitted actual job-programme source data and locate the KHRM-299510 *planned* design package if available. Record missing inputs and reference calculations. KHRM is **not a reported failure or verified as-run record**.

**P1 — Well, survey, fluid, string and source-grounded computational primitives.** Define typed/versioned plans: directional survey (MD, inclination, azimuth, TVD), casing and hole profile, component dimensions/weights, depth anchors, fluid density and rheology, planned stages and operating constraints. Preserve source location/revision and explicit units; no silent interpolation or default OEM data. Implement independently tested volume, buoyancy, hydrostatics and basic force/geometry functions as appropriate.

**P2 — Torque-and-drag engineering engine.** Provide pickup/slack-off/rotating string-weight and torque predictions versus measured depth, with documented soft-string/stiff-string model choice and limitations, friction, inclination, contact, buoyancy and optional sensitivity ranges. Distinguish hookload at surface from loads delivered to a downhole component. Do **not** claim high-angle/stiff-string/buckling capability unless implemented and benchmarked.

**P3 — Circulating hydraulics engine.** Model sourced flow paths and pressure-loss contributions across running string, tools, liner and annulus with explicitly chosen fluid rheology and units. Show losses by section, total modeled rig standpipe pressure only when source configuration supports it, and sensitivity. **Rig SPP is not automatically seat differential or cement-unit discharge pressure.**

**P4 — Surge/swab and tripping envelope.** Predict pressure changes against depth, tripping speed and well/fluid conditions, including model limitations and pressure boundaries only where supplied. Do not infer safe tripping speed or hanger preset from speed alone; equipment-dependent limits require authorized source.

**P5 — Source-gated hanger, ball-seat, running-tool and liner-top packer mechanics.** Calculate pressure-force and effective-area effects where geometry is documented; compare applicable differential pressures, loads, seat shear/release and tool-setting conditions **only with exact model/size/revision/configuration source criteria**. Distinguish physics prediction, original engineer's design value, and authorized OEM limit. Never invent Baker Hughes ratings or substitute training-example numbers.

**P6 — Planned design benchmark and integration into skill.** Reproduce available original design outputs **independently**, compare on equal measurement/domain/MD/unit basis, record differences and sensitivity; flag uncomparable or missing reference cases. Integrate every accepted module into `skills/liner-hanger-rca/scripts/`, document entrypoints and schemas inside `skills/liner-hanger-rca/`, and ensure the `SKILL.md` workflow actually invokes them.

**P7 — Historical evidence comparison and investigation.** Only when genuine recorded rig data and job logs are provided: preserve raw time-series, align verified clocks, identify rig-vs-cement signals, calculate observed depth/rate/load/pressure relationships, compare with planned stage/depth-dependent envelopes, distinguish model differences from approved-limit deviations, assess alternative failure mechanisms and produce a reviewable report. If no records, return **not available** rather than fabricate a fault.

**P8 — Skill-only release gate.** Fresh-environment test by installing `skills/liner-hanger-rca/` without repository-root docs or private machine paths; execute a synthetic planned-design workflow and a synthetic retrospective investigation via documented APIs. Verify requirements, dependencies, schemas, examples and UI-build handoff are all contained within skill. This **does not** replace independent professional engineering sign-off for operational use.

## Repeat cycle for Codex

1. Read `STEERING.md`, `AGENTS.md`, `TODO.md`, `skills/liner-hanger-rca/SKILL.md` and the relevant implementation and tests.
2. Select the **first eligible** task in the active `LH-CALC` sequence, obey dependencies. Do not skip a blocked gate to label a later one accepted.
3. Audit existing code before writing new code. Implement the smallest useful vertical slice **inside the skill**; keep backward compatibility.
4. Run focused tests and the **full** test suite; include negative, missing-input, unit/domain, conservation, boundary and sensitivity cases.
5. Compare physical model outputs against an **independently checked** analytical/published/authorized benchmark, not only self-generated expected results. Document exact source, model assumptions, tolerances and discrepancies.
6. Review failure states and uncertainty. Record tested result, files, known gaps, approvals required and commit SHA in `TODO.md` and skill-local validation documentation.
7. Commit/push **only permitted, verified code and metadata**, then advance to next task **if and only if** completion criteria are met and the execution session remains active.

**Autonomy boundary:** This is a repeatable instruction for Codex when it is running, **not an active schedule, background worker, or promise of unattended execution from ChatGPT**. Codex must stop and report when required proprietary sources/benchmark data are unavailable, independent validation cannot be established, tests fail repeatedly without safe resolution, safety assumptions are unverified, or a real-operation sign-off is required. No infinite retries, fabricated passes or self-certified physical validation.

## Engineering validation and sign-off

- **Software verification:** test execution, regression, units, dimensions, code review and reproducible numbers.
- **Model validation:** independent known-answer problems, proper model applicability, sensitivity and uncertainty; record **verified**, **provisionally benchmarked**, **unvalidated**, **unsupported** separately.
- **Job-specific comparison:** original engineer's result is a comparison target; matching it is not independent proof of correctness.
- **Operational approval:** reserved for suitably qualified human engineers and approved manufacturer/operator documentation; neither Codex nor ChatGPT may certify a model, approve limits or release operating instructions unilaterally.

**Confidentiality:** Never commit private Baker Hughes manuals, drawings, customer well data, full job packages or other restricted content to public Git. Preserve references and appropriately licensed/synthetic fixture data only. Existing synthetic RCA evidence and 219-test baseline remain intact.

## What counts as complete?

All P1–P6 model families are implemented with explicit scope, tests, independent reference checks and skill-local API documentation; missing exact tool-specific data remains fail-closed. The P7 workflow works on synthetic recorded rig data and authentic records only if available. P8 fresh-install skill-only integration passes. Each unmet physical/OEM/human sign-off gate remains open and visibly labelled. **Do not mark the overall engineering calculations 'complete' merely because the code runs.**
