# LH-017 — Uploaded 15-case bulk report engineering-content review

**Date:** 2026-11-12  
**Evidence:** User-provided `lh017-bulk.zip` containing 15 Markdown reports, 15 JSON evidence records and `validation-manifest.json`. Local Windows suite previously confirmed **178 passed in 11.66 s**.  
**Review outcome:** **Synthetic report export and structural consistency passed. Meaningful fault-mechanism engineering acceptance not granted.**

## Cross-package integrity

ZIP contains one directory and 31 files: 15 `.md`, 15 corresponding `.json`, 1 manifest. For every case, manifest case ID, report status, conclusion, hypothesis count and source ID set agree with JSON; report ID and case ID appear in matching Markdown. No cross-file consistency mismatches detected.

| Family | Normal | Anomalous | Ambiguous |
|---|---|---|---|
| Ball drop/seating/water hammer | 1 | 1 | 1 |
| Hanger setting | 1 | 1 | 1 |
| Running-tool release | 1 | 1 | 1 |
| Cementing | 1 | 1 | 1 |
| Liner-top packer setting | 1 | 1 | 1 |

All 15 reports: `draft_unapproved`, conclusion `undetermined`; all evidence records `unreviewed`; no approved tool model/size/revision. Five normal reports: 0 hypotheses. Five anomalous and five ambiguous: 2 each. No physically confirmed tool state was claimed. Five ambiguous cases contain zero chronologically verified events.

## Content deficiencies to address as a coordinated batch

**P1 — No measurable discriminating signals or first supported departures.** All 15 scenarios are narrative-only (no `screening_details` in evidence), despite reports containing pressure/hookload/torque/flow references. All five anomalous reports have **zero rule screening candidates**. This is acceptable for evidence-workflow smoke tests, but insufficient to validate physical-response reasoning. Add synthetic values/units and source-localized chronological data for the *relevant* surface channels, including baselines and alternatives; avoid inventing approved OEM rules.

**P1 — Artificial for/against relationships.** The five anomalous cases reuse identical rationale text across families. One qualitative observation is tagged as supporting one mechanism and contradicting another without a specific measured physical difference or independently justified discrimination. Refactor into explicit family-specific interpretation hypotheses with distinct sourced evidence, label unsupported relationships `context`/`unresolved`, and reject unreasoned causal implications.

**P1 — Observation classification/provenance.** A `measured_observation` is output even though its summary is qualitative and no measured value/units/source row exist. The fictional source IDs and lack of CSV row/page locators must be visible as synthetic gaps. Add typed observation provenance or treat such notes as `reported_event` or `engineer_annotation`, as appropriate. No phantom physical measurements.

**P2 — False screen-entry formatting.** All five ambiguous cases contain an `evidence_gap` unrelated to any screen rule. `investigation_report.compile_report` currently places all `evidence_gap` records in `screening_findings`; rendered section reads `None; rule: None`. Separate general evidence-quality gaps from screening-unverifiable results, and render explicit absent screening detail without `None` tokens.

**P2 — Minimal real chronology.** Each normal report has one timed record; each anomalous report has two events sharing a timestamp (surface note plus fictitious assessor annotation), and an unplaced daily report. All five families reuse a single synthetic clock, with no pump-stage sequencing, multi-channel correlation, or before/after changes. This does not support retrospective reconstruction, although times are not fabricated as independently verified.

**P2 — Repeated boilerplate checks.** The general `required_evidence` field for all mechanism questions is the same. Make each check specify the actual instrument/source/configuration distinction and what would falsify an interpretation.

## Decision

- **Software acceptance at this point:** 178-test regression, 15-case synthetic report generation, and manifest/report structural consistency verified.
- **Engineering content acceptance:** **not granted**. Current batch is a narrative/evidence-organization smoke test, not a fault-signature validation suite.
- **Remediation approach:** one bulk correction and one complete suite rerun, not sequential family-by-family work. Strengthen synthetic time-series and reasoning contract first. Preserve conservative `undetermined` conclusion, unknown BH model-specific ratings and separation of rig/cement sources.
- **Still blocked by external evidence:** actual Baker Hughes model/size/revision, authorized operating/SU/TU instructions, exact source page references, genuine well records and competent independent engineering signoff.

Do not publish this as an approved OEM engineering performance model or start UI/job-package generation.
