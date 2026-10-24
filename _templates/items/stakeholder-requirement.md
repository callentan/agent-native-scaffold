---
schemaVersion: 1
id: REQ-NNN
kind: stakeholder-requirement
scope: PROJECT/CTX-NNN
contentState: draft
upstream: []
targets: []
---
# REQ-NNN: TBD

> Blank form; not a confirmed requirement. Read the [stakeholder requirement guide](../../stakeholder-requirements/README.md#req-writing) and [domain input conventions](../../stakeholder-requirements/README.md#domain-inputs) first; copy to `stakeholder-requirements/REQ-NNN-<slug>.md` as needed. Confirm and replace `PROJECT/CTX-NNN`, placeholder IDs, title, and anchors; keep existing content, check links from the actual location, then delete this notice.

<a id="basis"></a>
## Source basis

| Field | Content |
|---|---|
| Proposer, source, and locatable basis | TBD |
| Record date and source baseline | TBD; without confirmation, do not write approved |
| Related product goals, users, or stakeholders | TBD: cite the product description; do not write a separate PRD |
| Business meaning and source explanation of domain inputs | TBD: applicable concepts, contexts, CAP/UC, RULE/INV, or QAS; links to the original text are for navigation only; if not applicable, say so |

Identity, scope, content state, and parseable upstream are maintained only in the frontmatter, following the [metadata conventions](../../domain-model/README.md#artifact-metadata). The body keeps no second relationship/status table; old domain sources without metadata still use plain relative links. A confirmation statement needs a real source and a confirmed baseline and cannot be prefilled.

<a id="business-need"></a>
## Business need and scope

- One business need and its rationale: TBD.
- Applicable objects, preconditions, and scope: TBD.
- Non-goals and constraint sources: TBD.
- Open facts and their impact on this requirement: TBD.

Rule text stays in the domain model; here, cite the rules and explain the need without a second copy of rule values or text.

<a id="acceptance"></a>
## Business acceptance

Copy the block for each item. Use a unique ID that includes the owning REQ and a fixed ASCII anchor; `AC-01` alone is not enough. All content is TBD; the example ID is not a formal acceptance criterion.

<a id="req-nnn-ac-01"></a>
### REQ-NNN-AC-01: TBD

| Item | Content |
|---|---|
| Business preconditions and scenario scope | TBD |
| Business action or trigger | TBD |
| Observable business outcome and pass criterion | TBD |
| Boundaries, exceptions, or forbidden outcomes | TBD; keep undefined parts open |
| Related rules/contexts and confirmation source | TBD: ID, stable link, and basis |

Run results are not recorded here. The VT holds its business acceptance targets and is found by searching for the full ID; a missing VT or a not-run status is not a pass, and passing software checks do not automatically prove that this item holds.

<a id="changes"></a>
## Changes and open items

| Date and baseline | Change or content to be confirmed | Source, rationale, and confirmation status |
|---|---|---|
| TBD | TBD | To be confirmed |

When an acceptance criterion is withdrawn or renamed, keep its basis and historical references and do not reuse the old ID; after a change, check the semantic impact on downstream software requirements, design, and verification.
