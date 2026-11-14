# LH-CALC-02 — experimental 3D inclined/azimuthal soft-string (v0.1)

**New batch committed 2026-11-14. NEW REGRESSION PENDING.** Prior user-confirmed software baseline: **460 passed in 14.44 s** at `7f7e741`. This is a strictly bounded research implementation, **NOT a validated field directional-well calculator or OEM/liner-hanger operating model**.

## Physics and sourced research

For a single two-station interval, assumed inclination and unwrapped azimuth each vary linearly with measured depth `m`. Denote:

- `i` inclination from down vertical, `a` azimuth; `ki = di/dm`, `ka = da/dm`, both signed in radians/metre
- `T` positive tensile force, `w` distributed buoyed weight N/m, source-labelled Coulomb `mu_ax` and `mu_rot`
- `s` distance from bottom to top, `i(s)=i_bottom-ki*s`

The **Johancsik-type** 3D soft-string contact magnitude per length in the current signed-planar convention is:

```text
n(s) = hypot(w*sin(i(s)) - T(s)*ki,
             T(s)*sin(i(s))*ka)     [N/m]
dT/ds = w*cos(i(s)) + mode*mu_ax*n(s)
mode = +1 pickup, -1 slackoff, 0 rotation
dM_rotation/ds = mu_rot*n(s)*contact_radius
```

It resolves build/drop normal and horizontal azimuthal normal components orthogonally and **reduces exactly to the previous signed planar solver when azimuth does not change**. The published normal-force formulations vary in inclination-difference and tension-endpoint sign convention: force/dogleg sign must be checked against actual survey orientation and engineering references, not inferred from a scalar expression alone.

Research starting points:
- Johancsik, Friesen, Dawson (1984), *Torque and Drag in Directional Wells—Prediction and Measurement*, SPE 11380. https://doi.org/10.2118/11380-PA
- Example 3D discrete soft-string expression with distinct azimuth/inclination components: https://www.mdpi.com/2076-3417/13/20/11396
- Delft thesis describing contact/tension/torsion discretisation and assumptions: https://repository.tudelft.nl/file/File_c5ba4514-0fe1-422f-ab84-4a265ed9c184?preview=1

These sources support **a family of soft-string contact equations**; **no published measured field example has been independently reproduced**, and a graduate thesis is not an OEM certificate.

## Independent analytical limiting cases

1. **Planar equivalence:** `ka=0` dispatches to the earlier already-tested weighted planar RK4 solver. Its explicit contact-side transition guard remains in force.
2. **Horizontal pure azimuth turn with zero buoyed distributed weight:** `i=90°`, `w=0`, `ki=0`, `ka=Δa/L`. Then `n=T|ka|` and exact `Ttop_pu=Tbottom exp(mu_ax |Δa|)`, `Ttop_so=Tbottom exp(-mu_ax |Δa|)`, `Ttop_rot=Tbottom`, `Mrot=mu_rot*Tbottom*|Δa|*r`. Independent capstan reference for 15°, 45°, 60° and 90° turns.
3. **Inclined pure azimuth turn with zero buoyed weight:** with constant inclination `i`, `n=T sin(i)|ka|`; the exact sliding exponents become `mu_ax sin(i)|Δa|`.
4. **Symmetry:** reversing the sign of an azimuth change preserves the scalar contact/tension magnitudes for the uniform same-inclination example. Azimuth wrap 350°→10° correctly takes the shortest +20° turn.
5. **RK4 discretization:** 32→64→128 subdivisions for a fictional positive-weight azimuthal turn; numerical refinement is not validation of the physical assumptions.
6. **Continuous 3D profile split invariance:** fictional horizontal 0°→60° azimuth turn across 100 m, split into two 50 m segments 0°→30° and 30°→60°. Distinct pickup/slackoff/rotating tensile boundaries propagate upward and total rotating contact torque equals both segments' sum. When distributed weight is zero, exact horizontal capstan exponent applies to whole profile.

## Implementation

- `scripts/torque_drag_3d.py`: `SpatialCurveInputs` and `predict_spatial_curve`; one homogeneous 3D angular-gradient segment, source input checks and independent three-mode RK4.
- `scripts/run_torque_drag_3d.py`: strict offline JSON single-segment CLI.
- `scripts/torque_drag_spatial_profile.py`: `SpatialProfileInterval`, `SpatialProfile`, `predict_spatial_profile`; propagate three independently derived tensile mode boundaries bottom-up.
- `scripts/run_torque_drag_spatial_profile.py`: strict JSON multi-interval CLI.
- `examples/synthetic_torque_drag_3d.json`, `examples/synthetic_torque_drag_spatial_profile.json`: fictional 90° inclined horizontal turning intervals, **not KHRM or real operating records**.
- `tests/test_torque_drag_3d.py` and `tests/test_torque_drag_spatial_profile.py`: separate independent analytic limits, symmetry, split invariance, survey continuity, negative and CLI cases.

```powershell
cd C:\dev\liner-hanger-project\skills\liner-hanger-rca
py scripts/run_torque_drag_3d.py examples/synthetic_torque_drag_3d.json
py scripts/run_torque_drag_spatial_profile.py examples/synthetic_torque_drag_spatial_profile.json
```

## Explicit exclusions and open engineering acceptance

- These are **not actual 3D measured wellbore mechanics**. The survey is represented by exactly two stations per interval with **constant angular gradients in the chosen angle parametrization**, not minimum-curvature interpolation at each RK4 step. Station TVD boundary checks use the separately existing minimum-curvature survey procedure and do not prove agreement between these distinct interpolation models.
- No fully sourced published real-well torque/drag dataset has been independently recreated. No field friction calibration, 3D wall-side contact transfer/finite stiffness, buckling, compression, tooljoint geometry, pressure effects, combined axial+rotation, bit/liner-hanger forces, or operating bounds.
- 3D contact-side changes where the two signed normal components pass through near-zero **are not yet resolved with a physically constrained contact-loss state model**. The 3D solver must not be used for field applications; the planar reduction inherits the previously implemented sampled sign-change fail-closed guard.
- Azimuth turn beyond ±90° in one interval and exactly 180° direction ambiguity are rejected; inclination only 0°–90°; each point must retain source ID/location/revision; intermediate mode-derived loads unreviewed and not field measurements.
- No automatic postprocessing can label the 3D loads as rig hookload or liner-hanger setting loads. They describe candidate section-top axial tensions and rotation contact torque **only within the stated assumed model**.

**LH-CALC-02 remains 6/7 (~86%), overall 2/9 (~22%).** To accept the last engineering checkpoint, independently verify a substantial published or approved 3D weighted well profile, reconcile trajectory interpolation/physical sign/contact state and complete qualified human applicability review. The new regression has not yet been run by the user; do not update the verified 460 passing baseline until it is.
