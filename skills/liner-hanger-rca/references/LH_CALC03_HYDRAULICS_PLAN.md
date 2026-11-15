# LH-CALC-03 — Circulating hydraulics: implementation and acceptance plan

**Status:** IN PROGRESS — scope and engineering contract established 2026-11-15. No implementation, numerical benchmark or acceptance claimed by this document.

## Power-law concentric-annulus research model — 2026-11-15

**Source:** Rémi Deterre et al. (2020), *The flow of power-law fluids in concentric annuli: A full analytical approximate solution*, *Journal of Non-Newtonian Fluid Mechanics* **285**, 104392, DOI **10.1016/j.jnnfm.2020.104392**, published governing momentum Eq.6, radial stress Eq.7 and zero-shear continuity formulation around Eq.13/17; https://www.sciencedirect.com/science/article/pii/S037702572030152X . The new implementation uses the published **governing equation**, but an independently programmed *numeric radial quadrature and bisection* rather than an attributed source numerical example. Do not imply the authors published our synthetic fixture or approved our solver.

**Model:** Stationary coaxial no-slip walls `Ri, Ro`, isothermal, steady, fully-developed **laminar** axial power-law flow `tau=K |du/dr|^n`. Radial momentum integration gives `|tau(r)|=(G/2)|rm²/r-r|` where `G=-dp/dz>0`, `Ri<rm<Ro`; at `rm` the shear stress is zero and axial velocity maximal. Choose `rm` so the integrated shear-rate-driven velocity rises from inner and outer walls are equal, exactly imposing no slip on **both** stationary boundaries. For that `rm`, numerically integrate the discharge coefficient via the first radial velocity moment, `Q = pi*(G/(2K))^(1/n)*{ integral_Ri^rm (rm²-r²)|rm²/r-r|^(1/n)dr + integral_rm^Ro (r²-rm²)|r-rm²/r|^(1/n)dr }`. Invert `G=2K*(Q/C)^n` and `DeltaP=G L`. `Q=0` gives no meaningful zero-shear radius and returns `None`, **not a fictional measured position**. No hydraulic-diameter pipe substitution.

**Implemented files:** `scripts/power_law_laminar_annulus.py`, `scripts/run_power_law_laminar_annulus.py` strict offline JSON CLI, `examples/synthetic_power_law_laminar_annulus.json`, `tests/test_power_law_laminar_annulus.py`, `tests/test_run_power_law_laminar_annulus.py`. A separately coded comparison at `n=1` against existing **closed-form exact Newtonian annulus** was performed at radius ratios 0.20, 0.50, 0.80; computed relative deviations **~3.75e-12, 2.29e-13, 5.38e-14** respectively. Independent law `DeltaP ∝ Q^n` and numerical Simpson refinement checks cover `n=0.4, 0.7, 1.0, 1.4`. The full GitHub regression and the latest zero-flow-undefined shear-radius guard **must be checked** before claiming hosted passes.

**Restrictions:** Radius ratio `Ri/Ro` bounded to **0.15–0.85** and power-law exponent `n` to **0.3–1.5** as provisional conservative numerical test domains, **not field/OEM applicability bands**. Fixed concentric walls; no pipe/casing movement, eccentricity, rotation, cuttings, time-dependent rheology, yield stress, temperature/pressure dependence, local restrictions, momentum entrance effect, or supported turbulence. Caller-provided laminar assertion/reference remains unverified by code; the refinement difference exposes numerical sensitivity, not physical validity. `standpipe_pressure_pa=null`, `engineering_acceptance=false`. Even a passing full suite leaves full-rig complete pressure comparison/qualified review **OPEN**.

## Power-law laminar circular-pipe model — 2026-11-15

