# Product description and stakeholder requirements

This directory takes the place of a PRD: product goals, users, scope, and constraints are maintained here, and each REQ records only one stakeholder requirement and its business acceptance. Domain rules belong in the [domain model](../domain-model/README.md) and software behavior in the [software requirements](../software-requirements/README.md); do not treat an entire PRD as a single REQ.

<a id="product"></a>
## Product description (TBD)

| Content | Confirmed information or questions to be confirmed |
|---|---|
| Product goal, problem to solve, and value | TBD |
| Users, operators, and related stakeholders | TBD |
| Observable basis for business success | TBD; do not prefill it as achieved |
| In-scope items | TBD |
| Out-of-scope items | TBD |
| Business, compliance, and delivery constraints | To be confirmed |
| Fact sources, confirmer, and date | TBD |
| Open questions, their impact, and who needs to confirm them | TBD |

An unfilled section does not mean "no constraints". When a fact that affects behavior is missing, clarify it first; an open item that only affects later work can remain open, with a stated reason why it does not block the current task.

<a id="req-writing"></a>
## Write a REQ

1. Look up existing requirements and [domain facts](../domain-model/README.md#sources), and confirm the sources, current status, applicable contexts, and rules. Do not automatically turn a proposal into an approved item.
2. When a new requirement is needed, use the [REQ form](../_templates/items/stakeholder-requirement.md) and save it as `stakeholder-requirements/REQ-NNN-<slug>.md`. `NNN` and `<slug>` are placeholders; the number is assigned when the real artifact is created.
3. Write one business need, its applicable scope, non-goals, and observable business acceptance. Reference domain rules instead of maintaining a duplicate copy of their values or full text; the acceptance states the conditions and method for judging that the goal is met.
4. Give each acceptance criterion a full ID and a stable ASCII anchor, for example `REQ-NNN-AC-01` with `req-nnn-ac-01`. Number multiple acceptance criteria individually, and keep the ID when the wording changes; a withdrawn criterion keeps its change basis, and its old number is never reused.
5. Follow the [verification guide](../verification/README.md#coverage-check): start from all acceptance criteria to find business acceptance VTs. Passing SR tests do not automatically prove that REQ business acceptance has passed.

Links between formal files take the following form; this only illustrates the syntax and is not an existing requirement:

```markdown
[REQ-NNN-AC-01](REQ-NNN-<slug>.md#req-nnn-ac-01)
```

An SR keeps its own upstream REQ links, and a VT keeps its own target links. To find downstream items, search in reverse; do not maintain another mapping or verification results in the REQ. A standalone maintenance request can serve directly as the task basis; there is no need to invent a REQ.

<a id="domain-inputs"></a>
## Use optional domain inputs

When there are many sources, you can reference existing SD/CTX, CAP, UC, RULE, INV, and QAS; for the forms and default locations, see the [domain artifact guide](../domain-model/README.md#strategic-forms). They are not a mandatory prerequisite chain for a REQ, and existing rules in the lightweight README remain valid sources. A REQ states the business need and acceptance; domain facts and rule text are still read from their original owners.

The new [REQ form](../_templates/items/stakeholder-requirement.md) declares identity, scope, content state, and upstream in the frontmatter; the body only explains why the sources support this requirement. Replace placeholders according to the [metadata conventions](../domain-model/README.md#artifact-metadata); do not convert old REQs automatically or change existing acceptance IDs/anchors. Old sources without metadata keep ordinary links; do not invent canonical keys. Open requirement questions and business source gaps must name the accountable owner; a fully filled-in form is no substitute for confirmation.

When the current task genuinely has an intended-use or risk basis, reference the [optional Intended Use/risk control materials](../domain-model/README.md#governance-forms) and their original source/decision baselines; the product description does not keep its own copy of the intended-use or risk text. An unknown environment, scope limitation, or governing policy blocks confirmation of the related requirements; for candidate changes, first list the impact according to [intended use revision](../.github/skills/define-requirements/SKILL.md#intended-use), and do not assume new product claims or regulatory classifications by default.

<a id="quality-inputs"></a>
## Quality attribute inputs

When a standalone quality requirement is needed, use the [QAS form](../_templates/items/quality-attribute-scenario.md) and save it as `stakeholder-requirements/QAS-NNN-<slug>.md`; do not store quality metrics separately in domain rules or in the product description.

- Fill in the source of stimulus, stimulus, environment, object, response, and response measure separately, stating the source and scope of each.
- A measure needs an observable criterion, a unit/statistical definition or another way of judging, and its basis. Without a value or method, keep `draft`, record the specific gap, and name who needs to confirm it; do not fill in a typical SLA, regulatory classification, or platform guarantee.
- A QAS's standalone criteria use owner-qualified acceptance IDs/anchors; [validation scenarios or VTs](../verification/README.md#domain-scenarios) reference the specific items. For non-behavioral concerns, keep only the specification and the inputs still needed; do not force an executable scenario.
- When the requirement baseline changes, re-review the semantic impact on UCs, design, and verification, and keep the original run baselines and results. Filling in a QAS or passing schema validation does not mean that quality acceptance has passed.

<a id="requirements"></a>
## Formal requirement entry points

There are no formal REQs yet. After creating a real requirement, append a link to its file here; each REQ is authoritative for its own text, acceptance criteria, and status, and coverage gaps are listed in the [verification index](../verification/README.md#coverage-index).
