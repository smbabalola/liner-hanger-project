# LH-CALC-01 — Independent equation review, software and engineering acceptance boundaries

**2026-11-14 review state:** Analytical desk review by assistant; **not signed-off by an independent qualified engineer**. Review is a critical inspection of the implemented model's assumptions and analytic limit cases, **not** an actual OEM or operator model acceptance.

## Reviewed mathematical checks

1. **Uniform cylinder:** `V=π ID² L/4`. Unit `m²×m=m³`. 1m diameter, 1m length → `π/4≈0.7853981634 m³`.
2. **Concentric annulus:** `V=π(boreID²−pipeOD²)L/4`. 0.2m/0.1m by 10m → `0.2356194490 m³`. **Not a statement about annular friction, washouts or eccentricity.**
3. **Static pressure:** `Δp=ρgΔTVD`, constant `ρ` and `g=9.80665m/s²`; water 1000kg/m³ over 100m downward TVD gives `980665Pa`. MD must never be substituted for TVD. A fluid column with depth-dependent density requires future integration by depth.
4. **Open flooded pipe in pressure-balanced fluid:** `W=(m' − ρπ(OD²−ID²)/4)g L`. The material-volume subtraction is valid only with identical internal and external densities and **both ends open/equilibrated**; it is **not** surface hookload, downhole effective axial tension, sealed-pipe buoyancy, end-cap pressure, hanger load or buckling. The sign may be negative if the configuration is buoyant; don't clamp results.
5. **Minimum curvature:** `β=acos(cos i1 cos i2+sin i1 sin i2 cosΔazi)`, `RF=2tan(β/2)/β`, `ΔTVD=ΔMD(cos i1+cos i2)RF/2`. Verified analytic limit: 0°→90° over 100m yields `200/π≈63.661977236758m`. Horizontal straight section yields effectively zero ΔTVD. The model rejects a 180-degree dogleg singularity.
6. **Synthetic whole-section example:** Survey MD 0→100m, TVD 0→100m, bore=0.2m, pipe OD=0.1m, pipe ID=0.08m: pipe capacity `0.5026548246m³`, annular capacity `2.3561944902m³`, 1000kg/m³ fluid static pressure `980665Pa`. These independent arithmetic checks are reproduced in `tests/test_planned_job_section.py`, but test execution must still be confirmed for that new file.

## Engineering limitations that MUST survive future API work

- **Provenance is not authenticity.** A non-empty `source_id` or caller-provided `review_status="reviewed"` proves neither actual document availability nor independently approved OEM limits.
- **Station anchoring and datum:** The first station TVD is explicitly supplied at the first station MD. Section start/end MD must exactly match existing survey stations. A true whole-well integration needs a reviewed interpolation strategy, datum reconciliation and multi-interval geometry/version management; absent today.
- **Floating-point directional trigonometry:** Integration mixes Python binary floating-point trig with Decimal container values, so do not represent it as high-precision geodesy. Near-zero dogleg behavior, azimuth wrap, dogleg sensitivity and survey noise warrant further testing.
- **Fluid assumptions:** One uniform fluid density, no rheology, temperature/pressure changes, buoyancy gradients, non-Newtonian circulation, trapped liquids/gas or cement displacement.
- **Section limitations:** No coupling enlargement, washout, eccentricity, centralizer, open-hole dogleg clearance, completion hardware restrictions, hole enlargement or condition of annulus.
- **Tool implications:** None. No OEM torque/drag coefficient, setting threshold, shear pressure, ball seating, cement pressure or downhole mechanical state can be inferred from this static section calculator.
- **Potential physical consistency check:** Dry linear mass is treated as separately sourced rather than derived from metal dimensions and steel density; no material-property consistency review has been done. A realistic pipe catalog cross-check is needed before treating real job values as verified.

## Acceptance / next step

- **Prior verified regression:** 248 tests (2026-11-14) on Windows before `planned_job_section.py`.
- **New software gate:** 15 `test_planned_job_section.py` cases, expected combined suite 263; **not yet independently confirmed as passing**.
- **CI enhancement:** root `.github/workflows/skill-regression.yml` runs complete skill suite for Python 3.11 and 3.12, with `requirements-test.txt` in the skill. Workflow has been committed, **but no successful CI result is currently verified**.
- **Overall LH-CALC-01 remains open**. Assistant analytical review is complete at limited theoretical scope; *independent professional acceptance, real-case numerical verification and full regression of the new integration* are not.

**Next development gate:** Once regression is confirmed, the minimal uniform-section primitive slice may be accepted **at its explicitly limited scope** if remaining engineering/data-review conditions are met; then start `LH-CALC-02` torque-and-drag with an independent reference. Do not silently turn a one-section static model into a production field design model.
