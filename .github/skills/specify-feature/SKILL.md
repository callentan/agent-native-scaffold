---
name: specify-feature
description: Use when a feature or maintenance task has a basis but its software acceptance, delivery slice, architecture constraints, sequence, architecture specification, or verification plan is not yet precise. Not for unclear business rules or insufficient sources (use define-requirements), or for maintaining or generating code (use implement-task or generate-code).
---

# Specify behavior and the verification plan

Before implementation, decide what to observe, which layer accepts it, and how each item is judged. You may complete specifications, necessary design, and the verification plan first, but **never prefill run results**. The activities below are not an automatic role pipeline.

## Choose the activity

Complete the common steps first. Then choose only the activities this task needs:

- [Derive software requirements](#derive-requirements): turn REQ/UC/INV/CAP/QAS sources into software requirements (SR).
- [Optional delivery slice](#delivery-slice): organize delivery into a user story (US), only when delivery needs organizing.
- [Necessary architecture and decisions](#design-architecture): record an independent structural constraint (ABB) or a real trade-off (ADR).
- [Pre-implementation verification plan](#plan-verification): plan how each in-scope acceptance item is verified (VT).
- [Sequence description](#sequence-diagram): describe one scenario's interaction paths (SEQ).
- [Compile the architecture specification](#build-architecture-spec): compile the source views into a Markdown architecture specification (SWAS).

The activities do not form a mandatory chain:

- A US is optional. SR and VT need not go through a US.
- ABB and VT can each proceed independently once their own necessary inputs are complete.
- Small maintenance may reuse the task's completion conditions without building a full artifact chain.

## Inputs

- Required:
  - The task: scope, non-goals, completion conditions, and read/write authorization.
  - The basis: the actual model and REQ/UC/INV/CAP/QAS, or a locatable independent maintenance request.
  - All current acceptance criteria, with their baselines.
  - The actual configuration, or not-configured state, in the [development guide](../../../docs/development.md).
- When applicable:
  - Related SR/US/ABB/ADR/VT, interfaces, or sequences, with their respective baselines.
  - An adopted [BC configuration](../../../architecture/README.md#bc-configuration): check its identity, source roots/paths, pinned objects, read-only nature, and registration references.

Read only materials that apply to this task and were actually provided. Configuration does not grant execution rights.

## Common steps

1. Read the source text first. Distinguish what is actually confirmed, what is a candidate, and what is unknown.
2. When sources are insufficient, go back to [define-requirements](../define-requirements/SKILL.md).
   - Do not treat an Approved label, an implementation constant, or a draft INV as a binding fact.
3. State whether this session is analysis, drafting, or an authorized revision.
4. Check every file you will write and its existing content. On conflict, stop writing.
5. When metadata is adopted, fill it in according to the [existing contract](../../../domain-model/README.md#artifact-metadata):
   - Put source relationships and content declarations in frontmatter.
   - In the body, state meaning, reading navigation, and criteria.
   - Do not migrate old lightweight materials automatically.
6. Run the chosen activities. Each one follows the same pattern: purpose, inputs, actions, output, and stop points.

<a id="derive-requirements"></a>
## Derive software requirements

Purpose: determine, item by item, the behavior the software must express, and record it as SRs with software-layer acceptance criteria.

Inputs: the actual REQ acceptance criteria, UC paths, source rules/INVs, CAP/context responsibilities, and applicable QAS; existing SRs.

Actions:

1. From those inputs, determine item by item the behavior the software must express.
2. Record each item's source locations, confirmation basis, and pinned baselines.
3. When identity is missing, use an authorized note first. Do not invent canonical references.
4. Fill in the [SR form](../../../_templates/items/software-requirement.md#basis) following the [SR guide](../../../software-requirements/README.md#sr-writing). New drafts are always `draft`.
5. Declare locatable sources in `upstream`. Explain the refinement rationale in the body.
6. Write normal/allowed, boundary, rejection, error, and forbidden side-effect cases separately.
7. When an interface, eligibility-lapse, concurrency, or metric policy is missing, list specific questions. Do not make decisions on behalf of the business.
8. Give every software acceptance criterion a full owner ID and a stable anchor.
   - Write only criteria observable at the software layer.
   - Leave the rules in their source text.
9. Check existing SRs to avoid duplicate numbers, duplicate requirements, or silent overrides.
10. For source changes, go through [semantic impact](../verify-change/SKILL.md#impact) first. Then plan the layered VTs in [Pre-implementation verification plan](#plan-verification).

Output: SRs with source locations, baselines, and anchored software acceptance criteria, plus specific questions for missing policies.

Stop points:

- A missing source or an ambiguity blocks confirmation of the corresponding requirement. Keep the known parts as drafts or questions.

<a id="delivery-slice"></a>
## Optional delivery slice

Purpose: organize delivery into a US only when delivery needs to be organized.

Inputs: the slice's basis, such as SRs with their confirmation basis and the applicable UC/INV; the actual roles/value, paths, and constraints.

Actions:

1. Decide whether there is an independent delivery need.
   - If there is none, skip creating a US. Skipping does not affect SRs, design, or VTs that can be planned directly.
   - Independent maintenance tasks still follow their original basis.
2. Otherwise, use the [US form](../../../_templates/items/user-story.md) and the [delivery guide](../../../user-stories/README.md#delivery).
3. For a formal slice based on SRs, first verify the confirmation basis of the SRs and the applicable UC/INV.
4. Describe the scope, change locations, dependencies, and checklist from the actual roles/value, paths, and constraints.
   - Do not invent roles.
   - Do not split stories by fixed technical layers.
   - Do not copy a second set of acceptance criteria.
5. Put task progress in the US body and content declarations in frontmatter. Runs belong in the VT.

Output: a US, only when delivery needs organizing, in the location given in the delivery guide.

Stop points:

- When sources are unconfirmed, keep only candidate splits and blockers. Do not make implementable commitments.

<a id="design-architecture"></a>
## Necessary architecture and decisions

Purpose: record design only for an independent structural constraint or a real trade-off. Neither an ABB nor an ADR requires a US first.

Inputs: the actual SRs, CAP/contexts, interfaces, applicable QAS/ADRs, and existing design; the [architecture rules](../../instructions/architecture.instructions.md).

Actions:

1. Read the inputs. Read the architecture rules explicitly.
2. Write an [ABB](../../../_templates/items/architecture-building-block.md) only for an independent structural constraint. Write an [ADR](../../../_templates/items/architecture-decision.md) only for a real trade-off.
3. Following the [architecture guide](../../../architecture/README.md#building-blocks), describe owned/consumed facts, responsibilities, dependencies, and collaboration direction.
4. Give a source for every technology choice, interface/dependency version, and runtime/deployment, observability, or quality statement.
   - Do not presuppose a four-layer directory structure or a platform.
5. Keep domain dependencies separate from legitimate composition-root wiring. Wiring is not a pass for controllers to bypass domain rules.
6. Give each real design constraint its own VC/anchor, or reference its original owner. Plan suitable criteria for it in the VT.
7. Hand incoming ADRs to [incoming-adr](../define-requirements/SKILL.md#incoming-adr). Decisions and notifications do not take effect automatically.

Output: ABBs or ADRs, only when warranted, in the locations given in the architecture guide.

Stop points:

- Undecided ADRs, draft QAS, and unknown versions or boundaries support only candidates and gaps.

<a id="plan-verification"></a>
## Pre-implementation verification plan

Purpose: before implementation, decide for every in-scope acceptance item which layer verifies it, how it is judged, and against which baselines.

Inputs: every in-scope REQ, UC/INV/QAS, SR, necessary design item, and maintenance completion condition; the actual environment, method, command/cwd, and report location.

Actions:

1. First, following the [full acceptance inventory](../../../verification/README.md#coverage-check), list the owner, full ID, source text, and baseline of every in-scope item, **including items without a VT**.
2. Following the [verification layers](../../../verification/README.md#layers), plan business, software, applicable design, or document checks separately, using a [VT](../../../_templates/items/verification-test.md#plan).
3. In each `targets` entry, declare the actual `scope/id#anchor` and a local `criterionAnchor`.
4. In the VT body, keep per item the independent criterion, observation method, preconditions/forbidden side effects, and open items.
   - Do not also copy a target-relationship table.
5. Trace each item back to its source owner, anchor, and layer. A single "all passed" cannot cover multiple targets.
6. When Gherkin is needed, use the [feature file](../../../_templates/items/verification-test.feature) following the [companion guide](../../../verification/README.md#feature-companion).
   - The feature file exclusively holds the scenario text. The VT keeps navigation to the actual file/baseline and the per-item criteria.
   - Use only known normal/negative cases and measures. Safety tags need a named source.
   - Without step implementations or a runner, the feature file is only a text plan. Do not call it automated.
7. Record the object, requirement/task, and VT plan baselines.
8. Verify the actual environment, method, command/cwd, and report location.
9. Keep layers apart:
   - Business acceptance is not an aggregate of software results.
   - Never enter document checks as behavioral runs.
10. Register navigation, checked baselines, and gaps in the [verification index](../../../verification/README.md#coverage-index). Do not build a separate result table.
11. Before implementation and runs, check complete coverage and semantic impact with [verify-change](../verify-change/SKILL.md#coverage).

Output: VTs (and feature companions when needed) with per-target criteria, baselines, and gaps, registered in the verification index.

Stop points:

- When a source or identity is missing, record an exact gap first. Do not work backward from existing VTs or narrow the scope.
- When the project, command, or report is missing, mark each affected target `not-run` and state the gap. Do not invent test identifiers.
- Draw conclusions in the original record only when actual evidence supports them.

<a id="sequence-diagram"></a>
## Sequence description

Purpose: describe one scenario's interaction paths using only what the sources support.

Inputs: this scenario's actual UC, ABBs, rules, participants, and event/interface contracts with their versions.

Actions:

1. Read the inputs. Use a [SEQ](../../../_templates/items/sequence-diagram.md).
2. For each path, describe the direction from provider/producer to user/consumer, the message meaning, and the known expectations for success, rejection, and error.
3. Adopt an asynchronous boundary only when existing sources explicitly state asynchronous integration or event consumption.
4. When there is only a conceptual exchange between contexts, do not invent synchronous calls, brokers, retries/timeouts/idempotency/ordering, or delivery guarantees.
5. In Mermaid, express only the parts traceable to a source. Mermaid is not a runtime test.
6. Before revising a confirmed diagram, check authorization, the old and new baselines, and the verification impact. Do not overwrite the original evidence.

Output: a SEQ in the location given in its guide.

Stop points:

- When the ABB participant mapping or a contract is missing, mark the description as partial and record the gap. Defer the diagram if necessary.

<a id="build-architecture-spec"></a>
## Compile the architecture specification

Purpose: compile a Markdown architecture specification that shows how complete each source view is.

Inputs: the business, logical, runtime, and deployment sources within the authorized scope; a model/implementation summary, if provided.

Actions:

1. Following the [SWAS](../../../_templates/items/architecture-specification.md), read the business, logical, runtime, and deployment sources within the authorized scope.
   - Do not modify read-only domain sources.
2. If a model/implementation summary is provided, check its source baselines and go back to the source text. When no summary is provided, do not fake an export.
3. Keep the [nine source views](../../../architecture/README.md#architecture-specifications) and their original baselines. Give each view a state:
   - `unverified`: the source is missing, unreadable, or unverifiable. List the specific gap.
   - `partial`: the source is partially readable.
   - `available`: only when the source is complete.
4. Treat these states as source completeness only. They do not indicate acceptable risk, approval, or release.
5. Produce only a Markdown compilation. This method provides no PDF/presentation renderer.

Output: a SWAS in Markdown, in the location given in its guide.

Stop points:

- Errors in required inputs still block.
- Do not fill in missing ABB, risk, deployment, or release materials with infrastructure or classifications.

## Outputs

- Create or revise SRs, VTs and their companions, and the verification index as needed.
- Put US, ABB/ADR, and SEQ/SWAS in the locations given in their respective guides. Do not leave formal content in the forms.
- For code work, use [implement-task](../implement-task/SKILL.md) to maintain existing code and [generate-code](../generate-code/SKILL.md) for initial generation. Each needs its own development inputs and authorization.

## Done when

Deliver this specification/plan only when:

- All in-scope acceptance criteria have been inventoried.
- Each target and its layer are explicit.
- The pre-implementation verification plan and its gaps are locatable.

Delivery does not mean behavioral verification has passed. Without an application, application checks are not applicable to documentation tasks, and planned business/software VTs remain `not-run`.

## Stop conditions

- Stop the affected specification confirmation or implementation when any of these holds:
  - Sources cannot determine behavior.
  - Acceptance targets cannot be located.
  - Boundaries conflict.
  - Authorization is unclear.
- Stop writing when a file to be written conflicts with its existing content.
- Then keep known drafts and exact gaps.
- **Do not finish the task by deleting in-scope acceptance criteria, forcing a US, or borrowing results from another layer.**
