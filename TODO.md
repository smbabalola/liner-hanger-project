# TODO — Master Skill Development Register

**Purpose:** The authoritative backlog for **Baker Hughes-only retrospective fault-finding skill v1**. The earlier broad engineering tasks are preserved below as a deferred record, not release blockers. Read [START_HERE.md](START_HERE.md) and [AGENTS.md](AGENTS.md) before work.

## Status and task discipline

- `[ ]` Pending / not yet accepted; `[x]` Accepted with documented evidence.
- A task may be labelled **IN PROGRESS** or **BLOCKED**, but its checkbox remains unchecked until every acceptance criterion is met.
- Do not infer completion from previous conversations, screenshots or standalone prototypes. Inspect actual files.
- Work on **one task at a time**. No UI/app implementation during the skill-release phase.
- Each task completion must include: changed file paths, tests run and outputs, engineering evidence checked, limitations, commit SHA, and reviewer/approval if applicable.
- Keep new suggestions in **Deferred / change requests** until explicitly prioritised.


## First-release decision (approved 2026-11-12)

- **Locked v1:** Baker Hughes retrospective fault finding, supported by actual BH-SYS-2016 and BH-HYD-2020 training guides. See [first-release scope](docs/first-release-scope.md).
- **Architecture:** one manufacturer-extensible backend, **Baker Hughes only activated** in v1. Halliburton and other manufacturers later, after documentation review.
- **Original sources:** 132-page Systems guide + 99-page Calculations/Hydraulics guide; third provided PDF was an identical copy. These are copyrighted; do not publish the PDFs.
- **Do not assume** all BH models are supported. A 38-entry pre-existing catalog is only an inventory/simulation reference; its placeholder pressure/load/dimension numbers are not verified OEM ratings.

## v1 development gates — CURRENT AUTHORITATIVE TASK ORDER

### Gate A — Recover, audit and baseline

- [ ] **LH-001 — Complete source and asset inventory [IN PROGRESS; initial audit 2026-11-12].** The v1.5 archive (46 files), v1.4 (45 files) and v1.2 knowledge package (14 files) were inspected; the v1.5 pytest suite passed **14/14** in a separate cloud workspace. LinerForge BH catalogue/profile source reviewed read-only; placeholder lengths/ratings identified and excluded from engineering rules. Initial deliverable **`docs/asset-audit.md`** committed. **Remaining before acceptance:** audit newer separate HTML prototypes and source rights, confirm local artifact paths and repeat tests locally. **Accept when:** versions/contents reconciled, assets and permissions registered, no heuristic presented as validated.
- [ ] **LH-001A — Review the two recovered Baker Hughes training guides [IN PROGRESS; FAMILY SHORTLIST ADDED].** Original documents recovered, duplicate identified; original source/page matrix in `docs/baker-hughes-document-inventory.md`. Added `docs/bh-v1-equipment-coverage-gate.md` (2026-11-12, commit `0272ac3`) with 16 candidate equipment groups, five evidence-led investigation tracks, required source/revision gates, and BHA length/anchor constraints. **Remaining:** confirm exact source pages and actual family/model/size/revision/part for at least one job assembly, obtain required SU/TU and approved source rights as applicable, resolve SDD SU/TU reference conflict, engineering review. **Accept when:** each chosen v1 candidate rated inventory-only / mechanism-described / model-specific-reviewed / unavailable with page-exact support and specific usable subset selected. No quantitative BH operating limits yet approved.
- [x] **LH-001B — Confirm v1 scope.** User explicitly approved Baker Hughes retrospective fault-finding as first skill release on 2026-11-12. Decision and deferrals documented in `docs/first-release-scope.md`. Acceptance: scope documented and signed off by user.
- [ ] **LH-002 — Baseline existing investigation skill [FUNCTIONALLY VERIFIED; RIGHTS REVIEW PENDING].** v1.5 skill imported, committed and pushed (`39efee0`, `36fc811`). The browser-test dependency on Utah FORGE replay was replaced by a deterministic synthetic replay generator (`6c9c6ff`, `5176581`, `06bf6f6`); on 2026-11-12, user ran `py -m pytest -rs -q tests` on Windows and confirmed **14 passed, 0 skipped, 0 failed in 8.75 s**. No historical replay is required in HEAD and original BH manuals are excluded. **Remaining for full acceptance:** source-rights/history review because the original historical replay is still recoverable from earlier Git commits; any full fresh-clone/CI checks. **Accept when:** documented permission/history decision and clean reproducibility review completed.
- [ ] **LH-003 — Baseline normal and anomalous cases [112-TEST WINDOWS REGRESSION VERIFIED; ENGINEERING REVIEW PENDING].** Added fictional normal/anomalous scenarios in `skills/liner-hanger-rca/tests/fixtures/lh003_synthetic_cases.json`, 12 end-to-end checks in `tests/test_lh003_scenarios.py` and `docs/lh003-synthetic-scenario-validation.md` (2026-11-12). Both exercise BHA tally, internal geometry, operating-limit screening, evidence timeline and competing hypotheses. User pulled through commit `b3bdc15` and confirmed local Windows `py -m pytest -rs -q tests` → **112 passed in 19.96 seconds**, 0 failures/skips reported. Cases use **fictional parameters and review flags, never actual Baker Hughes limits**; normal case does not prove tool setting; anomalous case retains a screening candidate, missing geometry, rig-vs-cement sensor gap, contradictory interpretations and no confirmed root cause. **Remaining:** independent technical review of scenario/evidence plausibility, source/rights check and authorized real-case ingestion where available. **Accept when:** software regression and engineering/source acceptance criteria are documented and passed.

