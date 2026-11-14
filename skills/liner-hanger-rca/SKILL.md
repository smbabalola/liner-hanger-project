---
name: liner-hanger-rca
description: Evidence-led, retrospective investigation of liner hanger running, setting, release, cementing and packer anomalies using job programmes, rig time-series logs, equipment records and drilling-fluids information. Use when asked to reconstruct a liner-hanger event, distinguish symptoms from initiating causes, develop and test failure hypotheses, or draft an auditable root-cause investigation report.
---

# Liner Hanger Root-Cause Investigation (RCA) Skill — v1.5

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
