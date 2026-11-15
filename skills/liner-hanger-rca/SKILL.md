---
name: liner-hanger-rca
description: Evidence-led, retrospective investigation of liner hanger running, setting, release, cementing and packer anomalies using job programmes, rig time-series logs, equipment records and drilling-fluids information. Use when asked to reconstruct a liner-hanger event, distinguish symptoms from initiating causes, develop and test failure hypotheses, or draft an auditable root-cause investigation report.
---

# Liner Hanger Root-Cause Investigation (RCA) Skill — v1.5

## Current engineering verification checkpoint (2026-11-15)

**Latest verified full-skill software result:** [GitHub Actions run 43753403289](https://github.com/smbabalola/liner-hanger-project/actions/runs/43753403289), code commit `55f78b7`: Python **3.11: 766 passed** (23.76s); Python **3.12: 766 passed** (26.34s), no failures/skips. This covers the restricted LH-CALC-03 rheology/pressure-loss and CLI tests. Previous 605-case [run 43718419410](https://github.com/smbabalola/liner-hanger-project/actions/runs/43718419410) is retained as historical software evidence only. Both logs were inspected, and the browser tests ran after Playwright/Chromium installation. Historical statements below that the MC 3D engine, browser tests, or 567/568/605 expected tests were *not full-suite verified* are superseded **only as to software regression**. They remain historical development notes, not evidence of field validation. **LH-CALC-02 stays OPEN at 6/7 (~86%); accepted programme 2/9 (~22%).** A genuinely comparable independent nonzero-weight 3D force/torque benchmark, contact-state/stiffness applicability assessment and qualified engineering sign-off remain absent. No source-authenticated Baker Hughes operating limit or OEM endorsement follows from this software pass. Read `references/LH_CALC02_EXTERNAL_BENCHMARK_REGISTER.md` and `references/LH_CALC02_ENGINEERING_REVIEW.md` before external comparison or any operational interpretation.

## Mission
Act as an **investigation assistant** supporting a qualified liner-hanger/well-engineering team. Recreate the investigation's evidence-based method, **not any proprietary Baker Hughes internal procedure**. Establish what was planned, what happened, when the first verified departure occurred, what evidence supports or contradicts each candidate mechanism, and what would be required to close the investigation.

This is **retrospective decision support**, not a live-control, barrier-verification, emergency-response or equipment-operation system. Never recommend specific real-time manipulation, pressure, force, rotation, release, well-control or remedial actions. Escalate active hazards to the designated operator's procedures and competent on-site authority. Never certify the system safe or claim a root cause is proved without the required testing and sign-off.

## How to run this skill
1. If the user supplies an incident, capture the incident scope, equipment family (hydraulic-set, mechanical-set, expandable, other/unknown), stage, observed failure, jurisdiction/operator constraints and whether the well is currently secure. If an active integrity/well-control issue is alleged, prioritize formal escalation; do not conduct real-time troubleshooting.
2. Ask for the **minimum viable investigation pack** only when absent: (a) job programme and relevant OEM procedures/revisions, (b) operations log with time base, (c) pressure/flow/hookload/torque/depth time-series when available, (d) BHA/string/equipment configuration and component identifiers, (e) fluid and wellbore conditions, and (f) incident narrative. If only partial records exist, perform an explicitly *provisional* investigation.
3. Preserve originals; assign evidence IDs and record author/source, capture time, data time base, units, calibration status, integrity/hash (if supplied), and gaps. Keep a distinction between **observed**, **reported**, **calculated**, **inferred** and **unknown**. Never invent values or OEM criteria.
4. Read `references/KNOWLEDGE_BASE.md` and `references/SOURCE_REGISTER.md` first, distinguishing public generalizations from job-specific OEM requirements. Then read `references/INVESTIGATION_METHOD.md`. Use its staged workflow in order. Refer to `references/DATA_INTAKE.md` for evidence fields and `references/HYPOTHESIS_LIBRARY.md` for non-exhaustive hypothesis families.
5. If machine-readable CSV logs are available, optionally use `scripts/build_timeline.py` to combine event annotations and samples. This script provides **timestamp alignment only**, not failure detection or root-cause diagnosis. Time-zone offsets must be explicit. Inspect its output and quality warnings.
6. Build a **planned vs observed operational timeline** with the setting method and procedure revision driving the expected sequence. Extract the earliest **supported** anomalous signature; do not confuse the time of detected failure with initiating cause.
7. Maintain a hypothesis/evidence matrix including two or more credible alternatives. For each: predicted observable signatures, supporting evidence IDs, contradictory evidence IDs, unknowns, potential tests, and status. Ask what evidence would **falsify** the favored explanation.
8. Separate the **physical failure mode**, **initiating mechanism**, **contributing conditions** (wellbore, hydraulic, fluids, operational, configuration, manufacturing/assembly etc.), and **systemic causes** (procedure, training, design, management of change, interfaces). A missing signal is not proof of the component state.
9. Output an investigation in `references/REPORT_TEMPLATE.md` structure. State whether the cause is **confirmed**, **probable**, **possible**, or **undetermined** and explain *why*. 'Confirmed' needs independently verified physical evidence or appropriately validated reconstruction plus expert review; not merely AI confidence.
10. End with an evidence gap list, prioritized follow-up tests/questions, reversible preventive controls, and the names/roles needed for independent technical review. Report data limitations and sources alongside findings. For well integrity/barrier implications, explicitly flag operator review.

## Guardrails (mandatory)
- **Do not substitute generic pressure, torque or force thresholds for OEM instructions.** Required sequence and setpoints are product-, job- and revision-specific.
- Do not confuse surface signals with downhole tool conditions. Explain friction, depth, hydrostatic/temperature influences and sensor location; correlate surface/downhole data only where available and aligned.
- WITS/WITSML, EDR and rig data can be noisy, derived, time-shifted or mislabeled. Check time synchronization, sample rate, gaps, filtering, sensor units and calibration before interpreting.
- Distinguish rig **operations logs / time-series** from **petrophysical wireline logs**. For this skill, wireline and formation-evaluation logs are **outside the default input scope**. The investigation relies on surface operational logs and job documents; any petrophysical data requires a specific justification and approval.
- Hanger setting confirmation, running-tool release and packer setting are separate evidentiary questions; they can exhibit distinct signatures and need procedure-specific proof.
- State uncertainty instead of filling gaps. Use alternative hypotheses and negative evidence (what should have appeared if the hypothesis were true?).
- Protect confidential operator/OEM records, personal data, serial numbers and proprietary drawings; invite anonymisation, confirm authorization to use records, do not publish them, and do not imply rights to Baker Hughes proprietary processes.
- No autonomous operational advice, no 'safe to resume' recommendation, no assignment of personal blame, no automatic incident closure. Stop at investigative findings for expert sign-off.

## Final output contract
Return, in order:
1. **Scope and known limitations** (incident, equipment family, data sufficiency, hazards)
2. **Evidence register** (IDs, provenance, units, time zone, quality issues)
3. **Plan vs actual timeline** (timestamps, action, expected, observed, data links)
4. **First verified deviation**, distinguished from failure recognition
5. **Signal and system analysis** (pressure, flow, depth, axial load, torque, fluids, downhole where available)
6. **Hypothesis/evidence matrix** with support, contradictions and falsification tests
7. **Causal chain** including failure mode, trigger, contributing factors and organizational safeguards
8. **Conclusion with justification and explicit uncertainty**
9. **Missing evidence and next investigative tests**
10. **Prevention/learning recommendations**, action owners to be assigned by operator, and **independent sign-off required**

## Referenced background
This general workflow is inspired by public descriptions of liner hanger data interpretation and incident investigation principles; see `references/SOURCES.md`. API Spec 19LH concerns equipment specification and **does not cover installation/field maintenance**; it is not a field-operation procedure. For operations, use authorized job-specific procedures and OEM instructions.


## Core competence and continual learning, v1.2
- Read `references/KNOWLEDGE_BASE.md` for OEM-neutral engineering concepts and observed signatures. This is a **knowledge reference**, not a running procedure.
- Read `references/SOURCE_REGISTER.md` for public evidence provenance and manufacturer-specific distinctions. The source register must be refreshed and reviewed before production use.
- Read `references/INGESTION_AND_RULES.md` before extracting job requirements or training PDFs. Apply the source precedence: approved job procedure -> applicable OEM manual/specification for the exact tool and revision -> verified case findings -> public background. Do not merge conflicting criteria silently.
- When the user supplies their training PDFs, extract candidate concepts with page-level citations and review status; preserve copyright and confidentiality permissions; never silently upgrade them to validated operational rules.
- Treat repeated job replays as **examples for retrieval and review**, not automatic proof of a mechanical root cause or permission to alter thresholds. Engineer-confirmed outcomes can enter the case library; unverified anomalies remain unconfirmed.
- Use `schemas/job_knowledge_template.json` and `schemas/case_record_template.json` for structured records. Do not invent approval, observed telemetry or measurements.
- A user's request for visual playback is satisfied by a separately generated dashboard artifact; this skill specifies what the playback must show but does not itself claim to be a GUI or rig monitoring service.

## V1.3 — Investigation-first replay + approved procedure checker

The skill must now support two distinct, auditable outputs:

1. **Operational replay:** measured rig time-series, annotated reported events, and a full surface-to-downhole drill pipe/running tool/liner schematic. The entire schematic must respond to the **same playback cursor**. A report-guided illustration MUST be labelled as such and must never be presented as measured string depth or exact event alignment.
2. **Procedure compliance register:** read `references/PROCEDURE_COMPLIANCE.md`; create an engineer-reviewed `schemas/procedure_rulebook_template.json` from the actual applicable OEM/job programme, then use `scripts/check_procedure.py` to compare the verified requirements to rig data. List every contiguous screened deviation with start/end, signal, observed extrema, rule reference, sample count, source data quality and unresolved evidence gaps. Keep `unverifiable` distinct from `met` and `deviation`.

Use `scripts/extract_procedure_candidates.py` only to collect PDF lines for human review. Never approve a new numerical threshold from an AI extraction or a training PDF. The initial Utah FORGE example in `examples/utah_forge_16A_78_32` has actual measurement charts and a **report-guided, not time-calibrated** animation; it has no OEM job procedure and therefore does not claim any procedural breach. Open its `replay.html` to demonstrate play/pause, one-cursor schematic movement, the investigation observations, import of approved rulebooks, and export of a structured investigation JSON.

V1.3 still provides **retrospective decision support**, not automated failure attribution, live operational recommendations or root-cause certification. Retain all earlier safeguards and test cases. This is ONE skill package with an offline visual output, not a separate app.

## V1.3.1 — Sensor-driven casing-run validation example
The existing skill also includes a second benchmark at `examples/utah_forge_16B_78_32/`. This is **not** a liner hanger installation: it is 7-inch full-length production casing, included to validate synchronized Pason 10-second telemetry, tripping KPI connection logs, and physical depiction of an assembly from surface. Distinguish a depth channel *used as a proxy* from independently verified string shoe depth. Do not treat tripping slip-to-slip time as casing-tong makeup torque. Rig standpipe pressure does not measure independent cementing unit pressure. Without an approved job procedure there are no confirmed breaches.


## V1.4 — Engineer-controlled annotations and investigation documentation

Read `references/ENGINEER_ANNOTATIONS.md`. Preserve the existing synchronized replay and approved-procedure check. In the 16B example the engineer can select an interval across any plotted channel; the corresponding time window is highlighted on every plot. The engineer can zoom into the selected measurements, annotate a narrower interval, save an identified/reviewable observation, attach supporting files, link source/procedure references, export/import JSON evidence bundles, and produce a printable report. Notes and attachments must be exportable without a service or proprietary application. Original recorded measurements remain unchanged.

The optional review-candidate scanner is heuristic, only based on aggregate telemetry, and never auto-approves findings, causal conclusions or procedural violations. Distinguish measured vs interpreted, and approved procedure noncompliance vs an unanswered procedure question. The `16B` casing example is NOT a liner-hanger job. This standalone offline investigation example is an output of **this skill**, not a second application.

Reusable implementation is `assets/annotation_workspace.{js,css}` with `scripts/add_annotation_workspace.py` for 16B-style replay files. The earlier 16A HTML does not yet use this adapter. Keep the QA/browser-tested single-cursor playback intact. Browser note storage is best-effort and never retains attachment bytes; instruct engineers to export the complete evidence JSON. Protect operator documents as confidential case material.


## V1.5 — Contextual, in-chart engineering annotations

Continue to use the v1.4 evidence schema and original timestamp/sensor caution, but present its editor **next to the selected chart window in a modal dialog**, not in a notebook below the chart. Point or range marks are shown on every telemetry track. Paused playback: hovering a saved highlight gives a concise evidence preview and clicking opens the exact saved annotation for editing. During playback: do **not** open modal dialogs automatically; optionally show nonblocking information cards with explicit user control to pause and inspect, and allow suppression of all playback notifications. The notebook register lives in a collapsible right-side panel with access to filters, linked evidence, exports and review candidates.

The scene's running-string position must remain source-qualified and synchronized with the telemetry playback cursor, and all existing evidence and procedure-verification safeguards must survive UI updates. For offline examples, preserve the complete evidence bundle by explicit export; do not imply cloud backup or automatic file persistence. The implementation is `assets/annotation_workspace.{js,css}` embedded by `scripts/add_annotation_workspace.py`, which can upgrade v1.4 16B-style HTML to v1.5 without creating a second application or developer folder. See `references/ENGINEER_ANNOTATIONS.md`.

## LH-CALC-02 — Versioned minimum-curvature-consistent 3D research engine

**New, software-regression-pending experimental alternative**, not a change to the original linear-angle solver: `scripts/torque_drag_3d_minimum_curvature.py` exposes `predict_minimum_curvature_curve(SpatialCurveInputs)`; `scripts/torque_drag_spatial_profile.py` exposes `predict_minimum_curvature_profile(SpatialProfile)`. Both propagate explicitly sourced pure pickup, slackoff and rotation loads using the **same minimum-curvature great-circle tangent convention** as the survey TVD integration. The profile retains MD/TVD/inclination/azimuth/provenance continuity rejection and distinct mode-specific tension boundaries.

Offline JSON:
`python scripts/run_torque_drag_3d_minimum_curvature.py examples/synthetic_torque_drag_3d.json`
and `python scripts/run_torque_drag_spatial_profile_minimum_curvature.py examples/synthetic_torque_drag_spatial_profile.json`. Input JSON schemas remain those of the existing 3D section/profile runners. The source input example is **fictional**, not an approved well. A combined build-and-turn split test constructs the exact great-circle midpoint rather than averaging angles.

**MANDATORY:** Read `references/LH_CALC02_MINIMUM_CURVATURE_3D_MODEL.md` and `references/LH_CALC02_3D_TRAJECTORY_RECONCILIATION.md` before using these APIs. Independently check the great-circle capstan and zero-friction TVD limiting cases. These are **research values only, not rig hookload or liner-hanger operating limits**. The 37 new MC solver/profile/CLI tests **have not passed a full regression**; with the prior 25 diagnostic tests, the expected new collection is **567** versus last user-verified **505**. The physical-engineering acceptance of `LH-CALC-02` remains blocked.

## LH-CALC-02 — Independent 3D survey interpolation mismatch audit

For **research-only** comparison of survey interpolation conventions, import `audit_two_station_trajectory` from `scripts/trajectory_interpolation_audit.py` with explicit `length_m`, `top_inclination_deg`, `bottom_inclination_deg`, `top_azimuth_deg`, `bottom_azimuth_deg` and optional `steps` (multiple of four). This standalone numerical audit returns positions in **north/east/down metres**, endpoint TVD/position differences and sampled tangent differences for linear-in-MD angle interpolation versus great-circle minimum-curvature interpolation. It uses **no OEM or well data** and never returns a load, a safe deviation threshold, or a field-validated trajectory.

A fictional 100m 30°→60° inclination, 0°→60° azimuth combined turn differs by approximately **8.15076m at the endpoint**, demonstrating that the spatial force solver's assumed interpolant is not generally equivalent to the minimum-curvature survey validator. See `references/LH_CALC02_3D_TRAJECTORY_RECONCILIATION.md`. The **25 new geometry tests passed only in an isolated local run**; the full skill suite including them is **not yet verified** (530 expected vs latest user-run 505). Do not promote 3D torque/drag results to operational use or present the two trajectories as interchangeable.

## LH-CALC-02 — Experimental 3D azimuth/inclination soft-string, bounded research

`scripts/torque_drag_3d.py` now exposes `SpatialCurveInputs` / `predict_spatial_curve` for a sourced **single 3D interval** with independently integrated pickup/slackoff/pure-rotation loads. `scripts/torque_drag_spatial_profile.py` exposes `SpatialProfile` / `SpatialProfileInterval` / `predict_spatial_profile` to carry **three separate tensile modes** across surveyed tangent-continuous intervals and total rotating contact torque. Strict offline examples:
`python scripts/run_torque_drag_3d.py examples/synthetic_torque_drag_3d.json` and
`python scripts/run_torque_drag_spatial_profile.py examples/synthetic_torque_drag_spatial_profile.json`.

**MANDATORY:** Read `references/TORQUE_DRAG_3D_VALIDATION.md` before calling these interfaces. The documented Johancsik-type scalar normal formula has exact zero-weight horizontal-azimuth capstan, planar-reduction, and section-split limiting tests. It is **not** a field-validated 3D model: two survey stations per segment with constant angular rates, no stiffness, friction calibration, joint loads, contact transfer or real-well/OEM comparison. The 3D research code has **not yet passed a user-run Windows full regression**. Do not report candidate tension as rig hookload or hanger-setting force.

## LH-CALC-02 — Contiguous weighted planar profile (research, not a 3D well model)

`scripts/torque_drag_weighted_profile.py` provides `WeightedPlanarProfile`, `WeightedProfileInterval` and `predict_weighted_planar_profile`. Its portable offline entry point is `python scripts/run_torque_drag_weighted_profile.py examples/synthetic_torque_drag_weighted_profile.json`. It connects **source-qualified continuous planar arcs**, propagating pickup, slackoff and rotation tensile boundaries **separately**, and totals pure-rotation frictional contact torque. It strictly checks MD, TVD, inclination, azimuth, datum and survey revision continuity. **Any 3D turn, discrete tangent kink, contact-side transition, unsupported compression or missing source fails closed**. See `references/TORQUE_DRAG_WEIGHTED_PROFILE_VALIDATION.md` for the split-invariance analytical benchmark and source contract. This does not model a 3D tortuous well, rig hookload, or OEM hanger loads. The new profile code/tests have **not yet passed the user-run full Windows regression**.

## LH-CALC-02 — Planar weighted-curvature verification bundle (research only)

Before comparing any curved output with a planned job, read `references/TORQUE_DRAG_WEIGHTED_CURVE_VALIDATION.md`: the constant-contact-side weighted build/drop solution now has an **independent closed-form analytical benchmark**, not just straight/weightless limiting checks. `scripts/weighted_curve_audit.py` exports `compare_refinement(inputs, step_counts=(64,128,256))`, reporting tensile/contact/torque **resolution differences without self-certifying a tolerance**. The weighted RK4 solver **fails closed** on sampled changes of the signed wall-contact side (not a full contact-loss/transfer model), and reports `signed_contact_side` for each movement mode. Model remains limited to **one uniform planar arc**, cannot infer rig hookload or downhole liner-hanger force, and is **not field/OEM-approved**. New regression has not yet been confirmed.

## LH-CALC-02 — Weighted planar curvature RK4 (research, NOT field validated)

The research-only `scripts/torque_drag_weighted_curve.py` models **one** source-qualified, uniform open/flooded planar interval with signed gravity-plus-curvature contact and caller-specified integration steps; `scripts/run_torque_drag_weighted_curve.py` provides the JSON CLI:
`python scripts/run_torque_drag_weighted_curve.py examples/synthetic_torque_drag_weighted_curve.json`.

**Read `references/TORQUE_DRAG_WEIGHTED_CURVE_VALIDATION.md` before using it.** It compares exact zero-curvature, weightless-capstan and zero-friction limiting cases, plus RK4 refinement. It is **not integrated into the multi-section straight-profile solver**, cannot represent 3D azimuth turns, high-angle stiffness/buckling or any OEM mechanical ratings. It reports sectional candidate forces only, **not rig hookload, liner hanger setting force or safe operating limits**. The new tests are not yet user-verified by a full Windows regression.

## LH-CALC-02 — Ideal weightless bend benchmark (NOT weighted-well model)

`scripts/torque_drag_bend.py` and `scripts/run_torque_drag_bend.py` implement the **exact weightless capstan limit** for a positive-tension bend and independently sourced friction coefficients, angle, and contact radius. Reproducible fictional case: `python scripts/run_torque_drag_bend.py examples/synthetic_torque_drag_bend.json`. See `references/TORQUE_DRAG_BEND_LIMIT_VALIDATION.md`. This is **deliberately separate** from the weighted straight string profile and **must not be added to it to claim a weighted curved-well solver**. The new analytical and negative tests await a full user-verified regression. No OEM values, rig hookload, downhole tool force or operating guidance.

## LH-CALC-02 — Contiguous co-linear string profile v0.1 (under development)

Read `references/TORQUE_DRAG_PROFILE_VALIDATION.md` for `scripts/torque_drag_profile.py` and the offline `scripts/run_torque_drag_profile.py examples/synthetic_torque_drag_profile.json` contract. It propagates **separate** tensile boundaries for pickup/slack-off/pure rotation from deepest to shallowest sections and sums pure-rotation frictional contact torque. It requires **exact MD continuity, consistent TVD and datum/survey revision, unchanged inclination and azimuth across all segments**. Segment dimensions, weight and friction may vary. It rejects non-co-linear joints instead of pretending a dogleg has no force penalty. These are modelled section tensions, **not hookload or liner-hanger actuation loads**. The new 24 test cases have **not yet been full-regression verified on Windows**; the last verified suite was 310 tests.

## LH-CALC-02 — Straight-section torque-and-drag v0.1 (under development)

Read `references/TORQUE_DRAG_STRAIGHT_VALIDATION.md` before invoking:
- `scripts/torque_drag_straight.py`: source-qualified, **single straight section only** estimates of **section-top** pickup, slackoff and pure-rotation axial tensions, sliding friction, low-side normal force and pure-rotation contact torque, with hypothetical coefficient sensitivity; reuses `PlannedSection` and the LH-CALC-01 apparent weight calculation.
- `scripts/run_torque_drag.py`: offline JSON CLI: `python scripts/run_torque_drag.py examples/synthetic_torque_drag_straight.json`.
- `tests/test_torque_drag_straight.py` and `tests/test_run_torque_drag.py`: analytically benchmarked and negative-case tests **awaiting full Windows regression**.

This deliberately rejects build/turn doglegs, floating/string compression, unsupported inclinations, absent source and friction data. **Do not** call these outputs rig hookload, true downhole tool forces, field-safe pickup/slackoff or model-specific Baker Hughes ratings. This is not a multi-section soft-string engine, stiff-string engine, buckling or combined rotation-plus-axial-movement model; no operating advice. Only progress and regression evidence recorded in `STEERING.md` and `TODO.md` can close the development stage.

## LH-CALC-01 — Elementary engineering calculations (under development)

Read `references/ENGINEERING_PRIMITIVES.md` for the **currently implemented** skill-local APIs, independent numerical reference checks, units, assumptions, review gaps and limitations. Calculation modules:
- `scripts/engineering_primitives.py`: cylindrical internal/annular capacity (m³), single-fluid hydrostatic pressure difference (Pa) from **TVD**, and apparent weight (N) for an **open, completely flooded pipe** only.
- `scripts/directional_survey.py`: source-referenced MD/inclination/azimuth stations and minimum-curvature TVD integration; initial station TVD and datum must be supplied.
- `tests/test_engineering_primitives.py` and `tests/test_directional_survey.py`: focused analytical/negative regression tests.
- `scripts/planned_job_section.py`: initial source-identified, single-section wrapper joining minimum-curvature survey endpoints with capacity, static hydrostatics and open/flooded-pipe weight. Requires actual document IDs/locations/revisions for every input; no default well or manufacturer values; `tests/test_planned_job_section.py` adds 15 new tests awaiting full Windows verification. Read `references/ENGINEERING_PRIMITIVES.md` before using it. This is not a validated multi-section well model or OEM approval.
- `scripts/run_planned_section.py`: portable CLI for one strict sourced JSON section (`python scripts/run_planned_section.py examples/synthetic_planned_section.json`), using the **fictional** fixture stored inside the skill. Ten extra tests in `tests/test_run_planned_section.py` are pending a full regression. Outputs are analytical numerical candidates only; not an OEM-engineering approval or a well-operation recommendation.

These are **low-level computational primitives**, not approved job calculations. There is no complete source-validated planned-job model, torque/drag, circulating friction, surge/swab, tool actuation/rating or KHRM validation yet. Do not infer exact equipment limits or load/pressure at the liner hanger from these outputs. The skill's planned-design/retrospective comparison rules remain mandatory.

## Active planned-engineering development entrypoint (2026-11-14)

For requests to **design or verify a planned liner-hanger job**, not a reported failure, read `references/CALCULATION_BASELINE_AUDIT.md` first and use source-gated `scripts/bha_tally.py`, `scripts/equipment_specs.py` and `scripts/engineering_baseline.py` only for the functions they currently implement. These modules do **not** yet calculate validated torque/drag, hydraulics, surge/swab, or BH tool-setting pressures. Never mislabel an input/output comparison as an independent physical prediction.

Implementation and validation must follow the canonical workstream `LH-CALC-00` through `LH-CALC-08` specified by the repository steering instructions. The skill-local audit contains a standalone capability, evidence-gap and engineering benchmark inventory for future skill-only installation. Maintain this local reference as real calculations are implemented; do not require an application/UI or repo-root documents to execute a calculation once it is accepted. Preserve the retrospective RCA path above for **genuinely historical** rig evidence.

## Product requirement — self-contained, UI-ready skill (approved 2026-11-12)

**Single source of truth:** This directory, `skills/liner-hanger-rca/`, must ultimately be an independently installable, versioned engineering skill package. A coding assistant building the future interface should need only this **installed skill package** and case-specific licensed inputs—not a separate explanation of engineering requirements or undocumented files elsewhere in the repository. This is a **future acceptance requirement**, not a claim that the current v1.5 skill already meets it.

**Package must eventually include or explicitly bundle:**
- Executable, tested engineering functions for planned well/string configuration, design verification (torque/drag, pickup/slackoff, hydraulics, surge/swab, source-supported tool forces), and retrospective planned-versus-observed fault investigation.
- Source-gated Baker Hughes equipment identity/configuration rules, safe uncertainty handling, and no invented tool specifications or universal approved limits.
- Stable, documented data schemas, callable APIs, expected inputs/outputs and example fixtures suitable for an application/UI developer.
- A complete UI implementation specification **inside the skill**, describing job setup, planned design, verification, rig CSV import, synchronized charts, anomaly review, evidence and reporting workflows. The app itself is **not** required inside the skill today.
- Portable installation/entrypoint instructions and automated smoke/integration tests that run in a **fresh environment using this skill alone**. All runtime dependencies must be declared or bundled; no hidden reliance on repo-root `docs/`, `TODO.md` or personal source folders.

**Current status (2026-11-12):** Existing retrospective investigation instructions and scripts are present in the skill. `scripts/engineering_baseline.py` and its test suite are inside the skill directory; the user confirmed **219 passing tests** across the current project suite after commit `43fe431`. However, that module currently provides a gated *comparison contract*, not validated physical calculation solvers. The planned-design architecture currently lives in repo-level `docs/planned-design-and-fault-investigation-architecture.md`; it has **not yet been fully incorporated into a self-contained skill reference and callable workflow**. The current `SKILL.md` title/description and default workflow are still retrospective-centric. Do **not** tell users the complete design-and-investigation skill or its UI-readiness has been accepted.

**Release gate:** Before building a substantial UI, perform a clean-room install of the skill alone; have a coding assistant construct a minimal interface from its bundled schemas/API/requirements without consulting external project notes; exercise a planned design scenario and a synthetic historical investigation, and document what is available versus not yet implemented. Require explicit engineering acceptance of physical models independently of the UI integration test. Existing source-rights protections still apply: never package confidential OEM/customer PDFs into a distributable skill without authorization.

## LH-CALC-03 — Offline experimental circulating hydraulics (NOT a rig SPP calculator)

### Newly implemented bounded power-law concentric annular flow and circuit workflow

Run from the installed skill directory:

```bash
python scripts/run_power_law_laminar_annulus.py examples/synthetic_power_law_laminar_annulus.json
python scripts/run_power_law_circulation_budget.py examples/synthetic_power_law_circulation_budget.json
```

The annular model is an explicitly separate `power_law_laminar_annulus_pressure_loss(PowerLawFluid, FlowSegment, ...)` with stationary concentric walls, steady fully developed **laminar** power-law material, radial shear-stress zero location found by a no-slip boundary-value integral, then separately integrated pressure gradient; **not** a pipe hydraulic-diameter approximation. The restricted annular radius ratio is 0.15–0.85 and `n` 0.3–1.5 for the current research-tested numerical scope only. These are not equipment or mud operating limits. The coupled `partial_power_law_circulation_budget` requires a separate **caller-supplied, not independently authenticated laminar regime source ID for every straight pipe and annular segment**, optionally combines one separately source-labelled nozzle differential, and returns only a **partial loss ledger**. The zero-shear radius is `null` when no distributed flow field exists. Neither module models pipe rotation, eccentricity, yield stress, solids, turbulent/transition flow, thermal behavior, tool restrictions or pressure-transducer datum. Both always return `standpipe_pressure_pa=null`, `engineering_acceptance=false` and remain research-only. Governing equations and independent Newtonian annulus limit in `references/LH_CALC03_HYDRAULICS_PLAN.md`; acceptance evidence in `references/LH_CALC03_ACCEPTANCE_EVIDENCE.md`.



**Latest LH-CALC-03 software regression:** [GitHub Actions run 43757805273](https://github.com/smbabalola/liner-hanger-project/actions/runs/43757805273) at code commit `227d241` — **815 passed on Python 3.11 and 815 passed on Python 3.12**, zero failures or skips in either job (actual logs verified). This is a software result, not rig hydraulics approval. The older 766-case count in the historical checkpoint above is superseded for new software.

**Additional restricted power-law pipe calculation:**
```bash
python scripts/run_power_law_laminar_pipe.py examples/synthetic_power_law_laminar_pipe.json
```
This source-based `power_law_laminar_pipe.py` uses `tau=K gamma_dot^n`, `K` in **Pa·s^n**, strictly a fully developed **laminar circular pipe**, with separate source-labelled but caller-asserted laminar-regime evidence. `n=1` reduces to Newtonian Hagen–Poiseuille, and `DeltaP ∝ Q^n` for fixed geometry. It **does not** support power-law annular flow, transitional/turbulent flow, mud yield stress, casing eccentricity, OEM restrictions or rig standpipe-pressure predictions. See `references/LH_CALC03_HYDRAULICS_PLAN.md` for the published BYU Eq 7–8 source and exact validation boundary. `standpipe_pressure_pa=null`, `engineering_acceptance=false` at all times.



**Current research-only software APIs and CLI usage:**

```bash
python scripts/run_circulating_hydraulics.py examples/synthetic_laminar_circuit.json
python scripts/run_bingham_laminar_pipe.py examples/synthetic_bingham_laminar_pipe.json
python scripts/run_circulation_budget.py examples/synthetic_newtonian_component_budget.json
```

All paths are relative to the **installed skill root**; executable scripts use only Python standard library. Full implementation and source/acceptance details: `references/LH_CALC03_HYDRAULICS_PLAN.md`. Read it before interpreting numerical values.

1. `circulating_hydraulics.py`: source-checked **Newtonian, laminar, fully developed** circular pipe and concentric fixed-wall annulus per-segment pressure loss; rejects Re>2000 (simple conservative screening only). The names `outer_diameter_m` and `inner_diameter_m` represent **flow boundaries**, not necessarily metal tubular OD, and pipe `outer_diameter_m` is its **flow ID**.
2. `bingham_laminar_pipe.py`: source-checked **Bingham-plastic, laminar circular PIPE ONLY** Buckingham–Reiner equation, with nonzero yield and positive plastic viscosity; requires *separately established* laminar-regime assertion and evidence ID via strict CLI. Its plastic Reynolds estimate does not validate the regime. At zero flow and positive yield stress the differential is physically indeterminate; rejected. Bingham annulus/turbulence unsupported.
3. `circulation_restrictions.py`: independently sourced *incompressible nozzle/orifice differential* with externally established flow area, discharge coefficient and explicit source identity. May not be silently repurposed as a specific OEM running-tool internal restriction.
4. `circulation_budget.py`: explicit ordered **Newtonian** pipe/annulus, optional nozzle, return leg; sums only modeled component losses, rejects ambiguous flow paths and unsupported component regimes. Does not claim complete rig hydraulic equipment or pressure datum.

**MANDATORY:** All these inputs/examples are **fictional or caller-described**; none is a substitute for actual fluid test values, checked pump rate, flow split, true pipe/tubular internal diameters, annular clearances, tool restrictions and manufacturer/job configuration. Calculated component friction is **NOT rig standpipe pressure**, a ball-seat/setting differential, ECD, surge/swab, burst/collapse rating, qualified operating envelope or confirmation of actual pressure transducer calibration. Output **always contains `standpipe_pressure_pa: null` and `engineering_acceptance: false`**. Unsupported field scenarios fail closed; no rig operator instructions or OEM pressure values may be inferred. **LH-CALC-03 stage remains IN PROGRESS, not engineering accepted.**

