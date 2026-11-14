# LH-CALC-02 — weighted planar curvature, research model v0.1

**State (2026-11-14):** User independently verified the new code on Windows after pulling through commit `c6e44b3`: **410 tests passed in 17.08 s, zero failures**, including the weighted-curvature tests and prior suite. GitHub Actions run status remains unverified. Model is **NOT** a validated directional-well, rig hookload, hanger setting-load, OEM, or field-operational model.

## Implemented scope

`scripts/torque_drag_weighted_curve.py` models **one uniform planar curved interval** between **two actual sourced survey stations**: constant bore/pipe dimensions, flooded/pressure-balanced constant-density fluid, constant pipe mass and friction coefficients, inclination changing **linearly with measured depth**, **fixed azimuth**, and downward inclination 0°–90°. It deliberately does **not** support azimuth turns/3D curvature, multi-section propagation, interpolated/inferred survey stations, friction/casing changes inside the interval, compression/buckling, partial wall contact or unsupported OEM loads. The first-station TVD and exact survey MD endpoints come from the previously regressed `PlannedSection` contract. Source labels are mandatory but are not documentary authenticity checks.

A single sourced bottom tensile boundary is used for *three separate* assumed states: pure pickup (axial friction opposes upward movement), pure slack-off (opposite friction sign), and pure rotation with no axial sliding (axial friction omitted, rotation contact torque included). **Never mix these three states**.

## Mathematical model and signs

Let `s` be arc length **upward** from the deeper end of a planar section, `L` section MD length in metres, `i_b` deepest inclination (radians from vertical), `i_t` shallowest inclination, and `k=(i_b-i_t)/L` signed curvature per metre (positive = build down MD, negative = drop down MD). Then `i(s)=i_b−k s`.

Let `w` be positive distributed *buoyed* gravity force per metre, from the same flooded-pipe material-volume approximation as `LH-CALC-01`, and `T(s)` be positive tensile force. A two-dimensional, perfectly flexible string's tangent-normal force balance gives:

- Distributed contact reaction magnitude `n(s) = abs(w sin(i(s)) − k T(s))` **N/m**. The signed curvature contribution can reinforce or oppose the gravity normal; **do not simply add absolute curvature and gravity loads**.
- Axial pickup: `dT/ds = w cos(i(s)) + mu_ax n(s)`.
- Axial slack-off: `dT/ds = w cos(i(s)) − mu_ax n(s)`.
- Pure rotation axial tension: `dT/ds = w cos(i(s))`.
- Pure-rotation contact torque rate: `dM/ds = mu_rot n(s) r`.

Fourth-order Runge–Kutta solves the three positive-tension states separately with **explicit caller-specified integration_steps** (8–20000). At any intermediate step that implies negative tension, the model rejects compression/buckling rather than extrapolating. The axial `T` and normal/contact fields are recomputed separately for each movement mode; pure rotation torque uses its own tension state. This is a **single tangent-normal planar-contact approximation**, not a full high-angle stiff-string or quantitative drag analysis of an actual well.

## Independent benchmarks and convergence requirements

**Limiting reference A — straight section:** `k=0`, constant `i`. The equations integrate exactly to `Tpu=Tbottom+w L cos(i)+mu_ax*w L sin(i)`, `Tso=Tbottom+w L cos(i)−mu_ax*w L sin(i)`, `Trot=Tbottom+w L cos(i)`, `Mrot=mu_rot*w L sin(i)*r`. Cross-check against *independently already verified* `scripts/torque_drag_straight.py` for 0°, 30°, 60°, 90°.

**Limiting reference B — zero distributed weight:** choose a purely mathematical synthetic density/mass balance giving `w=0`. Then `n=abs(k)T`; `Tpu=Tbottom exp(mu_ax * abs(k)*L)`, `Tso=Tbottom exp(-mu_ax*abs(k)*L)`, `Trot=Tbottom`; `Mrot=mu_rot*Tbottom*abs(k)*L*r`. Compare directly against the **exact, separately implemented capstan benchmark** `scripts/torque_drag_bend.py`.

**Limiting reference C — zero axial friction but nonzero buoyed gravity:** `mu_ax=0`. For `k ≠ 0`, independently integrate `dT/ds=w cos(i_b−ks)` to obtain `Ttop=Tbottom + w [sin(i_b)−sin(i_t)]/k`; this must match all three tensile states.

**Convergence benchmark (fictional 100 m build from 0° to 60°):** for a 0.1 m OD, 0.08 m ID uniform open/flooded pipe, dry mass 15 kg/m, fluid 1000 kg/m³, deepest tension 20 kN, `mu_ax=0.2`, `mu_rot=0.3`, `r=0.05m`, numerical RK4 at 256 intervals gives approximately: pickup **34,214.052 N**, slack-off **26,217.838 N**, pure-rotation axial **29,871.993 N**, contact torque **298.240 N·m**. These reference values are *independently recomputed from the explicit ODE by a separate JavaScript RK4 arithmetic check*, not original engineer or OEM job outputs. Check 64, 128 and 256 subdivisions for convergence, and compare 256 against 512 when verifying tolerances. A future full solver must additionally compare against a published engineering benchmark or approved engineering calculations and test contact-wall side transitions and discretization sensitivity in realistic surveys.

## Extended engineering review — published formulation and exact nonzero-weight benchmark (2026-11-14)