### Gate B — Baker Hughes equipment and evidence model

- [ ] **LH-004A — Multi-OEM backend identity and source-gated BH knowledge packs [SCREENING REGRESSION VERIFIED; SOURCE APPROVAL PENDING].** Added `skills/liner-hanger-rca/scripts/operating_limit_screen.py`, negative/positive synthetic tests and `docs/operating-limit-screen.md`. User pulled `8e62196` and ran local Windows `py -m pytest -rs -q tests` on **2026-11-12: 63 passed in 10.37 s, 0 failed, 0 skipped**. Synthetic tests verify screening guards for manufacturer/revision/configuration, unit, stage, pressure basis, rig-vs-cement source and approval flags. These are **not actual manufacturer-certified setpoints**, and caller-supplied approval flags are not a secure verification workflow. **Remaining:** approved OEM technical documentation, rule source verification, authorization/governance, full knowledge-pack registry and engineering signoff. **Accept when:** full source traceability, cross-OEM isolation and revision mismatch checks pass with authorized records and reviewed end-to-end evidence.
- [ ] **LH-004 — Minimum retrospective case contract [BHA TALLY + EQUIPMENT SPECS TESTED; FULL CONTRACT PENDING].** Manual/.xlsx tally contract, nominal component-boundary MD engine, separate engineer-entered manufacturer/job specification records, review flags and referenced internal offset MD resolution committed in `skills/liner-hanger-rca/scripts/bha_tally.py` and `equipment_specs.py`, with tests and `docs/equipment-specifications-contract.md`. User confirmed the full local Windows regression on **2026-11-12: `py -m pytest -rs -q tests` → 39 passed in 10.09 s, 0 failed/skipped** after pulling `a88aeff`. These are synthetic software tests, **not** independent validation of actual Baker Hughes ratings or as-run geometry. **Remaining:** finish well/case/evidence model, approved review history and manufacturer-isolated applicability checks, independently verify geometry convention and exact OEM specifications. **Accept when:** complete contract and engineering acceptance tests pass.
- [ ] **LH-005 — Unit and evidence provenance.** Validated unit conversion, raw measurement preservation, sensor/channel identification and time alignment with uncertainty. **Accept when:** known-answer conversions and negative tests pass.
- [ ] **LH-006 — Historical CSV and chronological log ingestion.** Reuse previous processing scripts and preserve original sample cadence; robust matching of rig logs to reported events. **Accept when:** input/quality reports and an end-to-end time alignment fixture pass.
- [ ] **LH-007 — Investigation chronology and first supported deviation [TIMELINE REGRESSION VERIFIED; ENGINEERING REVIEW PENDING].** Added `skills/liner-hanger-rca/scripts/evidence_timeline.py`, tests and `docs/evidence-timeline-integration.md` (2026-11-12). Integrates limit screens as candidate/context/evidence-gap, links rule/telemetry sources, and orders only verified offset-aware timestamps. On **2026-11-12**, user pulled through `77ef10c` and reported **77 passed in 8.05 s** on Windows (`py -m pytest -rs -q tests`), after two harmless command-paste/path errors. **Not yet validated:** actual source clock provenance, planned-vs-observed reconciliation, confirmed first deviation, or engineering-reviewed fault hypotheses. **Accept when:** event citations resolve and independently confirmed time alignment supports a documented first deviation without invented chronology.

