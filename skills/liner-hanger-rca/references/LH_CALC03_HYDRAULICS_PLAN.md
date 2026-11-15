# LH-CALC-03 — Circulating hydraulics: implementation and acceptance plan

**Status:** IN PROGRESS — scope and engineering contract established 2026-11-15. No implementation, numerical benchmark or acceptance claimed by this document.

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
