# Delivery slices and implementation checklists

A US organizes the scope, steps, status, and record links of one delivery; it is not a second copy of the requirements. When a delivery slice is needed, use the [US form](../_templates/items/user-story.md) and save it as `user-stories/US-NNN-<slug>.md`; there are no formal USs yet.

<a id="delivery"></a>
## When to use

When related work needs to be implemented in steps or its scope needs to be tracked separately, you can create a US; for the activity entry point, see the [specify-feature delivery slice](../.github/skills/specify-feature/SKILL.md#delivery-slice). When an existing maintenance request, defect, or issue already states the goal, scope, basis, and completion conditions, use it directly; do not force it into a user story, and do not require completing REQ/SR/US/ABB first.

## Filling in and completion

- In the new form, fill in the identity and scope that are already clear, the draft content state, and `upstream` according to the [metadata conventions](../domain-model/README.md#artifact-metadata). The body only navigates to the actual task basis, REQ/SR, UC/INV, and baselines and explains the value of the slice, without keeping a separate copy of upstream or content state; old materials are not required to migrate.
- A formal slice based on an SR must first check the real confirmation basis of the applicable sources; an unconfirmed SR/INV does not produce an implementable commitment. The benefiting role, normal/alternative/rejection paths, and constraints come from the original text; do not add actors or invent separate ACs just to fit the story sentence pattern.
- List the change locations, dependencies, and implementation checklist according to user value, risk, and independently verifiable scope; do not force a split by fixed technical layers. Requirement text, rules, and acceptance criteria are still read from their sources; ticking off work items neither creates new acceptance criteria nor replaces VTs.
- Record **Task progress** with `todo`, `in-progress`, `blocked`, `review-ready`, or `done`; it is separate from `contentState` in the frontmatter, starts as `todo`, and its completion basis must not be prefilled.
- Reference the [verification records](../verification/README.md) and [related logs](../logs/README.md), and keep gaps, items pending re-review, and items not run. `done` only means that the agreed task is complete; it does not automatically mean that business acceptance has passed or that the work has gone live.

A VT points directly to the REQ, SR, necessary design, or standalone maintenance completion conditions it verifies; a US is not a mandatory traceability layer. ABBs and VTs depend only on the inputs each needs; neither requires completing a US first or waiting for the other. When the upstream or the slice scope changes, first check the acceptance criteria, unknowns, and the applicability of old results, and propose progress/scope revisions that need confirmation; do not automatically mark them as confirmed or hide gaps by narrowing the scope.
