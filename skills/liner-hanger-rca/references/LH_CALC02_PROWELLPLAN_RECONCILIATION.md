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
