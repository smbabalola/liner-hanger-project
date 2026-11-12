# TODO — Master Skill Development Register

**Purpose:** The single authoritative execution backlog for the skill-first phase. Read [START_HERE.md](START_HERE.md) and [AGENTS.md](AGENTS.md) before work.

## Status and task discipline

- `[ ]` Pending / not yet accepted; `[x]` Accepted with documented evidence.
- A task may be labelled **IN PROGRESS** or **BLOCKED**, but its checkbox remains unchecked until every acceptance criterion is met.
- Do not infer completion from previous conversations, screenshots or standalone prototypes. Inspect actual files.
- Work on **one task at a time**. No UI/app implementation during the skill-release phase.
- Each task completion must include: changed file paths, tests run and outputs, engineering evidence checked, limitations, commit SHA, and reviewer/approval if applicable.
- Keep new suggestions in **Deferred / change requests** until explicitly prioritised.


## Architecture decision and documentation recovery (recorded 2026-11-12)

- **Agreed:** One multi-OEM backend, manufacturer/tool/model/revision selection, Baker Hughes first, Halliburton and others later. See [docs/multi-manufacturer-architecture.md](docs/multi-manufacturer-architecture.md).
- **Pending:** Final confirmation whether the *first release* is Baker Hughes-specific retrospective fault finding or the broader engineering skill. Keep the existing tasks as provisional until that decision; don't begin feature implementation while requirements are unresolved.
- [ ] **LH-001A — Recover the original BH training PDFs and rate each tool.** Historical references: `Liner Hanger Systems.pdf` and `Liner Hanger Hydraulics.pdf`. Confirm authorization, page-level coverage, operating details, specs, revisions and diagnostic evidence. Record a sufficient/partial/insufficient decision per tool. The working workbook is `Liner_Hanger_Multi_OEM_Inventory.xlsx`, supplied separately, not yet committed.
- [ ] **LH-001B — Confirm initial-release product scope.** Present documented coverage, agree fault-finding-only vs comprehensive engineering, then update these governance files and priorities without losing prior work.
- [ ] **LH-004A — OEM identity and knowledge pack contract (after LH-001B).** Manufacturer registry and tool/model/revision selectors in backend records, rule isolation and explicit unavailable states. No app UI work.

## Release gates and task sequence

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

## Current checkpoint

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

## Deferred / change requests (outside current skill gate)

- Full app/UI development using the completed skill APIs, guided by established UI/UX skill.
- Real-time WITSML/ETP integration and live shadow mode; no live field guidance without separate safety case.
- Engineer–virtual-driller voice communication and training simulation.
- Manufacturer-specific automated fault attribution requiring licensed OEM tool designs and review.
- Cloud hosting, multi-tenant accounts and field deployment.

**Scope changes:** Record proposed additions here with rationale and acceptance impact. Do not begin them during an active task without explicit reprioritisation.
