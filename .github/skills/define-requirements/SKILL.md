---
name: define-requirements
description: Use when business goals or rules are unclear, a domain model has gaps or drift, terms conflict across contexts, or a published interface, incoming ADR or Intended Use changes.
---

# Clarify domain facts and stakeholder requirements

First make the business meaning and its sources clear, then write observable business acceptance criteria. Build only the models and requirements the current task needs, and never fill unknown facts with technical patterns.

## Inputs

- The goals, users, scope, constraints, and sources provided by the user; which of them are confirmed and which are only proposals.
- The existing [product description](../../../stakeholder-requirements/README.md#product), domain model, REQs, and the basis for this change.
- The location, version/date, fact owner, and confirmation basis of each actual file or supplied excerpt; the drafts or revisions wanted this time, and the allowed read/write scope. If the original location or version is missing, record it as unknown; do not fabricate it.
- Read ADRs, Intended Use, and governance/risk materials only when this task actually provides them and they apply; they are not prerequisites for every project. When the work is extraction from sources rather than clarification of business meaning, use [reverse-engineer-domain](../reverse-engineer-domain/SKILL.md).

## Choose this session's activity

For a new domain or incomplete facts, use the [interview](#interview); for an existing model, use [knowledge crunching](#distill); for incoming external vocabulary, commitments, or decisions, use [glossary sync](#glossary-sync), [Published Interface](#published-interface), [incoming ADR](#incoming-adr), or [Intended Use revision](#intended-use) respectively. These are focused entry points into the same method; you need not go through every activity each time.

First confirm whether this session is analysis, drafting, or an authorized revision; without write authorization, return only findings, questions, or drafts. Confirming business meaning and being allowed to write files are two separate things; neither can be inferred from roles, deadlines, code, or document status.

<a id="interview"></a>
## Interview and iterative confirmation

1. Organize the goals, users, in-scope and out-of-scope matters, and sources against the inputs, and enter them in the corresponding sections of the product description. Ask only about gaps that would change current behavior or scope. In each round, restate the new facts, candidate interpretations, conflicts, and questions to be confirmed, and record the actual respondent, the basis, and the confirmed baseline; without an answer, do not simulate the expert. Distinguish questions that block current decisions from those that can wait. For purely technical or documentation maintenance, state that business modeling is not applicable and work directly from the explicit task; do not manufacture REQs.
2. In [shared terms](../../../domain-model/README.md#terms), explain the business meaning and context; in [concepts and relationships](../../../domain-model/README.md#concepts), record the concepts and state meanings together with each relationship's direction, multiplicity, and the conditions under which it holds. Keep unknown relationship constraints open; a bare list of nouns is not enough.
3. In [context responsibilities](../../../domain-model/README.md#contexts), state clearly what each context is and is not responsible for, the facts it owns, and the external facts it only consumes; in [directed information exchange](../../../domain-model/README.md#exchanges), make explicit the provider → user direction, the fact owner, and known business agreements. Do not force a split into services, and do not assume aggregates, repositories, or other tactical design by default.
4. Assign stable rule IDs and anchors in the [rules section](../../../domain-model/README.md#rules), and write conditions, boundaries, forbidden behavior, and unknowns; record the fact sources, the nature and limits of the evidence, and the actual confirmer and date in the [sources section](../../../domain-model/README.md#sources). Only once a rule exists may a derivation be described with the [INV form](../../../_templates/items/invariant.md#basis); clarify strategic responsibility boundaries first, then discuss [tactical candidates](../../../domain-model/README.md#tactical-forms) as needed. Derivations, implementation constants, or high-confidence judgments are not business confirmation. Rule text is maintained in one place only; when an existing rule changes, first handle its dependencies with the [verify-change impact check](../verify-change/SKILL.md#impact).
5. When a formal stakeholder requirement is needed, use the [REQ form](../../../_templates/items/stakeholder-requirement.md#basis) following the [REQ guide](../../../stakeholder-requirements/README.md#req-writing); state the source, business need, and scope, and link the actual concepts, contexts, and rules. Acceptance criteria use the form's "preconditions and scenario → action → observable result → boundary/forbidden result" fields, and each one gets a full, stable ID that includes its owning artifact, plus an anchor, such as `REQ-NNN-AC-01`; do not copy rule text, and do not write just `AC-01`. Use a [UC](../../../_templates/items/use-case.md) or [QAS](../../../_templates/items/quality-attribute-scenario.md) as needed; when participants, postconditions, concurrency policies, metrics, or measurement methods are not provided, keep them as questions rather than filling them in from experience.
6. Keep questions, impact, and the confirmation basis in the REQ's "Changes and open items" section, and update the [formal requirements entry point](../../../stakeholder-requirements/README.md#requirements). Hand all of this session's business acceptance criteria to [specify-feature](../specify-feature/SKILL.md) for layered verification planning; do not substitute software checks for business acceptance. An unconfirmed REQ remains a draft; do not approve it on the user's behalf.

<a id="distill"></a>
## Knowledge crunching and model drift

- Using the given model version, expert statements, and actual usage clues, compare the language, concept relationships, rules, boundaries, and adopted tactical materials; list stubs and open items first. Distinguish wording ambiguity, business change, and implementation deviation; do not judge the model wrong from class names or directories alone.
- Following the [domain artifact review](../verify-change/SKILL.md#domain-review), return findings with the source/location, severity rationale, impact chain, and the decision needed. Keep the old model and conflicting sources, and propose candidate interpretations, boundary adjustments, or BL/ADR suggestions. Without an actual decision, do not restructure the architecture or rename globally, and do not claim that the model is healthy or the drift is eliminated.

<a id="glossary-sync"></a>
## Glossary sync

1. Against the actually provided local/external glossary versions, list for each term its context, original definition and location, and its confirmed or open basis; distinguish synonyms, homonyms (same name, different meaning), external-only terms, local-only terms, and unconfirmed terms. When a version is missing, make only a provisional comparison and state which differences cannot be confirmed; unconfirmed terms do not become unified definitions.
2. Keep the distinct meanings of same-named terms in different contexts, and propose qualified names, mappings, aliases, or deprecation options. List the impact along rules, UC/REQ, interfaces, and known consumers, and who needs to decide; do not silently adopt an external "standard term", and do not replace terms globally.
3. Revise the original glossary owner only after both the specific choice and the write scope are confirmed, keeping old names, source versions, the deprecation basis, and historical references; updating an external source needs separate authorization. When there are conflicts or missing versions, deliver an alignment proposal; do not report a finished comparison as unified language.

<a id="published-interface"></a>
## Published Interface evolution

1. Make clear whether this session is documenting existing commitments or revising them; read the supplied contract, model/glossary, original version, proposed differences, and known consumers. Using the [PI form](../../../_templates/items/published-interface.md#direction), separate the provider → consumer direction, the fact owner, and the actual commitments; a consumer's need does not automatically become a commitment.
2. Compare element meanings, applicability conditions, missing values, and failure handling, and record potential breaking changes and consumer impact. A semantic change cannot be called compatible just because field names are unchanged. When the original contract, the consumers, or the error policy is missing, mark it as to be confirmed, stop compatibility guarantees and release decisions, and do not assume a failure strategy.
3. In the [evolution section](../../../_templates/items/published-interface.md#evolution), propose the version, migration/compatibility window, withdrawal, and notification plan. Base version suggestions on the actual versioning policy, and propose a corresponding version bump for known breaking changes; when the current version or policy is unknown, do not invent a version number. The notification draft lists the recipients, old and new baselines, differences, impact, and items to be confirmed; **a draft is not a sent notification**. Actual notification, source changes, and release each require separate authorization and an original record.

<a id="incoming-adr"></a>
## Incoming ADR

Read the actually provided ADR text, its version/decision baseline, its proposer or decider, and the purpose of handling it now; a summary, a title, or the word "Accepted" alone cannot authenticate a decision. Following the [semantic impact check](../verify-change/SKILL.md#impact), list the affected rules, contexts, REQ/QAS, design, Published Interfaces, consumers, and verification, plus conflicts and the applicable scope that needs confirmation.

Produce impact findings, BLs, or an authorized [local ADR proposal](../../../_templates/items/architecture-decision.md), noting the locations to update, the accountable owners, and a notification draft; the external ADR keeps its original owner and history. When the incoming text/baseline or authorization is missing, stop the adoption and changes that depend on it; you may still return known issues. Do not automatically edit external wikis, notify consumers, or generalize the incoming decision to this project.

<a id="intended-use"></a>
## Intended Use revision (optional)

Handle only **existing files** provided by the user: the current full content and baseline, the target sections, the proposed content/rationale, the fact owner, and the scope allowed to change. When necessary source text is missing, request it first; do not create substitute facts or require ordinary projects to supply medical/QMS materials.

Compare goals, users, use environment, in-scope and out-of-scope matters, and constraints; when the source involves patients, safety, or regulation, also check the corresponding changes. List the affected contexts, REQ/QAS, interfaces/consumers, and verification, and cite the actually provided governance/risk basis. Keep uncertain scope expansion or safety impact as questions and, as the source requires, submit them to the actual accountable owner and the applicable risk/regulatory owner for review; if no escalation rule is given, ask them to define one. Do not decide on your own that a risk is acceptable, and do not perform the risk analysis on their behalf.

Produce section-level differences and impact/escalation proposals, who needs to confirm what, and the blocked actions. Without the accountable owner's decisions on applicable scope and risk, do not confirm the new use or change downstream commitments. An authorized revision must still keep the old baseline and unresolved items; complete documentation does not imply compliance or approval.

When a standalone record is needed, use the [Intended Use form](../../../_templates/items/intended-use.md) and the [governance guide](../../../docs/governance.md#intended-use) to record sources, proposals, actual decisions, and impact; existing source text is still maintained by its owner, and the form does not fill in missing source text. For risk materials, use only the [risk control reference](../../../_templates/items/risk-control.md) to locate external sources and residual gaps. Unknown environments, limitations, or responsibility policies block the corresponding confirmation; do not assume a medical classification or add an approval chain.

## Outputs and completion

Domain facts go into the existing sections of `domain-model/README.md` or the models it already links; product information goes into `stakeholder-requirements/README.md`; create `stakeholder-requirements/REQ-NNN-<slug>.md` as needed. Standalone domain artifacts, QAS, and BLs use the [existing locations](../../../domain-model/README.md#optional-forms), and ADRs go where the [architecture guide](../../../architecture/README.md#decisions) places them; incoming materials and Intended Use keep the ownership and location of the supplied files. Forms are only a starting point; do not leave formal content in `_templates`.

When metadata is adopted, follow the [current contract](../../../domain-model/README.md#artifact-metadata) to keep a single home for identity, scope, content state, and upstream relationships; the body states the basis, derivation, and questions without copying a status/relationship table again. When the scope or ID is missing, keep an authorized plain note first; old lightweight materials are not forcibly migrated. Record confirmation, task progress, and run results separately.

Requirement drafts can be delivered once terms, concepts and relationships, rules, responsibilities, and directed exchanges have a basis, each acceptance criterion can be located, and open items and impact are explicit; this does not mean business acceptance has been run. A maintenance task need only deliver its statement of applicability.

## Stop conditions

When behavior sources are missing, rules conflict, or responsibility boundaries are unclear, stop the affected refinement and raise the specific questions that need confirmation. You may keep the known parts and open drafts, but must not derive default policies, forge confirmations, or fill in facts under deadline pressure.
