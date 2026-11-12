# LH-015 — Competing-hypothesis investigation register v0.1

**Status:** Implementation and synthetic tests committed; **Windows full regression, end-to-end engineering source review and acceptance remain pending**. No actual Baker Hughes technical-unit operating limits are loaded.

## Files and integration

- `skills/liner-hanger-rca/scripts/hypothesis_review.py` — typed `Hypothesis`, `EvidenceAssessment` and `DiscriminatingCheck`; `assess_case()` and JSON adapter.
- `skills/liner-hanger-rca/tests/test_hypothesis_review.py` — synthetic normal/fault cases, competing alternatives, contradictions, evidence-gate and cross-case tests.
- Links directly to **existing** `EvidenceEvent` records in `scripts/evidence_timeline.py`; revalidates event IDs and rejects cross-case references. No GUI or source CSV mutation.

## Investigation policy

`fault_investigation` requires at least two engineer-authored competing hypotheses; `normal_operation_review` may contain zero. Each hypothesis captures a **mechanism question**, title, investigated stage, optional source reference and explicit human-authored evidence relationships (`supports`, `contradicts`, `context`, `unresolved`) with rationale, assessor, and draft/review state. Discriminating checks describe **questions and required retrospective evidence**, not field-operating commands.

Each linked evidence event retains its original type, source IDs, summary, time state, channel information where available, and review status. A contradictory event stays contradictory; an unlinked event is reported for completeness; missing/gap evidence stays unresolved.

- `evidence_gap` may only be `unresolved`.
- `screening_context` (inside a supplied bound) cannot by itself support or contradict a mechanism.
- `screening_candidate` (outside a supplied bound) cannot by itself prove a mechanism; include it as `context` or `unresolved`. A separate engineer-authored source-linked interpretation is needed to make a mechanism-specific argument.
- Even a genuine `measured_observation` or `engineer_annotation` can have different explanations; the link is an **engineer's proposed relationship**, not a diagnostic rule.
- Approximate/unknown event times are not converted into precise ordered times. Events marked `verified` only propagate their original timezone-aware timestamp.
- Multiple events may be correlated or based on the same source; **no independent evidence strength, probability or confidence score** is computed.
- The four `balance` statuses (`mixed_evidence_for_review`, `support_reported_for_review`, `contradiction_reported_for_review`, `insufficient_evidence`) are organisational labels only.
- Every output has `investigation_conclusion: "undetermined"` and `confirmed_failure_mechanism: null`. A later controlled engineer sign-off workflow, not the presence of two evidence links, is required before a conclusion is authorised.

**Important limitations:** This MVP does not establish whether an engineer is authorised; review statuses are user-supplied flags. It does not establish causal exclusivity, relative timing/proximity, physical or hydraulic plausibility for a particular BH configuration, raw sensor integrity, or model-specific applicability. Full model-gated mechanism rules require exact authorised Baker Hughes tool and service-unit references. No automatic root cause, rig safety decision, pump/pressure conversion, or operational advice is produced.

## Run Windows regression

```powershell
cd C:\dev\liner-hanger-project
git pull origin main
cd .\skills\liner-hanger-rca
py -m pytest -rs -q tests
```

Prior user-confirmed full regression: **77 passed in 8.05 seconds** (2026-11-12). Additional tests have been committed but **no new test pass is claimed** until actual execution results arrive.

## Next gated work

Verify results on Windows; independently assess realistic normal and anomalous synthetic case reviews with sources, timeline, equipment identity and alternatives; then add approved case-level sign-off, hypothesis falsification conditions and a traceable report. No scenario can be promoted to a validated BH mechanism without model/size/revision evidence and engineering review.
