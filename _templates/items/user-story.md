---
schemaVersion: 1
id: US-NNN
kind: user-story
scope: PROJECT/CTX-NNN
contentState: draft
upstream: []
targets: []
---
# US-NNN: TBD

> Optional delivery form; not a second copy of the requirements. Read the [delivery guide](../../user-stories/README.md) and the [metadata conventions](../../domain-model/README.md#artifact-metadata) first, then copy it to `user-stories/US-NNN-<slug>.md` as needed. When an existing maintenance request or issue is sufficient, no US is needed. Once the project/context is clear, replace all placeholders, delete this notice, and check the relative links.

<a id="task"></a>
## Task and scope

| Field | Content |
|---|---|
| Task progress | todo (not started); distinct from the frontmatter content state |
| Source reading navigation and rationale for adoption | TBD: original text and baseline of the actual SR, UC/INV, REQ, or issue; artifact relationships belong in upstream |
| Beneficiaries and delivered value | TBD: use only roles and goals from the sources; without participant material, list it as a missing item |
| Delivery goal for this story | TBD; do not copy the requirement text |
| Normal/alternative/rejection paths and invariants in this slice | TBD: navigation to the original acceptance and the slicing rationale; do not write a separate set of ACs |
| Included work and change locations | TBD |
| Excluded work | TBD |
| Dependencies, prerequisite inputs, and owners | TBD |
| Source of completion conditions | TBD: cite the original acceptance or task agreement |

`upstream` declares the actual sources, and `contentState` and confirmation records belong in the frontmatter; the table above does not store these fields again. A formal delivery slice based on an SR must verify the confirmation basis of the SR and any applicable UC/INV; the word Approved alone or a draft source is not enough to establish an implementable commitment. An existing standalone maintenance request is not forced into a US because of this.

<a id="checklist"></a>
## Implementation checklist

- [ ] TBD: one concrete work item and its inputs.
- [ ] TBD: related verification and record work.

The checklist only tracks work; it does not add a new set of business/software acceptance criteria. Split by value and verifiable scope, not forcibly by fixed technical layers; task progress can change to `in-progress`, `blocked`, `review-ready`, or `done`, and each change leaves its actual basis. When upstream changes, first re-review the slice and its verification impact; do not automatically roll back content statements or overwrite old results.

<a id="records"></a>
## Record entry points

| Content | Actual link or missing item |
|---|---|
| Changed artifacts, implementation, or review records | TBD |
| VTs, standalone maintenance checks, and raw results | TBD; no run records yet |
| Development log and handoff | TBD |
| Gaps, items pending re-review, and items not run | TBD |
| Blockers, basis for scope changes, and next steps | TBD |

VTs trace directly back to REQ/SR, necessary design, or standalone maintenance completion conditions; a US is not a mandatory layer. `done` does not automatically mean the requirement passed acceptance, was merged, or went live.
