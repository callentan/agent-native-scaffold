---
schemaVersion: 1
id: DS-NNN
kind: domain-service
scope: PROJECT/CTX-NNN
contentState: draft
upstream: []
targets: []
---
# DS-NNN: TBD domain service candidate

> Optional record of a domain operation; not an application-service or network-service design. First read the [tactical forms guide](../../domain-model/README.md#tactical-forms) and the [metadata conventions](../../domain-model/README.md#artifact-metadata). Copy it to `domain-model/DS-NNN-<slug>.md` only when needed; confirm and replace `PROJECT/CTX-NNN`, the ID, title, and anchors, fix relative links, keep any existing division of responsibilities, and then delete this hint.

<a id="basis"></a>
## Sources and candidate basis

- Known domain behavior with UC/RULE/INV sources and versions: TBD.
- Candidate reasons why the operation does not fit an existing entity/value object: TBD.
- Open questions and who needs to confirm them: TBD.

Upstream declarations belong in the frontmatter; the body describes the business operation and its responsibilities. The existence of a service class does not prove that this pattern is needed.

<a id="operation"></a>
## Domain operation

| Design information | Content |
|---|---|
| Business meaning and goal of the operation | TBD |
| Inputs, preconditions, and fact owners | TBD |
| Outputs, postconditions, and the basis for judging them | TBD |
| RULEs/INVs used and the boundaries where they apply | TBD: navigation to the source text |
| Facts that may change and facts that must explicitly not change | TBD |
| Rejections, exceptions, and undefined policies | TBD |

<a id="collaboration"></a>
## Collaboration and division of responsibility

- Required collaborators, direction, and their respective responsibilities: TBD.
- Ownership of non-domain duties such as orchestration, authorization, transport, and persistence: Not decided; do not fold them into the domain service automatically.
- Business basis for state/lifecycle, ordering, or concurrency constraints: Not provided.

<a id="questions"></a>
## Open items and evolution

- Gaps in ownership, collaboration, or policy, and related BLs: TBD.
- Who needs to supply what, old and new baselines, and impact: TBD.
