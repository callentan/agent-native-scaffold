---
schemaVersion: 1
id: AGG-NNN
kind: aggregate
scope: PROJECT/CTX-NNN
contentState: draft
upstream: []
targets: []
---
# AGG-NNN: TBD aggregate candidate

> Optional tactical record; it does not predetermine a consistency boundary. First read the [tactical forms guide](../../domain-model/README.md#tactical-forms) and the [metadata conventions](../../domain-model/README.md#artifact-metadata). Copy it to `domain-model/AGG-NNN-<slug>.md` only when needed. Confirm the project and context, replace `PROJECT/CTX-NNN`, the ID, title, and anchors, fix relative links, keep any existing design, and then delete this hint.

<a id="basis"></a>
## Sources and candidate basis

- Location and baseline of known business facts, UCs, RULEs, and INVs: TBD.
- Candidate reasons for using an aggregate and the limits of that derivation: TBD; without a basis for the boundary, do not promote it to a decision.
- Open questions and who needs to confirm them: TBD.

Upstream declarations live only in the frontmatter. The body explains how the constraints relate to the boundary and does not infer business rules from class structure.

<a id="boundary"></a>
## Responsibility and consistency boundary

| Design information | Content |
|---|---|
| Business responsibility it is proposed to carry | TBD |
| Candidate root, business identity, and their source | Not decided |
| Candidate internal entities/value objects and reasons for including them | Not decided |
| Facts explicitly outside the boundary and their owners | TBD |
| RULEs/INVs that must be maintained together and when they apply | TBD: navigation to the source text and rationale |
| Evidence still missing for the boundary choice, or alternatives | TBD |

<a id="lifecycle"></a>
## Lifecycle and actions

| Known business state or action | Preconditions and constraints to maintain | Forbidden side effects or unknown policies | Source |
|---|---|---|---|
| TBD | TBD | TBD | TBD |

<a id="collaboration"></a>
## Collaboration outside the boundary

- Other owners, required facts, and direction of collaboration: TBD.
- Candidates for cross-boundary identity references and for published facts/events: Not decided.
- Concurrency, consistency, failure handling, and the basis for these decisions: Not provided; do not assume a transaction, lock, or messaging solution.

<a id="questions"></a>
## Open items and impact

- Missing boundary, identity, or rule evidence and related BLs: TBD.
- Accountable owner and next step: TBD.
- Old and new baselines, and related design and scenario/VT items pending re-review: TBD; this form does not prove that software implements the constraints.
