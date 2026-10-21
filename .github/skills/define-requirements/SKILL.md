---
name: define-requirements
description: Use when business goals or rules are unclear, a domain model has gaps or drift, terms conflict across contexts, a Published Interface or Intended Use changes, or an incoming ADR must be handled. Not for extracting candidates from existing documents or code (use reverse-engineer-domain) or for software requirements, design, and verification plans (use specify-feature).
---

# Clarify domain facts and stakeholder requirements

Use this method to clarify domain facts and write stakeholder requirements (REQs). Make the business meaning and its sources clear first, then write observable business acceptance criteria. Build only the models and requirements the current task needs, and never fill unknown facts with technical patterns.

## Choose the activity

Each activity is a focused entry point into this one method. Run only the activity this session needs; you need not go through every activity each time.

- New domain or incomplete facts → [Interview and iterative confirmation](#interview). This is the core flow that builds the product description, domain model, and REQs.
- Existing model, or suspected model drift → [Knowledge crunching and model drift](#distill).
- Incoming external vocabulary → [Glossary sync](#glossary-sync).
- Incoming external commitments, or a Published Interface change → [Published Interface evolution](#published-interface).
- Incoming external decision → [Incoming ADR](#incoming-adr).
- Change to an existing Intended Use → [Intended Use revision](#intended-use) (optional).
- Extraction from sources rather than clarification of business meaning → use [reverse-engineer-domain](../reverse-engineer-domain/SKILL.md) instead.

Before any activity, collect the Inputs and confirm the session mode (next two sections). Outputs and Stop conditions at the end apply to every activity.

## Inputs

Collect for every activity:

- The goals, users, scope, constraints, and sources the user provided, and which of them are confirmed and which are only proposals.
- The existing [product description](../../../stakeholder-requirements/README.md#product), domain model, and REQs, and the basis for this change.
- For each actual file or supplied excerpt: its location, version or date, fact owner, and confirmation basis. If the original location or version is missing, record it as unknown. Do not fabricate it.
- The drafts or revisions wanted this time, and the allowed read and write scope.

Read ADRs, Intended Use, and governance or risk materials only when this task actually provides them and they apply. They are not prerequisites for every project.

Each activity lists its own additional inputs.

## Session mode and confirmation

1. Confirm whether this session is analysis, drafting, or an authorized revision.
2. **Without write authorization, return only findings, questions, or drafts.**

- Confirming business meaning and permission to write files are two separate things. Never infer either one from roles, deadlines, code, or document status.
- Derivations, implementation constants, and high-confidence judgments are not business confirmation.

<a id="interview"></a>
## Interview and iterative confirmation (core flow)

Build the product description, domain model, and REQs that the task needs, confirming facts round by round with actual respondents.

Inputs: the shared inputs, the open questions, and an actual respondent for each confirmation round.

Steps:

1. Check applicability. For purely technical or documentation maintenance, state that business modeling is not applicable. Work directly from the explicit task instead of the steps below. Do not manufacture REQs.
2. Fill in the product description. Organize the goals, users, in-scope and out-of-scope matters, and sources against the inputs. Enter them in the corresponding sections of the [product description](../../../stakeholder-requirements/README.md#product).
3. Confirm in rounds.
   - Ask only about gaps that would change current behavior or scope.
   - Separate questions that block current decisions from questions that can wait.
   - In each round, restate the new facts, candidate interpretations, conflicts, and questions to be confirmed.
   - In each round, record the actual respondent, the basis, and the confirmed baseline.
4. Record terms and concepts.
   - In [shared terms](../../../domain-model/README.md#terms), explain the business meaning and context.
   - In [concepts and relationships](../../../domain-model/README.md#concepts), record the concepts and the meanings of their states. For each relationship, state its direction, multiplicity, and the conditions under which it holds.
   - Keep unknown relationship constraints open. A bare list of nouns is not enough.
5. Record context responsibilities and exchanges.
   - In [context responsibilities](../../../domain-model/README.md#contexts), state what each context is and is not responsible for. Also state the facts it owns and the external facts it only consumes.
   - In [directed information exchange](../../../domain-model/README.md#exchanges), state the provider → user direction, the fact owner, and known business agreements.
   - Do not force a split into services. Do not assume aggregates, repositories, or other tactical design by default.
6. Record rules and their sources.
   - In the [rules section](../../../domain-model/README.md#rules), assign stable rule IDs and anchors. Write the conditions, boundaries, forbidden behavior, and unknowns.
   - In the [sources section](../../../domain-model/README.md#sources), record the fact sources, the nature and limits of the evidence, and the actual confirmer and date.
   - Maintain rule text in one place only. When an existing rule changes, first handle its dependencies with the [verify-change impact check](../verify-change/SKILL.md#impact).
   - Describe a derivation with the [INV form](../../../_templates/items/invariant.md#basis) only after its rule exists.
   - Clarify strategic responsibility boundaries first. Then discuss [tactical candidates](../../../domain-model/README.md#tactical-forms) as needed.
7. Write a REQ when a formal stakeholder requirement is needed.
   - Use the [REQ form](../../../_templates/items/stakeholder-requirement.md#basis) and follow the [REQ guide](../../../stakeholder-requirements/README.md#req-writing).
   - State the source, business need, and scope. Link the actual concepts, contexts, and rules. Do not copy rule text.
   - Write each acceptance criterion in the form's fields: preconditions and scenario → action → observable result → boundary or forbidden result.
   - Give each acceptance criterion a full, stable ID that includes its owning artifact, plus an anchor, such as `REQ-NNN-AC-01`. Do not write just `AC-01`.
   - Use a [UC](../../../_templates/items/use-case.md) or [QAS](../../../_templates/items/quality-attribute-scenario.md) as needed.
   - When participants, postconditions, concurrency policies, metrics, or measurement methods are not provided, keep them as questions. Do not fill them in from experience.
8. Close out the REQs.
   - Keep questions, impact, and the confirmation basis in the REQ's "Changes and open items" section.
   - Update the [formal requirements entry point](../../../stakeholder-requirements/README.md#requirements).
   - Hand all of this session's business acceptance criteria to [specify-feature](../specify-feature/SKILL.md) for layered verification planning. Do not substitute software checks for business acceptance.

Record and return: the updated product description and domain model sections, the REQs with their open items, and the acceptance criteria handed to specify-feature. For maintenance, return the statement of applicability.

Stop points:

- Without an answer, do not simulate the expert.
- An unconfirmed REQ remains a draft. Do not approve it on the user's behalf.
- For missing behavior sources, conflicting rules, or unclear responsibility boundaries, see Stop conditions.

<a id="distill"></a>
## Knowledge crunching and model drift

Compare an existing model with current knowledge and report the drift as findings that need a decision.

Inputs: the given model version, expert statements, actual usage clues, and the adopted tactical materials.

Steps:

1. List stubs and open items first.
2. Using the given model version, expert statements, and actual usage clues, compare the language, concept relationships, rules, boundaries, and adopted tactical materials.
3. For each difference, distinguish wording ambiguity, business change, and implementation deviation. Do not judge the model wrong from class names or directories alone.
4. Following the [domain artifact review](../verify-change/SKILL.md#domain-review), write each finding with its source or location, severity rationale, impact chain, and the decision needed.
5. Keep the old model and the conflicting sources. Propose candidate interpretations, boundary adjustments, or BL/ADR suggestions.

Return: the findings and proposals from steps 4 and 5.

Stop point: without an actual decision, do not restructure the architecture, rename globally, or claim that the model is healthy or the drift is eliminated.

<a id="glossary-sync"></a>
## Glossary sync

Compare local and external glossaries and propose how to align them.

Inputs: the actually provided local and external glossary versions, with each term's definitions and contexts.

Steps:

1. For each term, list its context, original definition and location, and its confirmed or open basis.
2. Distinguish synonyms, homonyms (same name, different meaning), external-only terms, local-only terms, and unconfirmed terms.
3. When a version is missing, make only a provisional comparison. State which differences cannot be confirmed.
4. Keep the distinct meanings of same-named terms in different contexts. Propose qualified names, mappings, aliases, or deprecation options.
5. List the impact along rules, UC/REQ, interfaces, and known consumers, and who needs to decide.
6. Revise the original owning glossary only after both the specific choice and the write scope are confirmed. Keep the old names, source versions, deprecation basis, and historical references.

Return: the term comparison, the options, the impact, and who needs to decide. When there are conflicts or missing versions, deliver an alignment proposal. Record only the confirmed glossary revision from step 6.

Stop points:

- Unconfirmed terms do not become unified definitions.
- Do not silently adopt an external "standard term". Do not replace terms globally.
- Updating an external source needs separate authorization.
- When there are conflicts or missing versions, do not report a finished comparison as unified language.

<a id="published-interface"></a>
## Published Interface evolution

Document or revise what a Published Interface commits to its consumers, and propose how it evolves.

Inputs: the supplied contract, model or glossary, original version, proposed differences, known consumers, and the actual versioning policy.

Steps:

1. Make clear whether this session documents existing commitments or revises them.
2. Read the inputs. Using the [PI form](../../../_templates/items/published-interface.md#direction), separate the provider → consumer direction, the fact owner, and the actual commitments. A consumer's need does not automatically become a commitment.
3. Compare element meanings, applicability conditions, missing values, and failure handling. Record potential breaking changes and consumer impact. Do not call a semantic change compatible just because field names are unchanged.
4. In the [evolution section](../../../_templates/items/published-interface.md#evolution), propose the version, migration or compatibility window, withdrawal, and notification plan.
   - Base version suggestions on the actual versioning policy.
   - For known breaking changes, propose a corresponding version bump.
5. Draft the notification. List the recipients, old and new baselines, differences, impact, and items to be confirmed.

Record and return: the direction and commitments, the compatibility findings, the evolution proposal, and the notification draft.

Stop points:

- When the original contract, the consumers, or the error policy is missing, mark it as to be confirmed. Stop compatibility guarantees and release decisions. Do not assume a failure strategy.
- When the current version or versioning policy is unknown, do not invent a version number.
- **A draft is not a sent notification.** Actual notification, source changes, and release each require separate authorization and an original record.

<a id="incoming-adr"></a>
## Incoming ADR

Assess the impact of an incoming external ADR on this project.

Inputs: the actually provided ADR text, its version or decision baseline, its proposer or decider, and the purpose of handling it now.

Steps:

1. Read the inputs. A summary, a title, or the word "Accepted" alone cannot authenticate a decision.
2. Following the [semantic impact check](../verify-change/SKILL.md#impact), list the affected rules, contexts, REQ/QAS, design, Published Interfaces, consumers, and verification. Also list conflicts and the applicable scope that needs confirmation.
3. Produce impact findings, BLs, or an authorized [local ADR proposal](../../../_templates/items/architecture-decision.md). Note the locations to update, the accountable owners, and a notification draft.

Record and return: the results of step 3. The external ADR keeps its original owner and history.

Stop points:

- When the incoming text or baseline, or the authorization, is missing, stop the adoption and the changes that depend on it. You may still return known issues.
- Do not automatically edit external wikis, notify consumers, or generalize the incoming decision to this project.

<a id="intended-use"></a>
## Intended Use revision (optional)

Assess a proposed change to an existing Intended Use and route its scope and risk decisions to the accountable owners.

Inputs: handle only **existing files** provided by the user:

- the current full content and its baseline
- the target sections
- the proposed content and rationale
- the fact owner
- the scope allowed to change
- the governance or risk basis, when actually provided

Do not require ordinary projects to supply medical or QMS materials.

Steps:

1. When necessary source text is missing, request it first. Do not create substitute facts.
2. Compare the goals, users, use environment, in-scope and out-of-scope matters, and constraints. When the source involves patients, safety, or regulation, also check the corresponding changes.
3. List the affected contexts, REQ/QAS, interfaces and consumers, and verification. Cite the actually provided governance or risk basis.
4. Keep uncertain scope expansion or safety impact as questions. As the source requires, submit them for review to the actual accountable owner and the applicable risk or regulatory owner. If no escalation rule is given, ask them to define one.
5. When a standalone record is needed, use the [Intended Use form](../../../_templates/items/intended-use.md) and the [governance guide](../../../docs/governance.md#intended-use) to record sources, proposals, actual decisions, and impact. The owner still maintains the existing source text; the form does not fill in missing source text.
6. For risk materials, use only the [risk control reference](../../../_templates/items/risk-control.md) to locate external sources and residual gaps.

Record and return: section-level differences, impact and escalation proposals, who needs to confirm what, and the blocked actions. An authorized revision must still keep the old baseline and unresolved items.

Stop points:

- Do not decide on your own that a risk is acceptable. Do not perform the risk analysis on the owners' behalf.
- Without the accountable owner's decisions on applicable scope and risk, do not confirm the new use or change downstream commitments.
- Unknown environments, limitations, or responsibility policies block the corresponding confirmation.
- Do not assume a medical classification or add an approval chain.
- Complete documentation does not imply compliance or approval.

## Outputs

- Domain facts → the existing sections of `domain-model/README.md`, or the models it already links.
- Product information → `stakeholder-requirements/README.md`.
- New REQs → `stakeholder-requirements/REQ-NNN-<slug>.md`, as needed.
- Standalone domain artifacts, QAS, and BLs → the [existing locations](../../../domain-model/README.md#optional-forms).
- ADRs → where the [architecture guide](../../../architecture/README.md#decisions) places them.
- Incoming materials and Intended Use → keep the ownership and location of the supplied files.

For every output:

- Use forms only as a starting point. Do not leave formal content in `_templates`.
- When metadata is adopted, follow the [current contract](../../../domain-model/README.md#artifact-metadata) to keep a single home for identity, scope, content state, and upstream relationships. In the body, state the basis, derivation, and questions; do not copy a status or relationship table again.
- When the scope or ID is missing, keep an authorized plain note first. Do not forcibly migrate old lightweight materials.
- Record confirmation, task progress, and run results separately.

## Done when

- Requirement drafts can be delivered once all of these hold:
  - terms, concepts and relationships, rules, responsibilities, and directed exchanges have a basis
  - each acceptance criterion can be located
  - open items and impact are explicit
- Deliverable drafts do not mean that business acceptance has been run.
- A maintenance task need only deliver its statement of applicability.

## Stop conditions

- When behavior sources are missing, rules conflict, or responsibility boundaries are unclear, stop the affected refinement.
- Then raise the specific questions that need confirmation. You may keep the known parts and open drafts.
- Do not derive default policies, forge confirmations, or fill in facts under deadline pressure.
- Each activity also lists its own stop points.
