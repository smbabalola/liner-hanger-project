# LH-003 — Connected synthetic normal/anomalous investigation fixtures

**2026-11-12 · Status: implemented, local full-suite verification and engineering review pending.**

## Goal

Exercise the existing retrospective backend modules **as a connected workflow**, rather than interpreting individual passing unit tests as a complete case investigation. These are testing fixtures only: no real well, no Baker Hughes technical-unit specifications, no actual setting-pressure limits, no customer field record and no claim of downhole state.

## Changed assets

- `skills/liner-hanger-rca/tests/fixtures/lh003_synthetic_cases.json` — two declarative fictional cases, explicit source references and expected screening results.
- `skills/liner-hanger-rca/tests/test_lh003_scenarios.py` — replays each case through existing `bha_tally`, `equipment_specs` (internal offset), `operating_limit_screen`, `evidence_timeline`, and `hypothesis_review` without altering their existing engineering logic.

The synthetic `200 psi` maximum is **not** a BH rating, recommended setting pressure, safe limit or job setpoint. It is an arbitrary numeric threshold to test comparisons. The fixture's apparent approvals, time alignment and engineering reviewers are explicitly artificial test flags, NOT validated approvals or calibrated sensors. No tool internal pressure is inferred from rig SPP.

## Case A — LH003-NORMAL-SYNTH

- Nominal as-run top-reference MD `1500 m` on fictional RKB; synthetic component lengths `3.5 m + 1.0 m`; fictional and reviewed slip-reference offset `1.2 m` yields nominal `1501.2 m MD` **only within the fixture**.
- Two fabricated rig SPP samples, `160` and `180 psi`, with explicitly fictional sensor and clock verification flags. Both screen `within_screening_bounds`.
- A daily report says the operation completed but is available with **date-level precision only** and cannot confirm actual hanger state.
- Expected output: no screening candidates, no automatic hypotheses, no forced failure; `confirmed_failure_mechanism=null` and `investigation_conclusion=undetermined`.
- This is a **software control scenario**, not proof of a successful real liner-hanger job.

## Case B — LH003-ANOMALOUS-SYNTH

- Fictional component length is **unknown**, internal offset is unreviewed; calculated internal MD stays unavailable. Top anchor alone does not establish the component bottom or slip position.
- Fabricated rig SPP `185 psi` is within the synthetic bound; `215 psi` produces a later **screening candidate** only, not evidence of a verified failed hanger setting.
- A deliberately inconsistent `220 psi` entry is labeled `rig_standpipe` but the fictional rule requires `cement_unit_discharge`; the mapping/equivalence are unverified. Expected: **unverifiable evidence gap**, never cementer-pressure proof. Rig Pump 2 and cement-unit pump are not equated.
- A date-only report alleges failure; its timestamp remains unknown and unplaced. An unrelated synthetic surface hookload observation and competing engineer annotation carry explicit but fictional clock/source provenance.
- Two engineer-authored questions examine **ball seating uncertainty** and **setting-system uncertainty**, with supportive/contradictory interpretations and historical-record discriminating questions. These are *competing questions*, not conclusions or BH-approved failure mechanism rules.
- Expected output: earliest verified flagged candidate points to the `215 psi` synthetic sample, not an actual first deviation; disputed interpretations remain visible; root cause `null`, conclusion `undetermined`.

## Acceptance checks

Test file checks complete data flow, source retention, exact OEM identity gating via existing screen, nominal geometry, unknown-depth handling, rule/measurement context, uncertain report time, competing hypotheses, contradiction preservation, case isolation, and the rule that no screening result proves mechanism or success.

**Execute on existing Windows checkout:**

```powershell
cd C:\dev\liner-hanger-project
git pull origin main
cd .\skills\liner-hanger-rca
py -m pytest -rs -q tests
```

Latest previously confirmed baseline before this change: **100 passed twice** on 2026-11-12 (23.72 s and 8.06 s). **Do not claim new tests passed until the actual local result is received.**

## Engineering acceptance limitations

This is an **integrated software regression**, not an independent reference-based validation of the five BH fault families. The fixture does not import raw high-frequency rig CSV, calculate dynamic hydraulics, model pipe movement, evaluate actual time synchronization, or verify actual BH equipment specs. Qualified review must assess whether a case's hypotheses and observed signatures are physically plausible for an exact supported BH model/size/revision; approved case procedure and measured source data remain prerequisites.

Next: use the resulting fixture evidence as test input for the report and remaining source-gated investigation workflow; keep LH-003 unchecked until both technical content and rights/source review are accepted.
