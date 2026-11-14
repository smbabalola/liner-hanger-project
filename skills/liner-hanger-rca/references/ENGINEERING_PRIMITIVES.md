# LH-CALC-01 — Elementary geometry and constant-density statics (first vertical slice)

**Status:** Elementary primitives passed Windows regression (248/248, 2026-11-14). Source-identified single-section bridge added **after** that verification; its 15 new tests and full-suite regression are **pending**. **LH-CALC-01 is not yet accepted**: end-to-end source bridge regression and independent engineering applicability review remain. A **minimum-curvature trajectory integrator is implemented and locally focused-tested**; it has not been verified against a real KHRM survey.

## Scope and callable API (inside this skill)

Module: `scripts/engineering_primitives.py`. Import in an offline application via Python. Functions require explicit units and return a `Decimal` SI quantity; they do not accept unsourced guesses as implied job data.

| Function | Inputs | Return | Model scope |
| --- | --- | --- | --- |
| `tubular_capacity(inside_diameter, diameter_unit, length, length_unit)` | supported diameter and length units `m, mm, in, ft` | internal volume **m³** | uniform unobstructed straight pipe, not total fluid system |
| `annular_capacity(bore_diameter, pipe_outer_diameter, diameter_unit, length, length_unit)` | positive bore and pipe diameters, bore larger than pipe | concentric annular volume **m³** | no coupling, washout, eccentricity or displacement effects |
| `hydrostatic_pressure_difference(fluid_density, density_unit, delta_tvd, depth_unit)` | `kg/m3, g/cm3, ppg` and **signed true vertical depth difference** | signed static pressure **Pa** | constant fluid density; not rig SPP/seat differential/ECD/absolute pressure |
| `flooded_pipe_apparent_weight(outer_diameter, inner_diameter, diameter_unit, dry_linear_mass, linear_mass_unit, fluid_density, density_unit, length, length_unit)` | metal OD, ID, dry linear mass `kg/m` or `lbm/ft`, fluid density, length | segment apparent gravitational weight **N** (positive downward) | FULLY FLOODED, OPEN, uniform wall, same internal/external fluid density, pressure-balanced; no pressure-end forces or tool internals, **not hookload** |

Inputs must have caller-owned original source ID/revision/cell/page and case-specific applicability. These elementary functions **do not confer source authentication**: planned-job apps must validate source records through the skill's `equipment_specs.py` and `engineering_baseline.py` interfaces before comparing a result with a job value.

### Minimum-curvature directional survey

Module: `scripts/directional_survey.py`. `integrate_minimum_curvature(stations=[SurveyStation(...)], depth_unit="m"|"ft", start_tvd=..., start_tvd_unit="m"|"ft", datum=...)` returns `TVDStation` records with MD and TVD in metres, source-defined inclination and azimuth in degrees, and dogleg radians. Each survey station carries a non-empty source reference. The **first survey station's TVD must be supplied**, not silently assumed to be zero at its MD. Strictly increasing MD, inclination 0–180 degrees and azimuth 0–<360 degrees are required. A 180-degree dogleg is rejected as singular; missing or malformed station inputs raise `SurveyError`.

The classic minimum-curvature method computes dogleg `β=acos(cos i1 cos i2+sin i1 sin i2 cos(Δazi))`, ratio factor `RF=2 tan(β/2)/β` (unity in the zero-dogleg limit), and `ΔTVD=ΔMD (cos i1 + cos i2) RF/2`. Trigonometric calculations use floating point internally and output `Decimal` for convenient downstream units; this is **not arbitrary precision survey computation**. Straight vertical 100m→100m TVD, straight horizontal 100m→~0m, steady 60-degree inclination 100m→50m and 0→90-degree 100m build→~63.661977m are independently checkable limiting geometries. No interpolation beyond provided stations or signed operator approval is implied.

### Source-identified planned-job section bridge — new, not yet Windows-regressed

Module `scripts/planned_job_section.py` exports `SourcedNumber` and `PlannedSection` (with `validate()` and `calculate()`). **Only one uniform planned section at a time**; not a whole-well summation.

Required fields: case/section IDs, common MD/TVD datum, survey ID/revision, ordered `SurveyStation` items with explicit MD unit, sourced first-station TVD, two **exact-match** survey station MD endpoints, bore ID, pipe OD/ID, dry linear mass, fluid density, and an explicit `flooded_open_pipe=True` assertion. Every quantitative input carries `source_id`, `source_location`, `source_revision`, `unit`, `review_status`. Missing sources, incompatible units/geometry, absent exact station endpoints, invalid MD order or non-flooded conditions raise `PlannedSectionError` rather than supplying defaults. A caller-provided `review_status="reviewed"` means only user-entered review metadata, **never verified OEM approval**.

