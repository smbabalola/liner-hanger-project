# LH-CALC-02 — connected weighted planar intervals (research v0.1)

**Status (2026-11-14): IMPLEMENTED; NEW WINDOWS REGRESSION NOT YET VERIFIED.**
Last actual user-confirmed full skill regression: **432 passed in 13.82 s** at code commit `bf7838e`. This module is **not a qualified field model** and does not implement 3D directional-well torque/drag.

## Exact scope and data contract

`scripts/torque_drag_weighted_profile.py` connects one or more **source-qualified planar weighted RK4 intervals**. Each interval has exactly two sourced survey stations, a single constant azimuth (unchanged over the **entire** profile), a 0–90° inclination and **linearly varying inclination within that interval**. The top of the lower interval must match the bottom of the upper interval in **MD, TVD (1 micrometre purely numerical comparison), inclination and azimuth**. Case ID, survey ID, survey revision and TVD datum must match. Duplicate section IDs and survey gaps/overlaps fail closed. The first-station TVD must be independently supplied for *each* interval, not silently inferred or adjusted by this engine.

Each interval may have different source-labelled geometry, dry weight, fluid density, friction coefficients, contact radius, and RK4 step count. Within one interval these properties are uniform. A change in trajectory curvature derivative at a joint is allowed **only if tangent direction stays continuous**; any discrete kink is rejected. There are no added point-load, point-contact, tool-joint or dogleg transition forces.

Separate **pickup**, **slackoff** and **pure-rotation** tensile boundary values are propagated **from bottom to top**. The single user-provided bottom source boundary is used as a nominal starting value for all three hypothetical pure motion states. All newly calculated interface tensions are labelled `MODEL-DERIVED-NOT-OEM` and **unreviewed**. Friction torque is accumulated only for pure rotation. Profiles are deliberately marked `unreviewed_inputs` when model-derived boundaries are present; no automated engineering approval is given.

Every interval independently uses `predict_weighted_curve`, so its fail-closed rules (compression, negative buoyed weight, unsupported azimuth turn, sampled contact-side reversal and nonfinite arithmetic) still apply.

## Standalone interface

- `scripts/torque_drag_weighted_profile.py`: `WeightedProfileInterval`, `WeightedPlanarProfile`, `predict_weighted_planar_profile`.
- `scripts/run_torque_drag_weighted_profile.py`: offline JSON CLI; `intervals_top_to_bottom` array and `bottom_tension` source-number record. Every interval includes `planned_section`, sourced `axial_friction`, `rotational_friction`, `contact_radius`, and integer `integration_steps`.
- `examples/synthetic_torque_drag_weighted_profile.json`: a fictional 100 m 0°→60° build, split exactly into 0°→30° and 30°→60° 50 m segments, with explicit mathematical TVD at 50 m, not real well/job/OEM inputs.
- `tests/test_weighted_planar_profile.py`: split invariance, mode continuity, torque conservation, unequal friction, survey/geometry invalidity, compression/contact transition propagation.
- `tests/test_run_torque_drag_weighted_profile.py`: standalone CLI, numeric benchmark, malformed input and source-qualification checks.

```powershell
cd C:\dev\liner-hanger-project\skills\liner-hanger-rca
py scripts/run_torque_drag_weighted_profile.py examples/synthetic_torque_drag_weighted_profile.json
```

## Independent analytical integration benchmark

For a **fictional uniform 100 m 0°→60° planar build**, the sectional ODE is the same as `TORQUE_DRAG_WEIGHTED_CURVE_VALIDATION.md`. Because 0°→30° over 50 m and 30°→60° over 50 m have the same signed curvature `k` and the same uniform weight/friction, splitting the integral must not alter the solution beyond RK4 truncation/rounding.

All mode-specific interface tensions must satisfy `T_top(lower,mode) = T_bottom(upper,mode)`, and the purely rotational wall-contact torque is the sum of sectional contributions. The independent closed-form weighted constant-contact-side equations in `tests/test_weighted_curve_independent_benchmarks.py` give these expected totals:

| Benchmark | Expected approximate result |
|---|---:|
| Top pickup axial tension | 34,214.052132 N |
| Top slackoff axial tension | 26,217.837754 N |
| Top pure-rotation axial tension | 29,871.993236 N |
| Total pure-rotation contact torque | 298.240234 N m |

These numerical totals use the **same known mathematical planar assumptions** as the single-section reference; they are not evidence of accuracy in a complete as-drilled well.

## Exclusions and acceptance gate

**Not implemented:** 3D inclination-and-azimuth changes, multi-station 3D trajectory curvature, real string stiffness, wall-side transfer/contact loss, casing coupling, dynamic motion, pressure area effects, tool joint/BHA forces or true rig hookload. A real Baker Hughes liner-hanger job remains unavailable for source-verified engineering comparison. Source IDs are metadata, not authenticity proof. The model must never present surface loads as certified equipment setting or running limits.

**Pending:** user-run **full Windows regression** of the new code and 28 expected test cases (previously 432; **460 expected total**), independent external full-well torque-and-drag benchmark, qualified engineer review and explicit owner-approved scope decision. Keep `LH-CALC-02` **6/7 (~86%) IN PROGRESS** and overall accepted stages **2/9 (~22%)**, no false acceptance claim.
