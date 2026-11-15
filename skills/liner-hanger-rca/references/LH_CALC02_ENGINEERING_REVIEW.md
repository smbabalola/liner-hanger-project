# LH-CALC-02 — engineering applicability and acceptance review

**Review date:** 2026-11-14  
**Decision:** **DO NOT ACCEPT LH-CALC-02 AS A COMPLETE FIELD-READY ENGINE.** This document is a technical review checklist, not a qualified engineer's sign-off. The software has four distinct, intentionally bounded models; the resulting outputs must not be labelled a complete torque-and-drag profile or used to set operating limits.

## Verification evidence matrix

| Capability | Module | Mathematical benchmark | Status and boundary |
|---|---|---|---|
| One straight uniform section | `torque_drag_straight.py` | Inclined-plane free-body equilibrium, vertical/horizontal/zero-friction limits | Independently analytic, software tests passed; **not rig hookload** |
| Multiple co-linear straight sections | `torque_drag_profile.py` | Split-invariance, force/torque conservation, independent 100 m hand result | Software tests passed; refuses changes in orientation between sections |
| One ideal weightless bend | `torque_drag_bend.py` | Exact capstan exponential and mode-dependent normal integrals | Software tests passed; **weightless limiting case**, not weighted dogleg |
| One uniform **weighted planar** arc | `torque_drag_weighted_curve.py` | Exact zero-curvature, weightless, zero-friction limits; *new* independently integrated **constant-side weighted build/drop exact solution**; refinement audit | **User verified the full updated Windows suite: 432 passed in 13.82 s at `bf7838e`**, including the new analytical and transition checks. One uniform planar interval only |

## Published engineering basis — independently located

- Johancsik, Friesen & Dawson (1984), *Torque and Drag in Directional Wells—Prediction and Measurement*, SPE 11380, https://doi.org/10.2118/11380-PA. The original soft-string formulation models Coulomb friction using computed sidewall contact; the published paper describes comparison with measured field responses. **We have not replicated its specific field dataset.**
- Aadnøy & Andersen (2001), *Design of oil wells using analytical friction models*, *Journal of Petroleum Science and Engineering*, https://www.sciencedirect.com/science/article/abs/pii/S0920410501001474 — analytical soft-string treatment and distinct axial/rotational modes.
- Public technical breakdown with build/drop wall-normal force diagrams and the gravity-versus-tensile-curvature direction: https://core.ac.uk/download/pdf/147134737.pdf . This is secondary reference evidence, not an authorized Baker Hughes load chart.

The independent mathematical check is the **new exact integrating-factor solution** documented in `TORQUE_DRAG_WEIGHTED_CURVE_VALIDATION.md`; the original published well-specific results are **not claimed as reproduced**.

## Assumptions that still limit applicability

1. The weighted solver has only **two known survey stations** with linearly changing inclination, fixed azimuth, and 0–90° inclination. This is not a full directional survey and does not model turns, tortuosity or local dogleg severity.
2. Uniform tubular geometry, metal buoyancy from open flooded pressure-balanced pipe, constant density and dry linear mass; tool joints, BHA stiffness, pressure end-area and flow effects omitted.
3. Three **separate**, assumed pure motions: pickup, slackoff and rotation; no combined axial+rotation friction vector, motor/bit torque or downhole setting sequence.
4. **Contact-side transitions are now rejected** when sampled, rather than assigned a seamless `abs(normal)` contact model; a contact-gap/contact-transfer model is still unimplemented.
5. No bending stiffness, buckling or compression model; no matching verified as-run sensor and no original KHRM-299510 engineering result validated.
6. A source ID and `reviewed` field only track input provenance, not authenticity or OEM engineering approval.
7. Step-size refinement measures numerical discretization only and **does not validate the physical equations**; field deviations and uncertainty envelopes require different evidence.

## Connected weighted planar profile implementation (software-regression verified)

A source-gated `torque_drag_weighted_profile.py` module and JSON CLI now **implement a research-only string of continuously joined planar weighted intervals**. Separate pure-motion tensile modes are propagated bottom-to-top, and rotational friction torque is accumulated. It rejects unsupported 3D azimuth turns, MD/TVD mismatches, survey revision mismatches, discrete angle kinks, compression and within-interval sampled wall-side transfers. Synthetic two-interval calculations are cross-checked against one 100m uniform planar interval with the same source-labelled physical inputs, preserving separate bottom-to-top tensile boundaries and summed pure-rotation friction.

