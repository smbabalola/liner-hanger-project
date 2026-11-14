# LH-CALC-02 — co-linear multi-section load propagation (v0.1)

**Status (2026-11-14):** User independently ran the full Windows regression after pulling through commit `a7e1822`: **334 passed in 12.85 s, zero failures**. This verifies the initial co-linear multi-section implementation against the unit/integration suite. It does not provide curved-well/dogleg model validation, Baker Hughes job-specific validation or operational sign-off.

## Why the first profile model is deliberately co-linear

Joining two straight sections with different inclinations/azimuths without modelling dogleg contact would omit the tension-dependent normal force at the change of direction. Thus this v0.1 profile supports **multiple different tubular dimensions, masses and friction coefficients along ONE common straight trajectory** only. Each interval has precisely two sourced survey stations with the same inclination/azimuth, and **all intervals must share this orientation**, case ID, survey ID/revision and TVD datum. All MD boundaries must be exactly contiguous, with consistent TVD at joints to 1 µm numerical tolerance (not an allowance for an actual 1 µm datum mismatch). It refuses a dogleg/turn, survey conflict, a gap/overlap, negative tension/compression, floating string, unsupported mud state or unreviewed OEM assumptions if a source is missing.

There is **no** curvature, capstan, dogleg bending, helical buckling, stiff-string, simultaneous axial + rotary movement, tool/bit torque or pressure-end-force physics in this initial model.

## Skill-local API and integration

- `scripts/torque_drag_profile.py`: `ProfileInterval(section, axial_friction, rotational_friction, contact_radius)`; `StraightProfile(intervals_top_to_bottom=(...), bottom_tension=...)`; `predict_straight_profile(profile)`.
- `scripts/run_torque_drag_profile.py`: strict offline JSON parser and CLI, optional `--output`.
- `examples/synthetic_torque_drag_profile.json`: fictional two-section source-qualified fixture, explicitly marked `unreviewed` and **not KHRM-299510 or Baker Hughes data**.
- `tests/test_torque_drag_profile.py`: analytical force balance, identical-material split invariance, three-mode tension propagation, different friction/weight, torque accumulation, and fail-closed geometry/source cases.
- `tests/test_run_torque_drag_profile.py`: schema, CLI and independent numerical expected values.

Run, from the standalone skill directory:

```powershell
py scripts/run_torque_drag_profile.py examples/synthetic_torque_drag_profile.json
```

JSON results report `top_section_tensions_n.pickup`, `.slackoff`, `.rotation`, `total_friction_contact_torque_nm`, and `sections_top_to_bottom`, including **each interval's separate bottom/top state** and **cumulative torque from the deepest section upward**. Sources, model ID, limitations and warnings are retained. The single supplied deepest-boundary tension is applied to three independent hypothetical motions; computed intermediate boundaries are explicitly labelled model-derived/unreviewed, **not source-set downhole forces**.

### Independent analytical two-section benchmark

Fictional straight string in 1000 kg/m³ fluid, total measured length 100 m, at 60° from vertical, with OD 0.10 m, ID 0.08 m, dry linear mass 15 kg/m, axial friction 0.20, rotary friction 0.30 and contact radius 0.05 m. Two intervals of 50 m each have identical properties. At the deepest boundary, source-labelled fictional tension = 20,000 N.

From **separate** inclined-plane equilibrium, displaced material volume = `π(0.1²−0.08²)×100/4`, buoyed weight `W=(1500−1000 V_metal) ×9.80665 = 11937.2100363 N`, normal `N=W sin(60°)=10337.9271418 N`, axial gravity `G=W cos(60°)=5968.6050182 N`. Summing the two sections must reproduce the 100 m single section:

| Independent reference | Expected |
|---|---:|
| Top pickup tension | 28,036.1904465 N |
| Top slackoff tension | 23,901.0195898 N |
| Top pure-rotation axial tension | 25,968.6050182 N |
| Total frictional contact torque | 155.0689071 N·m |

Independent conservation checks: at each boundary `top(lower,mode)=bottom(upper,mode)`; for each mode, `T_top = T_deep + Σ segment axial weight ± Σ segment axial friction`; `torque_total=Σ μ_rot_i N_i r_i`. Frictional torque is additive **only under the specified purely rotating co-linear assumptions**. The lower source tension does not imply any known liner-hanger force.

These are analytic Newtonian statics limiting-case benchmarks, not a published directional-well field data match or human OEM signoff.

## Verification gates

**Software-verification gate PASSED:** the 15 profile calculations and 9 JSON/CLI checks were included in the user's full Windows regression: **334 passed in 12.85 s** at checked-out commit `a7e1822`. GitHub Actions CI execution status remains independently unverified.

Further independent applicability review and curved/dogleg tension-induced wall-contact calculations are necessary **before LH-CALC-02 full acceptance**. Preserve the source data/uncertainty and never call section-top tension the rig hookload or equipment-setting force.
