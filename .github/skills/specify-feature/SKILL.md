---
name: specify-feature
description: Use when a feature or maintenance task has a basis but its software acceptance, delivery slice, architecture constraints, sequence or verification plan is not yet precise.
---

# Specify behavior and the verification plan

Before implementation, decide what to observe, which layer accepts it, and how each item is judged. Specifications, necessary design, and the verification plan may be completed first, but run results must never be prefilled; the activities are not an automatic role pipeline.

## Inputs

- The task, scope, non-goals, completion conditions, and read/write authorization; the actual model and REQ/UC/INV/CAP/QAS, or a locatable independent maintenance request.
- All current acceptance criteria, related SR/US/ABB/ADR/VT, interfaces or sequences, and their respective baselines; read only materials that apply to this task and were actually provided.
- The actual configuration, or not-configured state, in the [development guide](../../../docs/development.md); when a [BC configuration](../../../architecture/README.md#bc-configuration) is adopted, also check its identity, source roots/paths, pinned objects, read-only nature, and registration references. Configuration does not grant execution rights.

## Choose the activity first

Read the source text first and distinguish what is actually confirmed, what is a candidate, and what is unknown. When sources are insufficient, go back to [define-requirements](../define-requirements/SKILL.md); do not treat an Approved label, an implementation constant, or a draft INV as a binding fact. Make clear whether this session is analysis, drafting, or an authorized revision; check every file to be written and its existing content, and stop writing on conflict.

Choose the subsections below according to the task. SR/VT need not go through a US, and ABB and VT can each proceed independently once their own necessary inputs are complete. Small maintenance may reuse the task's completion conditions without building a full artifact chain. When metadata is adopted, fill it in according to the [existing contract](../../../domain-model/README.md#artifact-metadata): source relationships and content declarations go in frontmatter, while the body states meaning, reading navigation, and criteria; old lightweight materials are not migrated automatically.

<a id="derive-requirements"></a>
## Derive software requirements

1. From the actual REQ acceptance criteria, UC paths, source rules/INVs, CAP/context responsibilities, and applicable QAS, determine item by item the behavior the software must express. Record source locations, the confirmation basis, and pinned baselines. A missing source or an ambiguity blocks confirmation of the corresponding requirement, while known parts may stay as drafts/questions. When identity is missing, use an authorized note first; do not invent canonical references.
2. Fill in the [SR](../../../_templates/items/software-requirement.md#basis) following the [SR guide](../../../software-requirements/README.md#sr-writing); new drafts are always draft. `upstream` declares locatable sources, and the body explains the refinement rationale; write normal/allowed, boundary, rejection, error, and forbidden side-effect cases separately. When an interface, eligibility-lapse, concurrency, or metric policy is missing, list specific questions; do not make decisions on behalf of the business.
3. Give every software acceptance criterion a full owner ID and a stable anchor; write only criteria observable at the software layer, and leave the rules in their source text. Check existing SRs to avoid duplicate numbers, duplicate requirements, or silent overrides. For source changes, go through [semantic impact](../verify-change/SKILL.md#impact) first, then plan the layered VTs below.

<a id="delivery-slice"></a>
## Optional delivery slice

Use a [US](../../../_templates/items/user-story.md) and the [delivery guide](../../../user-stories/README.md#delivery) only when delivery needs to be organized. For a formal slice based on SRs, first verify the confirmation basis of the SRs and the applicable UC/INV; unconfirmed sources leave only candidate splits and blockers, not implementable commitments. Describe the scope, change locations, dependencies, and checklist according to the actual roles/value, paths, and constraints; do not invent roles, do not split stories by fixed technical layers, and do not copy a second set of ACs.

Task progress belongs in the US body, content declarations in frontmatter, and runs in the VT. When there is no independent delivery need, skip creating a US; this does not affect SRs, design, or VTs that can be planned directly, and independent maintenance tasks still follow their original basis.

<a id="design-architecture"></a>
## Necessary architecture and decisions

1. Read the actual SRs, CAP/contexts, interfaces, applicable QAS/ADRs, and existing design, and explicitly read the [architecture rules](../../instructions/architecture.instructions.md). Write an [ABB](../../../_templates/items/architecture-building-block.md) only for an independent structural constraint, and an [ADR](../../../_templates/items/architecture-decision.md) only for a real trade-off; neither requires a US first.
2. Following the [architecture guide](../../../architecture/README.md#building-blocks), describe owned/consumed facts, responsibilities, dependencies, and collaboration direction. Technology choices, interface/dependency versions, runtime/deployment, observability, and quality all need sources. Undecided ADRs, draft QAS, and unknown versions or boundaries support only candidates and gaps; do not presuppose a four-layer directory structure or a platform.
3. Keep domain dependencies separate from legitimate composition-root wiring; wiring is not a pass for controllers to bypass domain rules. A real design constraint has its own VC/anchor or references its original owner, and the VT plans suitable criteria for it. Hand incoming ADRs to [incoming-adr](../define-requirements/SKILL.md#incoming-adr); decisions and notifications do not take effect automatically.

<a id="plan-verification"></a>
## Pre-implementation verification plan

1. Following the [full acceptance inventory](../../../verification/README.md#coverage-check), first list the owner, full ID, source text, and baseline of every in-scope REQ, UC/INV/QAS, SR, necessary design item, and maintenance completion condition, including **items without a VT**. For a missing source/identity, record an exact gap first; do not work backward from existing VTs or narrow the scope.
2. Following the [verification layers](../../../verification/README.md#layers), plan business, software, applicable design, or document checks separately, using a [VT](../../../_templates/items/verification-test.md#plan). Each `targets` entry declares the actual `scope/id#anchor` and a local `criterionAnchor`; the body keeps, per item, the independent criterion, observation method, preconditions/forbidden side effects, and open items, without also copying a target-relationship table. Trace back to the source owner, anchor, and layer; a single "all passed" cannot cover multiple targets.
3. When Gherkin is needed, use the [feature file](../../../_templates/items/verification-test.feature) following the [companion guide](../../../verification/README.md#feature-companion). It exclusively holds the scenario text, while the VT keeps navigation to the actual file/baseline and the per-item criteria. Use only known normal/negative cases and measures; safety tags need a named source. Without step implementations or a runner, there is only a text plan; do not call it automated.
4. Record the object, requirement/task, and VT plan baselines, and verify the actual environment, method, command/cwd, and report location. When the project, command, or report is missing, mark each affected target `not-run` and state the gap; do not invent test identifiers. Business acceptance is not an aggregate of software results, and document checks must not be entered as behavioral runs.
5. Register navigation, checked baselines, and gaps in the [verification index](../../../verification/README.md#coverage-index); do not build a separate result table. Before implementation and runs, check complete coverage and semantic impact with [verify-change](../verify-change/SKILL.md#coverage); conclusions are drawn in the original record only when actual evidence supports them.

<a id="sequence-diagram"></a>
## Sequence description

Read this scenario's actual UC, ABBs, rules, participants, and event/interface contracts and versions, and use a [SEQ](../../../_templates/items/sequence-diagram.md). For each path, describe provider/producer → user/consumer, the message meaning, and the known expectations for success/rejection/error. When the ABB participant mapping or a contract is missing, mark the description as partial and record the gap; defer the diagram if necessary.

Adopt an asynchronous boundary only when existing sources explicitly state asynchronous integration or event consumption. When there is only a conceptual exchange between contexts, do not invent synchronous calls, brokers, retries/timeouts/idempotency/ordering, or delivery guarantees. Mermaid expresses only the parts traceable to a source; it is not a runtime test. Before revising a confirmed diagram, check authorization, the old and new baselines, and the verification impact; do not overwrite the original evidence.

<a id="build-architecture-spec"></a>
## Compile the architecture specification

Following the [SWAS](../../../_templates/items/architecture-specification.md), read the business/logical/runtime/deployment sources within the authorized scope; if a model/implementation summary is provided, check its source baselines and go back to the source text. When no summary is provided, do not fake an export, and do not modify read-only domain sources.

Keep the [nine source views](../../../architecture/README.md#architecture-specifications) and their original baselines: a missing, unreadable, or unverifiable source is `unverified` with the specific gap listed, a partially readable one is `partial`, and only a complete source is `available`. These states indicate only source completeness, not acceptable risk, approval, or release. Errors in required inputs still block; missing ABB, risk, deployment, or release materials cannot be filled in with infrastructure or classifications. Produce only a Markdown compilation; this method provides no PDF/presentation renderer.

## Outputs and completion

Create or revise SRs, VTs/companions, and the index as needed; US, ABB/ADR, and SEQ/SWAS go to the locations given in their respective guides, and formal content does not stay in the forms. Existing code maintenance uses [implement-task](../implement-task/SKILL.md), and initial generation uses [generate-code](../generate-code/SKILL.md); each needs its own development inputs and authorization.

Deliver this specification/plan only when all in-scope acceptance criteria have been inventoried, each target and its layer are explicit, and the pre-implementation verification plan and gaps are locatable; this does not mean behavioral verification has passed. Without an application, application checks are not applicable to documentation tasks, and planned business/software VTs remain `not-run`.

## Stop conditions

When sources cannot determine behavior, acceptance targets cannot be located, boundaries conflict, or authorization is unclear, stop the affected specification confirmation/implementation, and keep known drafts and exact gaps. Do not finish the task by deleting in-scope acceptance criteria, forcing a US, or borrowing results from another layer.
