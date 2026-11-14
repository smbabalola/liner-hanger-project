# LH-CALC-02 — 3D trajectory/contact reconciliation work package

**Date:** 2026-11-14  
**State:** OPEN — geometry diagnostic and separate MC-consistent 3D force/profile solver implemented; new full skill regression and external physical validation pending.  
**Last user-verified regression:** 505 passed in 13.10 s at `6e79693`.

## Concrete discrepancy to investigate

The experimental spatial solver `scripts/torque_drag_3d.py` propagates an idealized tangent with linearly changing inclination and unwrapped azimuth over each two-station interval. The sourced planned-section validator independently integrates survey TVD with a minimum-curvature algorithm. Agreement at station endpoints is **not proof** that tangent direction, integrated TVD, lateral position, distributed gravity, or 3D contact force are consistent within the section. The model must remain research-only until this mismatch has been quantified and dispositioned.

## Current independently computed finding — synthetic geometry only

Implemented `scripts/trajectory_interpolation_audit.py` with `audit_two_station_trajectory(...)`; `tests/test_trajectory_interpolation_audit.py` contains **25** independent geometry/negative test cases. This module does **not** import the torque/drag force solver. It compares two trajectories over the **same two station tangents and measured-depth length**, integrating unit tangent vectors independently with composite Simpson quadrature, sampled at 0, 25, 50, 75 and 100% of the interval:

- **Linear angles:** `t(u) = (sin(i(u))cos(a(u)), sin(i(u))sin(a(u)), cos(i(u)))` where `i` and shortest-unwrapped `a` vary linearly in fraction `u=MD/L`.
- **Minimum curvature:** endpoint unit vectors `t0,t1`, dogleg `beta=acos(t0 dot t1)`, and great-circle tangent `t_mc(u) = [sin((1-u) beta)t0 + sin(u beta)t1]/sin(beta)`; degeneracy at 180-degree dogleg is rejected.
- Position `r(u)=L integral_0^u t(v) dv` in **north/east/down metres**. Calculated deltas are **between mathematical interpolation conventions**, not against an observed well path.

**Synthetic 100 m example, inclination 30°→60°, azimuth 0°→60°:**

| Comparison | Calculated difference |
|---|---:|
| End TVD, linear angles minus minimum curvature | **−2.98576451 m** |
| Euclidean end-position disagreement | **8.15076067 m** |
| Maximum of five sampled unit-tangent differences | **0.123642**, dimensionless |

The two interpolations agree to numerical accuracy in the straight, constant-heading planar build/drop, and horizontal 90°-inclination azimuthal-turn special cases. **They do not generally agree for combined build+turn, nor for all lower-inclination pure azimuth turns.** Their endpoint tangents coincide by construction, but the integrated endpoint position may not. Therefore earlier 3D force tests do not validate the consistency of full 3D survey geometry; the force solver is **unchanged**, uncalibrated and research-only.

**Actual local isolated check:** `python -m pytest -q test_trajectory_interpolation_audit.py` in a scratch test directory with the pure geometry module: **25 passed in 0.12 s**. The new two files were then committed in the skill. This **is not the full repository Windows regression**; after +25 new cases, **530 tests expected**, not verified. GitHub's available commit-status and PR-workflow-run queries returned no runs/statuses, so no CI pass is claimed.

**Engineering decision:** Quantification is a completed research subtask, **not reconciliation**. Do not convert any model result to hookload, liner-hanger setting forces, inferred clearance or an OEM limit. No arbitrary acceptable positional error threshold has been invented.

## Next executable engineering slice

1. Inspect `directional_survey.py`, `planned_job_section.py`, `torque_drag_3d.py`, and `torque_drag_spatial_profile.py` before changing formulas.
2. Implement a *separate*, pure independent trajectory reference that integrates the unit tangent vector over measured depth with high-accuracy quadrature, and explicitly compares its path against minimum-curvature station interpolation. Do not reuse the production torque-and-drag integrator to generate expected values. Preserve inclination-from-vertical and azimuth conventions and units.
3. Test exact straight vertical, straight inclined, planar build/drop, constant-inclination azimuth turn, and combined build-and-turn cases. Include azimuth wraparound, near-vertical heading degeneracy, station-splitting invariance, and unsupported 180-degree dogleg. Record the independent reference method, numeric tolerances and convergence/refinement evidence.
4. For each fictional sourced survey, report MD, integrated TVD, horizontal displacement, endpoint tangent mismatch and maximum/intermediate deviation between the two interpolation conventions. **Never silently report minimum-curvature station TVD as the linearly interpolated RK4 path TVD.**
5. Where the geometry models disagree materially, fail closed or explicitly select/document one consistent trajectory convention throughout survey validation and gravity/contact integration; do not silently force agreement at endpoints.
6. Independently check signs of the two normal-reaction components and the limiting case where contact approaches zero. Keep unmodelled contact loss, side transfer, stiffness, buckling and compression unsupported unless validated.
7. Run focused negative and limiting tests, then the full skill test suite after code changes. Record actual outputs and any failures; compare a separate published/qualified **nonzero-weight 3D directional-well benchmark** when available. A synthetic self-check is not a field benchmark.

