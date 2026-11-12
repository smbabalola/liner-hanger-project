# LH-017 — Bulk content remediation: 15 cases in one coordinated change

**Date:** 2026-11-12. **Status:** Committed; local full regression and re-export pending.

## Source review triggering this implementation

Inspection of user-provided `lh017-bulk.zip` (15 Markdown/JSON pairs and manifest) found purely narrative "measured" events without recorded units or values, identical generic for/against links in all anomalous cases, just one/two timestamped events, and non-rule evidence gaps rendered as `None; rule: None`. Findings: `docs/lh017-bulk-output-engineering-review.md`.

## What was implemented, across all 15 cases

1. **Six typed synthetic surface records per case:** three source-sample timestamps (08:00, 08:10, 08:12 UTC), two distinct instrument/source channels per family. Every record states numeric value, unit, measurement domain/basis, fictional CSV row and revision, sample clock and channel quality. Each case's values are *invented illustrative telemetry*, **not** expected or validated Baker Hughes physical response curves or operating thresholds.
2. **Five distinct measurement families:**
   - Ball/seat: fictional **rig standpipe pressure** (psi gauge) and **rig pump rate** (L/min).
   - Hanger setting: fictional **surface hookload** (klbf) and **rig standpipe pressure** (psi gauge).
   - Running-tool release: fictional **top-drive surface torque** (ft-lbf) and **surface hookload** (klbf); hydraulic/mechanical release is **not** chosen.
   - Cementing: fictional **rig pump rate** and **rig returns rate** (L/min); rig source data **must not** be described as cement-unit discharge measurements.
   - Liner-top packer: fictional **surface hookload** (klbf) and **surface string movement** (m). Actual element movement/packoff remains unknown.
3. **Evidence classes:**
   - Normal and anomalous samples have fictional, explicitly labeled aligned source timestamps and become typed `measured_observation` events. These fictional quality flags **do not authenticate** the source.
   - Ambiguous samples preserve their numeric raw values and raw source timestamps, but are `evidence_gap` records with `time_state=unknown` and `timestamp=null` due to deliberately unverified units/channel mapping/clock.
   - Daily notes stay `reported_approximate`, unplaced. Assessor interpretation is a separate **unplaced annotation**, not a verified physical event.
4. **Competing explanations:** Each family includes specific two-sided interpretation rationales and distinct discriminating evidence requests. Anomalous associations are conservatively **context** and **unresolved**, not binary causal `supports`/`contradicts`: the invented records cannot establish a physical mechanism. All causes remain `undetermined`.
5. **Renderer contract:** Added a typed `measurement_details` field to evidence events and report JSON and a visible "Surface sample" entry in Markdown, with source row location. General unruled `evidence_gap` entries are no longer mislabelled screening findings, so `None; rule: None` must disappear; genuine unverified operating-rule screens remain in the screening section.
6. **Validation manifest:** Now includes counts of source measurements, verified events, unplaced events and rule screens per case.

## Tests and expected behavior

Updated `tests/test_lh017_bulk_scenarios.py` for 6 timed observations per normal/anomalous case and 0 placed events per ambiguous case. Added parametrized assertions across all 15 for typed source measurement, clear missing provenance, clock treatment and no fake screen; five family-specific rationale tests; and negative controls for missing numeric samples and invalid clock states.

Previous verified Windows baseline: **178 passed in 11.66 s**. **New estimated collection: 201**; actual count and pass/fail remain pending local execution. No tests have been run in this coding environment against the user Windows checkout.

```powershell
cd C:\dev\liner-hanger-project
git pull origin main
cd .\skills\liner-hanger-rca
py -m pytest -rs -q tests
py scripts/lh017_bulk_scenarios.py --output-dir reports/lh017-bulk
```

The exporter writes the same 15 JSON/Markdown pairs plus one manifest; the local `reports/` folder remains Git-ignored. After the run, the updated ZIP should be inspected as a single package for data fidelity, contradictions, chronology and traceability.

## Critical limitations

- **No actual OEM model, size, revision, service/technical unit, job program or approved performance threshold is available** to these fixtures. Pressure/hookload/torque magnitudes are illustrative samples, not physically benchmarked fault signatures; no validated ball arrival, setting, release, cement placement or packer packoff.
- Contextual mechanism questions remain hypothetical and need competent independent engineer validation against authorized documents and records.
- Fictional CSV row locations are demonstration provenance only; do not describe them as real historical source citations.
- No job-package generation, application UI or operational setpoint recommendation.

**LH-017 remains in progress**; this is a bulk software/content remediation, not completed engineering validation.
