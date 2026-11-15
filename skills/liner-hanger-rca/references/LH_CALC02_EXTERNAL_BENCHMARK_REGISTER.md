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


## Candidate E — NORCE / SPE Open-Source Drilling Community, published 2026 transient 4n-DOF simulator

**E. Cayeux, S. Moi, L. P. Volpi, G. Pelfrene (2026), _An Open Source, Online, Near Real-Time 4n Degree of Freedom Transient Torque and Drag Model_, IADC/SPE-230785-MS, published 10 March 2026.** DOI: https://doi.org/10.2118/230785-MS ; reference implementation: https://github.com/Open-Source-Drilling-Community/Simulator4nDOF (Apache-2.0 per source repository/paper; check specific subcomponent licensing before reuse).

The paper describes a publicly inspectable, containerized transient axial/torsional/lateral model and reports validation against field high-frequency measurements from North Sea fixed and floating platforms. The public repository includes model and test projects and interfaces for simulation cases. This is a credible **independent physics and test-harness comparison candidate**, rather than the synthetic data sets or the already documented self-ODE DOP853 reproduction.

**Crucial comparability restriction:** this model includes transient motion, stiffness, radial clearance/contact and coupled physical effects absent in our quasi-static soft-string solver. A matching numerical result cannot be claimed without extracting a reproducible **quasi-static, frictional, nonzero-weight 3D limit** and matching complete survey/pipe/fluid/friction/contact/bottom-load data, boundary and observable definitions, units and numerical tolerance. Its published field validation does **not transfer** to this project's solver. Public availability of the source does not establish availability of the underlying North Sea field records or their redistribution rights.

**Decision (2026-11-15):** source and repository identified; **no simulator run, data extraction, input crosswalk, force match or review performed**. Record as an external validation lead only. Next: inspect the upstream ModelTest/SimulatorTest fixtures and associated 2026 paper examples, select a reproducible static limit if available, compare explicitly with our supported contact regime, and reject non-equivalent cases. Do not commit upstream source or field data to this project.

## Candidate B deeper source crosswalk — 2026-11-15

The publicly reproducible `welleng` notebook/article at https://jonnymaserati.github.io/2022/05/22/an-example-of-welleng-torque-drag.html documents control nodes (MD 0/731.5/1280/3718 m; inclination 0/0/44/44 deg; azimuth 0 deg throughout), 30 m resampling, an example BHA (6.5 in/4 in drill collars for 372 ft at 146.90 lb/ft; 4.5 in/4 in HWDP for 840 ft at 46.90 lb/ft; 5 in/3.625 in pipe at 20 lb/ft), casing/open-hole friction 0.39, the cited 9.8/8.33 SG fluid conversion and WOB 10,000 N, bottom torque 2,712 N m, overpull 50,000 N. Its wellbore assembly references 8.5 in nominal diameter, while tooljoint diameters are separately included. The plotted T&D curves are not a published machine-readable per-station force/torque table in the article, and the source explicitly omits high-dogleg sections from the original paper.

**Physical equivalence verdict: NOT COMPARABLE as a full 3D weighted validation target.** All survey azimuths are constant, making it a planar case. The skill's constant-mass/two-station per section model omits tooljoint distributions and bottom torque, WOB/overpull and other nuances of the example, so simply matching selected values by tuning missing details would be misleading. An independently executed `welleng` reference with explicit outputs might qualify as a restricted **planar software comparator** only after documenting precise boundary and unit mappings, and it would **not satisfy** the outstanding combined inclination+azimuth 3D field/independent benchmark acceptance gate. No solver output comparison or qualified sign-off is claimed in this review.

## Next acceptance substeps

- [x] Identify and read independent published source candidates and record **exactly what each supports and lacks**.
- [ ] Obtain all source inputs and outputs required for one **physically equivalent** benchmark; compare unit systems, bottom conditions, motion modes, angle conventions, wall radius and pipe mass/buoyancy basis. Do not tune missing values to match reported results.
- [ ] Establish a nontrivial **nonzero-weight 3D** (inclination + azimuth) published/qualified actual comparable torque/drag dataset, with an independent engineering reviewer.
- [ ] Run the current **568 expected** full skill regression (locally or verified CI) and record actual count/failures; no pass-by-assumption.
- [ ] Record discrepancy tables and qualified model applicability/field-use decision; unsupported configurations remain unavailable.

**Confidentiality:** publish only scholarly citations and small independently derived numerical fixtures; never upload copyrighted papers, Baker Hughes job packages, or customer records.
