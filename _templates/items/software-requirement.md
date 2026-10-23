---
schemaVersion: 1
id: SR-NNN
kind: software-requirement
scope: PROJECT/CTX-NNN
contentState: draft
upstream: []
targets: []
---
# SR-NNN: TBD

> Blank form; not a confirmed software specification. Read the [software requirement guide](../../software-requirements/README.md#sr-writing) and the [metadata conventions](../../domain-model/README.md#artifact-metadata) first, then copy it to `software-requirements/SR-NNN-<slug>.md` as needed. Replace `PROJECT/CTX-NNN`, the ID, the title, and anchors only after the project/context is clear; delete this notice and check the relative links from the actual location; do not migrate old material.

<a id="basis"></a>
## Basis, context, and scope

| Field | Content |
|---|---|
| Source reading navigation, baselines, and derivation rationale | TBD: original text and versions of the actual REQ/UC/INV/CAP/QAS, and which facts support this specification |
| Standalone maintenance task basis (when applicable) | TBD: location, completion conditions, and authorization of the actual request/issue; do not invent an artifact identity |
| Owning context and business boundaries | TBD |
| Explanation of related domain concepts and rules | TBD: navigation to the original text and applicability; do not copy the rule text |
| Record date and proposer | TBD; this SR's content state and confirmation statements belong in the frontmatter |
| Scope and non-goals for this work | TBD |

The frontmatter `upstream` is the only place for declared upstream relationships, using actual `scope/id#anchor` values. This section only explains the sources and where to read them; it does not maintain another mapping or status table. When an old lightweight source or standalone request has no canonical identity, keep a plain link and record the missing item; do not invent IDs to get through the parser. While sources are unconfirmed, keep only candidates and questions; do not promote a draft INV or a code constant to a mandatory software requirement.

<a id="behavior"></a>
## Software behavior and boundaries

| Condition or situation | Required software behavior and observable output | Error handling, forbidden side effects, or boundaries | Sources and open items |
|---|---|---|---|
| Normal/allowed condition: TBD | TBD | TBD | TBD |
| Boundary condition: TBD | TBD | TBD | TBD |
| Rejection condition: TBD | TBD | TBD | TBD |
| Error or invalid input: TBD | TBD | TBD | TBD |

UCs provide paths, INVs explain the constraints of the source rules, CAPs/contexts describe responsibilities, and QASs provide sourced quality criteria; adopt only the inputs that this task needs and that can be read. When policies for errors, concurrency, failure, or side effects are missing, ask about each one; do not fill them in with common implementations.

<a id="interfaces"></a>
## Interface and responsibility agreements (when applicable)

| Provider → user | Inputs, outputs, and their meaning | Fact owner and responsibility boundary | Agreement on failure or unmet preconditions | Source and confirmation status |
|---|---|---|---|---|
| TBD | TBD | TBD | To be confirmed | TBD |

If there is no interface, state why it does not apply; keep undecided protocols, timing, or implementations open, and do not derive business decisions from technical habits.

<a id="acceptance"></a>
## Software acceptance

Give each item a software result that can be judged. When copying the block, change the full ID and anchor. `NNN` is only a placeholder and must not be kept as a real number.

<a id="sr-nnn-ac-01"></a>
### SR-NNN-AC-01: TBD

| Item | Content |
|---|---|
| Reading navigation and rationale for this item's refinement basis | TBD: explain how the declared sources support this item; relationships still belong in the frontmatter |
| Preconditions, inputs, and actions | TBD |
| Expected software behavior and per-item pass criteria | TBD |
| Related boundaries, errors, and side effects that must not occur | TBD |
| Rule references and parts not yet clarified | TBD |

VTs reference this item directly, without requiring a US. Test identifiers, run results, and applicability are recorded by the VT and raw reports; this table does not maintain another copy of verification results.

<a id="changes"></a>
## Changes and open items

| Date and baseline | Change or question and its impact | Source, confirmation basis, or who must confirm |
|---|---|---|
| TBD | TBD | TBD |

Changes, withdrawals, or renames keep their historical basis, and old IDs are not reused. When upstream rules change, re-review the boundaries, acceptance, and linked VTs even if this file did not copy the specific values.
