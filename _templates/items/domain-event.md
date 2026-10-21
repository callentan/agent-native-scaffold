---
schemaVersion: 1
id: EVT-NNN
kind: domain-event
scope: PROJECT/CTX-NNN
contentState: draft
upstream: []
targets: []
---
# EVT-NNN: TBD domain event candidate

> Optional modeling record for a business fact that has occurred; not a message publication or a delivery guarantee. First read the [tactical forms guide](../../domain-model/README.md#tactical-forms) and the [metadata conventions](../../domain-model/README.md#artifact-metadata). Copy it to `domain-model/EVT-NNN-<slug>.md` only when needed; confirm and replace `PROJECT/CTX-NNN`, the ID, title, and anchors, fix relative links, keep any existing fact definitions, and then delete this hint.

<a id="basis"></a>
## Sources and candidate basis

- Known business facts and actions with UC/RULE/INV sources and versions: TBD.
- Candidate reasons for recording it as an event: TBD; do not infer from a message class that a business fact has already occurred.
- Open questions and who needs to confirm them: TBD.

Upstream belongs in the frontmatter; the body owns the event's meaning and lifecycle constraints.

<a id="meaning"></a>
## Occurrence conditions and fact ownership

| Event information | Content |
|---|---|
| Fact that has occurred, as the event expresses it | TBD; a command still waiting to run cannot substitute for it |
| Conditions under which the occurrence can be established, and at what point in time | Not provided |
| Producer and fact owner | TBD |
| Business meaning of the identity, associated objects, and time of occurrence | Not decided |
| Basis for the triggering rule/invariant and for revocation or correction | TBD: navigation to the source text; if unknown, record a question |

<a id="values"></a>
## Information elements

| Business element | Meaning, unit, or referenced identity | Basis for validity/visibility, and gaps |
|---|---|---|
| TBD | TBD | TBD |

Record only the necessary business information here; do not invent a wire schema, topic, database, or broker.

<a id="consumers"></a>
## Consumption and versioning

- Known consumers, their purposes, and the information they need: TBD; keep unknown consumers open.
- Semantic version, compatibility, and the Published Interface source: Not provided.
- Agreements on duplication, ordering, loss, timeliness, and failure handling: Not provided; no delivery semantics are promised.
- Responsibility for publication, correction, and revocation, and the lifecycle impact: Not decided.

<a id="questions"></a>
## Open items and evolution

- Missing evidence on occurrence conditions, consumers, or versions, and related BLs: TBD.
- Who needs to supply what, old and new baselines, and notification proposals: TBD; do not publish events or send notifications automatically.
