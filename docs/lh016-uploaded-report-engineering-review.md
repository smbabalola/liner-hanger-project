# LH-016 — Uploaded synthetic report content review

**Date:** 2026-11-12  
**Basis:** User-uploaded local exports `lh003-normal-synth.md`, `lh003-normal-synth.json`, `lh003-anomalous-synth.md`, `lh003-anomalous-synth.json` generated after **133 passed in 8.92 s**.  
**Outcome:** Functional artifact generation **confirmed**; report engineering acceptance **not granted**. These are fictional synthetic fixtures, not a real BH job.

## Verified behaviour

- Both JSON/Markdown exports exist and agree on status `draft_unapproved`, review `not_completed`, and conclusion `undetermined`.
- Normal case: 2 within-screening-context events, no forced mechanism, approximate daily report unplaced; internal reference MD 1501.2 m is explicitly synthetic.
- Anomalous case: 1 within-screening-context, 1 outside-screening candidate, 1 unverifiable cement measurement, two competing hypotheses, surface hookload interpretation and uncertain daily report; internal geometry unavailable.
- Cement unit discharge is **not** inferred from rig standpipe pressure. Report describes source/sensor mismatch.
- Earliest screening candidate at 08:10 is explicitly **not** the proven initial failure; no tool state asserted.

## Engineering / audit defects to fix before LH-016 acceptance

1. **P1 — Ambiguous event ID timestamps:** The unverifiable cement event is unplaced (JSON `timestamp:null`, `time_state:unknown`) but event ID embeds `2026-01-01T08:20:00Z`. Separate stable opaque event ID from reported/raw source sample time and verified event time; do not emit misleading temporal identity.
2. **P1 — Numeric findings omitted in human report:** For within/outside/unverifiable screening, the human-readable artifact does not display the observed numerical quantity, configured bound, unit, pressure basis, sensor location, comparison applicability or calculation reference. For hookload, event provides no recorded magnitude; preserve as unavailable rather than inventing one. Add verified sourced fields to reporting contract after checking upstream model availability.
3. **P1 — Hypothesis link rationale omitted:** JSON report lists for/against event IDs but loses assessment rationale and assessor identity visible in LH-003 source fixture; a professional report must make why an event supports/contradicts a hypothesis inspectable, with original provenance and status.
4. **P1 — Source locator/revision absent:** Synthetic source IDs alone are insufficient for field investigation. Add source-location/page/line/row/channel and revision fields where supplied; fail transparently on absent values instead of inventing. Model-specific BH verification pending.
5. **P2 — Same-timestamp ordering:** At 08:12 both measured observation and annotation occur. They are sorted but the document must note simultaneity/no established causal ordering.
6. **P2 — Normal-case outcome language:** Clearly distinguish “no screened deviations in these samples” from verified successful setting/operation; `undetermined` status still appropriate.
7. **P2 — Rendering usability:** Extremely long event IDs obscure chronology and gap lists. Provide stable short display labels with exact IDs still available in evidence index/JSON, and plain-language descriptions for `unlinked_event_ids`.

## Release boundary

These findings do **not** invalidate the software regression; they constrain its acceptance claim. The engineer has not verified actual tool settings, accepted a root-cause finding, or signed this review. No job-package generation/UI tasks are approved by this document.