**Source and derivation:** Brigham Young University, *Non-Newtonian Fluid Math*, Eqs. (7) and (8), https://www.et.byu.edu/~wheeler/Non-Newtonian_Fluid_Math.pdf . For an isothermal steady incompressible power-law fluid `tau=K gamma_dot^n`, `K` has units `Pa s^n` (not `Pa s` unless `n=1`), `n` is unitless, `v=4Q/(pi D^2)`; the laminar circular-pipe wall stress is `tau_w=K[(3n+1)/(4n) * 8v/D]^n`, and `DeltaP=4L tau_w/D`. This is the explicit, separately derived Metzner–Reed/Rabinowitsch relation and not a calibration to a published pressure target. The current model refuses to infer a laminar regime from a density and plastic-viscosity approximation; the caller supplies a separately established laminar-regime assertion **plus source identifier**, explicitly labelled *not authenticated* by the software. The 0.1–2 research-only exponent guard prevents extreme/poorly characterised exponents and is not an industrial validity limit.

**Implementation/contract:** `scripts/power_law_laminar_pipe.py`, `scripts/run_power_law_laminar_pipe.py` (strict offline JSON), `examples/synthetic_power_law_laminar_pipe.json`, `tests/test_power_law_laminar_pipe.py`, `tests/test_run_power_law_laminar_pipe.py`. Source-based independent equation and exact `n=1` Newtonian reduction, `DeltaP ∝ Q^n` sensitivity, zero-flow/length and malformed-evidence/invalid-geometry fail-closed tests. This calculation applies **only** to a *circular internal pipe in independently confirmed laminar flow*, not to a power-law annulus, an actual dynamically changing mud with yield stress, Herschel–Bulkley flow or turbulent/transition regime. No observed mud rheogram, pump/running-tool data or operator pressure comparison is claimed. Its outputs always include `standpipe_pressure_pa=null` and `engineering_acceptance=false`.

**New-code test status:** GitHub CI on commit `227d241` pending verification at time of authoring. Do not count tests until job logs are reviewed; stage remains LH-CALC-03 OPEN regardless of software pass.

## New source-supported research models — 2026-11-15

**Status: code, executable offline examples and tests committed; latest full GitHub regression to be verified before the cases are counted.** All files are in the portable `skills/liner-hanger-rca/` skill, not a separate application.

### 1. Bingham-plastic circular-pipe laminar flow (not annulus)

- Module `scripts/bingham_laminar_pipe.py`; runner `scripts/run_bingham_laminar_pipe.py`; fixture `examples/synthetic_bingham_laminar_pipe.json`; tests `tests/test_bingham_laminar_pipe.py` and `tests/test_run_bingham_laminar_pipe.py`.
- **Independent published source:** *Perry's Chemical Engineers' Handbook*, 7th ed., *Fluid and Particle Dynamics*, Eq. **6-59**, public educational excerpt at https://schneider.cheme.cmu.edu/Files/Perry%27s%20Chemical%20Engineers%27%20Handbook%207th%20Edition/6.%20Fluid%20and%20Particle%20Dynamics.pdf . Let `tau_w=DeltaP D/(4 L)`, `a=tau_y/tau_w`; fully developed Bingham-plastic laminar circular pipe has `Q=pi D^3 tau_w/(32 mu_plastic) * [1-4a/3+a^4/3]`. The implementation solves only the **physical tau_w>tau_y branch**, with a monotone bisection and stable factorisation `(1-a)^2 (a^2+2a+3)/3`; matches independent forward equation, zero-yield Newtonian limit and positive-yield sensitivity.
- Assumptions: SI, fixed circular flow ID, incompressible Bingham rheology with **sourced/independently measured** plastic viscosity and yield stress, steady fully developed laminar, no slip/sag, nonzero pipe section. Bingham flow regime cannot be determined merely from the Newtonian-style plastic Reynolds; requires an explicit, *externally established* laminar-regime assertion and evidence identifier; both remain **caller-declared / NOT authenticated**. No annular Bingham implementation, transition/turbulent law, actual mud profile or field approval.
- **Safety-corrected boundary:** When `Q=0` with `tau_y>0`, a static plug may sustain a **range of nonzero pressure gradients**. Pressure is therefore **indeterminate**, not zero; the code refuses to return a numeric differential in that case. Zero-length component has zero distributed friction. Runtime always returns `standpipe_pressure_pa=null`, `engineering_acceptance=false`.

