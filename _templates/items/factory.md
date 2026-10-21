---
schemaVersion: 1
id: FAC-NNN
kind: factory
scope: PROJECT/CTX-NNN
contentState: draft
upstream: []
targets: []
---
# FAC-NNN: TBD factory candidate

> Optional record of a creation responsibility; it does not require the Factory pattern. First read the [tactical forms guide](../../domain-model/README.md#tactical-forms) and the [metadata conventions](../../domain-model/README.md#artifact-metadata). Copy it to `domain-model/FAC-NNN-<slug>.md` only when needed; confirm and replace `PROJECT/CTX-NNN`, the ID, title, and anchors, fix relative links, keep any existing creation rules, and then delete this hint.

<a id="basis"></a>
## Sources and candidate basis

- Known creation behavior with UC/RULE/INV sources and versions: TBD.
- Candidate reasons for a separate creation responsibility: TBD; simple construction does not need a separate factory.
- Open questions and who needs to confirm them: TBD.

The frontmatter holds the upstream; the body explains what creation means and does not copy a set of business rules.

<a id="creation"></a>
## Creation responsibility

| Design information | Content |
|---|---|
| What is created and the business reason | TBD |
| Required inputs, preconditions, and the owner of each fact | TBD |
| Initial state and constraints that must be maintained | TBD: navigation to the source text |
| Responsibility for generating and assigning identities/values | Not decided |
| Business result observable after success | TBD |
| Result and forbidden side effects when creation is not possible | Not provided; do not assume partial success or automatic retry |

<a id="collaboration"></a>
## Collaborators and boundaries

- Callers, required domain collaborators, and direction: TBD.
- Which validations belong to source rules and which still lack a decision: TBD.
- Division of responsibility between creation and the subsequent lifecycle, persistence, and publication: TBD; this form does not automatically authorize storage or messaging side effects.

<a id="questions"></a>
## Open items and evolution

- Missing creation/identity/failure rules and related BLs: TBD.
- Who needs to supply what, old and new baselines, and affected materials: TBD.