### Gate C — Five documentary investigation workflows

- [ ] **LH-BH-101 — Ball drop / water hammer and seating questions.** BH-HYD-2020 lesson; distinguish water hammer, seating and evidence insufficiency. **Accept when:** worked synthetic test identifies alternatives and evidence gaps without treating timing as proof.
- [ ] **LH-BH-102 — Hanger setting questions.** Compare available load/pressure/string movement evidence with documented expected event **for selected config**. **Accept when:** supported/contradicted hypotheses and configuration limits are stated.
- [ ] **LH-BH-103 — Running-tool release questions.** Work across applicable documented hydraulic or mechanical release families; distinguish tool response from surface sensor ambiguity. **Accept when:** both scenario test and unsupported-model test pass.
- [ ] **LH-BH-104 — Cementing-stage fault questions.** Compare stage logs with available rig or cement-unit data; enforce sensor/source separation, losses and float/packoff alternatives. **Accept when:** rig-only and missing-cementer cases never invent cement pressures or volume.
- [ ] **LH-BH-105 — Liner-top packer setting questions.** Compare reported set-down/transferred load, packoff position and alternative causes. **Accept when:** synthetic evidence-led findings are reviewable and fail closed on missing specs.
- [ ] **LH-BH-106 — Source-gated supporting calculations.** Implement only essential deterministic, tested checks for the five investigations (capacity, basic hydrostatics/force/weight as supported). **Accept when:** each calculation passes independent source-linked examples; universal tool ratings are forbidden.

### Gate D — Report, validation and release

- [ ] **LH-015 — Competing-hypothesis/evidence engine [SOFTWARE REGRESSION VERIFIED; ENGINEERING CASE REVIEW PENDING].** Added `skills/liner-hanger-rca/scripts/hypothesis_review.py`, `tests/test_hypothesis_review.py`, and `docs/competing-hypotheses-contract.md` (2026-11-12). Fault mode requires two hypotheses, retains supporting/contradicting evidence, unresolved gaps and discriminating questions; screening prompts alone cannot establish a mechanism. On **2026-11-12**, user pulled through `471dc13` and independently ran the full Windows suite **twice: 100 passed in 23.72 s and 100 passed in 8.06 s**, no failures/skips reported. **Still pending:** normal and anomalous full investigation fixtures, independently reviewed failure mechanism/falsification criteria, secure review/signoff and report integration. **Accept when:** test case-level evidence/hypotheses and alternatives are independently reviewed, normal operation does not force a failure and no unsupported root cause is asserted.
- [ ] **LH-016 — Retrospective fault-finding report [127/127 WINDOWS REGRESSION PASSED; REPORT INSPECTION/ENGINEERING REVIEW PENDING].** Added `skills/liner-hanger-rca/scripts/investigation_report.py`, `tests/test_investigation_report.py` and `docs/retrospective-engineering-report.md` (2026-11-12). Deterministic draft JSON/Markdown with source-linked chronology, screening, hypotheses, contradictions and gaps, never an authorised root cause. First local run: 125 passed, 1 failed (test expected timeline mismatch but received correct hypothesis mismatch); test split into two independent checks in `0ddb11f`. User pulled through `7b2aa0d` and reran `py -m pytest -rs -q tests` on Windows: **127 passed in 8.54 s; 0 failures/skips**. **Remaining:** generate and inspect actual normal/anomalous draft report outputs for readability and evidence completeness; source/rights and engineering review; controlled sign-off workflow. **Accept when:** outputs are source-traceable, all uncertainty explicit and independently reviewed.
- [ ] **LH-017 — Scenario regression and engineering review.** Source/units/timestamp tests, five fault-family scenarios, normal control, cross-OEM rejection, unsupported BH variant rejection and independent review of model-dependent interpretations. **Accept when:** all release blockers resolved.
- [ ] **LH-018 — Skill v1 release gate.** Portable skill layout, clean installation, references, permission review, scenario tests, documentation and known limitations. **Accept when:** reviewed and tagged; UI is still a separate approval.

