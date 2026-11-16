# REAL-01 — Product capability and integration audit

**Date:** 2026-11-16. **Status:** Completed code/path inventory; no implication of real-job acceptance. **Scope:** Existing GitHub repository contents, not private Baker Hughes files or locally uncommitted Windows assets.

## Existing components

| Capability | Existing location | Observed code state | Integration decision |
| --- | --- | --- | --- |
| Single browser case shell | `skills/liner-hanger-rca/app/index.html`, `app.js` | Visible, one file-based offline app; CSV/event/rulebook picker, synthetic fixtures, playback, basic static SVG assembly, notes, Markdown report and case JSON; synthetic Chromium tests | **KEEP as single shell**, reorganize primary replay layout, extend imports instead of rewriting a new frontend |
| Historical plotted rig replay | `scripts/build_investigative_replay.py` | Generates large Utah FORGE-focused HTML from 5-minute CSV and events; embeds numerous charts and illustrative assembly; not reusable general-case browser runtime | **REFERENCE/EXTRACT design and visual techniques only**; avoid case-specific hardcoded logic or mistaken depth inference |
| v1.5 investigative annotations | `assets/annotation_workspace.js`, `annotation_workspace.css`, `scripts/add_annotation_workspace.py` | Rich chart selection, saved range overlays, hover cards, evidence source references, author/review status, selectable detail zoom, attachments and local export. Coupled to `caseData`, column-index layout, `scrub`, `zoom`, fixed Utah/Pason assumptions | **ADAPT** richer review/hover/attachments to current time-keyed case schema. Do not inject as-is: incompatible original runtime contract |
| Existing MVP annotations | `app/app.js`, `app/index.html` | Chart drag and modal range notes work with persist/export, but only title/kind/body/source and limited hover tooltip | **EXTEND**, preserving tested interactions and enhancing evidence links/reviewer fields |
| Running-tool / liner / drillstring view | `scripts/build_investigative_replay.py`, `app/index.html` | Visually distinguishes components; old generator motion is explicitly report-guided, not sensed; new shell moves only with `running_depth` | **KEEP honesty guard**, improve engineering assembly/tally positions, zoom/orientation and synchronized event panel; never display manufactured activation |
| Exact-time & evidence chronology | `scripts/build_timeline.py`, `scripts/evidence_timeline.py`, `scripts/check_procedure.py` | Strict dated records and distinct measured/reported/screening candidates with source/review identity; Python modules currently disconnected from browser app | **CONNECT through local backend adapter** after case import contract is settled; retain browser-first usability during migration |
| Procedure candidate extraction | `scripts/extract_procedure_candidates.py` | Extracts page-referenced review candidates from PDFs, does **not** approve operating values; needs PDF processing dependency | **BACKEND/OPTIONAL**; support manual procedure/event entry when source cannot be parsed; never auto-approve PDF candidates |
| BHA as-run/planned tally | `scripts/bha_tally.py` | Source-gated manual and XLSX parsing, explicit units/reference anchor, planned vs as-run distinction; no graphical editor | **REUSE via local backend**, add UI mapping and display when actual tally available |
| Deterministic engineering RCA draft | `scripts/investigation_report.py`, `scripts/evidence_timeline.py` | Evidence-linked backend report compiler expects typed timeline/equipment/hypothesis inputs; current JS report is simpler, disconnected | **BACKEND/INTEGRATION**, replace simplified report once bridge is tested; don't imply unchanged backend semantics |
| Research hydraulics and other calculations | `scripts/*hydraulics*`, `scripts/*circulation*`, relevant LH-CALC modules | Research-only models/tests, many physically restricted cases; no user-visible need to complete calculations before RCA workspace | **DEFER**, preserve. Only show source-specified calculated insights with limitation flags |
| Baker Hughes evidence coverage | `docs/baker-hughes-document-inventory.md`, `docs/lh017-real-case-engineering-evidence-gate.md` | Equipment/procedure PDFs and drawings identified; **no proven complete source-matched historical rig telemetry** for required real-case benchmark | **REAL-05 blocker** until permission, as-run events and timestamped telemetry are confirmed |

## Why the narrow demo feels unlike the product

The `app` is an intentionally self-contained JavaScript implementation with simpler case schema, chart, schematic, rule evaluator and report. It does **not** invoke the richer Python evidence timeline, OEM procedure candidate extractor, BHA tally or full report compiler. The v1.5 annotations were implemented for a different fixed dataset and never integrated. The demonstration's Import / Replay / Deviations / Notes / Report tabs prioritize a software workflow over an **investigation workstation screen**, and lack the case-document/source workspace used by actual RCA engineers.

## Single integration architecture — avoid another demo

1. **Canonical source-aware case model** in the existing offline app: distinct telemetry files, operating reports, approved/unapproved procedure references, BHA/component descriptions and fluid/mud records; source IDs, units, clocks, datum, review level, and original file identity. Exportable portable case with clear notice if raw binary files are **not** embedded. Importers never silently recast measured vs reported vs assumed data.
2. **One central Replay workspace** within the same `app`: synchronized plots and engineering wellbore/assembly next to chronology/annotations, with selecting/zooming/time range and signal quality indications. Keep high-quality v1.5 hover/review concepts but adapt to current case format. Avoid frame-dependent fake downhole tool position.
3. **Optional local Python adapter** when features require `evidence_timeline.py`, `bha_tally.py`, `check_procedure.py`, `extract_procedure_candidates.py` or `investigation_report.py`. A Python loopback backend can communicate with the same frontend; validate source/units contract and preserve a file-only limited mode. Do not claim current browser JavaScript has backend parity.
4. **Document first, automated inference second**: procedure source and revisions, operator log, equipment tally and telemetry must be linked before evaluating deviations. Preserve candidate vs confirmed distinction. Missing source => evidence gap; unsupported file => manual entry plus source link.
5. **One authorized real historical case acceptance** on the same UI, cross-checking replay timestamps/events and output against original sources. No source-closed internal diagnosis or synthetic acceptance substitute.

## Immediate work order

- **REAL-01:** Inventory complete. The chosen architecture is **extend the existing app** (no replacement shell) and introduce an optional local Python bridge only where necessary. Mark only this gate complete.
- **REAL-02:** Build an **independent evidence file registrar** for job reports, procedures, equipment schematics and mud/fluid reports; source IDs, type, file name, analyst-provided provenance, timestamp and review status. Allow structured events/telemetry to be imported separately. Then add column mappings and units/time corrections without reprocessing source evidence.
- **REAL-03:** Rearrange the screen around playback, not import forms; reuse enhanced assembly and annotation interaction features.
- **REAL-04/05:** Integrate source-linked procedural evidence, report and actual job acceptance.

## Constraints

Do not commit Baker Hughes/customer confidential PDFs, actual job data, credentials or uploaded records into the public repo. Historical 939×2 GitHub regression was for the **synthetic offline demo** and stays valid historical evidence, not product completion. No user Windows smoke or source-verified real job acceptance yet.
