---
name: verify-change
description: Use when assessing acceptance or domain artifacts, querying current inventory, reviewing backlog evidence, or checking coverage and result applicability after a rule or baseline change.
---

# Verify acceptance, impact, and evidence

Start from the complete list of delivery acceptance criteria; never work backward from existing VTs to infer the scope. Complete traceability, an actual run, and a successful run are three different conclusions.

## Inputs

- The current task and the complete delivery scope; the actual model, REQs, SRs, necessary design, and maintenance completion conditions.
- The Git branch, commit, and uncommitted scope; the requirement and VT baselines; all related VTs, existing runs, and raw reports.
- The check mode and authorization; the actual object and the [development configuration](../../../docs/development.md#project-registration), or what is missing from it.
- A domain review additionally needs the artifacts, sources, contexts, and open questions actually provided this time; a query needs an explicit root directory, object type, and filter scope; a BL check needs the original question and the decision evidence. Include governance/risk materials only when they are provided and apply.

<a id="review-mode"></a>
## Confirm the mode first

Only execution mode performs the authorized checks and recording described below. **Read-only review mode** only reads existing materials, checks evidence, and returns findings; in this mode, the run and write steps below serve only to list pending actions: do not run verification commands, and do not modify VTs, the index, logs, or other output files. Report what needs to be run and what is missing; never fabricate results or approve on behalf of the authorizer. This convention is not a client-enforced permission boundary.

Domain reviews, inventory queries, and BL reviews are read-only by default; to run anything or save a report, first obtain specific authorization for that task. A locatable file, a valid structure, traceability coverage, an actual run, success, and current applicability each rest on a different basis; "Approved", a role name, or a commit cannot replace a named decision, scope, and baseline.

<a id="coverage"></a>
## Coverage check

1. Following the [acceptance inventory](../../../verification/README.md#coverage-check), read all acceptance sources within this scope, and record for each item its owner, full ID, source link, layer, and baseline; include the related UC/INV/QAS, REQs, SRs, necessary design, maintenance conditions, and **targets without a VT**. Even if every existing VT has valid file links, do not skip the full inventory. Exclusions need a confirmed basis; gaps must not be removed by narrowing the scope.
2. For each item, search the target fields of VTs/validation scenarios, and check whether the method, preconditions, boundaries, and independent criterion are sufficient to judge that acceptance criterion. Then **trace back every actual target**: Does the file/anchor exist? Do the full ID and the owner/item match? Is the layer correct? Does the criterion really cover the target? With metadata, look up by `scope/id#anchor`; for old materials, still check against the original owner ID and stable links, without migrating them just to look them up. List same-number-different-owner IDs, generic headings, omissions, and dangling targets separately, with exact IDs/locations. When the input gives no identity, record the actually available sources and the gaps and ask for them; do not invent target numbers.
3. Check source relationships: the upstream basis stays in the [SR](../../../software-requirements/README.md#traceability), and target relationships stay in the [target declarations of VTs/scenarios](../../../verification/README.md#domain-scenarios). When metadata is adopted, `upstream` / `targets` belong in frontmatter, and body criteria are located by `criterionAnchor`; old records keep their original fields. The [verification index](../../../verification/README.md#coverage-index) only registers navigation, baselines, gaps, and reference differences; it does not copy acceptance text, reverse mappings, or another result table.

When authorized to run the tool, call `trace_report(root, delivery_ids)` through the [actual coverage interface](../../utilities/README.md#traceability); the complete list comes from step 1 and must not be rebuilt from VTs. Trace back all actual targets, and keep input errors and source locations. The layer and criterion checks are a mechanical lower bound; they cannot replace the semantic review in step 2 or prove execution.

<a id="domain-review"></a>
## Domain artifact review

Read the in-scope sources and current artifacts. First inventory all applicable acceptance criteria as described above, then check term meanings, concept relationships, the basis from rules to INVs, the facts owned/consumed by contexts, UC paths, QAS measures, and adopted interface/tactical conventions. Do not force optional materials that were not adopted; list the confirmation basis, unknown facts, and model drift separately.

Each finding includes: the actual source and file/line or section, the object baseline, the observation or inference, severity and its rationale, the affected artifacts/targets, the decision or evidence needed, the suggested action, and any existing BL. Severity expresses the impact of this issue; do not assign clinical/regulatory levels on your own. When a file, ID, accountable owner, or evidence is missing, state it item by item; when there is no BL, suggest creating one, and do not pretend it has been created or resolved.

Output findings and residual gaps; do not automatically refactor, correct statuses, or declare the model healthy. Content that says "confirmed/approved" but lacks a named decision and an applicable baseline cannot be confirmed as approved; structural validation cannot authenticate identity either. For candidate interpretations of language/boundaries, use [knowledge crunching](../define-requirements/SKILL.md#distill); actual changes still go back to an authorized task.

When a standalone record is needed, use the [review form](../../../_templates/items/review-record.md) and the [governance field guide](../../../docs/governance.md#ownership); for evaluating a tool's use, also use the [tool record](../../../docs/ai-tooling.md#adoption) to locate the version, configuration, inputs, evidence, and decision scope. Read-only mode still returns only the findings corresponding to these fields, without running checks or writing forms; running or saving requires authorization for this session. Keep actual decisions separate from VT results; keep gaps for unknown risks or missing decisions, and do not fill in values just to make an export complete.

<a id="query"></a>
## Query the actual inventory

Read the actual files for the given root directory, object type, scope, and question; sort stably by path and full identity, and return the matches, the scope actually read and not read, counts, source versions, and exact gaps. "No formal object" and "unreadable" are different conclusions; do not infer objects from blank forms, directory names, or future files. Querying one kind of inventory is not full acceptance coverage; for coverage questions, still start from [all acceptance criteria](#coverage).

A query does not generate a model, backfill artifacts, or create a persistent index. If a derived summary exists, return its source and check its baseline; a summary cannot replace the source text, and without a summary, read the existing materials. The [parser and formal artifact checker](../../utilities/README.md#artifact-checker) handle metadata, identity, structure, placeholders, and local links, separately from the coverage interface. Read-only review mode does not run tools; when authorized to run them, record the explicit root, the complete current inventory, the optional exact base, the actual counts, and the read-set digest; `empty` does not count as a pass. When separately authorized to derive or check the model, use the [model interface](../../utilities/README.md#model-export) and the [optional local source manifest](../../contracts/README.md#model-sources); the source states of the nine views are not business results, and files are written only with explicit authorization for new output.

<a id="bc-review"></a>
## BC derivation and implementation boundary review

Starting from the [complete acceptance criteria](#coverage), check the actual SRs, optional US, ABB/ADR, VT/companion, SEQ/SWAS, and source baselines. By default, follow [read-only mode](#review-mode), and do not generate or run anything automatically. Formal relationships and content state follow the existing metadata, and the body only explains sources and independent criteria; old lightweight materials are not forcibly migrated.

- Do the REQ/UC/INV/CAP/QAS sufficiently support the software behavior, rejections/errors, and forbidden side effects that have been written? Are unconfirmed sources, roles, metrics, and concurrency/failure policies still explicitly open? Does the US only organize slices rather than become a mandatory bridge, and do ABB/VT depend only on their own required inputs?
- Do ABB/ADR contain only sourced structural constraints and real trade-offs? For code-related reviews, explicitly read the [architecture](../../instructions/architecture.instructions.md), [coding](../../instructions/coding.instructions.md), [security](../../instructions/security.instructions.md), and applicable [test rules](../../instructions/tests.instructions.md), even if the actual directories do not match. Distinguish a legitimate wiring entry point from a business-logic bypass, and do not infer permissions from boundary names.
- Does each VT trace back, item by item, to the actual owner/anchor, an independent criterion, and the actual scenario/test location? Does the `.feature` file exclusively hold the scenario text? Without an application, step implementations, a runner, or a report, keep `not-run`; Approved, test names, and parser success prove neither approval nor execution.
- Does the SEQ distinguish conceptual participants from actual ABBs/interfaces, and keep sourced directions and asynchronous contracts without inventing transport guarantees? Is the readability of the SWAS's nine source categories checked against the source text/baselines, and when ABB/deployment/risk/release materials are missing, is the gap kept rather than invented infrastructure or approval?
- Did initial generation go through the [generate-code preflight](../generate-code/SKILL.md#preflight), listing all exact paths, sources/acceptance criteria, and the authorized scope? Non-empty conflicts, path mismatches, or missing development inputs must have a blocker record; skipping does not count as complete generation. Existing maintenance checks the task/diff/reproduction rather than overwriting with an initializer; read-only sources and owner content must be preserved.

Return findings using the [existing fields](#domain-review): actual location, baseline, rationale, impact, and gaps. Actual changes or runs still need specific authorization; this subsection adds no checker, security audit, or application pass verdict.

<a id="backlog-review"></a>
## Open question and BL review

Check each item against the original question, conflicting sources, impact/blocked scope, actual accountable owner, and [decision evidence](../../../_templates/items/backlog-item.md#decision). Report items still awaiting an answer, items decided but not yet implemented, items with insufficient evidence, and items that can be recommended for closure; these are categories of this review's findings, not replacements for the original status enumeration. Only locatable and applicable decision/handling evidence supports a closure recommendation; an expired date, a schedule, an implementation constant, complete links, or a self-declared "done" is not enough.

Using the [finding fields](#domain-review), list the residual impact and the acceptance criteria/VTs still to be checked; statistics state the scope actually inventoried this time, and unknown items are not counted as resolved. Update the original BL's handling progress, decision basis, and follow-up review only when authorized to modify it, keeping its history; `contentState`, handling progress, actual run results, and current applicability are never converted into one another.

<a id="impact"></a>
## Semantic impact (before runs)

1. Compare the old and new rules, contexts, acceptance criteria, and baselines, and record the actual changed IDs/locations, sources, and confirmation state. Following references and business meaning, trace the dependent models, UC/INV, REQ/QAS, SRs, US, ABB/ADR, SEQ/SWAS, scenarios/VTs with their companions, and tasks; for boundary changes, also check CAP, the context map, Published Interfaces, and consumers. Even if a value exists in only one rule file, the behavioral boundaries of the artifacts that reference it may still be affected. Include [incoming ADRs](../define-requirements/SKILL.md#incoming-adr), [Intended Use](../define-requirements/SKILL.md#intended-use), and governance/risk references only when they are actually provided and apply; when a source is missing, state that the affected judgment cannot be completed, and do not make risk decisions on anyone's behalf.
2. Following the [impact guide](../../../verification/README.md#change-impact), list the affected items with their sources, rationale, severity, who needs to confirm what, and the suggested order. Update acceptance boundaries, error/forbidden side effects, and VT expectations only after the change is confirmed and the modification is authorized, and keep regression scenarios that still hold. Give a rationale for any no-impact judgment; clarify unconfirmed business changes first, without changing rules or deleting original acceptance criteria on your own. A suggested order is not a change that has been made.
3. Keep the actual results of old runs with their original object, requirement, and VT baselines; in the original result's [applicability section](../../../_templates/items/verification-test.md#applicability), append an `unverified` entry for the current baseline with the impact rationale. Never rewrite an old success as a new success or as a historical failure; new checks must be appended as separate records.

When authorized to run the tool, use the [impact candidate interface](../../utilities/README.md#impact-candidates) `impact_report(root, base_sha, task_ids=())`. Pass the exact full commit and any provided task keys, and read the current snapshot; old and new dependencies, deleted sources, and removed references all keep their reasons. Candidates do not represent final business impact, severity, or confirmation; non-canonical dependencies and unknown semantics are still checked as described above. The tool does not write back to rules or original results, and does not run VTs.

## Runs and records

1. Following the [verification layers](../../../verification/README.md#layers), determine which objects can currently be run and the per-item criteria. Without an application, application checks are not applicable to documentation tasks, and planned business/software VTs remain `not-run`. When an application exists but the object, environment, or command is unavailable, the related checks are `not-run` with the specific reason; they must not be skipped by calling them not applicable.
2. Run only actually configured and authorized commands, cwd, or explicit manual steps. Following the [execution guide](../../../verification/README.md#execution), check the actual scope, the discovered/executed/skipped counts, and the per-target observations; zero discovered tests, all skipped, missing evidence, or a zero exit code alone cannot establish acceptance success.
3. Append to the [VT actual run section](../../../_templates/items/verification-test.md#runs) the actual object/requirement/VT baselines, time, environment, steps, raw report, and per-item results; anything not run stays `not-run`, and skips are recorded as `skipped` with the reason. When a report is inaccessible, state the limitation; do not invent links or backfill results that were not observed.
4. [Standalone document checks](../../../docs/development.md#document-checks) use their own object, criteria, results, and baselines, and may be recorded in a document-layer VT or an existing authorized check record; never enter them into a planned behavioral VT. Business acceptance cannot be derived by aggregating software passes either. Use [record-handoff](../record-handoff/SKILL.md) to link the authoritative records, exact gaps, and remaining actions; the log does not copy result tables.

## Outputs and completion

Authorized records go into `verification/README.md#coverage-index`, the target/run/applicability/gap sections of the related `verification/VT-NNN-<slug>.md`, and the actual report entry points; necessary acceptance changes go back to their owners. Domain issues go, as needed, into the open-items section of the original artifact or the [formal location for BLs](../../../domain-model/README.md#strategic-forms); do not create a separate result or status mirror. Read-only reviews and queries only return locatable findings, inventory, evidence limitations, and suggested run items; they do not write files.

Once all acceptance criteria have been checked, dangling/uncovered items are explicit, semantic impact has been traced, actual evidence is locatable, and items not run are kept, you may report this check as complete, together with its scope. Only when actual evidence for each target meets its criterion may the corresponding acceptance criterion be declared passed.

## Stop conditions

When the complete scope or a necessary source is unreadable, the confirmation basis conflicts, check prerequisites are missing, a run fails, or authorization is insufficient, stop the affected runs and pass declarations, and keep the known findings and next steps. Never delete scope, invent targets, or fill gaps with results from another layer.
