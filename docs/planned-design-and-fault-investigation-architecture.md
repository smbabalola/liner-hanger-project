# Engineering design baseline → retrospective fault investigation (approved direction)

**Decision date:** 2026-11-12  
**Decision:** User clarified that a Baker Hughes execution/job package is **planned engineering evidence**, not evidence of a failure or that work was executed. The project should eventually support **independent engineering design/verification** and later compare historical operations with that planned baseline for fault investigation. This expands earlier BH-only fault-finding-v1 scope **by explicit user direction**. Do not misrepresent earlier source-gating or software tests as physical-model approval.

## Product stages and separation of evidence

1. **Planned engineering calculation / design verification:** read a *planned* well survey and bore/casing geometry; proposed running string and liner hanger assembly, planned fluid properties, equipment specifications, SOP and engineering results. Preserve the original design assumptions and revisions. Independently calculate expected loads and hydraulic predictions, assess known approved equipment limits, and present differences from the original engineer's calculations.
2. **Historical operation reconstruction — only if supplied:** use source-identified rig surface data, chronological activity/job logs and *verified as-run* assembly. Calculate tripping speeds and observed load/pressure/pump-rate patterns, with uncertainty and correct rig versus cement-unit source identity.
3. **Retrospective fault review:** compare actual measurements with the independently validated planned envelope **only when basis, tool revision, stage, measured depth, fluid, units and sensor locations are comparable**. Classify (a) breach of approved source-specific limit, (b) difference from model prediction with model uncertainty, (c) unverified or incomparable observation. Establish earliest supported discrepancy and hypothesize causal mechanisms without declaring downhole state from a surface signature alone.

An execution package **without field records** can populate only stage 1 and possibly a simulated scenario. Never fabricate as-run telemetry or label planned values 'actual'.

## KHRM-299510 candidate benchmark (documentation intake not yet completed)

Earlier user-supplied filename inventory includes a well sketch, a 7-inch ZXPN/2RH work breakdown / bill of materials, 7-inch 26-lb schematic workbook, tieback seal/extension operating procedures, drawings and signed ticket. **Filename descriptions are not verified technical content**. Their numerical results, survey, actual string/casing tally, mud properties, rated limits and revision applicability have not yet been extracted from readable attachments in this session. Their availability and rights must be checked before ingesting. The package is an **initial planned design verification candidate**, never a reported fault.

Benchmark plan:
- Extract each engineering input **with source filename/revision/page/cell**; record status `known`, `missing`, `conflicting` or `unverified`, and classify planned/as-run/observed.
- Extract each **original benchmark output** and calculation basis separately from inputs. A case lacking an original result cannot support numerical agreement claims.
- Record equation/version, sensitivity assumptions and dimensional units; compare independent predictions with original results and state exact deviation, uncertainty and whether comparison is valid.
- A matching number alone does not establish model validity. Require independent published/authorized benchmark, conservation/units checks, boundary/negative tests, and competent engineering review.

## Calculation families and dependency graph

| Family | Inputs required | Calculated outputs | Main validation risks |
|---|---|---|---|
| Wellbore and string | Directional survey with MD/inclination/azimuth and accepted interpolation; casing/open hole IDs, roughness, section lengths; actual component OD/ID/length/weight; tool geometry & effective buoyancy | Segment geometry, volume capacities, nominal string weights, reference depths | Missing survey, planned/as-run confusion, MD/TVD mismatch, unit mixing |
| Torque and drag | Above plus mud density, contact/friction model and supported friction factors (cased/open-hole), direction of travel, buckling/rotation assumptions, fluid buoyancy and contact forces | Pickup, slackoff, rotating weight and torque **versus measured depth**; modeled overpull available where ratings are reviewed | No universal friction factor; model depends on survey, friction assumptions, string stiffness, calibration, tool contact and rotation |
| Surge and swab | Above plus rate of tripping vs depth, annular clearances, mud rheology and compressibility, circulation/flow constraints | Modeled transient pressure envelope for defined tripping rates and well configuration | No fixed 'safe trip speed' without full model and formation integrity limits; never infer preset from tripping speed alone |
| Circulation hydraulics | Fluid rheology/density, temperature where applicable, workstring/liner/tubular ID/OD, flowpath, pump rates, returns/annuli and verified hydraulic model | Pressure loss by segment, equivalent circulating density where model permits, expected standpipe pressure under documented conditions | Rig SPP ≠ ball-seat differential or cement-unit discharge; flow-path and nozzle/seat restrictions must be source mapped |
| Actuation/ball-seat/packer/running tool | Exact BH model/size/revision/assembly, source-approved differential/force/set/shear/lock limits, confirmed seat/packoff locations | Pressure differential/force/load comparisons **only when source and model support them** | Training worked examples are not approved ratings; no predicted seat shear or tool set/release from pressure alone |

These are engineering **requirements**, not implemented physical-model capabilities. The existing `bha_tally.py`, `equipment_specs.py`, `operating_limit_screen.py` and `evidence_timeline.py` should be reused after validation, not replaced by an unrelated app.

## Shared planned-versus-observed data contract

Each comparable quantity requires:
- `case_id`, `component_id`, `stage`, `parameter`, location and domain (rig SPP, seat differential, hookload, trip speed, rig pump versus cementing unit).
- `basis`: `planned_input`, `independently_calculated`, `original_design_result`, `observed_surface`, `inferred` (explicitly flagged) or `unknown`.
- Value, unit, pressure basis and explicit unit/engineering domain equivalence.
- Source ID, source location (page, Excel cell or CSV row), revision, document/clock provenance and review/approval status.
- Relevant MD/TVD, time or job-stage alignment, and separate planned versus verified as-run equipment basis.
- Method/model version, uncertainty/sensitivity range and whether calculated output is validated.
- `approved_limit` record separate from a `model_prediction`: neither a training example nor original design result is automatically an OEM acceptance criterion.

Comparison results must distinguish `not_comparable`, `incomplete`, `prediction_difference` and `source_approved_limit_screening`. **No 'breach' without a truly verified approved limit.**

## Planned benchmark development acceptance order

1. Source inventory and case-specific input/output extraction (no tool settings invented).
2. Data contracts and validation tests, including an **unavailable** result for missing survey, friction factors, rheology, model or source-approved tool criteria.
3. Numerical engines, each benchmarked first to independent worked problems and documented physical assumptions. Implement model families in a coordinated batch if practical, but **do not bypass individual model acceptance**.
4. KHRM numerical comparison with original design figures where both full inputs and original results are actually accessible; report sensitivity bands instead of a false pass if important assumptions are unknown.
5. Preserve the accepted LH-017 synthetic failure reports. Attach future historical CSV only after verifying clock/channel provenance and as-run distinctions.

## Scope safeguards

- Baker Hughes first; general computational backend may later support other OEMs, but no cross-OEM rules now.
- Distinguish pickup/slackoff/rotating hookload predictions from **hydraulic force at a tool**, which needs effective areas, differential-pressure distribution and actual configuration.
- Never claim to certify operations, provide real-time control commands or approve a trip rate, pressure or overpull from undocumented assumptions.
- Proprietary engineering documents remain outside public Git; register only allowable metadata/derived test fixtures.
- No UI development in this stage; preserve old prototypes as reference.

**Action state:** Architectural decision documented. No source-based KHRM numerical benchmark extracted or physical solver verified yet.
