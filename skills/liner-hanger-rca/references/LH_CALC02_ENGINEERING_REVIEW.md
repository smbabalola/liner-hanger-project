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

## Acceptance gate — next bounded sequence

- [x] Basic straight, co-linear, exact weightless bend and planar weighted module implemented, with full updated user Windows regression of **432 passed in 13.82 s** at `bf7838e`.
- [x] Published contact-law sources located and separately derived weighted **constant-contact-side** analytical solution documented.
- [x] Unsupported sampled contact-side changes fail closed; refinement differences exposed without numeric self-certification.
- [x] **Full regression after bulk validation changes:** user pulled `bf7838e` and ran `py -m pytest -rs -q tests` inside the skill on Windows: **432 passed in 13.82 s**, no failures. No separate focused run is claimed.
- [ ] Independently reproduce an authorized/published **nontrivial full weighted directional well profile** or verified original engineering comparison, including physical signs, assumptions and tolerances.
- [ ] Verify continuous multi-interval weight/force/contact transfer, MD/TVD, source revisions and 3D azimuth doglegs; or formally approve a much narrower planar-only scope **without** claiming a full P2 engine.
- [ ] Complete suitably qualified human review of physical applicability and operational exclusion before any real-well use. These conditions cannot be self-certified by the AI.

**Decision today:** Keep `LH-CALC-02` at **6/7 (~86%) IN PROGRESS**; overall **2/9 (~22%)** stages accepted. Do not advance to `LH-CALC-03` on the basis of software tests alone. The next batch should target either the supported multi-interval 3D model plus independently authenticated evidence, or a documented scope decision by the project owner and qualified reviewer.

## Confidentiality

Only fictional synthetic test data and citations are in this review; proprietary Baker Hughes drawings/job packages and customer well data are excluded from public Git.
