# LH-CALC-02 — 3D trajectory/contact reconciliation work package

**Date:** 2026-11-14  
**State:** OPEN — engineering validation protocol recorded; not implemented or passed as a new test batch.  
**Last user-verified regression:** 505 passed in 13.10 s at `6e79693`.

## Concrete discrepancy to investigate

The experimental spatial solver `scripts/torque_drag_3d.py` propagates an idealized tangent with linearly changing inclination and unwrapped azimuth over each two-station interval. The sourced planned-section validator independently integrates survey TVD with a minimum-curvature algorithm. Agreement at station endpoints is **not proof** that tangent direction, integrated TVD, lateral position, distributed gravity, or 3D contact force are consistent within the section. The model must remain research-only until this mismatch has been quantified and dispositioned.

## Next executable engineering slice

1. Inspect `directional_survey.py`, `planned_job_section.py`, `torque_drag_3d.py`, and `torque_drag_spatial_profile.py` before changing formulas.
2. Implement a *separate*, pure independent trajectory reference that integrates the unit tangent vector over measured depth with high-accuracy quadrature, and explicitly compares its path against minimum-curvature station interpolation. Do not reuse the production torque-and-drag integrator to generate expected values. Preserve inclination-from-vertical and azimuth conventions and units.
3. Test exact straight vertical, straight inclined, planar build/drop, constant-inclination azimuth turn, and combined build-and-turn cases. Include azimuth wraparound, near-vertical heading degeneracy, station-splitting invariance, and unsupported 180-degree dogleg. Record the independent reference method, numeric tolerances and convergence/refinement evidence.
4. For each fictional sourced survey, report MD, integrated TVD, horizontal displacement, endpoint tangent mismatch and maximum/intermediate deviation between the two interpolation conventions. **Never silently report minimum-curvature station TVD as the linearly interpolated RK4 path TVD.**
5. Where the geometry models disagree materially, fail closed or explicitly select/document one consistent trajectory convention throughout survey validation and gravity/contact integration; do not silently force agreement at endpoints.
6. Independently check signs of the two normal-reaction components and the limiting case where contact approaches zero. Keep unmodelled contact loss, side transfer, stiffness, buckling and compression unsupported unless validated.
7. Run focused negative and limiting tests, then the full skill test suite after code changes. Record actual outputs and any failures; compare a separate published/qualified **nonzero-weight 3D directional-well benchmark** when available. A synthetic self-check is not a field benchmark.

## Acceptance evidence still missing

- Quantified interpolation-consistency results for a nontrivial weighted combined-build/turn well profile.
- Independent reference solution with traceable source, units, parameters, tolerances and difference table for pickup, slackoff and rotational torque.
- Qualified engineering judgement of soft-string validity, wall contact and handling of unsupported states.
- OEM/operational limits for any specific liner-hanger configuration, if ever used for actual operations.

**Gate decision:** LH-CALC-02 stays **6/7 (~86%) IN PROGRESS**; accepted programme **2/9 (~22%)**. The 505 test result verifies existing software only. Do not mark the gate complete from this protocol or make field recommendations.

**Confidentiality:** Use fictional or explicitly licensed datasets only in public GitHub; do not upload Baker Hughes manuals, KHRM job records or proprietary calculations.
