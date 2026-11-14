# LH-CALC-02 — independently sourced external benchmark intake

**Date:** 2026-11-14. **Gate:** OPEN. This is a source-input crosswalk, **not** an independent validation pass or permission for operational use. The new minimum-curvature research solver has **568 expected software tests**, not yet verified in the full Windows skill suite; last user-confirmed suite **505 passed in 13.10s** at `6e79693`.

## Candidate A — Texas A&M dissertation with published force/torque values

**Ruktai Ace Prurapark (2009), _Torque and Drag Calculations in Three-Dimensional Wellbores_, Texas A&M University, Chapter VIII (printed pp. 77–86).** Public repository PDF: https://oaktrust.library.tamu.edu/bitstream/1969.1/ETD-TAMU-2009-05-403/2/PRURAPARK-DISSERTATION.pdf

Documented numerical material:

- Printed p.78, Table 8.1: a **planar lowering/build** sample, KOP=1,509ft, EOC=3,308ft, friction 0.1, effective weight 19.5lb/ft, curvature radius 1,146ft, 0°→90° angular range, nominal lower boundary 10,000lb, and **reported top force −9,504lb**. The sign is compression, **which our current positive-tension model expressly rejects**. Do not fabricate a positive-tension equivalent or call this a matching validation.
- Printed pp.79–83, Figs.8.3–8.5 and Eqs.8.14–8.26: another **planar** extended-reach rotational example with 40,000lbf end-of-curve tension, a published 54,480lbf KOP calculation (plot 54,481lbf at MD 1,509ft), and 3,760ft-lbf KOP torque. Reported inputs include KOP 1,509ft, stated 5.08°/100ft build, friction 0.333, 9.6ppg drilling fluid, dry weight 16.6lb/ft and steel density 65.5ppg. The exact section angle convention, full pipe geometry/displacement and contact/torque-radius definition require verification before importing the numerical target.
- Printed pp.84–86, Table 8.2 gives a **3D survey design problem** with target MD 6,955.28ft, TVD 5,000ft, north −3,000ft, east 2,000ft, and a tie-on row that includes inclination 57°, azimuth 300° and dogleg severity 5°/100ft. This is **not a complete as-surveyed torque-and-drag history or sufficient multi-interval load benchmark**.

**Decision:** useful independent published known-answer/counterexample for parts of the model. **NOT yet reproduced** on the skill's exact sourced input basis; does not satisfy the missing published **nonzero-weight combined build/azimuth** force benchmark.

## Candidate B — reconstructable open-source research example

**Jonny Corcutt (2022), _An Example of using welleng's Torque and Drag module_:** https://jonnymaserati.github.io/2022/05/22/an-example-of-welleng-torque-drag.html

Describes a simplified version of an example from Johancsik et al. Includes trajectory control points 0m/0°, 731.5m/0°, 1,280m/44° and 3,718m/44° (constant azimuth); 30m interpolated survey; explicit three-component string dimensions/weights; 8.5in wellbore and 0.39 sliding friction; fluid density 9.8/8.33 SG; optional 10,000N WOB, bottom torque, and overpull. The worked example explicitly **omits higher-dogleg features**. It demonstrates a reproducible software-to-software **planar** comparison but is not an independent field measurement or qualified OEM source.

**Decision:** potentially useful source-qualified section/profile software comparator once definitions of buoyancy, tool-joint radius, bottom boundary and actual output arrays are extracted; **not yet reproduced**. Do not copy the third-party program into the skill without a separate license/source review.

## Candidate C — published 3D comparison, incomplete data for exact reproduction

**_Efficient Design of Three-Dimensional Well Trajectories with Formation Constraints and Optimization_**, Processes (2025), https://www.mdpi.com/2227-9717/13/4/1215

Published 2,715m three-dimensional example, friction coefficient 0.25 in casing and 0.30 in open hole, fluid density 1.16g/cm³, bottom torque 3,000N·m and WOB 30kN. Reports 3D torque comparisons against WELLPLAN, with approximately 1.5–1.8% stated section differences. However, complete machine-readable survey/pipe-by-pipe mass/diameter and comparable absolute force/torque results are **not extracted** from the available text. The publication's claimed model agreement must not be inherited as our model's verification.

**Decision:** relevant **3D published validation lead**, but **not a reproducible numerical gate yet**.

## Candidate D — independent mathematical integration of our declared ODE

Separate high-precision SciPy DOP853 evaluation of our own fictional 100m combined build/turn with documented OD, ID, linear mass, density, friction, radius and end tension. Exact output table and math in `LH_CALC02_MINIMUM_CURVATURE_3D_MODEL.md`. This is a **proper independent numerical method comparison**, not an independent physical or field truth source.

## Next acceptance substeps

- [x] Identify and read independent published source candidates and record **exactly what each supports and lacks**.
- [ ] Obtain all source inputs and outputs required for one **physically equivalent** benchmark; compare unit systems, bottom conditions, motion modes, angle conventions, wall radius and pipe mass/buoyancy basis. Do not tune missing values to match reported results.
- [ ] Establish a nontrivial **nonzero-weight 3D** (inclination + azimuth) published/qualified actual comparable torque/drag dataset, with an independent engineering reviewer.
- [ ] Run the current **568 expected** full skill regression (locally or verified CI) and record actual count/failures; no pass-by-assumption.
- [ ] Record discrepancy tables and qualified model applicability/field-use decision; unsupported configurations remain unavailable.

**Confidentiality:** publish only scholarly citations and small independently derived numerical fixtures; never upload copyrighted papers, Baker Hughes job packages, or customer records.
