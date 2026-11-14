# LH-CALC-02 — straight-section soft-string torque-and-drag v0.1

**State:** Initial implementation committed; **new full Windows regression and CI results are not yet verified**. The only previously user-verified full suite is **273 passed at commit `15c9dec`**. A model-specific independent analytical known-answer check has been developed, but this is **not** a qualified engineer's sign-off, production whole-well model or Baker Hughes equipment clearance.

## Inputs and skill-local entrypoint

`scripts/torque_drag_straight.py` exports `StraightTorqueDragInputs`, `predict_straight_section(case)` and `friction_sensitivity(case, axial_candidates, rotational_candidates)`. It **reuses** `scripts/planned_job_section.py` and the existing minimum-curvature and buoyancy primitives; it does not create a second unverified string source of truth.

For a runnable standalone example:

```powershell
cd C:\dev\liner-hanger-project\skills\liner-hanger-rca
py scripts/run_torque_drag.py examples/synthetic_torque_drag_straight.json
```

The fixture is **entirely fictional**. JSON contains a `planned_section` identical in shape to the prior calculator, plus four `SourcedNumber` records: `axial_friction` (dimensionless unit `1`), `rotational_friction` (unit `1`), `contact_radius` (length), `bottom_tension` (force). Every value needs source ID, source location, source revision, and review status. The `bottom_tension` is an **independent tension boundary at the lower end of this one section**, not a default hookload, weight on bit, or guessed force on the hanger. Friction must be input separately for axial sliding and pure rotation; there are **no default friction coefficients**.

`run_torque_drag.py` emits JSON on stdout or `--output file.json`; errors print `unavailable:` and return exit code 2. Non-finite, missing, negative friction, unsupported curvature, non-flooded conditions, negative apparent buoyed weight, negative bottom tension and predicted compression are rejected. Outputs contain SI `_n` or `_nm` units, full source provenance, explicit assumptions, unreviewed/numeric-candidate status, and warning.

## Physics: deliberately restricted and separated movement modes

For a single straight, constant-inclination, uniform section of measured length `L` (not TVD), inclination `i` from vertical, and *open/flooded pressure-balanced* positive apparent gravity weight `W`:

- **Normal (low-side) wall contact:** `N = W sin(i)`.
- **Weight contribution along pipe axis:** `G = W cos(i)`.
- **Axial drag:** `D = μ_ax N`.
- **Section-top pickup tension, pure axial pull:** `T_PU = T_bottom + G + D`.
- **Section-top slackoff tension, pure axial lowering:** `T_SO = T_bottom + G − D`.
- **Section-top pure-rotation axial tension:** `T_ROT = T_bottom + G` (no simultaneous axial motion).
- **Pure rotation contact torque:** `M_ROT = μ_rot N R_contact`, in N·m.

These are static Coulomb friction/weight force-balance equations for a **straight section**, not the complete Johancsik dogleg/tension-contact model. Rotation torque is frictional **contact torque only**; no bit cutting, motor, bearing, mechanical tool, viscous/hydraulic or pipe torsional-transmission torque. The pure-rotation tension expression excludes axial friction **only because simultaneous axial travel is outside scope**.

The return fields `top_pickup_tension_n`, `top_slackoff_tension_n`, `top_pure_rotation_tension_n`, `off_bottom_contact_torque_nm`, `low_side_normal_force_n`, `axial_drag_force_n`, `buoyed_section_weight_n` and `bottom_boundary_tension_n` are **not** rig hookload. They omit traveling block/crown block, pipe handling, dynamics, surface friction, drilling line and other loads. These cannot be equated to axial load at a liner hanger, running tool, ball seat or packer.

**Applicability check:** exactly two sourced survey stations with identical inclination and azimuth, between 0° and 90° inclination. Any dogleg/turn is explicitly rejected. No high-angle curved interval, dogleg stress/normal tension, torsional stiffness, helical buckling, compression, washouts, eccentricity, mixed mud properties, slip-stick, simultaneous axial + rotation, or operating recommendation. A future full-profile engine must treat these separately with sourced models and benchmarks.

## Independent reference basis

