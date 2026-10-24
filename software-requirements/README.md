# Software requirements

An SR records how the software should behave, including boundaries, errors, interface agreements, and software acceptance. It is neither product goals nor an implementation task list; its upstream basis is the actual REQ/UC/INV, related CAP/QAS, or an explicit maintenance request. The derivation activity uses [specify-feature](../.github/skills/specify-feature/SKILL.md#derive-requirements); it is not a mandatory artifact pipeline.

<a id="sr-writing"></a>
## From basis to software acceptance

1. Read the [stakeholder requirements](../stakeholder-requirements/README.md), the [actual domain materials](../domain-model/README.md#optional-forms), or the explicit task; check scope, full acceptance identities, original text, and baselines. UCs provide paths, an INV must have a source rule, CAPs/contexts provide responsibilities, and QASs provide sourced quality criteria. These are inputs where applicable; not every artifact is required each time.
2. For a standalone specification, copy the [SR form](../_templates/items/software-requirement.md) and save it as `software-requirements/SR-NNN-<slug>.md`. Following the [metadata conventions](../domain-model/README.md#artifact-metadata), fill in scope, identity, and upstream once project/context is clear; the initial state is draft. Pure maintenance can keep using the existing task; do not force a REQ, SR, or US, and do not migrate old materials automatically.
3. Write observable behavior for normal/permitted cases, boundaries, rejections, errors, and forbidden side effects; do not conflate an unmet condition with an execution error. A missing source, unconfirmed INV, or ambiguity yields only candidates or questions, never mandatory requirements. For undecided protocols, concurrency, eligibility expiry, or metrics, record each gap separately and fill in no technical defaults.
4. Give each software acceptance criterion a full ID and a fixed ASCII anchor, for example `SR-NNN-AC-01` and `sr-nnn-ac-01`. Reference rule text from its source, add only software-level observable judgment conditions, and do not copy the rule into several places.
5. Before implementation, find or plan software behavior VTs for the acceptance criteria per the [coverage check](../verification/README.md#coverage-check). Uncovered boundary or error scenarios stay a gap; a single normal-path check cannot stand in for all behavior.

<a id="traceability"></a>
## References and changes

In a new SR, `upstream` alone declares the relationships, using the full `scope/id#anchor` of each source; the body explains the derivation rationale and navigates to the source text and baseline, with no second mapping or content-state table. `AC-01` alone, without its owning artifact, is not enough to locate a criterion. Old lightweight sources and standalone requests without metadata keep ordinary links; list missing identities explicitly and do not invent numbers to make parsing work.

A VT references SR acceptance criteria directly, without going through a US. To find a REQ's downstream items, search the upstream fields of SRs; to find an SR's verification, search the target fields of VTs. Do not hand-maintain two sets of opposite relationships.

Requirement confirmation, software implementation, and actual runs each need their own evidence. A complete form, schema validity, or an upstream marked Approved does not prove the accountable owner's confirmation; before forming an implementable requirement, check the actual decision and applicable baseline. Without source identities, known behavior may be organized in authorized notes, but formal traceability cannot be claimed complete.

Applicable [intended use/risk references](../docs/governance.md#intended-use) are still maintained by their original owners; an SR only refines software behavior that has a basis. When external analysis, an acceptance decision, or control verification evidence is missing, list the related gaps; do not invent risk scores in the SR or use a [review record](../_templates/items/review-record.md) in place of the original VT. When a tool's purpose/configuration changes, keep the old evidence and re-review current applicability according to the [re-evaluation guide](../docs/ai-tooling.md#requalification).

```markdown
[SR-NNN-AC-01](SR-NNN-<slug>.md#sr-nnn-ac-01)
```

The ID and link above are placeholder syntax only. Real numbers and anchors are assigned at creation; when renaming, fix links at the same time; a withdrawn criterion keeps its basis, and its ID is not reused. Handle semantic changes with the [impact check](../verification/README.md#change-impact); do not keep using old results just because the links still open.

<a id="requirements"></a>
## Formal requirement entry points

There are no formal SRs yet. Add file links as needed; business acceptance still belongs to REQs and software acceptance to SRs, and results are read from VTs and raw records.
