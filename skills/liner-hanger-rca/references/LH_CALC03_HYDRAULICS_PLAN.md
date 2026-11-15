# LH-CALC-03 — Circulating hydraulics: implementation and acceptance plan

**Status:** IN PROGRESS — scope and engineering contract established 2026-11-15. No implementation, numerical benchmark or acceptance claimed by this document.

## Development checkpoint — 2026-11-15

## Verified software regression and annular thin-gap stability — 2026-11-15

**Verification:** The first implemented Newtonian laminar pipe/concentric-annulus CLI and primitives were confirmed by actual GitHub Actions [run 43749939250](https://github.com/smbabalola/liner-hanger-project/actions/runs/43749939250) job logs: **690 passed** on Python 3.11 and **690 passed** on Python 3.12. Subsequent small-gap numerical stability fix and three regression cases are now verified at code commit `192c9c8`, [run 43752254732](https://github.com/smbabalola/liner-hanger-project/actions/runs/43752254732): **Python 3.11 693 passed in 7.17s**, **Python 3.12 693 passed in 27.93s**, no failures (both completed with success). These are software tests and analytical limiting checks, **not** a sourced full-rig hydraulic physical benchmark or acceptance.

**Specific defect mitigated:** Direct evaluation of the exact fully developed Newtonian concentric-annulus throughput coefficient `1-x^4-(1-x^2)^2/ln(1/x)`, where `x=Ri/Ro`, loses significant digits in nearly closed clearances from subtraction of similar terms. The skill's `circulating_hydraulics.py` now evaluates `t=log1p((Ro-Ri)/Ri)`; for `t < 0.01` it uses a derived `O(t^8)` conductance series (leading term `4t^3/3`), otherwise a stable `expm1` expression. The physical model and its laminar boundary remain unchanged. Two new synthetic narrow-gap cases independently compare against the **parallel-plate thin-gap limit** `dp≈6 μ L Q/(π Ro h^3)`, and a third tests inverse gap-cubed sensitivity; these do not claim either an OEM annulus gap or real tool dimensional applicability. Changes: `scripts/circulating_hydraulics.py` commit `d9c7308`, `tests/test_circulating_hydraulics.py` commit `192c9c8`.

**Acceptance:** LH-CALC-03 still **IN PROGRESS / NOT ACCEPTED**. No hydraulic mud rheology beyond Newtonian, no source-backed turbulent/transitional law, eccentricity, running-tool/liner restrictions or full pump-to-return pressure datum, real-measured SPP benchmark or qualified reviewer sign-off. The model output is **only partial straight-section circulation friction**, `standpipe_pressure_pa=null`. LH-CALC-02 stays PARKED OPEN 6/7; overall 2/9 accepted.



**Implemented in GitHub, but NOT yet full-regression verified or physically accepted.**
- `scripts/circulating_hydraulics.py`: strict SI Newtonian fluid and pipe/concentric-annulus geometry; laminar analytical pressure drop, velocity, Reynolds and per-segment audit trail; conservative rejection above Reynolds 2000 and malformed/nonfinite inputs.
- `scripts/run_circulating_hydraulics.py`: strict JSON offline entry point and failure exit codes.
- `examples/synthetic_laminar_circuit.json`: fictional two-leg (internal flow + return annulus) demonstration.
- `tests/test_circulating_hydraulics.py` and `tests/test_run_circulating_hydraulics.py`: independent closed-form Poiseuille / concentric annulus calculations, boundary/sensitivity and fail-closed CLI tests.
- Commits: `4e11ed7`, `02e032c`, `7b1d833`, `05308b4`, `ecd9e86`.

**Validated status:** no passing Python CI job has yet been verified for this new batch. A GitHub commit-status query produced no statuses; this is NOT a passing test. Do not infer success from committed test files.

**Physical scope:** straight constant-section fully developed, fixed-wall, isothermal incompressible Newtonian laminar flow only. Calculated laminar Reynolds uses hydraulic diameter for concentric annulus as a conservative screening gate, not a qualified annular transition prediction. No Bingham/Herschel–Bulkley/power-law flow, eccentric annular geometry, turbulent regime, bit/nozzle/fitting pressure loss, surface circuit, temperature/pressure-dependent rheology, solids, rotation or actual rig comparison. Output always sets `standpipe_pressure_pa=null`. The total is explicitly **partial modeled straight-segment friction**, never a validated circulating SPP.

**Remaining stage work:** run full regression and fix faults, add sourced rheology and realistic annular/pipe transition model and losses, implement complete input-audited rig-to-return circuit including bit/restrictions and pressure datum, independently reproduce reference calculations under equivalent assumptions, then qualified engineering review. LH-CALC-03 is **IN PROGRESS, not accepted**. LH-CALC-02 remains **PARKED OPEN 6/7**.

## Outcome and scope
Create portable skill-local circulating-hydraulics calculations for an explicitly described fluid and flow circuit. Model pressure losses separately for each validated segment of a rig → drillstring/running-tool/liner → annular return path, and sum comparable contributions to estimate circulating standpipe pressure **only where all required components, boundary conditions and measurement locations are identified**.

This module does **not** infer cement-unit pressure, ball-seat differential, setting pressure, plug bump, or any downhole activation pressure from standpipe pressure. It does not certify safe operating limits or actual Baker Hughes equipment ratings.

## Phase 1: source and interface audit
1. Inspect existing skill primitives, schemas, CLI patterns, and hydraulics references; identify reusable validated computations without changing LH-CALC-02.
2. Define input requirements: fluid rheology model, density and units; flow rate; temperature assumptions; each segment length, ID/OD, concentricity assumptions, roughness if supported, restriction/connection losses where source-backed, and explicit flow direction.
3. Clearly distinguish internal circular pipe flow from annular flow, Reynolds/flow-regime definitions, and pressure conversions. Require a declared and supported rheology model (e.g. Newtonian initially); leave other models unavailable until sourced and tested.
4. Require explicit pump/return circuit completeness and pressure-measurement datum before any rig standpipe pressure comparison.

## Phase 2: implement strict, limited calculations
- Begin with a well-defined Newtonian laminar **single circular conduit** case: pressure loss ΔP = 128 μ L Q / (π D^4) in SI units, with validated dimensions, viscosity, length, density, and flow. This is an initial analytical benchmark, **not** an assertion that wellbore flow is Newtonian or laminar.
- For annulus and turbulent/non-Newtonian cases, select and cite the appropriate physical model and applicability envelope *before* implementation. Do not silently substitute a pipe formula into an annulus or imply rheology support beyond what tests demonstrate.
- Aggregate only compatible supported segment losses and report unavailable sections separately; fail closed rather than silently producing a partial SPP total.

## Phase 3: validation and acceptance
- Independent known-answer hydraulic benchmarks, including unit conversions, laminar pipe analytical law, and selected published annular/non-Newtonian cases only if input-complete.
- Boundary tests: Q=0, Q near regime transition, increasing Q, invalid/negative dimensions, impossible annular clearances, unsupported rheology, missing flow-path legs, incompatible pressure datum, and inconsistent units.
- Monotonicity/sensitivity checks and segment-by-segment audit trail; no invented pressure tolerances.
- Full skill regression on supported Python versions and engineering review of applicability.

## Acceptance criteria
The TODO.md stage requirements apply: source-supported rheology, explicit rig/liner/annulus path, segment pressure losses and defensible rig pressure comparison where valid; independent benchmarks, physical/unit/flow boundary tests and full regression. Engineering use remains restricted until independent qualified review. Keep numerical input fixtures synthetic/public and do not put proprietary Baker Hughes or operator job packages in public GitHub.

## Previous stage
LH-CALC-02 is **parked, OPEN 6/7**. Its Pro Well Plan independent source-code reconciliation is complete, but an input-equivalent comparison with our solver and engineering applicability sign-off remain open. Starting 03 does **not** accept or release 02.
