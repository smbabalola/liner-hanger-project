# LH-017 — Revised 15-case output acceptance review

**Reviewed:** 2026-11-12.  
**Inputs:** User-uploaded `lh017-bulk-reviewed.zip` after Windows regression **201 passed in 9.81 s** and successful 15-pair export.  
**Decision:** **Synthetic report/evidence-handling and revised-content acceptance PASS**. **Physical engineering validation NOT ACCEPTED; LH-017 stays open.**

## File and manifest checks

ZIP contains exactly **15 Markdown reports**, **15 matching JSON reports** and one validation manifest (31 files). Every manifest entry agrees with corresponding JSON for case ID, source-set, status, hypothesis count, surface-sample count, verified-event count, unplaced-event count and screening-findings count. Every Markdown renders six labelled surface samples and the correct unapproved/undetermined conclusion. No report displays the prior phantom `None; rule: None` screen.

Across five investigation families and normal/anomalous/ambiguous classes:
- All 15 reports contain exactly **six** typed numerical observations/raw sample records, two channels with three timestamps each (08:00, 08:10, 08:12 UTC).
- Normal: six fictionally timestamp-verified measured observations, one approximate daily note, zero competing hypotheses.
- Anomalous: six fictionally timestamp-verified measured observations, one approximate daily note plus one unplaced engineering annotation, two competing hypotheses with family-specific **context/unresolved** rationales, without unsupported supports/contradicts labels.
- Ambiguous: six `evidence_gap` events with raw sample times but no verified event time; one approximate daily note; two unresolved hypotheses.
- All are `draft_unapproved`; conclusions `undetermined`; review `not_completed`; tool model/size/revision remain unavailable.
- The `screening_findings` sections remain **empty intentionally**: no authorized BH numeric rules are supplied.

## Engineering observations

- Ball/seat stage retains distinct rig standpipe pressure (psi gauge) and rig pump rate (L/min). No ball-state inference.
- Hanger setting retains surface hookload (klbf) and standpipe pressure (psi gauge), with different synthetic changes over time. No assertion of slips engaged.
- Running-tool release retains surface torque (ft-lbf) and hookload (klbf), with explicit tool-variant uncertainty. No release confirmation.
- Cementing retains rig pump and rig returns rates (L/min), not cement-unit source values. No unsupported cement-placement calculations.
- Liner-top packer setting retains surface hookload (klbf) and string movement (m), without certifying packoff or actual element position.
- Fictional CSV row locators and source revisions are present and visible, not real third-party source citations.

## Closure of previous findings

1. **No quantitative samples:** resolved for the synthetic evidence-handling milestone via two-channel, three-timepoint numerical examples; these are **not** measured field data or validated physical anomaly models.
2. **Generic binary supports/contradicts statements:** resolved by five different, evidence-specific rationale pairs, conservatively labelled context/unresolved.
3. **Qualitative notes misclassified as measured:** resolved by numeric values, units, named instruments and fictional CSV row references; ambiguous source samples are evidence gaps.
4. **Phantom screening entry `None; rule: None`:** resolved.
5. **Skeletal chronology:** materially improved to six timed observations across two channels per case, but remains illustrative rather than high-resolution historical reconstruction.
6. **Boilerplate discriminating checks:** materially improved with family-specific required historical evidence.

## What is NOT accepted

No independently reviewed Baker Hughes physical response curves; no approved exact model/size/revision/SU/TU numerical criteria; no real-job validated clock/channel identity or source rights; no identified first verified out-of-spec operational deviation; no engineer signature. Competing hypotheses are *questions* rather than tested causes. The bulk package is sufficient to accept software/report-content correctness **within this synthetic scope only**.

**Next engineering phase:** choose an authorized actual BH as-run configuration with correct manufacturer documentation and permitted historical surface rig time-series/job logs; establish reviewed expected responses and independently evaluate the five investigative families. Do not use synthetic sample magnitudes as real rig setpoints or performance expectations. UI and job-package builder remain deferred.
