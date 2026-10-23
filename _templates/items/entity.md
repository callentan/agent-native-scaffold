---
schemaVersion: 1
id: ENT-NNN
kind: entity
scope: PROJECT/CTX-NNN
contentState: draft
upstream: []
targets: []
---
# ENT-NNN: TBD entity candidate

> Optional tactical record; entities are not generated automatically from nouns. First read the [tactical forms guide](../../domain-model/README.md#tactical-forms) and the [metadata conventions](../../domain-model/README.md#artifact-metadata). Copy it to `domain-model/ENT-NNN-<slug>.md` only when needed. Confirm the project and context, replace `PROJECT/CTX-NNN`, the ID, title, and anchors, fix relative links, keep any existing business meaning, and then delete this hint.

<a id="basis"></a>
## Sources and candidate basis

- Known concepts and business facts with source location and version: TBD.
- Candidate reasons for needing a persistent identity: TBD; business identity cannot be derived from a database primary key.
- Open questions and who needs to confirm them: TBD.

Upstream belongs in the frontmatter; the body explains the entity's role and the basis for its rules.

<a id="identity"></a>
## Identity and responsibility

| Design information | Content |
|---|---|
| Business responsibility this concept carries | TBD |
| How the same object is recognized throughout its lifecycle | Not decided |
| How identity is created, its uniqueness scope, and the basis for invalidating it | Not provided |
| Mutable business state and its meaning | TBD |
| Difference from objects with equal values but a different identity | To be confirmed |
| Basis for deciding the owning boundary or aggregate | Not decided; do not infer it from the form's directory |

<a id="lifecycle"></a>
## Lifecycle and rules

| Action or state change | Conditions and RULEs/INVs to maintain | Rejection/termination/recovery boundaries | Source and gaps |
|---|---|---|---|
| TBD | TBD: navigation to the source text | TBD | TBD |

<a id="collaboration"></a>
## Collaboration and references

- Associated business concepts, direction, and cardinality constraints: TBD.
- Facts used but not owned, and their owners: TBD.
- Collaborators needed for creation/change and the basis for passing identity: TBD; do not assume a repository, table schema, or API.

<a id="questions"></a>
## Open items and evolution

- Identity, lifecycle, or boundary gaps and related BLs: TBD.
- Who needs to supply what, old and new baselines, and impact: TBD.