## Current checkpoint

**Active:** `LH-001` / `LH-001A` documentary and artifact audit. First archive/code audit and 14-test regression are recorded in `docs/asset-audit.md` (2026-11-12); not yet a full acceptance. **Scope:** confirmed; **no v1 skill implementation or test completion claimed**.
**Decision complete:** `LH-001B`.
**Source files:** original BH PDFs available only as user-provided conversation sources; the GitHub source register contains metadata/notes, not the copyrighted PDFs.

## Deferred original broad-engineering backlog (preserved for later)

### Gate A — Recover and audit (P0)

- [ ] **LH-001 — Inventory previous work.** Identify all accessible skill packages (`SKILL.md`, references, schemas, scripts), HTML v1.5 annotation prototype and later extensions, case datasets and prior tests. Produce `docs/asset-audit.md` with paths, versions, source, license/provenance, feature status (**skill / code / prototype-only / missing**), and what must not be copied. **Accept when:** every located asset is classified; skill and UI version claims are reconciled; no uninspected prototype is called validated.
- [ ] **LH-002 — Baseline existing skill.** Select the newest verified usable skill package, import it into `skills/liner-hanger-engineering/`, preserving source history and original artifact checksums/links in the audit. Do not silently merge conflicting copies. **Accept when:** package is structurally valid, references resolve, original functions are present, and a documented smoke test passes.
- [ ] **LH-003 — Build evidence and acceptance fixtures.** Register at least one successful and one anomalous case (synthetic or appropriately licensed), including expected facts, ambiguity, data source/time base and prohibited conclusions. **Accept when:** fixtures are reproducible, data permissions checked, expected outcomes independently reviewed where feasible.

### Gate B — Engineering data foundation (P0)

- [ ] **LH-004 — Unified job contract.** Define versioned, typed job/well geometry, directional survey, BHA/running tool, liner hanger, float equipment, fluids, planned procedure and equipment-specification schemas. Reuse relevant WellOptix concepts without coupling repositories. **Accept when:** round-trip fixtures, absent-field tests, depth/unit validation and provenance checks pass.
- [ ] **LH-005 — Unit and source policy.** Canonical units + selectable metric/oilfield displays; explicit source units, conversions, timestamps and calibration/uncertainty. **Accept when:** conversion reference tests pass; original values and units remain retrievable; no silent units guess.
- [ ] **LH-006 — Historical rig CSV pipeline.** CSV ingestion, column mapping, timestamp normalisation, gaps/duplicates, multi-pump rig channels, high-resolution source preservation, chart/replay-friendly derived views. **Accept when:** real/synthetic fixture loads end to end, incorrect mappings are caught, and raw sample count/timing are retained.
- [ ] **LH-007 — Job logs and evidence register.** Timestamped chronological events, source IDs and time-alignment confidence; support uncertain/approximate event times. **Accept when:** planned and recorded timelines can be joined without assigning false precision.
- [ ] **LH-008 — Engineering annotations contract.** Portable, editable point/range annotations, provenance and related telemetry snapshots, with classifications observed/reported/calculated/inferred and an audit trail. **Accept when:** annotations export/restore at the correct timestamp after replay without changing original measurements.

### Gate C — Calculations, operations and cementing (P1; required for skill release if in accepted release scope)