**Literature cross-check, not field calibration:** Johancsik, Friesen & Dawson, *Torque and Drag in Directional Wells—Prediction and Measurement*, SPE 11380 (1984), https://doi.org/10.2118/11380-PA, establishes a friction-times-wall-normal-load soft-string framework. Public engineering derivations explicitly distinguish **build** wall reaction (buoyed low-side gravity opposed by tensile curvature) from **drop** reaction (reinforcement). See https://core.ac.uk/download/pdf/147134737.pdf (build/drop force diagrams and normal-force balance), and https://www.sciencedirect.com/science/article/abs/pii/S0920410501001474 (Aadnøy & Andersen's analytical soft-string framework). We have **not** independently replicated their field data, full three-dimensional survey, friction calibration or complete published numerical job results.

**A stronger independent exact benchmark is now added** in `tests/test_weighted_curve_independent_benchmarks.py`. Within a single planar section where the **signed wall-contact side remains unchanged**, define `σ = sign(w sin(i) − kT)`, and `b = mode * μ_ax * σ`, where mode is +1 pickup, −1 slack-off, 0 pure rotation. Then `T'(s) + bk T(s) = w [cos(i(s)) + b sin(i(s))]`. A closed-form integrating-factor solution exists, independent of the production RK4 integrator:

```text
k=(i_bottom-i_top)/L   (nonzero)
A=w*(b*b-1)/(k*(1+b*b))
B=2*w*b/(k*(1+b*b))
P(i)=A*sin(i)+B*cos(i)
T_top=exp(-b*k*L)*T_bottom + P(i_top) - exp(-b*k*L)*P(i_bottom)
```

This reproduces **both weighted build and drop** reference solutions for all three movement modes (mathematically stronger than simply matching the pre-existing straight and weightless limiting models):

| Fictional 100 m planar section (20,000 N bottom) | Pickup top N | Slack-off top N | Pure-rotation top N |
|---|---:|---:|---:|
| 0°→60° build, μ_ax 0.2 | 34,214.05213166 | 26,217.83775350 | 29,871.99323562 |
| 60°→0° drop, μ_ax 0.2 | 36,985.98340222 | 23,969.69422630 | 29,871.99323562 |

The **analytic reference assumes invariant contact side**: for this fictional build `σ=−1`, drop `σ=+1`. It is an independent mathematical benchmark **derived from the declared model**, not an external well dataset or independent engineering certification.

**Contact-side behaviour:** Previously the `abs(w sin i − kT)` contact law silently permitted sign changes. That may involve changing wall side, contact loss/transfer or other mechanics unsupported by the simple continuous-contact assumptions. The solver now checks the signed reaction at every RK4 step and midpoint, reports `signed_contact_side` per movement mode (`−1`, `0`, `+1`), and **fails closed with `TorqueDragError`** on detected side transitions rather than presenting an unconstrained candidate number. A low-tension 0°→60° synthetic case explicitly tests this rejection. The sample-based guard is not a proof of physical wall contact or a replacement for stiff-string modelling.

**Numerical refinement diagnostics:** `scripts/weighted_curve_audit.py` exposes `compare_refinement(inputs, step_counts=(64,128,256))` to report **absolute differences** for all three tensile modes, their integrated contact reactions, and pure-rotation friction torque across successive RK4 resolutions. It performs no automatic pass/fail on engineering accuracy, no OEM limit check and no numerical self-certification. Real-world convergence must still be assessed with model applicability and evidence quality.

**Current acceptance boundary:** The signed planar contact equation and separately derived exact constant-side mathematical solution are reviewed, but independent professional sign-off, third-party field/profile benchmark, 3D azimuthal wall contact, joined weighted curves, pressure-end forces and operating constraints remain **OUTSTANDING**. `LH-CALC-02` remains **6/7 (~86%), overall 2/9 (~22%)** until an explicit acceptance decision on the remaining work.

## API, input contract and limitations

- `scripts/torque_drag_weighted_curve.py` — `WeightedCurveInputs(section, axial_friction, rotational_friction, contact_radius, bottom_tension, integration_steps)` and `predict_weighted_curve(inputs)`.
- `scripts/run_torque_drag_weighted_curve.py` — strict JSON CLI accepting `planned_section`, the four source-number inputs and an integer `integration_steps`.
- `examples/synthetic_torque_drag_weighted_curve.json` — entirely fictional 100m 0→60° planar build fixture.
- `tests/test_torque_drag_weighted_curve.py` — limiting exact benchmarks, step-size convergence, build/drop contact, sensitivity and negative-domain checks.
- `tests/test_run_torque_drag_weighted_curve.py` — CLI/schema and error cases.

```powershell
cd C:\dev\liner-hanger-project\skills\liner-hanger-rca
py scripts/run_torque_drag_weighted_curve.py examples/synthetic_torque_drag_weighted_curve.json
```

The outputs include **separate** pickup/slackoff/pure-rotation `top_tension_n` and mode-dependent `integrated_wall_contact_n`, pure-rotation `contact_torque_nm`, and raw input source-register metadata. These are **one section's shallow-end forces**, NOT rig hookload or verified load at a downhole component. No user is licensed to apply them as a safe operating load/pressure.

**Full Windows software-regression gate PASSED:** **410 passed in 17.08 s** at `c6e44b3`. **Engineering gate remains OPEN:** independent third-party weighted-curvature reference beyond limiting cases, physical applicability review including signed curvature/wall contact, source review and separation of the one-section solver from the multi-section legacy profile. Maintain `LH-CALC-02 6/7 (~86%)`, overall 2/9 (~22%) until those gates are explicitly accepted; no false-field certification.
