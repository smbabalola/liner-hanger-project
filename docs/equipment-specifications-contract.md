# Equipment specifications and internal BHA references — implementation v0.1

**Date:** 2026-11-12  
**Status:** Initial code and tests committed. Local regression and independent engineering review pending.

## Files

- `skills/liner-hanger-rca/scripts/equipment_specs.py` — typed `EquipmentRecord`, `EquipmentIdentity`, `SpecificationValue`, `InternalReference` and cautious comparison/geometry functions.
- `skills/liner-hanger-rca/tests/test_equipment_specs.py` — **13** synthetic-only tests for these contracts.
- Existing `skills/liner-hanger-rca/scripts/bha_tally.py` — planned/as-run tally, Excel candidate import, MD boundary calculations; unchanged.

## Record policy

A tool record stores `manufacturer_id`, family, model, nominal size, revision and part number. Specifications are separate **named** records with their type, explicit unit, value, origin (`manufacturer` or `job`), source ID/location, review status, identity of entrant/reviewer and dates.

- A job-specific record **never overwrites** a manufacturer record. `candidate_edit()` produces a new, unaccepted candidate, leaving the original unchanged. Application-level authorization and persistent immutable edit history **not yet implemented**.
- `reviewed` requires a reviewer and review timestamp. At present it is a *data flag*, not evidence of independent document verification, and it can be manually supplied. Future approval workflow must enforce authorization.
- `compare_job_to_manufacturer()` requires both values reviewed and matching parameter kind/unit; otherwise it returns `unavailable` or `not_comparable`. It returns only `numeric_comparison_only`, **never** a pressure or mechanical compliance verdict. This does not yet establish whether a job requirement is a minimum, maximum, window, absolute vs differential pressure, or whether both references describe the same pressure point.
- Numeric dimensions include length, OD, ID and ball diameter; supported length units are m, ft, mm and in. This first implementation stores the other numeric units as supplied, **not** verified conversions or safe operating units. Connection details, free-form custom string values and temperature-unit semantics require a later extension.
- Model/size/revision and source identity are currently recorded; rigorous manufacturer isolation and revision-gated rule application remain **LH-004A** tasks. No source-approved Baker Hughes values are seeded.

## Geometry policy

`InternalReference` describes a **known measured offset downwards from the component top**, for a particular installed component ID, with its source and review status. `internal_reference_md(tally, reference)` returns the nominal MD only when:

1. The selected tally resolves the component, with documented positive length.
2. The offset is non-negative, no greater than actual component length, and has explicit m/ft/mm/in units.
3. The offset source and review fields are present and marked reviewed.
4. The component top MD is calculable from a documented tally anchor.

Otherwise the function returns **None** for unreviewed/insufficient measurement, or raises a specific error for invalid/mismatched configuration. A reference named `hanger_slips`, `packer_element`, `ball_seat` etc. is **only a label**; the tool's actual mechanism, length, operating pressure and location are not inferred.

**Geometry limits:** Nominal measured depth only, not actual downhole position, TVD, pipe stretch, set-down movement, space-out shifts, thermal effects or an OEM certified reference geometry.

## Local regression

```powershell
cd C:\dev\liner-hanger-project
git pull origin main
cd .\skills\liner-hanger-rca
py -m pytest -rs -q tests
```

**Do not mark accepted before the user reports the results.** Baseline suite had 14 tests and prior BHA contract introduced 12 more; this module introduces 13 synthetic tests. Total expected collected tests: **39** with Python/pytest/openpyxl and Playwright Chromium available (actual collection output is authoritative).

## Future work

Secure identity/approval gate, immutable revision history, specification applicability (tool size/configuration, loading direction, differential vs absolute, units and sensors), checked operating envelopes, spreadsheet specification import, and reconciled field observations. Do not silently infer physical manufacturer dimensions from LinerForge templates.

Source basis: BH-SYS-2016 family/assembly overview; BH-HYD-2020 hydraulic concepts and troubleshooting context. Neither is authority here for any exact numerical OEM rating.