### 2. Incompressible nozzle/orifice differential

- Module `scripts/circulation_restrictions.py`, tests `tests/test_circulation_restrictions.py`.
- **Independent source:** Canada Mortgage and Housing Corporation (1995), *Vents and Orifice Flow*, §2.2, archived at https://publications.gc.ca/collections/collection_2018/schl-cmhc/nh17/NH17-201-1995-eng.pdf , `Q=C_d A sqrt(2 DeltaP/rho)`. Rearranged to `DeltaP=rho Q^2/(2 C_d^2 A^2)`, used in an independently checked known-answer case. Drilling-context reference: *Applied Drilling Circulation Systems: Hydraulics, Calculations and Models*, bit nozzle kinetic pressure equation, https://ndl.ethernet.edu.et/bitstream/123456789/3543/1/Applied%20Drilling%20Circulation%20Systems%20Hydraulics%2C%20Calculations%2C.pdf .
- Requires separately **sourced and independently validated** total flow area/discharge coefficient, constant density, negligible approach velocity, single-phase incompressible steady behavior, no cavitation; input source string is **not** authorization or evidence verification. The output must never imply that a Baker Hughes tool restriction can be represented by an arbitrary jet/orifice. Returns `standpipe_pressure_pa=null`, `engineering_acceptance=false`.

### 3. Auditable partial Newtonian circulation-component budget

- Module `scripts/circulation_budget.py`, strict CLI `scripts/run_circulation_budget.py`, case `examples/synthetic_newtonian_component_budget.json`, tests `tests/test_circulation_budget.py` and `tests/test_run_circulation_budget.py`.
- An **ordered, unique** `pipe_or_annulus -> optional source-described nozzle -> annular return` sequence with both legs explicitly declared. Computes and separately records only supported Newtonian laminar segment friction and isolated nozzle differential; rejects turbulent/unsupported sections instead of returning a partial result. Independent synthetic three-component known-answer sum checks the analytical pipe, annular and nozzle terms without using the production formulas.
- `status=partial_circuit_component_budget_only`, `standpipe_pressure_pa=null`, `engineering_acceptance=false` **always**. Output `boundary_coverage` explicitly records missing pressure-transducer datum, actual complete equipment restrictions, hydrostatic balance and measured rig comparison. No real-world liner hanger model, OEM hydraulic restriction rating or validated pressure limits are supplied.

### Remaining completion requirements

- [x] Restricted Newtonian laminar pipe + concentric annulus and documented independent analytical tests (not field acceptance).
- [x] Source-based Bingham-plastic **pipe-only** laminar relation and offline contract (subject to latest CI confirmation).
- [x] Source-backed **individually declared** nozzle/orifice pressure differential and limited partial component budget (subject to latest CI confirmation).
- [ ] Source-supported **annular and transitional/turbulent non-Newtonian rheology** and confidence/temperature/regime screening.
- [ ] Authorized **complete, exact-equipment rig → running-string/liner → nozzle/restrictions → annular return** configuration with all ID/OD/lengths, material fluid state, pump path, bypass/leaks, friction/flow assumptions, pressure-transducer locations, hydrostatic and surface backpressure boundary.
- [ ] Full published/authorized **input-equivalent end-to-end hydraulic benchmark** vs an independently computed field/model result; reconcile measured SPP sensor uncertainty and operating state.
- [ ] Independently qualified hydraulics/OEM/operator engineering applicability review and explicit sign-off; no automatic acceptance by model or AI.

**LH-CALC-03 remains IN PROGRESS, NOT ACCEPTED; LH-CALC-02 parked OPEN 6/7; overall 2/9 accepted stages.** Do not substitute synthetic model values for real well design or rig operations.

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