**Software regression verified:** user pulled through `7f7e741`, running the full skill Windows suite: **460 passed in 14.44 s, zero failures**, including 28 connected planar-profile checks. The model is still **not an independently validated multi-station 3D directional-well**. External published job/profile comparison and qualified engineering sign-off remain acceptance blockers.

## Experimental 3D research batch — additional unverified code

An **experimental 3D inclination-and-azimuth soft-string interval model** and **tangent-continuous multi-interval spatial profile** have now been committed. The model uses separate gravity/curvature normal components and the existing source-qualified geometry framework; its primary independent exact tests use weightless pure-azimuth capstan limits, `sin(inclination)` scaling, planar identity, wraparound, split invariance, boundary continuity and rejection of unsupported 3D turns. Strict offline JSON runners and fictional examples are documented in `TORQUE_DRAG_3D_VALIDATION.md`.

**Engineering limitation:** The 3D algorithm uses piecewise linear inclination and unwrapped azimuth, and does not physically resolve the 3D contact-transfer state or interpolate the trajectory exactly as the minimum-curvature TVD calculation does. No independent real-well data matching, published complete 3D benchmark, verified Baker Hughes tool forces or qualified engineering sign-off are available. This is not proof that the model is safe or predictive in an actual well.

**New tests unverified:** the user last confirmed **460 passing in 14.44 s** at `7f7e741`. The 3D batch adds **44 expected test cases** for a projected **504 total**, but this estimate is **not verification**. Preserve `LH-CALC-02` open at 6/7 (~86%), overall stages 2/9 (~22%).

## Latest verified experimental 3D regression — 2026-11-14

**User-run Windows verification:** After updating from `f584cbf` through `6e79693`, the user ran `py -m pytest -rs -q tests` from `skills/liner-hanger-rca`: **505 passed in 13.10 s, zero failures**. This includes the experimental 3D section/profile test families and the additional error-handling check for an undefined 180-degree survey dogleg. The original run (503 passed, 1 failed) identified a masked survey error, not a successful unsupported-geometry calculation; the runner fix preserved fail-closed rejection without changing physics.

**Engineering acceptance remains OPEN:** software-regression success is not an independently reproduced full 3D weighted well survey calculation, not a field comparison, and not a qualified physical or OEM sign-off. The spatial model still uses constant angular gradients rather than identical trajectory interpolation to the minimum-curvature TVD procedure; contact transfer and stiffness remain unmodelled. Maintain `LH-CALC-02` **6/7 (~86%)** and programme **2/9 (~22%)**.

## Versioned minimum-curvature 3D model and source-evidence update — 2026-11-14

A **separate** `scripts/torque_drag_3d_minimum_curvature.py` now uses one great-circle minimum-curvature tangent for sourced station TVD, projected buoyed gravity, curvature wall contact and three distinct movement modes. `scripts/torque_drag_spatial_profile.py` includes `predict_minimum_curvature_profile`; separate one-section/profile JSON CLIs and **38 new expected** independent/negative/CLI cases are committed. The prior 25-test isolated geometry-audit group and new 38 cases produce **568 expected total**, versus last confirmed full Windows suite of **505 passed in 13.10s** at `6e79693`. **The new full regression has NOT been run or certified**, and CI results remain unconfirmed.

Independent mathematical limiting evidence includes exact weightless great-circle capstan, zero axial-friction MC-TVD gravity integral, planar/horizontal old solver limits, true nontrivial great-circle midpoint split invariance, and a separate **DOP853 high-precision numerical calculation of the same fictional nonzero-weight vector ODE**. See `LH_CALC02_MINIMUM_CURVATURE_3D_MODEL.md`. This does not independently validate contact physics for a drilled well.

External public material has been inspected and classified in `LH_CALC02_EXTERNAL_BENCHMARK_REGISTER.md`: published planar numerical references (including an unsupported-compression case), a reproducible but planar open-source example, and a published 3D commercial-software comparison **without the complete source inputs/results needed for a valid apples-to-apples numerical check**. **No nonzero-weight 3D independent published or actual-well benchmark reproduced; no qualified engineer/OEM acceptance.** `LH-CALC-02` remains **6/7 (~86%) OPEN**, programme accepted stages **2/9 (~22%)**. The next step is 568-case actual full regression and physically equivalent external benchmark; do not advance to hydraulics stage prematurely.

