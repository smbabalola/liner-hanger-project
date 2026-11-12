# Evidence intake, reviewed rule extraction, and case learning

## A. Before training PDFs are ingested
1. Confirm uploader's right to supply and use each document, its confidentiality classification, and whether it can be processed for this project. Restrict raw files and extracted knowledge to the intended tenant/customer.
2. Register PDF/document identity: filename, manufacturer/tool family, part number, revision, publication date, page count, rights, origin and checksum. Retain page/section references and all relevant caveats.
3. Extract candidate **concepts**, **process steps**, **required checks**, **numeric thresholds/units**, **conditional branches** and **tool configurations** independently. Treat diagrams and captions as potentially meaningful; use reviewed page images where text extraction is incomplete.
4. Mark each extraction `unreviewed`, `engineer_approved`, `rejected`, `superseded`, or `ambiguous`. Store direct source pointer (file/page/section). Do not promote numeric limits without an engineer checking tool model, configuration and revision.
5. Explicitly resolve conflicts. A general course handout cannot override current job-specific approved procedures. Store revisions side-by-side and their effective use dates.

## B. Source precedence for a particular investigation
1. Approved job procedure/work pack and approved deviations/change controls for **that job**.
2. Approved OEM instructions/specifications that match the physical tool and revision.
3. Measured rig data, original logs and verified job narratives as **observations** — never as prescriptive limits.
4. Reviewed comparable cases as contextual precedents, with similarities and differences.
5. Public manufacturer/product background as explanatory context only.
Conflict must be surfaced to the engineer; evidence types should not be flattened into one unqualified 'truth'.

## C. Convert a procedure into stage checks
Each check contains `step_id`, `stage`, `condition`, `parameter`, `operator`, `specified_value`, `unit`, `measurement_location`, `tolerance`, `hold_time`, `validation_method`, `source_ref`, `review_status`. Do not insert defaults for absent numeric fields. Distinguish `measurable_from_log`, `manual_verification`, `not_verifiable` and `indeterminate_due_to_data_quality`.

## D. Replay and learning
Link each detected event to a time interval, depth interval, synchronized telemetry, linked procedure requirement, source IDs and engineer notes. Classify the event as `procedural_deviation`, `unexpected_pattern`, `data_quality_issue`, or `possible_mechanical_event`. Preserve alternative explanations.
Record final outcome as `not_investigated`, `suspected`, `probable`, `confirmed_by_engineer`, or `undetermined`, with verifier, evidence and competing hypotheses. A historical replay **without** a documented outcome is still useful but is *not* labelled training truth.

## E. Outputs and safeguards
The assistant can identify candidate deviations and prepare investigation summaries, but must not remotely direct field operations. Real-time incidents and barrier implications go through operator well-control/HSE procedures and an authorized competent engineer. Do not share customer-specific records between tenants without authorization.
