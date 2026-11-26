# Stakeholder requirements guide

This directory holds product scope, stakeholder requirements (REQ), and quality attribute scenarios (QAS). Keep this `README.md` as a static writing guide: maintain product goals, users, scope, and constraints in [product.md](product.md#product), and high-level area navigation in [INDEX.md](INDEX.md) when needed. Domain rules belong in the [domain model](../domain-model/README.md) and software behavior in the [software requirements](../software-requirements/README.md); do not treat an entire PRD as a single REQ.

<a id="req-writing"></a>
## Write a REQ

1. Look up existing requirements and [domain facts](../domain-model/README.md#sources); confirm sources, current status, applicable contexts, and rules. Do not turn a proposal into an approved item automatically.
2. For a new requirement, use the [REQ form](../_templates/items/stakeholder-requirement.md) and save it as `stakeholder-requirements/REQ-NNN-<slug>.md`. `NNN` and `<slug>` are placeholders; the number is assigned when the real artifact is created.
3. Write one business need, its applicable scope, non-goals, and observable business acceptance. Reference domain rules instead of duplicating their values or text; the acceptance states the conditions and method for judging that the goal is met.
4. Give each acceptance criterion a full ID and a stable ASCII anchor, for example `REQ-NNN-AC-01` with `req-nnn-ac-01`. Number each criterion individually and keep its ID when the wording changes; a withdrawn criterion keeps its change basis, and its old number is never reused.
5. Follow the [verification guide](../verification/README.md#coverage-check): start from all acceptance criteria to find business acceptance VTs. Passing SR tests do not automatically prove that REQ business acceptance has passed.

Links between formal files take this form; it illustrates syntax only and is not an existing requirement:

```markdown
[REQ-NNN-AC-01](REQ-NNN-<slug>.md#req-nnn-ac-01)
```

An SR keeps its own upstream REQ links, and a VT its own target links. To find downstream items, search in reverse; do not maintain another mapping or verification results in the REQ. A standalone maintenance request can serve directly as the task basis; there is no need to invent a REQ.

<a id="domain-inputs"></a>
## Use optional domain inputs

With many sources, you may reference existing SD/CTX, CAP, UC, RULE, INV, and QAS (forms and default locations: [domain artifact guide](../domain-model/README.md#strategic-forms)). These are not a mandatory prerequisite chain for a REQ, and existing rules in the [lightweight domain overview](../domain-model/overview.md) remain valid sources. A REQ states the business need and acceptance; domain facts and rule text are still read from their original owners.

The new [REQ form](../_templates/items/stakeholder-requirement.md) declares identity, scope, content state, and upstream in the frontmatter; the body only explains why the sources support the requirement. Replace placeholders per the [metadata conventions](../domain-model/README.md#artifact-metadata); do not convert old REQs automatically or change existing acceptance IDs/anchors. Old sources without metadata keep ordinary links, and no canonical keys are invented. Open requirement questions and business source gaps must name the accountable owner; a fully filled-in form is no substitute for confirmation.

When the current task genuinely has an intended-use or risk basis, reference the [optional Intended Use/risk control materials](../domain-model/README.md#governance-forms) and their original source/decision baselines; the product description keeps no copy of intended-use or risk text. An unknown environment, scope limitation, or governing policy blocks confirmation of related requirements; for candidate changes, first list the impact per [intended use revision](../.github/skills/define-requirements/SKILL.md#intended-use), and do not assume new product claims or regulatory classifications by default.

<a id="quality-inputs"></a>
## Quality attribute inputs

When a standalone quality requirement is needed, use the [QAS form](../_templates/items/quality-attribute-scenario.md) and save it as `stakeholder-requirements/QAS-NNN-<slug>.md`; do not store quality metrics separately in domain rules or in the product description.

- Fill in the source of stimulus, stimulus, environment, object, response, and response measure separately, stating the source and scope of each.
- A measure needs an observable criterion, a unit/statistical definition or another way of judging, and its basis. Without a value or method, keep `draft`, record the specific gap, and name who needs to confirm it; do not fill in a typical SLA, regulatory classification, or platform guarantee.
- A QAS's standalone criteria use owner-qualified acceptance IDs/anchors; [validation scenarios or VTs](../verification/README.md#domain-scenarios) reference the specific items. For non-behavioral concerns, keep only the specification and the inputs still needed; do not force an executable scenario.
- When the requirement baseline changes, re-review the semantic impact on UCs, design, and verification, and keep the original run baselines and results. Filling in a QAS or passing schema validation does not mean that quality acceptance has passed.

## Navigation and discovery

Individual `REQ-NNN-<slug>.md` and `QAS-NNN-<slug>.md` files are authoritative for their own text, acceptance criteria, and status, and are discovered directly in this directory without modifying this `README.md`. Use [INDEX.md](INDEX.md) only for high-level capability or domain navigation when needed, and track acceptance coverage gaps in [verification/INDEX.md](../verification/INDEX.md#coverage-index).
