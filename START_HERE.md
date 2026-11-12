# START HERE — Liner Hanger Project

**Project:** Liner Hanger Engineering Skill  
**Phase:** Skill-first development; application/UI work deferred  
**Canonical repository:** `smbabalola/liner-hanger-project`  
**Canonical local checkout:** `C:\dev\liner-hanger-project`  
**Source of task truth:** [TODO.md](TODO.md)  
**Working rules:** [AGENTS.md](AGENTS.md)

## Mission

Finish a reusable, tested liner-hanger engineering skill before building an app interface. It should help qualified engineers prepare, reconstruct, evaluate, explain, and report **historical** liner-hanger operations, including successful jobs and jobs requiring investigation. It must distinguish facts, calculations, interpretations, hypotheses, and verified conclusions.

The skill is **not** a live operations controller, OEM instruction substitute, well-control decision system, or certified root-cause investigator.

## Current state — what is known, not assumed

Earlier work is **outside this new repository until inventoried and imported**. Do not describe it as implemented here until its source files and tests have been examined.

Known prior assets to inspect:
- RCA skill `SKILL.md` packages (v1.0/v1.2 located); supporting references, timeline scripts, schemas, and examples may exist in older packages.
- v1.5 **annotated HTML replay** with historical rig channels, case-specific schematic, in-chart annotations, and evidence review.
- Later **HTML prototype extensions** for menu navigation, well setup, fluids, cementing, rig/cement pumps, units, report drafts, and CSV rig import.
- Historical Pason and case material; a Utah FORGE investigation example; synthetic test files.
- `WellOptix` as a reference for the *well data model*, not a project to copy or alter.

**Important:** `v1.5` is a verified label for the *playback/annotation prototype*, **not evidence that a consolidated skill v1.5 package exists**. Audit actual artifacts before assigning skill versions or completion status. Prototype features are not automatically backend modules or validated engineering models.

## Locked scope — skill release first

The skill release covers:
1. Job, well, geometry, directional survey, BHA/running tool, fluid and procedure data contracts; missing-data and unit management.
2. Historical rig CSV ingestion and high-resolution time-series preservation, provenance, channel mapping, time alignment and quality checks.
3. Chronological operational reconstruction and evidence-linked engineer annotations, for both successful and unsuccessful operations.
4. Verified deterministic core calculations (well/string volumes and hydraulics/placement **only when inputs and independently checked methods suffice**).
5. Separate rig-pump and cement-unit data sources; planned cement stages; rig-only response interpretation when cementer data is missing.
6. Planned-versus-observed comparisons with explicitly identified measurement sources and uncertainties.
7. Optional structured hypothesis/failure investigation; do not force a failure outcome.
8. Field service and engineering analysis report generation with traceable evidence and human review.

Not for this release: production UI redesign, LLM driller, voice training simulator, live WITSML, real-time field commands, manufacturer certification, or automated equipment-specific root-cause certainty. Capture ideas in the deferred backlog; do not silently change scope.

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

The release is eligible only when all **P0 / release-gate** items in `TODO.md` are accepted, their tests run, the source and validation registers exist, a clean-install instruction works, and **at least one successful and one anomalous historical/synthetic case** produce auditable outputs without invented facts. Known engineering limitations must be documented.

Only after the skill-release gate passes do we begin app architecture/UI integration as a **new, explicitly approved** workstream.

## Project history

The original prototype work must be preserved as evidence/reference; it should not be promoted to production code by copying the entire HTML file into `SKILL.md`. Consolidate reusable engineering functionality behind testable interfaces.

**Next action:** `LH-001` — audit/inventory the existing skill packages, prototype files, scripts and representative datasets; record located files, versions, dependencies and test evidence before importing them.
