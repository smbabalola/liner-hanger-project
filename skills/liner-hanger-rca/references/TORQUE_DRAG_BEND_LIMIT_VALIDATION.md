# LH-CALC-02 — weightless curved-contact analytical benchmark

**Status:** Implemented as a *separate, exact limiting case*, **not** a weighted directional-well solver. New tests and the full Windows regression are **not yet confirmed**. Prior user-confirmed suite: **334 passed in 12.85 s** on `a7e1822`.

## Physical derivation and engineering validity

For an ideal perfectly flexible, continuously contacting string around a fixed bend with **zero distributed weight**, let the positive tensile load at the bottom of the bend be `T0`, the positive total turn angle be `theta` in radians, and independent Coulomb friction factors be `mu_ax` for pure axial motion and `mu_rot` for pure rotation. An infinitesimal change of direction produces contact reaction `dN = T d(theta)`. For axial pickup, `dT = mu_ax dN`, giving `Ttop_pickup = T0 exp(mu_ax theta)`. For slackoff the direction is reversed: `Ttop_slackoff = T0 exp(-mu_ax theta)`. **These are exact capstan limiting-case equations**, not an accepted downhole force prediction for a weighted or stiff drillstring.

Integrated normal reactions depend on movement mode:

- Pickup: `N_pickup = T0 (exp(mu_ax theta)-1)/mu_ax`.
- Slackoff: `N_slackoff = T0 (1-exp(-mu_ax theta))/mu_ax`.
- Pure rotation, no axial travel: `N_rot = T0 theta`, axial tension stays `T0`, contact torque `M_rot = mu_rot T0 theta r`.
- When `mu_ax=0`, both sliding normal expressions use the continuous limit `T0 theta`.

The endpoint `theta=0` returns identity tension/zero contact; 180° is accepted as a mathematical domain boundary. Values greater than 180°, negative coefficients, missing source references, zero/compressive bottom tension or absent explicit `zero_distributed_weight=true` are rejected. Very large exponential arguments are rejected to avoid meaningless numerical overflow.

**Source contract:** Every numerical input uses the `SourcedNumber` record with explicit unit, source ID/location/revision and review status. The unitless coefficient uses `1`; angle supports `deg` or `rad`; force supports `N`, `kN`, `lbf`; contact radius supports length units. `reviewed` is caller-provided metadata and **never proves OEM approval**.

## Independent known-answer check (fictional only)

For `T0=10000 N`, `theta=90°=pi/2`, `mu_ax=0.2`, `mu_rot=0.3`, and `r=0.05 m`, independently calculate `x=0.2 pi/2`, then compare:

| Expected calculation | Independent reference expression |
|---|---|
| Pickup tension | `10000 exp(x)` N |
| Slackoff tension | `10000 exp(-x)` N |
| Pure-rotation axial tension | `10000` N |
| Pickup normal reaction | `10000(exp(x)-1)/0.2` N |
| Slackoff normal reaction | `10000(1-exp(-x))/0.2` N |
| Pure-rotation contact normal | `10000 pi/2` N |
| Pure-rotation frictional contact torque | `0.3*10000*(pi/2)*0.05` N m |

Independent invariants: `Tpickup * Tslackoff=T0²` for equal coefficients and a weightless bend, and pure-rotation contact torque is independent of axial friction. These are the classic analytical capstan equilibrium and limiting behavior, **not self-derived production wellbore reference data**.

## Skill module and executable example

- `scripts/torque_drag_bend.py`: `IdealBendInputs`, `predict_ideal_bend`.
- `scripts/run_torque_drag_bend.py`: JSON CLI and `run_payload` for strict source-bound inputs.
- `examples/synthetic_torque_drag_bend.json`: fictional unreviewed 90-degree weightless case.
- `tests/test_torque_drag_bend.py`: exact analytical values, continuity/reciprocity, zero limits, positive-only tension, unit equivalence, negative cases.
- `tests/test_run_torque_drag_bend.py`: CLI and invalid-source-schema cases.

```powershell
cd C:\dev\liner-hanger-project\skills\liner-hanger-rca
py scripts/run_torque_drag_bend.py examples/synthetic_torque_drag_bend.json
```

**Critical limitation:** The actual running string has distributed buoyed weight, inclination/azimuth variation, local dogleg radius, contact pressure, torsional stiffness, tool-joints and perhaps frictional contact loss. **DO NOT add the weightless capstan results to the earlier weighted co-linear straight-profile engine to claim a full curved-well solution.** A real directional-well solver must integrate `T` and the vector wall reaction with both gravity and curvature; those equations, combined axial/rotation states, discretization convergence, signed dogleg geometry and model applicability still need separate benchmarks and engineering review.

**New regression gate:** 25 new analytical/negative tests and eight CLI tests **expected**, making **367 total** when collected with the 334 user-verified baseline. This is an estimate, **not evidence of passing tests**. Professional, source-specific and OEM field validation are still unavailable. `LH-CALC-02` stays open at 6/7 (~86%) until the weighted-curvature model and final review are accepted.