`calculate()` produces an auditable dictionary with SI decimal-string results: section MD length, signed ΔTVD, internal tubular volume, concentric annular volume, static pressure difference from constant-density ΔTVD, and open/flooded segment apparent weight; source register, assumptions and warning are included. `status` is `numeric_candidate_only` if *all* numeric inputs are marked reviewed or `unreviewed_inputs` otherwise. No design acceptance, safe hookload, pressure limit, surge/swab or equipment-state judgement.

Example **synthetic** vertical 100 m section, bore 0.2 m, pipe OD 0.1 m, ID 0.08 m, 15 kg/m dry mass and 1000 kg/m³ water:
- Pipe internal volume = π×0.08²×100/4 = **0.5026548245743669 m³**.
- Annular volume = π×(0.2²−0.1²)×100/4 = **2.356194490192345 m³**.
- Static pressure difference = 1000×9.80665×100 = **980665 Pa**.
- These are **hand-derivable geometric/statics references**, not source values from a Baker Hughes or KHRM package.

`tests/test_planned_job_section.py` adds **15 proposed** integration tests: vertical/horizontal geometries, source-review status, unit equivalence, mandatory-source checks and fail-closed invalid/incomplete scenarios. They have **not yet been run in the user's Windows checkout**. The **last verified** full regression remains **248 passed**, preceding this code. Expected number if all new tests are collected is **263**, not a pass claim. Any failure must be corrected before marking the stage accepted.

**Next engineering tasks before acceptance:** verify full suite locally; perform independent engineering review of boundaries (notably open/flooded buoyancy and survey datum applicability); expand to sourced multi-section well profile only when component boundaries/survey stations are defensible. KHRM original-job numerical evidence remains unavailable.

## Documented independent reference equations and analytical checks

The following are elementary cylindrical geometry/statics identities, not vendor-specific Baker Hughes calculations.

- Circle area `A = πD²/4`; a cylinder's unobstructed internal volume `V = AL`.
- Annular area `A = π(D_bore² - D_pipe_OD²)/4` and volume `V = AL`.
- Static fluid of constant density: `Δp = ρgΔTVD`, with **positive ΔTVD downward** and `g = 9.80665 m/s²` as the standard acceleration used consistently in this slice. For constant density, ΔTVD—not MD—is the appropriate difference. The equation is discussed in OpenStax *University Physics Volume 1*, §14.1: https://openstax.org/books/university-physics-volume-1/pages/14-1-fluids-density-and-pressure
- For an **open, flooded** straight pipe with identical internal/external fluid, displacement is the wall **material** volume `A_metal L`, and `W_app = (dry_linear_mass × L - ρ × A_metal × L)g`. This is a restricted elementary buoyancy balance, not a general downhole effective-tension or pressure-end-force analysis.

### Independently hand-computable expected answers

1. A 1 m ID pipe 1 m long: `π/4 = 0.7853981633974483 m³`.
2. A 0.2 m bore and 0.1 m OD pipe, 10 m long: `π(0.2² − 0.1²)×10/4 = 0.2356194490192345 m³`.
3. Water `ρ=1000 kg/m³`, downwards `ΔTVD=100 m`: `Δp = 1000×9.80665×100 = 980665 Pa`; upward 100 m gives `-980665 Pa`.
4. Fully flooded open pipe, OD=0.2 m, ID=0.1 m, L=2 m, dry linear mass=100 kg/m, ρ=1000 kg/m³: wall material volume `0.0471238898038469 m³`; apparent load `(200−47.1238898038469)×9.80665 ≈ 1499.20 N`. This is not the load on a hanger or the rig hook.

**Focused validation evidence:** In an isolated local Python sandbox a matching implementation plus 29 focused pytest cases (14 primitive cases and 15 directional-survey cases) returned **29 passed in 0.06 s**. **Windows full-suite regression confirmed by the user on 2026-11-14:** checked out through commit `0749d96`, ran `py -m pytest -rs -q tests` in `skills/liner-hanger-rca`, obtained **248 passed in 8.26 s** with no failed tests. This is software verification only, not independent manufacturer or professional engineering approval.

## Missing work before LH-CALC-01 can be checked off

- Extend implemented source-referenced survey and MD/TVD separation with survey-version governance, station-depth datum consistency and whole-well profile integration, as required by planned-job workflows.
- [x] Initial source-identified uniform-section wrapper for survey, wellbore/pipe geometry, mass and fluid density. **Pending:** real-case source approval, multiple sections and more advanced fluid rheology, as applicable to subsequent stages.
- Explicit exception and missing-data tests across a complete planned well geometry scenario and comparisons with independently reviewed results.
- [x] Full local Windows `py -m pytest -rs -q tests` regression, **248 passed in 8.26 s** (2026-11-14). Independent review of model applicability and benchmark arithmetic still pending.
- Never use KHRM-299510 actual dimensions, fluid densities or approved BH limits without source pages/cells/revision and permission to use them. KHRM package extraction remains blocked; numerical functions remain generic.

**Release boundary:** this slice supports **offline engineering calculations** only. It cannot establish safe tripping, casing burst/collapse, torque/drag, liner setting, cementing pressure, ball-seat shear, a successful job or fault causation.
