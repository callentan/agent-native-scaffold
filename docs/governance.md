# Optional governance and decision records

This page is guidance on fields and ownership, not an approval process. Adopt the forms below only when the current task has an applicable policy, a requirement from an accountable owner, or a decision that must be referenced independently. Small maintenance can keep using the original task and log; do not fabricate a QMS, organizational roles, or approval instances. The existence of these forms does not mean this project is a medical product, and it introduces no clinical, regulatory, or risk classification.

<a id="records"></a>
## Choose records by actual need

| Material to keep | Form and default formal location | Shared method |
|---|---|---|
| Human review, findings, and sourced decisions; waivers where applicable | [Review record](../_templates/items/review-record.md); `verification/REVIEW-NNN-<slug>.md` | [verify-change](../.github/skills/verify-change/SKILL.md#domain-review), read-only by default |
| Tool purpose, evaluation scope, and the actual source of authorization | [Tool qualification and use](../_templates/items/tool-qualification.md); `verification/TQ-NNN-<slug>.md` | [verify-change](../.github/skills/verify-change/SKILL.md); fields are described in the [AI tooling guide](ai-tooling.md) |
| Sourced purpose, users, environment, in-scope and out-of-scope uses, and change proposals | [Intended Use](../_templates/items/intended-use.md); `domain-model/IU-NNN-<slug>.md` | [define-requirements](../.github/skills/define-requirements/SKILL.md#intended-use) |
| References to external risk analysis, controls, and decisions | [Risk control reference](../_templates/items/risk-control.md); `domain-model/RC-NNN-<slug>.md` | [Impact check in verify-change](../.github/skills/verify-change/SKILL.md#impact) |

These are on-demand locations and do not require creating empty directories; existing project locations and original owners stay unchanged. When first organizing purpose material that has already been provided, you may keep a draft following [interview and fact organization](../.github/skills/define-requirements/SKILL.md#interview). A **revision** still requires the existing complete file, its original baseline, and actual authorization; a new form cannot replace a missing original. Review mode returns findings only; the existence of a form does not grant permission to run anything or save records.

<a id="ownership"></a>
## Each field has a single owner

| Information | Sole owner and how to read it |
|---|---|
| This record's identity, scope, content declaration, and actual formal relations | [Existing frontmatter](../domain-model/README.md#artifact-metadata); the body does not repeat the ID or contentState or mirror the relations |
| Original policy, purpose, risk analysis, and acceptance decisions | The owner of the actual source and its fixed baseline; the local form records only the necessary notes and locations and does not take over external authority |
| Review object, criteria, findings, and decision boundaries | The review record body; the "Review conclusion" under `decision` is neither the contentState nor a VT result |
| Tool configuration, proposed use, evaluation, and applicability | The tool use record; the original evaluation steps, observations, and results are still read from the VT or actual report |
| REQ/SR/design requirements and verification results | Their own original artifacts; a review cannot rewrite their results, narrow the acceptance scope, or record missing tests as passed |
| Handoff and derived views | The [log](../logs/README.md) keeps only entry points; model/SWAS reference only sources and baselines and do not copy decision or risk text |

Add `upstream` only for real source relations; add `targets` only for actual acceptance targets with independent criteria. When the review object or an external file has not adopted the metadata, keep plain file/section navigation and do not invent a canonical ID. Downstream impact is a follow-up item and a reading entry point; do not maintain opposing relation tables in multiple places. Artifacts with the same number in different scopes must be located by the full `scope/id#anchor`; a decision from another context cannot confirm this object.

<a id="decisions"></a>
## Decisions, confirmation, and waivers

- A new form stays `draft`. The actual reviewer's and decision maker's name/role declarations, basis of accountability, original decision text, date, object baseline, and scope of applicability each need a source; an Agent self-review must not be called an independent human review. State explicitly who is missing, what evidence is missing, and which conclusion it blocks.
- `confirmed` requires `confirmation.by/reference/baseline` per the existing contract, and only this record's confirmation declaration is stored in the frontmatter. Confirming the record does not mean the tool it covers is approved or the risk is accepted; the original decision may also be a rejection or a request for more evidence. The schema checks only the shape of the declaration and does not authenticate identity, authority, or signatures; the actual decision must still be checked against its original text.
- Record a waiver only when an applicable requirement and an authorized decision actually exist: the waived clause and its baseline, the rationale, the scope/duration or expiry condition, the source of compensating measures, the named decision, and the items needing re-review. Without an authorizer or evidence it is a proposal; an empty form, a checkbox, `Approved`, `Reviewed-by`, a role name, or a commit trailer cannot substitute for it.
- The optional [commit-msg hook](../.github/hooks/README.md) checks the text shape of `Reviewed-by` for managed staged paths, and only after it has been explicitly installed. It does not verify names/roles/emails, generate reviewers, rewrite messages, or approve waivers. Disabling the hook or using the native bypass is not a verified review either; server-side gates need their own real configuration and evidence.
- When the baseline of the object, requirements, tool version/configuration, purpose, or policy changes, keep the original decision and evidence and reassess applicability with the [impact method](../.github/skills/verify-change/SKILL.md#impact). An old pass does not automatically become a new pass, nor can it be rewritten as a historical failure.

<a id="intended-use"></a>
## Intended Use and external risk boundaries

The use record states the actual purpose, users, environment, scope, and excluded uses, and distinguishes current sources from candidate changes. Record patient, clinical, safety, or regulatory sources only when the source material actually involves them; do not prefill product claims, medical classification, or RA approval. An unknown environment, constraint, responsible policy, or decision blocks confirmation of the affected use; the known parts can remain a draft that lists who needs to supply what.

Trace scope- or safety-related changes through the actual context, REQ/QAS, SR, design, interfaces/consumers, risk, and verification, and list section-level differences, escalation needs, and items not run. Escalation targets and conditions follow this project's real policy; without such a policy, ask the accountable owner to decide. Do not assign a classification yourself or assume that every project follows the same chain.

The risk control form only references the actual external analysis, control owners, requirements/design/verification, and acceptance or rejection decisions. It does not calculate risk, fill in default severity or residual scores, or claim compliance with any legal standard. When a source is not provided or unreadable, or a decision is missing, explicitly record accessibility, location clues, accountability gaps, and the blocked judgments; describe nonexistent local files in text and do not create clickable fake evidence.

<a id="source-views"></a>
## Use the existing model source interface

When a model is needed, explicitly select the original artifacts and their real byte/object baselines according to the [existing source contract](../.github/contracts/README.md#model-sources); do not copy summary data separately. Markdown is read directly from the following original owner fields; keep the anchors and the two-column table labels:

| Original record | Required source location |
|---|---|
| review-record | "Review conclusion" and "Limitations and notes" under `decision` |
| risk-control | "Pre-mitigation risk" under `analysis`, the `control` body, "Residual risk" under `residual`, and the actual REQ/VT sources |

Write unknown values as "Not provided: specific missing item" or "Unknown: reason"; do not fabricate conclusions, risk figures, or reverse relations to obtain `available`. A readable source with missing fields/links is `partial`; an optional source that is not provided or unreadable, or whose baseline cannot be verified, is `unverified`. Errors in required primary inputs still fail. The tool qualification form can serve as a governance-related source, but it alone cannot replace the review record that direct governance needs; select sources by their actual relations and do not create an approval chain for the export. A view's `available` means only that the queried sources are complete; it is not substantive approval.

<a id="limits"></a>
## Records and execution permissions

Keep only [minimal tool/task/decision pointers](ai-tooling.md#minimal-record); full sessions, credentials, patient data, or production data are not required. Access sensitive sources through their original authorized entry points, record their access restrictions, and do not copy sensitive content for traceability.

Running, saving records, modifying sources, and sending external notifications are each subject to the current authorization; Markdown, forms, and read-only intent are not ACLs, sandboxes, or client or platform gates. Link actual results and gaps following the [handoff method](../.github/skills/record-handoff/SKILL.md), and do not treat Agent observations as real human participation or native permission tests.
