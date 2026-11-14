# START HERE — Liner Hanger Project

> **ACTIVE STEERING UPDATE (2026-11-14):** Read [STEERING.md](STEERING.md) first, then the top **LH-CALC** section of [TODO.md](TODO.md). The user approved an integrated calculation-design-verification workstream *inside* `skills/liner-hanger-rca/`; earlier statements below deferring all broad calculations or requiring RCA-only v1 completion first are historical and superseded **for the LH-CALC workstream**. UI development, cross-OEM support, unapproved OEM limits and operational sign-off remain deferred. The user-confirmed baseline is **219 passing software tests**, not physical model validation.


**Project:** Liner Hanger Project — Baker Hughes Retrospective Fault-Finding Skill (first release)  
**Phase:** Skill-first development; application/UI work deferred  
**Canonical repository:** `smbabalola/liner-hanger-project`  
**Canonical local checkout:** `C:\dev\liner-hanger-project`  
**Source of task truth:** [TODO.md](TODO.md)  
**Working rules:** [AGENTS.md](AGENTS.md)

## Mission

Finish a reusable, tested **Baker Hughes-only retrospective fault-finding skill** as the first release, before developing the application UI or broader engineering capabilities. Its job is to reconstruct historical liner-hanger operations from surface data and job records, identify the first supported deviation, evaluate alternatives, and draft evidence-linked investigation findings for competent engineering review. It must distinguish facts, calculations, interpretations, hypotheses, and verified conclusions.

The skill is **not** a live operations controller, OEM instruction substitute, well-control decision system, or certified root-cause investigator.


## Manufacturer-extensible design (agreed)

The eventual application and underlying skill use **one shared backend** supporting multiple equipment companies. The case selects `manufacturer_id → tool family → model/size → revision/configuration`; only that manufacturer's approved rule/knowledge pack can be applied. **Baker Hughes is first**. Halliburton and others are future additions and must not be represented as supported before source and test validation. The same generic telemetry, evidence, timeline and report engines remain shared. See [docs/multi-manufacturer-architecture.md](docs/multi-manufacturer-architecture.md).

**Release scope LOCKED on 2026-11-12:** first deliverable is **Baker Hughes retrospective fault finding**, not the broader well-planning/cementing simulator. Core investigation infrastructure must remain manufacturer-extensible. Halliburton and other knowledge packs are deferred. See [docs/first-release-scope.md](docs/first-release-scope.md).

## Current state — what is known, not assumed

Earlier work is **outside this new repository until inventoried and imported**. Do not describe it as implemented here until its source files and tests have been examined.

Known prior assets to inspect (do not recode from scratch):
- RCA skill `SKILL.md` packages (v1.0/v1.2 located); supporting references, timeline scripts, schemas, and examples may exist in older packages.
- v1.5 **annotated HTML replay** with historical rig channels, case-specific schematic, in-chart annotations, and evidence review.
- Later **HTML prototype extensions** for menu navigation, well setup, fluids, cementing, rig/cement pumps, units, report drafts, and CSV rig import.
- Historical Pason and case material; a Utah FORGE investigation example; synthetic test files.
- `WellOptix` as a reference for the *well data model*, not a project to copy or alter.

**Version note:** A ZIP titled `liner-hanger-investigation-skill-v1.5.zip` has been located and inspected for its file members; v1.5 is also used for the annotated HTML prototype. The ZIP's internal functions must still be tested and accepted before calling them validated. Prototype features are not automatically backend modules or engineering-validated models.

## Locked scope — Baker Hughes retrospective fault-finding skill v1

The first release covers:
1. **Manufacturer/equipment identity:** Baker Hughes family/model, running tool, packoff/ball-seat/packer configuration, revision if available; reject cross-OEM assumptions.
2. **Source-aware equipment knowledge:** the original Baker Hughes 2016 Systems and 2020 Hydraulics self-study guides, page-cited; model-specific rules gated pending exact Technical/Service Units and approved job procedures.
3. **Evidence intake:** historical surface rig CSV (high-resolution preserved), job programme/log, equipment and fluid information, timestamps, units and source quality.
4. **Chronological reconstruction:** running, circulation, ball drop, setting, running-tool release, cementing, packer setting as the available evidence supports.
5. **Fault-finding investigations:** deviations, observed signatures, competing hypotheses, contradictions, additional evidence needed; optional light-weight supporting calculations only where independently validated.
6. **Reports:** an auditable retrospective troubleshooting report with limitations and human review.

The initial five investigative families are ball drop/water hammer, hanger setting, running-tool release, cementing, and liner-top packer setting. Only a **document-supported subset of tools/scenarios** may be marked supported in the first release. A source guide does not make every model/revision fully diagnostically supported.

