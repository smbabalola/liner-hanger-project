# LH-CALC-02 — Pro Well Plan numerical reconciliation audit
Date: 2026-11-15. Classification: **OPEN — upstream documentation mismatch diagnosed, not resolved or accepted**.
Scope: reproduce pinned upstream code vs the source-documentation six scalars; do not promote to engineering acceptance.

## Reproduction basis
- Upstream `pro-well-plan/torque_drag` commit `701cfff5990e33b495f45e082364d608ee65db87`, `torque_drag/main.py` and `docs/source/calculations.rst`.
- Upstream `pro-well-plan/well_profile` commit `43375df82eaa53a890b5539808ed33d3d57f0817`, 100-station `well_profile/tests/trajectory1.xlsx`.
- Both docs and our pinned probe use `{'pipe': {'od':4.5,'id':4,'shoe':3000},'odAnn':5}`, `case='all'`, `torque_calc=True`, `wob=50`, `tbit=50`; `densities` and `fric` omitted.
- Existing hosted upstream execution: [Actions 43741984153](https://github.com/smbabalola/liner-hanger-project/actions/runs/43741984153), script `scripts/probe_prowellplan_reference.py`; reports `source_documentation_mismatch`. Outputs below rounded to four decimal places.

| Mode | Docs force (kN) | Executed force (kN) | Executed − docs (kN) | Docs torque (kN·m) | Executed torque (kN·m) | Executed − docs (kN·m) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| lowering | 372.2972 | 303.6872 | -68.6100 | 52.8897 | 56.1943 | +3.3046 |
| static | 422.8596 | 412.0743 | -10.7853 | 53.2488 | 57.6292 | +4.3804 |
| hoisting | 486.9781 | 579.6156 | +92.6375 | 53.6644 | 59.5750 | +5.9106 |

## Source-code causes of non-equivalence (confirmed in pinned upstream code)
1. `calc(..., fric=<scalar>)` **discards the supplied scalar**, setting every station friction to 0.24 unless `type(fric) is list`. Lists are read by station index. Our direct reproduction omits friction as the documentation does, so both ostensibly use the same **0.24 default**; this bug is a cross-solver/input-equivalence hazard, **not demonstrated as the reason for the documentation mismatch**.
2. `calc` computes buoyancy with `1 - rhof*(area_ann-area_inner)/(rhod*(area_ann-area_inner))`, algebraically `1-rhof/rhod` for nonzero denominator. This is a conventional fluid/steel density-ratio multiplier, but derived through annular/inner areas and assuming uniform fluids; string internal contents and pressure effects are not separately modeled. The skill's own fluid/weight, section mass and boundary conventions must be compared before using this upstream calculation as a physical reference.
3. The external force solver steps over rows in reverse, averages inclination using `trajectory[idx-1]` even at `idx=0` (Python negative-index wraparound), and takes angle deltas from `trajectory[idx+1]`. This is a **confirmed index-0 implementation peculiarity**, not independently proved to be responsible for all mismatched source-documentation numbers.
4. Upstream torque increments use `mu * normal * outer-pipe-radius` for *each* lowering/static/hoisting force state; outputs already include `tbit=50 kN·m`. They are not a directly equivalent pure-rotation torque test for our skill.
5. The documentation and pinned code show equivalent call argument text, but the documentation does not identify the precise source revision or XLSX byte hash used to generate its illustrative numbers. **Version/fixture drift is plausible but presently unproved.** No hidden input should be tuned to force agreement.

## Next discriminating checks
1. Capture XLSX SHA-256, the package module paths and versions, exact count/first/last trajectory rows, and defaults in the hosted report. Check whether original documentation-associated fixture/revision reproduces the six figures. Compare the upstream source history before attributing differences to version drift.
2. Run controlled upstream perturbations one-at-a-time: `fric=None`, `fric=[0.24]*n` (expected same), different friction *lists*, alternative documented densities, explicit string length, and compare first/last station, mode force and torque outputs. Never adjust parameters just to target the docs.
3. For an actual independent solver crosswalk, map *same survey stations, string mass, immersed buoyancy, friction, bottom axial/torque boundary, contact definition, axial motion mode, measured output location and units*. Exclude unsupported compression, tool joints, stiffness, or fluid/pressure effects. Quantify deviations over the whole 3D profile, not only six top scalars.
4. Qualified engineering reviewer to assess applicability/contact transfer/stiffness and sign off or explicitly restrict approved scope.

## Verdict
**The six upstream documentation values are not validated regression targets** under the pinned source and fixture. The third-party executable 3D reference is useful for controlled *software comparison* once its numerical inputs and output definitions are mapped; neither executable agreement nor this audit proves field physics. **LH-CALC-02 remains 6/7 OPEN**, no LH-CALC-03, no solver edits, no qualified acceptance.


## 2026-11-15 executed full-profile source-law reconciliation — **RESOLVED for pinned upstream implementation**

The first independent recurrence check initially failed due to an accidentally escaped newline that commented out the external `calc` assignment (GitHub run 43745922716); this was corrected immediately in commit `4bbcb4b`. The corrected [independent external probe run 43745962102](https://github.com/smbabalola/liner-hanger-project/actions/runs/43745985967) **completed successfully** and printed `independent_discrete_source_law_parity=true`. (If the linked run number changes under GitHub Actions retention, inspect the check-run job associated with commit `4bbcb4bdfe1ec62910c23ff4c8793c21a850f7b9`.)

The research probe now independently evaluates the **same discrete Johancsik-style equations** in a separate routine over the full pinned 100-station 3D trajectory, with source units and boundaries: 4.5/4in OD/ID, 5in annulus, 1.3/7.8 SG densities, 0.24 sliding friction, 50kN bottom axial force, 50kN·m bottom torque, lowering/static/hoisting. It evaluates gravity/buoyancy, azimuth and inclination normal-force terms, axial friction and accumulated friction torque, then compares **all depth-indexed output samples** for all modes against the separately installed original upstream package. The reference implementation uses the upstream's actual peculiar `idx-1` indexing convention; parity is about reproducing *its behavior*, not endorsing that indexing as physically correct.

**Observed maximum absolute discrepancy over all stations (from executed CI job log):**

| Quantity | Lowering | Static | Hoisting |
| --- | ---: | ---: | ---: |
| Force (kN) | 1.1368683772161603e-13 | 1.1368683772161603e-13 | 1.1368683772161603e-13 |
| Torque (kN·m) | 0 | 0 | 1.4210854715202004e-14 |

All are floating-point round-off; this is **a successful full-profile pinned-source algebraic reconciliation**. The original six *documentation* numbers remain mismatched, separately reported as `source_documentation_mismatch`. They are not approved regression targets. A full-profile match to the original source does **not** mean the current **liner-hanger skill solver** has been run on identical inputs or agrees with the upstream force outputs, and does **not** constitute field or OEM engineering validation. Distinguish these three outcomes:
1. **Resolved:** independently reimplemented recurrence vs installed pinned upstream model on 100-station 3D survey.
2. **Unresolved:** upstream documentation figures vs installed pinned upstream model (no historically pinned documentation/fixture provenance).
3. **Not yet executed:** physically equivalent model-to-model full 3D force crosswalk against the skill's continuous two-station minimum-curvature solver (different buoyancy, discrete vs continuous contact, movement and bit-torque semantics); qualified engineering signoff.

This is a real reconciliation result, but **LH-CALC-02 acceptance remains OPEN 6/7**, with no assertion of qualified physical model validity.