## Versioned physics follow-up — minimum-curvature force model committed (not full-regression verified)

A **separate** `predict_minimum_curvature_curve` algorithm and `predict_minimum_curvature_profile` wrapper now use great-circle tangent and its derivative for both buoyed-gravity projection and weighted soft-string contact reaction. The original linear-angle solver is retained, with its existing 505-test verified baseline unchanged. The new solver also verifies that its independently integrated minimum-curvature section TVD matches the sourced survey's minimum-curvature TVD, with an explicit source/units/status audit.

- Single and multi-interval strict JSON CLIs are available entirely inside `skills/liner-hanger-rca/scripts/`.
- Three test modules add **38** expected cases: exact weightless great-circle capstan, zero-friction gravity/TVD integral, old planar/horizontal limits, **nonzero-weight independent DOP853** numerical comparison, true great-circle tangent/MC-TVD split invariance, invalid sources and contact-side rejection.
- The independent DOP853 mathematical example for a fictional nonzero-weight combined build-and-turn gives pickup **32,312.01781392N**, slackoff **25,564.33537199N**, pure-rotation axial **28,701.20754776N** and rotation wall-contact torque **252.07886152N·m**. See `LH_CALC02_MINIMUM_CURVATURE_3D_MODEL.md` for the precise input contract, ODE, independent integration settings and distinctions from field validation.
- **New code not yet user-run verified.** Alongside the previous 25 independent geometry tests, **568 full-suite cases are expected** against the last user-confirmed 505; no GitHub CI run/pass has been verified.
- **Still blocked:** independent actual 3D weighted well benchmark, physical contact/wall-transfer model, stiffness/buckling applicability, and human/OEM engineering review. No accepted-stage percentage changes. The new outputs explicitly remain `unreviewed_inputs`, not rig hookload or liner-hanger operational limits.

## External benchmark candidate found — not reproduced or accepted

Mitchell, Bjørset and Grindhaug (2013), *Drillstring Analysis With a Discrete Torque/Drag Model*, **SPE/IADC 163477** (DOI `10.2118/163477-MS`), provides a publicly described **idealized build-and-hold** example based loosely on a Johancsik well. Reported inputs include a **2,400 ft KOP**, **5°/100ft** build to **44°**, a mixed drillstring (372ft drill collar at 100lbf/ft, 840ft heavy-weight pipe at 50lbf/ft, 10,988ft drillpipe at 19.5lbf/ft) and **9.8 lbm/gal** drilling fluid. Its **zero-friction** comparison reports **193,395lbf by hand**, **193,396lbf conventional model** and **193,397lbf discrete model** surface-load values. Sources: [paper metadata and mathematical example](https://www.researchgate.net/publication/266670783_Drillstring_Analysis_With_a_Discrete_TorqueDrag_Model) and [publicly visible result excerpt](https://www.scribd.com/document/738026090/Drillstring-Analysis-with-Discrete-Torque-Drag-Model). **Do not copy the proprietary paper/PDF into public Git**.

This is a **credible external reference candidate**, not a model validation result. It is **planar rather than a nontrivial 3D combined build-and-turn**, gives a **surface** value rather than a single-section downhole force, and its publication excerpt does not give the complete sourced inner/outer dimensions, section-to-survey matching, boundary conditions or all buoyancy inputs required to reconstruct exactly the reported example within the skill. Do **not** assume a missing pipe ID, fluid-displacement convention or boundary tension to force a match. A full data crosswalk and independent numerical reproduction are required before any benchmark checkbox can be accepted.

## Acceptance evidence still missing

- A source-qualified **nonzero-weight force-profile** comparison using a geometrically consistent trajectory (the fictional geometry-only comparison above does not meet this).
- Independent reference solution with traceable source, units, parameters, tolerances and difference table for pickup, slackoff and rotational torque.
- Qualified engineering judgement of soft-string validity, wall contact and handling of unsupported states.
- OEM/operational limits for any specific liner-hanger configuration, if ever used for actual operations.

**Gate decision:** LH-CALC-02 stays **6/7 (~86%) IN PROGRESS**; accepted programme **2/9 (~22%)**. The 505 test result verifies existing software only. Do not mark the gate complete from this protocol or make field recommendations.

**Confidentiality:** Use fictional or explicitly licensed datasets only in public GitHub; do not upload Baker Hughes manuals, KHRM job records or proprietary calculations.