## 2026-11-15 — external benchmark intake gate, without a published profile match

A research-only, standard-library fail-closed numerical comparison gate is now available at `scripts/benchmark_crosswalk.py` with exact source/physics/mode/unit/boundary/tolerance crosswalk requirements. Its separate 37-test isolated local suite **passed 37/37**, including incomplete provenance and contact-state inputs, inconsistent modes and nonfinite/oversized numbers. See `LH_CALC02_BENCHMARK_CROSSWALK_GATE.md`. This is an **intake mechanism**, not a reproduced published or field force case, and it returns `engineering_acceptance=false` even for numerical agreement. No change to torque/drag force equations or contact algorithm was made in this batch.

The current theoretical full-suite collection is **605 tests** (568 expected before this batch plus 37 new cases); **not verified as passing** in a full repository or Windows run. The latest user-confirmed full skill regression remains **505 passed at `6e79693`**. No authenticated GitHub Actions full-suite result or qualified physical applicability approval is available. `LH-CALC-02` remains **6/7 (~86%) OPEN**, programme **2/9 (~22%)**.

## 2026-11-15 — full skill CI regression VERIFIED; external physical benchmark still OPEN

GitHub Actions [run 43718419410](https://github.com/smbabalola/liner-hanger-project/actions/runs/43718419410) at code/workflow commit `2fab5b6` executed the **entire skill test suite**, with real browser provisioning and previously skipped Playwright checks. Actual logs: **Python 3.11: 605 passed, 0 skipped in 27.26s; Python 3.12: 605 passed, 0 skipped in 17.32s**. Prior references to *expected* 605 tests and 505 last confirmed are historical; they are superseded for this tested commit. Software integration verification is now satisfied.

External source Candidate B was inspected more deeply (see `LH_CALC02_EXTERNAL_BENCHMARK_REGISTER.md`). The public `welleng` example is azimuth-constant/planar, differs in detailed BHA/tooljoint/bottom-boundary construction and does not constitute an independently reproduced combined-build-and-turn weighted 3D well. **No published nonzero-weight full 3D contact-force/torque profile has been matched** on identical physical inputs and assumptions, and no qualified reviewer has approved contact-state/stiffness/field applicability. Therefore **LH-CALC-02 remains 6/7 (~86%) OPEN; programme 2/9 (~22%)**. Do not treat the regression success as rig-hookload or OEM engineering approval.

## Acceptance gate — next bounded sequence

- [x] Basic straight, co-linear, exact weightless bend and planar weighted module implemented, with full updated user Windows regression of **432 passed in 13.82 s** at `bf7838e`.
- [x] Published contact-law sources located and separately derived weighted **constant-contact-side** analytical solution documented.
- [x] Unsupported sampled contact-side changes fail closed; refinement differences exposed without numeric self-certification.
- [x] **Full regression after bulk validation changes:** user pulled `bf7838e` and ran `py -m pytest -rs -q tests` inside the skill on Windows: **432 passed in 13.82 s**, no failures. No separate focused run is claimed.
- [ ] Independently reproduce an authorized/published **nontrivial full weighted directional well profile** or verified original engineering comparison, including physical signs, assumptions and tolerances.
- [x] **Connected planar weighted intervals implemented and full software regression verified (460 passed).** MD/TVD/heading/survey provenance checks and mode-wise load/torque propagation have new synthetic tests; **experimental 3D soft-string code exists but is not yet regression-verified or field benchmarked**. Obtain external validation or explicitly approve a narrower research-only scope without claiming full P2 acceptance.
- [ ] Complete suitably qualified human review of physical applicability and operational exclusion before any real-well use. These conditions cannot be self-certified by the AI.

**Decision today:** Keep `LH-CALC-02` at **6/7 (~86%) IN PROGRESS**; overall **2/9 (~22%)** stages accepted. Do not advance to `LH-CALC-03` on the basis of software tests alone. The next batch should target either the supported multi-interval 3D model plus independently authenticated evidence, or a documented scope decision by the project owner and qualified reviewer.

## Confidentiality

Only fictional synthetic test data and citations are in this review; proprietary Baker Hughes drawings/job packages and customer well data are excluded from public Git.
