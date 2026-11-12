# Retrospective operating-limit screening — first implementation

**Date:** 2026-11-12  
**Status:** Code and synthetic regression tests committed; local Windows regression and engineering review pending. This is a **source/identity-gated screening component**, NOT a database of verified Baker Hughes tool ratings.

## Implementation

- `skills/liner-hanger-rca/scripts/operating_limit_screen.py`
- `skills/liner-hanger-rca/tests/test_operating_limit_screen.py`

The checker accepts `ApprovedLimit` and `Observation` objects (or equivalent JSON dictionaries through `screen_from_dict`). It deliberately has **no seeded equipment ratings or setpoints**.

An engineer may enter a documented numeric `maximum`, `minimum`, or `range` with: full `manufacturer_id/family/model/size/revision/configuration_id`, stage, parameter, quantity/unit, pressure basis, measurement domain, limit source ID/revision/location, reviewer/approval reference, and an explicit per-case authorization flag. The observation records the same tool identity plus measurement channel, source, timestamp, units/channel/time alignment and verified comparability.

**Screening is blocked** if any of the following disagree or are unverified: active release manufacturer (Baker Hughes only), exact model/size/revision/configuration, stage or parameter, quantity/unit, pressure basis (gauge vs absolute vs differential), measurement domain (e.g. rig SPP vs cement unit discharge), source approval for the case, sensor unit/mapping, clock alignment, or explicit equivalence between the recorded sensor and the pressure/load reference used by the limit.

The result is either:
- `unverifiable` with explicit reasons;
- `within_screening_bounds`; or
- `outside_screening_bounds`.

The last two mean only a **numeric comparison of documented, review-marked inputs**, never that the tool set/released, the barrier was verified or a root cause established. The reviewer/approval fields in this MVP are caller-provided: **there is not yet a secure approval workflow**. Likewise, a retrospective source record may be manually marked approved without independent proof; this must not be presented as a manufacturer-certified verdict.

**Scope limits and safeguards:**
- Deliberately **no automatic pressure/force conversions** and no assumed engineering units. Different units result in `unverifiable`, even if convertible. Unit conversion with full source audit is a separate validation task.
- Different named pressure phenomena are not interchangeable. Rig Pump 2 SPM is NOT cement unit pump information. Rig standpipe pressure is NOT a cementer discharge or downhole/internal pressure measurement just because units match.
- Comparison assumes observation and limit describe the same physical reference and sampling intent; `measurement_equivalence_verified` must be true. No hydraulic model or friction/pressure-loss corrections are inferred.
- All values and tool names in the tests are **fictional**. No Baker Hughes numerical ratings or design dimensions have been inferred from training guides, LinerForge estimates or simulated examples.
- A single observation check does not evaluate prolonged excursions, sensor measurement uncertainty, sample gaps, calibrated accuracy, stage timing confidence or sequence compliance. Those are subsequent evidence-processing tasks.

## Local test gate

```powershell
cd C:\dev\liner-hanger-project
git pull origin main
cd .\skills\liner-hanger-rca
py -m pytest -rs -q tests
```

Previous baseline was **39 passed**. The new suite adds parametrized negative tests; inspect the **actual** pytest total rather than relying on an estimated number. No claim of successful local execution is made here.

## Future linkage

After source-approved actual BH model technical units/job procedures and a reviewed case contract exist, this screen may attach its traceable, non-conclusive findings to the existing annotation/evidence engine. Adding a UI, real-time commands or automatically translating generic course examples into approved limits remains outside the v1 skill scope.
