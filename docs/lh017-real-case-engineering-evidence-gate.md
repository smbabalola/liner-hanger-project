# LH-017 — Authorized real-case engineering evidence gate

**Date:** 2026-11-12  
**Stage:** Start of genuine Baker Hughes case validation, **BLOCKED for case-specific diagnosis until accessible as-run and rig time-series evidence is verified**.  
**Previous milestone:** The 15-family/class synthetic content review was accepted and 201 Windows tests passed. That result is not physical engineering approval.

## Accessible evidence and source classifications

1. **Manufacturer training reference available in the project:** `Liner Hanger Systems.pdf` (BH-SYS-2016, 132-page source inventoried in `docs/baker-hughes-document-inventory.md`), source ranges for hanger/packer/running-tool/seat families. **Mechanism-level only**, not model/revision-specific limits or actual as-run installation.
2. **Manufacturer training reference available in the project:** `Liner Hanger Hydraulics.pdf` (BH-HYD-2020, 99-page source; particularly PDF pp82–96 troubleshooting). **Mechanism questions only**, not proof of any recorded well event or an approved operating envelope.
3. **Historical project note about a possible candidate job package:** prior project conversation referenced filenames `KHRM-299510 well sketch 2.pdf`, `KHRM-299510 WB - (OP) 7'' 26# ZXPN CSFL RS 2-RH SC EBS SOLO.pdf`, `INF - T901, KHRM-299510 7'' 26 LB ZXPN 2RH Schematic Rev-1.xlsx`, `SOP - One Trip - Tieback Seal Assembly Operating Procedures_Non CMT- Rev-A (1)(1).pdf`, `SOP - Tieback Milling Operation for Liner Top Extension Rev.D (1).pdf`, drawing sheets and `SIGN DT 58889+58890.pdf`. **This is a filename inventory from earlier conversation, not verified content or confirmation of the actual as-run configuration.** A project file search during the current session did not expose those attachments as readable documents. Do not publish a proprietary package or silently infer its contents.
4. **Authentic historical high-resolution surface rig time series:** **not located** in the presently accessible candidate-package inventory. A well sketch, signed ticket or procedural SOP alone does not establish the actual sensor time history or tool state.

## Evidence gates for a first actual case

| Gate | Required information | Current status |
|---|---|---|
| R1. Identity | Verified manufacturer, hanger type, model, size, revision and configuration; running tool; ball-seat/packoff; liner-top packer and cement accessories | Unknown for candidate case; filenames do not prove actual installed identity |
| R2. As-run configuration | Verified as-run versus planned tally, component identifiers, actual lengths, anchor/datum and MD depth basis | Not currently verified |
| R3. Approved documents | Authorized case-specific SOP/job program, applicable SU/TU, revision, precise page and evidence rights | Training manuals accessible, approved case-specific sources not verified |
| R4. Chronological job record | Timestamped daily drilling/completions log, service ticket, operation steps, stage transitions, ball/plug events and revision of reports | Not currently verified |
| R5. Surface measurements | High-resolution rig SPP, hookload, torque/RPM, depth/string position, rig pump rates/strokes, pumped volumes and returns if recorded. Cementing-unit channels must be separately mapped | **Unavailable in accessible case materials** |
| R6. Time and sensor provenance | Timestamp timezone, clock drift/alignment evidence, units, sensor location, pump mapping (rig vs cement-unit), missing/aggregated samples and data integrity | Not currently verified |
| R7. Independent engineering review | Mechanism alternatives, physical interpretations, contradictions, source citations, approved acceptance criteria, reviewer identity and signoff | Pending |
| R8. Rights/confidentiality | Authorization to analyze actual rig/operator/OEM documents and approved redistribution boundary | User must confirm/establish before any proprietary source publication |

## Offline review sequence (one batch, no phantom validation)

1. **Re-access the named candidate job documents in the project or local checkout; examine their contents and provenance.** Do not conflate the well sketch, as-designed bill of materials and actual as-run tally.
2. Build an **actual versus planned evidence crosswalk**: exact component and revisions, operation phases, source IDs, page/row references and unknowns. Everything not supported stays `unknown`.
3. Reconcile case procedures against the two BH training references **qualitatively** first. Do not activate numerical screens without authorized model-specific/job-specific sources.
4. Obtain historical rig surface logs/CSV and chronological job/fluids records; map pump circuits and verify timezone, units, sample rate, loss/return channels and depth proxies.
5. Execute the five investigation-family questions as applicable to **this actual equipment and operation**. A track absent from the job is `not_applicable`, not a failed test.
6. Submit draft retrospective packet for independent domain-engineer review. Explicitly state what would contradict each mechanism; keep conclusion `undetermined` where insufficient evidence.
7. Only accept **the demonstrably supported subset** for BH release, documenting all unsupported equipment and scenarios.

## Scope restrictions

No conversion of manufacturer course worked-example pressures or the synthetic six-sample cases into approved operating limits. No assumptions that rig `Pump 2` is the cementing unit, that rig SPP measures cement discharge, that daily log labels independently prove ball-seat or hanger state, or that time-of-day text is aligned telemetry. No wireline or formation-evaluation logs required as core inputs. No live operating commands, UI, job-package generator, or cross-OEM rule fallback.

**Decision:** LH-017 remains open. The next minimum input is one **readable, authorized case packet** (preferably the earlier KHRM-299510 files) with actual as-run details and, separately, historical surface rig CSV/time-series and job log. Until present, proceed with provenance inventory only, not a diagnosis.
