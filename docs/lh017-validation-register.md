# LH-017 — Engineering validation register (first negative-control batch)

**Date:** 2026-11-12  
**Scope:** Baker Hughes-only retrospective fault finding. **Status:** IN PROGRESS — synthetic regression pending; physical engineering validation blocked by authoritative source and real-case evidence gaps.

## Existing independently observed baseline

User ran local Windows `py -m pytest -rs -q tests` after pulling `1f67f66`: **137 passed in 8.03 s**. Both updated synthetic Markdown reports were uploaded and content-inspected. Their fictional values remain test fixtures.

## This batch: fail-closed negative controls

New file: `skills/liner-hanger-rca/tests/test_lh017_release_negative_controls.py`. Tests model a synthetic instrumented hanger-setting observation and compare against a fictional job-specific max pressure. These verify that changing one important source identity or evidence condition makes the screening **unverifiable**, not a mechanical or compliance verdict.

| Negative control | Expected response | Status |
|---|---|---|
| Halliburton, unknown and misspelled manufacturer identities | No fall-back to Baker Hughes rule | New tests pending Windows verification |
| Mismatched tool revision, model, nominal size or configuration | Fail closed | Pending |
| Rule `authorized_for_case=False` | `unverifiable` | Pending |
| Wrong pressure unit / absolute-vs-gauge basis | `unverifiable` | Pending |
| Cement-unit pressure channel presented for rig-standpipe rule | `unverifiable`, unplaced evidence gap | Pending |
| Unverified equivalence between instrument and rule | `unverifiable`, unplaced evidence gap | Pending |
| Missing source-clock alignment | Unplaced, no verified earliest deviation | Pending |
| Normal case | No fabricated mechanism or proof of tool setting | Pending |
| Anomaly case | Candidate only, independent review still required | Pending |

Estimated new test count: **15**. Previous baseline 137; expected full collection **152**, but local collection results are authoritative.

## Five physical fault families — validation blockers, not yet passed

1. **Ball drop / water hammer / seating:** scenario evidence needs independent documented behaviour; pressure transient alone cannot confirm ball landed or sheared.
2. **Hanger setting:** hookload, actual downhole support and friction effects must be separated; single surface load/pressure change is not proof of set.
3. **Running-tool release:** model-specific hydraulic vs mechanical sequence must be source-approved; surface response cannot alone certify release.
4. **Cementing stage:** rig SPP, cement unit discharge, rate, volume and returns require independent source mapping, time and flow path; no extrapolated cement placement.
5. **Liner-top packer setting:** set-down transfer, packoff/element position and independent alternative explanations require specific as-run assembly and reviewed instructions.

These are **pending documentary/engineering scenario acceptance**, not working physics models or field-ready diagnostics. Supported candidates remain mechanism-described only per `docs/bh-v1-equipment-coverage-gate.md`.

## Required engineering evidence before LH-017 acceptance

- At least one authorised actual BH variant/size/revision with exact SU/TU and procedure page citations; conflict in SDD references resolved if used.
- Independent expert review of physical response and falsifying signatures for all five included fault families; normal and deliberately ambiguous controls.
- Source/units/timestamp known answers, validated event mapping from actual rig time-series, authentic provenance and rights decision.
- Report citation checks resolve to source pages or time-series samples; unknowns remain unverified.
- Clean install and full regression, including cross-OEM and unsupported BH variant rejection.

This work does **not** implement job-package building, predicted run-in-hole loads, UI, or any live operating recommendations.

## Run

```powershell
cd C:\dev\liner-hanger-project
git pull origin main
cd .\skills\liner-hanger-rca
py -m pytest -rs -q tests
```

Record observed Windows result before advancing the acceptance state.
