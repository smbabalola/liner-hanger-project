# TODO — Real Liner Hanger RCA Product MVP

**Re-scoped 2026-11-16 following user clarification.** The goal is a **usable real-job investigation application**, not just the narrow offline synthetic demonstration. [STEERING.md](STEERING.md) governs. **REAL PRODUCT MVP: IN PROGRESS — NOT YET ACCEPTED.** The successful 2026-11-15 demo remains the starting point, not a product completion claim.

## Active release checklist (execute in order)

- [x] **REAL-01 — Audit and expose existing capabilities [COMPONENT AUDIT COMPLETE].** Inspect `skills/liner-hanger-rca/app/`, all prior replay/animation/annotation UIs, Python parsing/timeline/evidence/rule/report modules and launch instructions. Create one component map showing: working and visible / implemented but hidden / disconnected / genuinely absent; choose a single integrated local app architecture. **Pass:** grounded inventory and implementation sequence, no parallel disconnected shell.
- [ ] **REAL-02 — Actual job case and independent imports.** UI create/open/save/reopen investigations. Import telemetry files, chronological reports, procedures, schematic/assembly data and fluid records independently; support column/unit/time/depth mapping, provenance, timestamp synchronization diagnostics, absent channel/error states and preservation of raw source identities. Document supported formats; provide manual event/procedure entry where full PDF extraction is unavailable. **Pass:** user can build a case from separately provided real documents and measurements without editing code or JSON.
- [ ] **REAL-03 — Engineering replay workstation.** Make animated wellbore + running-tool/liner/drillpipe and time-aligned plots the primary screen; synchronize depth movement, SPP, hookload, torque, RPM, pump rate/volume, return-flow and reported job events when available. Provide play/pause, scrub/zoom and chart time-range selection. Use approximate clearly labelled assembly where dimensions are unknown; never simulate observed tool activation without evidence. **Pass:** source-matched replay is inspectable throughout a historical job.
- [ ] **REAL-04 — Investigation and persistence.** Link approved procedural steps to job events and telemetry; show supported potential deviations vs missing/ambiguous records, not fake OEM thresholds. Build range-note modal with edit, hover/selection reveal, saved reload; support observations, alternative failure hypotheses and reviewer disposition. **Pass:** a researcher can document and revisit a complete investigation.
- [ ] **REAL-05 — Auditable RCA report + real-case validation.** Export useful evidence-linked report including chronology, sources, plot/range references, candidate deviations, interpretations, limitations and review status. Perform full case investigation using a **user-authorized real liner-hanger job package with timestamped surface data**, cross-check against raw records, and do a Windows manual acceptance review. Retain normal/anomalous fixtures as automated regression. **Pass:** end-to-end real case completed and reviewed, with test logs and residual defects recorded; no unsupported engineering approval claim.

## Latest verified workstream activity — 2026-11-16

- **REAL-01: COMPLETE (code/path inventory only).** [Integration map](docs/real-mvp-component-integration-map.md) identifies the current browser app, earlier Utah FORGE replay, rich v1.5 chart annotation workspace, Python `evidence_timeline.py` / `check_procedure.py` / `bha_tally.py` / `investigation_report.py`, and the actual disconnections. Decision: **keep one existing browser shell**; adapt assets and add an optional Python bridge instead of building another unrelated demo.
- **REAL-02: IN PROGRESS.** Added **independent UI evidence-file register** under Import case: job reports, procedures, BHA/equipment drawings, fluids reports, telemetry source, other. Each source has a required ID, type, review declaration, file name, size, optional browser SHA-256 and no embedded binary; metadata persists with the case and appears in draft reporting. Added Playwright browser tests for restoring evidence after reload, JSON export and duplicate ID rejection. **This is metadata intake only**: PDF/OEM parsing, file byte storage, interactive column mapping and true multi-source reconstruction remain open.
- GitHub Action run for the latest evidence-register test commit `a1b7c9ec`: **awaiting verified final result** before updating test counts or claiming this stage passed. Historical full baseline remains **939 passing tests on each Python version** for the synthetic-only demo. Do not mark REAL-02 accepted.

## Immediately next work

1. Inspect which original assembly animation, chart interaction and investigation modules were never surfaced in the stripped-down offline demo. Reconnect proven components before implementing replacements.
2. Verify which provided Baker Hughes materials are **operating procedures/drawings** versus actual time-series surface data and job logs. Do not presume the existing PDFs contain usable telemetry.
3. Establish the single app case schema and source/provenance model; allow different files for each evidence type and sensible mapping of mixed rig-export formats.
4. Complete one visible vertical slice: import a time series + job log → animated replay + charts → select and annotate → procedure candidate → export. Then grow coverage and validate an authorized real case.
5. Run tests after each integration batch; update both files with precise passing evidence, observed defects and remaining gaps.

## Current verified baseline (historical, do not erase)

- The offline browser demonstration at `skills/liner-hanger-rca/app/index.html` has Import, Replay, Deviations, Notes and Report, and synthetic fixtures.
- [CI 43764373475](https://github.com/smbabalola/liner-hanger-project/actions/runs/43764373475) reported **939 passing tests on Python 3.11 and 939 on Python 3.12** for the previous demo release. It tested synthetic normal/anomalous cases, persistence, exports, invalid data handling and standalone folder portability. See `docs/mvp-local-release-evidence.md`.
- That demonstration does not establish independently imported real source-document ingestion, direct Python engine integration, a satisfactory central engineering replay UI, real-job evidence validation or a Windows user sign-off.
- Existing LH-CALC modules and research are **preserved and deferred**. Do not reopen specialized hydraulics as a condition of basic RCA product completion.

## Evidence register — update with actual observations

| Gate | Current state | Evidence required to close |
| --- | --- | --- |
| REAL-01 inventory | COMPLETE — documented in `docs/real-mvp-component-integration-map.md` | Existing browser app retained; richer annotation, replay, BHA, evidence and report engines mapped |
| REAL-02 real imports | OPEN | screen-driven multi-source case, mapping and reopening |
| REAL-03 visible replay | OPEN | synchronized assembly, events and telemetry on source data |
| REAL-04 procedure/notes | OPEN | traceable source comparisons and persistent range notes |
| REAL-05 report/real-case acceptance | OPEN | exported report checked against raw historical data, Windows user check |
| Previous demo | VERIFIED HISTORICAL | run 43764373475; does not close REAL gates |

**Data/approval blocker:** The existence of BH PDFs and drawings alone does not prove that timestamped SPP, hookload, torque, RPM, flow, volumes, depth and returns are available. Confirm source coverage before asserting REAL-05 is ready. Use only authorized job data and keep confidential materials outside public GitHub. Any real-job diagnoses remain engineering drafts pending qualified review.

**Definition of done:** You can investigate a genuine historical operation through one local application from independent evidence import to replay, procedure screening, annotations and audit-ready report **without programming**. All five REAL gates must be demonstrably satisfied. Preserve accurate status even if the target date cannot be met.