Deferred until after v1: broad job planning, full hydraulics and placement simulation, field-service operations report, full-featured cementing model, app UI, Halliburton/other OEM packs, voice driller, live WITSML, real-time commands, manufacturer certification, or claims of automatic definitive root cause. Preserve the earlier work as a future backlog. Capture ideas in the deferred backlog; do not silently change scope.

## Mandatory workflow — resume here

1. Read `START_HERE.md`, then `TODO.md`, then `AGENTS.md`.
2. Confirm repository/branch and working-tree status. Do not overwrite uncommitted changes.
3. Locate the **first eligible unchecked task** in `TODO.md`; inspect predecessors and acceptance criteria.
4. Inventory existing material before writing replacement code.
5. Work on **one task**, with a reproducible test or review artifact.
6. Run tests and check engineering evidence; record exactly what was and wasn't verified.
7. Update `TODO.md` status, acceptance evidence and blockers; commit narrowly scoped changes.
8. Repeat the same loop only if acceptance criteria pass. Otherwise fix or mark blocked.

## Engineering boundaries

- Distinguish **measured / reported / calculated / inferred / unknown** on every data product.
- Never fabricate missing measurements, float-valve specifications, setting pressures, pump output, cement position, or OEM limits.
- A rig pump channel named `Pump 2` is **not** cementer pump evidence without documented channel provenance.
- When the cement unit is isolated from rig pressure instrumentation, do not label rig standpipe pressure as measured cement-unit pumping pressure.
- Preserve original CSV cadence and originals; any chart downsampling must not replace forensic source data.
- Source every equipment-specific rule to an authorized manufacturer/model/revision document.
- Engineering analyses require review by a competent engineer; evidence does not automatically prove a root cause.
- Do not commit confidential customer, operator or proprietary OEM manuals without authorization. Use synthetic/public fixtures when needed.

## Definition of done: skill v1 release

The release is eligible only when all **v1 release-gate** items in `TODO.md` are accepted, the imported skill passes regression tests, its allowed Baker Hughes rules have page/model provenance, and a clean install processes **at least one normal and one anomalous synthetic/authorized case** without inventing measurements or model-specific limits. Exact models with inadequate source coverage must explicitly return 'insufficient documentation'. Known engineering limitations must be documented.

Only after the skill-release gate passes do we begin app architecture/UI integration as a **new, explicitly approved** workstream.

## Project history

The original prototype work must be preserved as evidence/reference; it should not be promoted to production code by copying the entire HTML file into `SKILL.md`. Consolidate reusable engineering functionality behind testable interfaces.

**Next action:** `LH-001` / `LH-001A` — finish asset and Baker Hughes source coverage audit, reconcile source-backed equipment families against LinerForge templates, and identify the supported v1 scenario subset. Do not automatically promote course worked-example values or LinerForge simulated ratings to operating criteria.

## 2026-11-12 approved scope expansion — planned engineering baseline and fault reconstruction

The user explicitly clarified and approved the integrated **planned design/verification → observed rig data → retrospective fault investigation** workflow. This is a new tracked workstream alongside the existing accepted synthetic fault-reporting milestone. It **supersedes the earlier blanket deferral of all design calculations** for this specific, approved workstream; UI, other manufacturers and unvalidated OEM rules remain deferred.

- **Before job execution:** the KHRM-299510 execution pack is a *planned* engineering benchmark (not proof of actual job execution or failure). Independently reproduce justified torque/drag pickup/slackoff loads, circulation hydraulics, surge/swab and documented tool force comparisons when inputs and authorized model-specific sources are sufficient.
- **After a reported problem:** ingest historical rig surface CSV and job chronology, identify where actual stage/depth/time measurements differ from the vetted planned envelope, distinguish a prediction difference from an approved-limit breach, and review competing causes. Do not assume a preset or ball-seat shear state from isolated pressure/velocity signals.
- **Cross-cutting:** all results retain input page/cell/row provenance, model assumptions, units, approved-tool/revision status and reviewer decisions. Original design output is a comparison target, not an independent physical truth.
- **Implementation order:** planned data/benchmark contract, independently checked physical solvers, case-specific comparisons, then planned-to-actual fault integration. Read `docs/planned-design-and-fault-investigation-architecture.md`. No numerical solver or KHRM benchmark is yet validated.

The prior statement that all engineering calculations are deferred is retained in historical context, **but no longer applies to this explicitly approved scope**. Track the actual work in `TODO.md`; do not silently tick pending BH engineering gates.