The force balance is consistent with the straight inclined-section relation in Aadnøy & Andersen, *Design of oil wells using analytical friction models*, Journal of Petroleum Science and Engineering (2001), https://www.sciencedirect.com/science/article/abs/pii/S0920410501001474. For the historical distinction between friction and wall-contact force, see Johancsik, Friesen & Dawson, *Torque and Drag in Directional Wells — Prediction and Measurement* (IADC/SPE 11380), abstract at https://www.osti.gov/biblio/5571160. These support the **general model**, not any specific Baker Hughes friction factor or tool rating.

### Independent analytical known-answer example (non-OEM)

Entirely **synthetic** uniform section: 100 m MD at constant 60° inclination; open flooded steel-shaped pipe OD 0.10 m, ID 0.08 m, dry linear mass 15 kg/m; fluid density 1000 kg/m³; bottom tensile boundary 20,000 N; axial coefficient 0.20; pure-rotation coefficient 0.30; contact radius 0.05 m. Independent equilibrium calculation uses `π` and the standard 9.80665 m/s²:

| Independent expected value | Result |
| --- | ---: |
| Apparent gravity weight `W` | 11,937.2100363 N |
| Low-side normal force `N` | 10,337.9271418 N |
| Axial weight component `G` | 5,968.6050182 N |
| Pickup top tension | 28,036.1904465 N |
| Slackoff top tension | 23,901.0195898 N |
| Pure-rotation top axial tension | 25,968.6050182 N |
| Pure-rotation contact torque | 155.0689071 N·m |

Independent checks: (1) vertical straight case: low-side contact = 0, so no wall friction/rotational contact torque; (2) horizontal straight case: gravity axial component = 0; (3) `T_PU−T_SO = 2 μ_ax N`; (4) torque scales with both `μ_rot` and contact radius; (5) higher axial friction raises pickup and lowers slackoff, but does **not** alter pure-rotation axial tension; (6) friction sensitivity returns `unreviewed_inputs` even when original inputs were labelled reviewed.

This is **independent hand/analytical benchmarking within the stated assumptions**, not a published full-well field benchmark or independent PE/OEM validation.

### Regression defect and corrective test (2026-11-14)

**Observed actual Windows run:** 308 passed, one failed (15.50 s). The failure was in `test_unsupported_inclinations_fail_closed[-1]`: the test constructed `case(-1)` through `run_planned_section.from_payload`, which correctly rejected invalid survey inclination *before* the torque-and-drag layer could issue its `TorqueDragError`. The upstream survey validation is a safety boundary; no code change was made to permit invalid inclinations.

**Test-only correction:** Build a valid planned section, then use `dataclasses.replace` to insert the unsupported inclination directly at the torque-and-drag API boundary. This tests the engine's translation of upstream survey error into `TorqueDragError`. An additional test explicitly asserts that the JSON source-intake layer continues to reject an inclination of −1 with `PlannedSectionError`. Change committed as `e601a1b`; **this new version has not yet been run on the user's Windows checkout**, so the stage remains open. Expected total collection now **310 tests** (one newly added negative test), not a pass claim.

## Validation state and remaining gate

Files added:
- `scripts/torque_drag_straight.py` — limited physics + hypothetical friction sensitivities.
- `scripts/run_torque_drag.py` — standalone JSON CLI.
- `examples/synthetic_torque_drag_straight.json` — explicitly fictional unreviewed fixture.
- `tests/test_torque_drag_straight.py` — analytical/zero-friction/zero-contact/sensitivity/unsupported-domain cases.
- `tests/test_run_torque_drag.py` — fixed known-answer numbers, CLI and malformed/missing-input checks.

**Original new full-suite run observed:** **308 passed, 1 failed**, due to a test setup crossing the upstream survey intake boundary. **Test-only correction committed** with one extra source-intake negative test; expected **310 tests** in the next run, **not yet verified**. The original 273-test legacy baseline remains preserved. Run `py -m pytest -rs -q tests` after pulling the new commits. CI status is not confirmed.

**LH-CALC-02 remains IN PROGRESS:** the straight-section model is a bounded first slice only. Required for full P2 acceptance are sourced multi-section/depth propagation, dogleg/tension contact when independently benchmarked, capability/uncertainty and sensitivity envelope review, full regression, and distinctions between section loads, hookload and downhole component force. No field or OEM approval is authorized.
