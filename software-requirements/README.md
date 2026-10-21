# Software requirements

An SR records how the software should behave, including boundaries, errors, interface agreements, and software acceptance. It is neither a statement of product goals nor an implementation task list; its upstream basis is the actual REQ/UC/INV, the related CAP/QAS, or an explicit maintenance request. The derivation activity uses [specify-feature](../.github/skills/specify-feature/SKILL.md#derive-requirements); it is not a mandatory artifact pipeline.

<a id="sr-writing"></a>
## From basis to software acceptance

1. Read the [stakeholder requirements](../stakeholder-requirements/README.md), the [actual domain materials](../domain-model/README.md#optional-forms), or the explicit task, and check the scope, full acceptance identities, original text, and baselines. UCs provide paths, an INV must have a source rule, CAPs/contexts provide responsibilities, and QASs provide sourced quality criteria; these are inputs where applicable, and you are not required to complete every artifact each time.
2. When a standalone specification is needed, copy the [SR form](../_templates/items/software-requirement.md) and save it as `software-requirements/SR-NNN-<slug>.md`. Following the [metadata conventions](../domain-model/README.md#artifact-metadata), fill in scope, identity, and upstream once the project/context is clear; the initial state is draft. Pure maintenance can keep using the existing task; do not force the creation of a REQ, SR, or US, and do not migrate old materials automatically.
3. Write down the observable behavior for normal/permitted cases, boundaries, rejections, errors, and forbidden side effects; do not conflate an unmet condition with an execution error. A missing source, an unconfirmed INV, or an ambiguity can only produce candidates/questions, never mandatory requirements. When protocols, concurrency, eligibility expiry, or metrics are undecided, record each gap separately and do not fill in technical defaults.
4. Assign each software acceptance criterion a full ID and a fixed ASCII anchor, for example `SR-NNN-AC-01` and `sr-nnn-ac-01`. Rule text is still referenced from its source; add only the judgment conditions observable at the software level, and do not copy the rule into several places.
5. Before implementation, find or plan software behavior VTs for the acceptance criteria according to the [coverage check](../verification/README.md#coverage-check). When boundary or error scenarios are not covered, keep the gap; a single normal-path check cannot stand in for all behavior.

<a id="traceability"></a>
## References and changes

In a new SR, `upstream` alone declares the relationships, using the full `scope/id#anchor` of each source; the body explains the derivation rationale and provides reading navigation to the source text/baseline, without maintaining a second mapping or content state table. `AC-01` alone, without its owning artifact, is not enough to locate a criterion. Old lightweight sources and standalone requests without metadata keep ordinary links; list missing identities explicitly and do not invent numbers just to make parsing work.

A VT references SR acceptance criteria directly, without going through a US. To find a REQ's downstream items, search the upstream fields of SRs; to find an SR's verification, search the target fields of VTs. Do not hand-maintain two sets of opposite relationships.

Requirement confirmation, software implementation, and actual runs each need their own evidence. A complete form, schema validity, or an upstream marked Approved does not prove confirmation by the accountable owner; before forming an implementable requirement, check the actual decision and the applicable baseline. Without source identities, you can organize known behavior in authorized notes, but you cannot claim that formal traceability is complete.

Applicable [intended use/risk references](../docs/governance.md#intended-use) are still maintained by their original owners; an SR only refines software behavior that has a basis. When external analysis, an acceptance decision, or control verification evidence is missing, list the related gaps; do not invent risk scores in the SR or use a [review record](../_templates/items/review-record.md) in place of the original VT. When a tool's purpose/configuration changes, keep the old evidence and re-review current applicability according to the [re-evaluation guide](../docs/ai-tooling.md#requalification).

```markdown
[SR-NNN-AC-01](SR-NNN-<slug>.md#sr-nnn-ac-01)
```

The ID and link above are placeholder syntax only. Real numbers and anchors are assigned when the artifact is created; when renaming, fix the links at the same time; a withdrawn acceptance criterion keeps its basis, and its ID is not reused. Handle semantic changes with the [impact check](../verification/README.md#change-impact); do not keep using old results just because the links still open.

<a id="requirements"></a>
## Formal requirement entry points

There are no formal SRs yet. Add file links as needed; business acceptance still belongs to REQs and software acceptance to SRs, and results are read from VTs and raw records.