- [ ] **LH-009 — Geometry and capacities.** Validated string/annular capacities and displacement-volume functions with direction/depth assumptions and independently checked answers. **Accept when:** numerical tolerances and edge cases are recorded in `docs/validation-register.md`.
- [ ] **LH-010 — Pump-source model.** Separate rig pump configurations (any count with aggregate flow where legitimately known) from cement-unit pumps; explicit channel provenance, missing data and pump changeovers; avoid double counting. **Accept when:** rig-only, cement-only, mixed, aggregate-only and unavailable-source fixtures pass.
- [ ] **LH-011 — Fluid and cementing stages.** Initial well fluid plus stage-based fluid identity, density, planned volumes/rates, timing, returns and float information; calculated volume budgets. **Accept when:** sequence and quantity reconciliation tests pass, unknown properties stay unknown, and equipment-specific assumptions are documented.
- [ ] **LH-012 — Cement placement estimates.** Model interfaces / top of cement only from verified geometry, flow path, stages and defensible cumulative volumes. Label planned vs recorded vs estimated placement, including possible losses. **Accept when:** independent numerical comparisons pass; insufficient inputs yield 'unavailable' rather than invented depths.
- [ ] **LH-013 — Predicted pressure screening.** Hydrostatic and hydraulic calculations with stated rheology, temperature, friction model and limits; compare only hydraulically relevant actual pressure measurements. **Accept when:** reference calculations pass; rig-only isolated-cementer test does NOT falsely compare rig SPP to cementer discharge.
- [ ] **LH-014 — Operational reconstruction.** Replay reconstruction as a **data and event product** (not an app): running, circulation, conditioning, setting, release, cementing, successful or anomalous. **Accept when:** event sequence is evidence-linked; uncertain operations are marked; chronological consistency tests pass.
- [ ] **LH-015 — Deviations and optional investigation.** Reuse the original evidence-led hypotheses/evidence matrix; alternative explanations, contradictions and insufficiency. No automatic 'failed job' classification. **Accept when:** successful case generates no manufactured fault; anomalous case generates reviewable hypotheses, not definitive OEM-specific RCA.

### Gate D — Reports and release (P0 acceptance before UI)

- [ ] **LH-016 — Dual reports.** Generate draft field-service operations report and detailed engineering analysis report from the same job/evidence record; support both successful and anomalous operations. **Accept when:** sample reports cite source/measurement IDs, assumptions and missing inputs; review/sign-off status is explicit.
- [ ] **LH-017 — Regression and engineering validation.** Automated tests for all critical parsers/contracts/calculations, historical job replay cases and insufficient-data safeguards. Populate a validation register with unvalidated items. **Accept when:** clean environment reproduces tests and all release-blocking failures are resolved.
- [ ] **LH-018 — Skill quality/release gate.** Check portability (`SKILL.md`, reference links, script invocations), run full skill scenario evaluations, documentation, sourcing/licensing, and independent engineering review on model-dependent conclusions. Tag a first skill release only after sign-off. **Accept when:** release checklist is complete and remaining caveats are documented.

## Historical checkpoint (superseded by v1 checkpoint above)

**Active task:** `LH-001` (pending).  
**Confirmed in this repository:** Initial README and project governance files only.  
**Not yet performed:** formal asset inventory, baseline import, skill regression testing, reference calculation validation.  
**Do not mark LH-001 complete merely because older prototypes exist.**

## Development loop record (copy once per task)

```text
Task ID:
Starting branch and commit:
Existing implementation found:
Gap / minimal change:
Files changed:
Tests and commands:
Observed results and engineering verification:
Known limits / missing evidence:
Reviewer / decision:
Ending commit SHA:
Next task:
```

## Additional future change requests (outside current skill gate)

- Full app/UI development using the completed skill APIs, guided by established UI/UX skill.
- Real-time WITSML/ETP integration and live shadow mode; no live field guidance without separate safety case.
- Engineer–virtual-driller voice communication and training simulation.
- Manufacturer-specific automated fault attribution requiring licensed OEM tool designs and review.
- Cloud hosting, multi-tenant accounts and field deployment.

**Scope changes:** Record proposed additions here with rationale and acceptance impact. Do not begin them during an active task without explicit reprioritisation.
