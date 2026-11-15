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

## 2026-11-15 — real North Sea published 3D geometry reproduction verified

**Independent source:** Knut Tveitan, University of Stavanger (2011), Table A-1 printed p.57, Well A. The table's five consecutive MD/inclination/azimuth/TVD/N/E readings at 1202.50–1318.10m were compared against the skill's minimum-curvature survey and the independent numerical great-circle integration in `trajectory_interpolation_audit.py`. The computed 12 independent component increments (4 intervals × north/east/down) agree with published differences within **0.008m**, below the explicit **0.02m** transcription/rounding tolerance. The skill's native `directional_survey.integrate_minimum_curvature` reproduces the five published TVD station positions within the same tolerance, using the *published starting TVD* as anchor. These are real 3D survey geometry values, not synthetic plotted curves.

`tests/test_published_tveitan_survey_geometry.py` introduced **14 tests** at commit `0effcf7`. Verified complete GitHub Actions [run 43722944618](https://github.com/smbabalola/liner-hanger-project/actions/runs/43722944618), Python **3.11 622 passed, 0 skipped in 16.99s** and Python **3.12 622 passed, 0 skipped in 26.60s**, from actual CI job logs. Source and discrepancy table: `LH_CALC02_EXTERNAL_BENCHMARK_REGISTER.md`.

**Acceptance is still OPEN (6/7).** Survey XYZ interpolation agreement proves neither the soft-string 3D wall normal/contact law nor a weighted pickup/slackoff or rotary torque response. The thesis fits friction to actual hookload data and contains pressure, changing fluids, tooljoint, missing-survey and surface blockweight effects; it does not supply a fully source-equivalent independent tabulated force profile ready for this solver. No engineering sign-off or field release may be claimed. Only remaining direction is a physically comparable weighted force benchmark and an external qualified applicability decision; don't advance hydraulics yet.

## 2026-11-15 — published independent 3D force/torque high-tension LIMIT CHECK VERIFIED

A separate, independent **published mathematical model** is now compared numerically with the skill's minimum-curvature 3D weighted soft-string engine: M. Fazaelizadeh, G. Hareland and B. S. Aadnoy, *Application of New 3-D Analytical Model for Directional Wellbore Friction*, *Modern Applied Science* 4(2), 2010, DOI **10.5539/mas.v4n2p2**, eqs (5),(6),(8),(13),(14). The paper's curvature friction is the high-tension approximation that neglects distributed pipe gravity *inside* contact-reaction friction, adding buoyed axial weight at the end; it is not identical to our weighted contact-vector ODE at finite operating tension. Real-source theory requires the discrepancy to become relatively small when bottom tension dominates buoyed string weight. Tests commit `aa9c3cd`: fictional combined build/turn 30°→60° inclination/0°→60° azimuth, **nonzero W~11.94 kN**, fictional bottom load **2 MN** (*asymptotic only, not a field load*), compare independently calculated published pickup/slackoff axial tension, pure rotation axial tension and contact torque within 1% of distinct model calculations. Two more tests require decreasing relative discrepancy for pickup/slackoff as tension increases 200 kN→2 MN; one test checks no field approval. Source equations, approximation differences, unit interpretation and acceptance boundary registered in `LH_CALC02_EXTERNAL_BENCHMARK_REGISTER.md`.

**Executed full GitHub Actions regression at code commit `aa9c3cd`**, [run 43736419628](https://github.com/smbabalola/liner-hanger-project/actions/runs/43736419628), Python **3.11: 629 passed in 24.23s**, Python **3.12: 629 passed in 26.99s**, **0 failures and 0 skipped** on each, authenticated from actual job logs. Production force solver was not changed. The benchmark is a *qualified asymptotic analytical source comparison* rather than a **complete real nonzero-weight 3D well with comparable published numeric load profiles**. Neither the journal's field figure nor the Tveitan published well supplies all traceable exact measured-force numerical outputs, equivalent pressure/tubular/contact conditions and blind calibrated friction coefficients in this session. No stiffness or wall-transfer/side-state physical equivalence review and no independently qualified human sign-off were performed. **Engineering acceptance remains LH-CALC-02 6/7 (~86%) OPEN, programme 2/9 (~22%)**.

## Acceptance gate — next bounded sequence

## 2026-11-15 — independent published weighted 3D contact-law limit

Source: Zhang et al. (2026), *Scientific Reports*, DOI https://doi.org/10.1038/s41598-026-78097-x, Eq. (16). A narrow continuous 3D *pure-rotation, horizontal, constant-axial-tension* reduction was derived from the independent published discrete soft-string normal-force contributions. Azimuth curvature provides the horizontal normal load while nonzero buoyed gravity provides the orthogonal vertical normal load. With total turn β (radians), bottom/through-section tension T and buoyed section weight W, the independently checkable **continuous-contact limit** is integrated normal force `hypot(T*β,W)`; integrated **frictional contact torque** is `mu_rot*r*hypot(T*β,W)`. Unlike earlier zero-weight capstan cases, these tests require **both finite weight and nonzero azimuth turn**. Published discrete microelement normals `2T sin(Δaz/2)` and `W/count` independently converge to the continuous equation under refinement. Neither relation models viscous torque or the paper's full tool assembly.

Four new cases (three angles, one discretization-refinement check) committed in `tests/test_published_3d_contact_limit.py` at `bd57763`. **Entire current GitHub regression verified from both actual job logs at that commit:** [run 43741012671](https://github.com/smbabalola/liner-hanger-project/actions/runs/43741012671): Python 3.11 **633 passed, 0 skipped, 19.94s**; Python 3.12 **633 passed, 0 skipped, 21.16s**. The prior 629-case baseline includes independently committed related synthetic analytical checks and is superseded.

**Classification:** independent *published equation limiting-case* validation of normal force/rotary friction in a restricted weighted 3D geometry, **not** independent published full-well 3D pickup/slackoff/torque numerical reproduction. Neither Eq. (16)'s full model nor surface hookload/stiff-string/contact transfer is validated by this limit. **LH-CALC-02 still OPEN, 6/7 (~86%); programme 2/9 (~22%).** Qualified independent physical applicability review and a complete source-equivalent external 3D force/torque benchmark remain outstanding.



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
