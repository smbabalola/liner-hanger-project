# LH-CALC-02 — minimum-curvature-consistent 3D soft-string v0.1

**Classification:** EXPERIMENTAL / RESEARCH ONLY. **New full regression NOT VERIFIED.** Current user-confirmed full skill baseline: **505 passed in 13.10s** at code commit `6e79693`. The separately committed trajectory audit introduced 25 unverified-in-full tests (530 expected). This research solver adds 37 further test cases, bringing the **expected new full collection to 567**; no Windows/CI passing result can be claimed for this batch.

## Why this is a new model, not a silent fix to the old one

The 3D solver in `torque_drag_3d.py` varies inclination and azimuth linearly in measured depth. In contrast, `directional_survey.py` uses minimum-curvature great-circle interpolation to integrate TVD. The independent geometry audit found an **8.15076067m endpoint separation and −2.98576451m TVD difference** for a fictional 100m 30°→60° build and 0°→60° turn. Neither convention is a measured path between sparse survey stations. Using one for gravity and another for survey continuity is internally inconsistent.

This module **does not replace the legacy solver or change its 505-test baseline**. It creates a separate versioned API:

- `scripts/torque_drag_3d_minimum_curvature.py` — `predict_minimum_curvature_curve(SpatialCurveInputs)`
- `scripts/run_torque_drag_3d_minimum_curvature.py` — strict sourced one-section JSON runner
- `scripts/torque_drag_spatial_profile.py` — `predict_minimum_curvature_profile(SpatialProfile)` alongside the preserved legacy `predict_spatial_profile`
- `scripts/run_torque_drag_spatial_profile_minimum_curvature.py` — strict sourced multi-interval JSON runner
- Existing synthetically labelled `examples/synthetic_torque_drag_3d.json` and `examples/synthetic_torque_drag_spatial_profile.json` are the input formats. The combined build/turn benchmark is generated within the tests.
- New tests: `tests/test_torque_drag_3d_minimum_curvature.py` (**22 cases**), `tests/test_run_torque_drag_3d_minimum_curvature.py` (**7 cases**), `tests/test_torque_drag_spatial_profile_minimum_curvature.py` (**8 cases**).

## Mathematical convention

Let `m` be measured depth increasing downward, `u=(m-m_top)/L`, `i` inclination from downward vertical, `a` azimuth clockwise from north, and `t=(sin i cos a, sin i sin a, cos i)` the downward unit tangent in north/east/down coordinates.

For two source-qualified endpoint tangents `t0,t1`, set `beta=acos(t0 dot t1)`. When `beta>0` and less than 180°:

```text
t(u) = [sin((1-u)beta) t0 + sin(u beta) t1] / sin(beta)
dt/du = beta [-cos((1-u)beta)t0 + cos(u beta)t1] / sin(beta)
dt/dm = (dt/du)/L
```

The gravity force per unit measured depth is `g=(0,0,w)`, where `w` is explicitly calculated buoyed weight N/m for an **open, flooded, pressure-balanced** source-qualified section. Its normal projection is `g_perp=g-(g dot t)t`. The **research soft-string** contact vector magnitude and mode-specific upward force equation are:

```text
n = norm[-g_perp - T(dt/dm)]        N/m
dT/ds = w * t_down + mode * mu_ax * n   N/m
mode = +1 pickup, -1 slackoff, 0 pure rotation
dM/ds = mu_rot * n * contact_radius     N m/m (rotation only)
s = L - (m-m_top)                       bottom-to-top MD coordinate
```

Signs are chosen to reproduce the previously implemented **planar signed normal reaction** `w sin(i)-T di/dm`. A sampled planar normal-side reversal or near-zero contact in a loaded curved section is rejected. This is **not a validated finite-radius contact-state or wall-transfer model**, and 3D contact-state transitions remain unresolved.

The sourced `PlannedSection.calculate()` uses the same great-circle station TVD convention; the new solver independently computes `L*(cos(i0)+cos(i1))/2 * RF`, with `RF=2 tan(beta/2)/beta`, and fails if the source-validator TVD differs beyond numerical tolerance. It reports both `minimum_curvature_delta_tvd_m` and `survey_delta_tvd_m` per section. Exact survey station MD, casing/tubular geometry, flooded/open assumption, friction sources and positive tensile state remain mandatory. Surface rig hookload is **not** output.

## Independent mathematical limiting checks added

1. **Weightless great-circle capstan:** for `w=0`, `n=T beta/L` and the exact force results are `T_top,pickup=T_bottom exp(mu_ax beta)`, `T_top,slackoff=T_bottom exp(-mu_ax beta)`. The pure-rotation axial force is `T_bottom` and friction torque is `mu_rot*T_bottom*beta*r`. Cases include straight, planar, combined inclination/azimuth and wraparound. These are mathematical references, not published field profiles.
2. **Zero axial friction:** `T_top=T_bottom + W * (cos i0+cos i1)/2 * RF`, for `W=wL`. The expectation is independently calculated from the endpoint minimum-curvature geometry in five cases, not from the new RK4 implementation.
3. **Legacy limits:** zero azimuth turn must agree with the existing signed-planar weighted solver; horizontal 90° azimuth turn must agree with the earlier linear-angle 3D model. A nonzero-weight combined build/turn deliberately **does not** agree with the old geometry convention.
4. **Refinement and invalid input:** 32/64/128 RK4 steps, invalid friction/geometry/steps, undefined survey doglegs and unreconciled section MD/TVD boundaries fail closed or produce research-only values.
5. **True 3D split:** a fictional 100m 30°→60° inclination and 0°→60° azimuth interval is split at the **great-circle tangent midpoint**, not the arithmetic midpoint of `i`/`a`. The second section receives the first section's independently calculated MC midpoint TVD. Section forces and cumulative rotation torque must match the single 100m interval. Nominal weight, friction and contact radius are identical across the two sections in this test.

## What is not independently validated

- No authentic published **nonzero-weight full 3D** benchmark has been reproduced. The previously listed SPE/IADC 163477 example is a potential external **planar** comparison but lacks a fully authenticated independent source-input crosswalk for this solver.
- Great-circle interpolation is a convention between two measurement stations, not proof of the actual as-drilled centreline, or whether the string maintains low-side contact.
- The normal-force model is an idealized **soft string**: no finite stiffness, buckling, friction calibration, localized tool joints, contact loss/transfer, pressure-end forces, combined rotation/tripping, wall clearance, liner-hanger tool forces or approved limits.
- The inter-sectional MD/TVD/heading checks use exact source labels and a 1µm purely **numerical** TVD continuity tolerance; that is **not** a real survey-measurement precision or acceptance threshold.
- All new solver outputs are explicitly `unreviewed_inputs` and have a warning. No runtime/software test result certifies field operational suitability.

**Engineering gate remains OPEN: LH-CALC-02 6/7 (~86%), overall 2/9 accepted (~22%).** Next steps: actual full skill regression, independently sourced nonzero-weight 3D well benchmark, physically reviewed contact-state and separate qualified applicability decision. Never include private Baker Hughes job documents or OEM manuals in this public repository.
