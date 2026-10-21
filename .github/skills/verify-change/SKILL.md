---
name: verify-change
description: Use when assessing acceptance coverage or domain and BC artifacts, querying the current inventory, reviewing open questions and backlog evidence, checking semantic impact and result applicability after a rule or baseline change, or recording authorized verification runs. Not for planning verification (use specify-feature) or handing off a task (use record-handoff).
---

# Verify acceptance, impact, and evidence

Use this method to check acceptance coverage, domain artifacts, open questions, semantic impact, and run evidence, and to record results when authorized. **Start from the complete list of delivery acceptance criteria; never work backward from existing VTs to infer the scope.** Traceability complete, actually run, run succeeded, and currently applicable are separate conclusions, each with its own basis (see [Keep conclusions separate](#conclusions)).

## Inputs

- General:
  - The current task and the complete delivery scope.
  - The actual model, REQs, SRs, necessary design, and maintenance completion conditions.
  - The Git branch, commit, and uncommitted scope.
  - The requirement and VT baselines.
  - All related VTs, existing runs, and raw reports.
  - The check mode and authorization.
  - The actual object and the [development configuration](../../../docs/development.md#project-registration), or what is missing from it.
- Per activity, in addition:
  - Domain review: the artifacts, sources, contexts, and open questions actually provided this time.
  - Query: an explicit root directory, object type, and filter scope.
  - BL review: the original question and the decision evidence.
- When applicable: governance/risk materials, only when they are provided and apply.

<a id="review-mode"></a>
## Choose the mode first

Do this before any activity below. The mode decides which steps you perform and which you only list.

1. Read the check mode and authorization from the task. If authorization for a step is insufficient, see Stop conditions.
2. Choose the mode:
   - Read-only review mode: the default for domain reviews, inventory queries, BL reviews, and BC reviews. To run anything or save a report in these activities, first obtain specific authorization for that task.
   - Execution mode: only this mode performs the authorized checks and recording described below.
3. In read-only review mode:
   - Read existing materials, check evidence, and return findings.
   - Treat each run and write step below, including every "Record" line, only as a pending action to list.
   - **Do not run verification commands or tools. Do not modify VTs, the index, logs, or other output files.**
   - Report what needs to be run and what is missing.
   - Never fabricate results or approve on behalf of the authorizer.
4. In execution mode, perform only the authorized checks and recording, following the activity steps below.

This mode is a working convention, not a client-enforced permission boundary.

<a id="conclusions"></a>
## Keep conclusions separate

Each conclusion rests on its own basis. Never let one conclusion stand in for another.

| Conclusion | Rests on | Not sufficient on its own |
| --- | --- | --- |
| Traceability complete | The full acceptance inventory, with every actual target traced back ([Coverage check](#coverage)) | Valid file links on every existing VT; a list rebuilt from existing VTs; a query of one kind of inventory; the mechanical layer and criterion checks of `trace_report` |
| Actually run | An observed run and its record ([Runs and records](#runs)) | "Approved"; test names; parser success; mechanical traceability checks |
| Run succeeded (criterion passed) | Actual evidence for each target that meets its criterion | Zero discovered tests; all tests skipped; missing evidence; a zero exit code alone; an `empty` result; aggregated software passes (for business acceptance); results from another layer |
| Currently applicable | The latest applicability entry for the current object, requirement, and VT baselines ([Semantic impact](#impact)) | An old result recorded under earlier baselines |
| Approved or confirmed | A named decision, with its scope and an applicable baseline | "Approved" or "confirmed/approved" text; a role name; a commit; test names; parser success |

- A locatable file and a valid structure are separate conclusions too. Structural validation cannot authenticate identity.
- Never convert `contentState`, handling progress, actual run results, and current applicability into one another.

<a id="coverage"></a>
## Coverage check

Purpose: confirm that every delivery acceptance criterion in scope has a target able to judge it, and that every actual target traces back correctly.

1. Build the full acceptance inventory, following the [acceptance inventory](../../../verification/README.md#coverage-check).
   - Read all acceptance sources within this scope.
   - Include the related UC/INV/QAS, REQs, SRs, necessary design, maintenance conditions, and targets without a VT.
   - List for each item its owner, full ID, source link, layer, and baseline.
   - Do not skip the full inventory, even if every existing VT has valid file links.
   - Exclude an item only on a confirmed basis.
   - Do not remove gaps by narrowing the scope.
2. Match each item to its targets.
   - Search the target fields of VTs/validation scenarios for the item.
   - Check whether the method, preconditions, boundaries, and independent criterion are sufficient to judge that acceptance criterion.
3. Trace back every actual target.
   - Locate it: with metadata, by `scope/id#anchor`; for old materials, still by the original owner ID and stable links. Do not migrate old materials just to look them up.
   - Does the file/anchor exist?
   - Do the full ID and the owner/item match?
   - Is the layer correct?
   - Does the criterion really cover the target?
4. Report identity problems separately, with exact IDs/locations: same-number-different-owner IDs, generic headings, omissions, and dangling targets.
   - When the input gives no identity, list the actually available sources and the gaps, and ask for them.
   - Do not invent target numbers.
5. Check that each relationship stays in its formal location:
   - The upstream basis stays in the [SR](../../../software-requirements/README.md#traceability).
   - Target relationships stay in the [target declarations of VTs/scenarios](../../../verification/README.md#domain-scenarios).
   - When metadata is adopted, `upstream` / `targets` belong in frontmatter, and body criteria are located by `criterionAnchor`. Old records keep their original fields.
   - The [verification index](../../../verification/README.md#coverage-index) only registers navigation, baselines, gaps, and reference differences. It does not copy acceptance text, reverse mappings, or another result table.
6. When authorized to run the tool, call `trace_report(root, delivery_ids)` through the [actual coverage interface](../../utilities/README.md#traceability).
   - Pass the complete list from step 1. Do not rebuild it from VTs.
   - Trace back all actual targets, and keep input errors and source locations.
   - Treat the tool's layer and criterion checks as a mechanical lower bound. They do not replace the semantic review in steps 2 and 3, and they do not prove execution.

- Return: the full inventory from step 1, the per-target findings from steps 2 to 4, and the exact gaps.
- Record: authorized results only, at the locations listed under Outputs.

<a id="domain-review"></a>
## Domain artifact review

Purpose: check domain artifacts against their sources and against each other, and return findings. Read-only by default (see [mode](#review-mode)).

1. Read the in-scope sources and current artifacts.
2. Inventory all applicable acceptance criteria first, as in [Coverage check](#coverage) step 1.
3. Then check the following, without forcing optional materials that were not adopted:
   - term meanings and concept relationships;
   - the basis from rules to INVs;
   - the facts owned or consumed by contexts;
   - UC paths and QAS measures;
   - adopted interface/tactical conventions.
4. List the confirmation basis, unknown facts, and model drift separately.
5. Write each finding with these fields. The BC and BL reviews reuse them.
   - The actual source and file/line or section.
   - The object baseline.
   - The observation or inference.
   - The severity and its rationale. Severity expresses the impact of this issue; do not assign clinical/regulatory levels on your own.
   - The affected artifacts/targets.
   - The decision or evidence needed.
   - The suggested action.
   - Any existing BL.
6. Handle what is missing:
   - When a file, ID, accountable owner, or evidence is missing, state it item by item.
   - When there is no BL, suggest creating one. Do not pretend it has been created or resolved.
7. Do not confirm content as approved when it says "confirmed/approved" but lacks a named decision and an applicable baseline. Structural validation cannot authenticate identity either (see [Keep conclusions separate](#conclusions)).
8. For candidate interpretations of language/boundaries, use [knowledge crunching](../define-requirements/SKILL.md#distill). Actual changes still go back to an authorized task.
9. When a standalone record is needed:
   - Use the [review form](../../../_templates/items/review-record.md) and the [governance field guide](../../../docs/governance.md#ownership).
   - When evaluating a tool's use, also use the [tool record](../../../docs/ai-tooling.md#adoption) to locate the version, configuration, inputs, evidence, and decision scope.
   - In read-only mode, return only the findings that correspond to these fields. Do not run checks or write forms.
   - Run checks or save the record only with authorization for this session.
   - Keep actual decisions separate from VT results.
   - Keep gaps for unknown risks or missing decisions. Do not fill in values just to make an export complete.
10. Do not automatically refactor, correct statuses, or declare the model healthy.

- Return: the findings, with the fields from step 5, and the residual gaps.
- Record: a standalone review or tool record from step 9, only when authorized.

<a id="query"></a>
## Query the actual inventory

Purpose: answer a question about which formal objects exist, from the actual files only. Read-only by default (see [mode](#review-mode)).

1. Read the actual files for the given root directory, object type, scope, and question.
   - Do not infer objects from blank forms, directory names, or future files.
   - If a derived summary exists, return its source and check its baseline. A summary cannot replace the source text.
   - Without a summary, read the existing materials.
2. Sort the matches stably by path and full identity.
3. Report "no formal object" and "unreadable" as different conclusions.
4. For coverage questions, still start from [all acceptance criteria](#coverage). Querying one kind of inventory is not full acceptance coverage.
5. Run tools only when authorized; read-only review mode does not run tools.
   - The [parser and formal artifact checker](../../utilities/README.md#artifact-checker) handle metadata, identity, structure, placeholders, and local links. They are separate from the coverage interface.
   - When authorized to run them, record the explicit root, the complete current inventory, the optional exact base, the actual counts, and the read-set digest.
   - `empty` does not count as a pass.
   - When separately authorized to derive or check the model, use the [model interface](../../utilities/README.md#model-export) and the [optional local source manifest](../../contracts/README.md#model-sources). The source states of the nine views are not business results.
   - Write files only with explicit authorization for new output.
6. Do not generate a model, backfill artifacts, or create a persistent index.

- Return: the matches, the scope actually read and not read, counts, source versions, and exact gaps. When tools ran under authorization, also return the run details from step 5.
- Record: no files by default. Write files only with explicit authorization for new output (step 5).

<a id="bc-review"></a>
## BC derivation and implementation boundary review

Purpose: check that a BC's derived requirements, design, verification, and generated or maintained code stay within their sources and authorized boundaries. By default, follow [read-only mode](#review-mode); do not generate or run anything automatically.

1. Start from the [complete acceptance criteria](#coverage).
2. Read the actual SRs, optional US, ABB/ADR, VT/companion, SEQ/SWAS, and source baselines.
   - Formal relationships and content state follow the existing metadata. The body only explains sources and independent criteria.
   - Do not forcibly migrate old lightweight materials.
3. Check requirements and slices:
   - Do the REQ/UC/INV/CAP/QAS sufficiently support the written software behavior, rejections/errors, and forbidden side effects?
   - Are unconfirmed sources, roles, metrics, and concurrency/failure policies still explicitly open?
   - Does the US only organize slices, rather than become a mandatory bridge?
   - Do ABB/VT depend only on their own required inputs?
4. Check architecture and code boundaries:
   - Do ABB/ADR contain only sourced structural constraints and real trade-offs?
   - For code-related reviews, explicitly read the [architecture](../../instructions/architecture.instructions.md), [coding](../../instructions/coding.instructions.md), [security](../../instructions/security.instructions.md), and applicable [test rules](../../instructions/tests.instructions.md), even if the actual directories do not match their `applyTo` patterns.
   - Distinguish a legitimate wiring entry point from a business-logic bypass.
   - Do not infer permissions from boundary names.
5. Check verification:
   - Does each VT trace back, item by item, to the actual owner/anchor, an independent criterion, and the actual scenario/test location?
   - Does the `.feature` file exclusively hold the scenario text?
   - Without an application, step implementations, a runner, or a report, keep `not-run`.
   - "Approved", test names, and parser success prove neither approval nor execution.
6. Check SEQ and SWAS:
   - Does the SEQ distinguish conceptual participants from actual ABBs/interfaces?
   - Does the SEQ keep sourced directions and asynchronous contracts without inventing transport guarantees?
   - Is the readability of the SWAS's nine source categories checked against the source text/baselines?
   - When ABB/deployment/risk/release materials are missing, is the gap kept, rather than invented infrastructure or approval?
7. Check generation and maintenance:
   - Did initial generation go through the [generate-code preflight](../generate-code/SKILL.md#preflight), listing all exact paths, sources/acceptance criteria, and the authorized scope?
   - Does each non-empty conflict, path mismatch, or missing development input have the required blocker record? Skipping does not count as complete generation.
   - Does existing maintenance check the task/diff/reproduction, rather than overwrite with an initializer?
   - Are read-only sources and owner content preserved, as required?
8. Make actual changes or runs only with specific authorization. This section adds no checker, security audit, or application pass verdict.

- Return: findings using the [existing finding fields](#domain-review): actual location, baseline, rationale, impact, and gaps.

<a id="backlog-review"></a>
## Open question and BL review

Purpose: classify open questions and BLs by their evidence, and recommend closure only where evidence supports it. Read-only by default (see [mode](#review-mode)).

1. Check each item against:
   - the original question;
   - conflicting sources;
   - the impact/blocked scope;
   - the actual accountable owner;
   - the [decision evidence](../../../_templates/items/backlog-item.md#decision).
2. Report the findings in these categories: items still awaiting an answer; items decided but not yet implemented; items with insufficient evidence; items that can be recommended for closure. These categories describe this review's findings; they do not replace the original status enumeration.
3. Recommend closure only on locatable and applicable decision/handling evidence. An expired date, a schedule, an implementation constant, complete links, or a self-declared "done" is not enough.
4. Using the [finding fields](#domain-review), list the residual impact and the acceptance criteria/VTs still to be checked.
5. State statistics for the scope actually inventoried this time. Do not count unknown items as resolved.
6. Update the original BL's handling progress, decision basis, and follow-up review only when authorized to modify it. Keep its history.
   - Never convert `contentState`, handling progress, actual run results, and current applicability into one another (see [Keep conclusions separate](#conclusions)).

- Return: the categorized findings, the residual impact, the items still to be checked, and statistics with their scope.
- Record: the update to the original BL from step 6, only when authorized.

<a id="impact"></a>
## Semantic impact (before runs)

Purpose: before any run, trace what a change to rules, contexts, acceptance criteria, or baselines affects, and mark old results for re-review.

1. Compare the old and new rules, contexts, acceptance criteria, and baselines. List the actual changed IDs/locations, sources, and confirmation state.
2. Trace the dependents by following references and business meaning: the dependent models, UC/INV, REQ/QAS, SRs, US, ABB/ADR, SEQ/SWAS, scenarios/VTs with their companions, and tasks.
   - For boundary changes, also check CAP, the context map, Published Interfaces, and consumers.
   - Even if a value exists in only one rule file, the behavioral boundaries of the artifacts that reference it may still be affected.
3. Include [incoming ADRs](../define-requirements/SKILL.md#incoming-adr), [Intended Use](../define-requirements/SKILL.md#intended-use), and governance/risk references only when they are actually provided and apply.
   - When a source is missing, state that the affected judgment cannot be completed.
   - Do not make risk decisions on anyone's behalf.
4. Following the [impact guide](../../../verification/README.md#change-impact), list the affected items with their sources, rationale, severity, who needs to confirm what, and the suggested order.
   - Give a rationale for any no-impact judgment.
   - A suggested order is not a change that has been made.
5. Handle acceptance changes:
   - Clarify unconfirmed business changes first. Do not change rules or delete original acceptance criteria on your own.
   - Update acceptance boundaries, error/forbidden side effects, and VT expectations only after the change is confirmed and the modification is authorized.
   - Keep regression scenarios that still hold.
6. Mark old results for re-review:
   - Keep the actual results of old runs with their original object, requirement, and VT baselines.
   - In the original result's [applicability section](../../../_templates/items/verification-test.md#applicability), append an `unverified` entry for the current baseline with the impact rationale.
   - Never rewrite an old success as a new success or as a historical failure.
   - Append new checks as separate records.
7. When authorized to run the tool, use the [impact candidate interface](../../utilities/README.md#impact-candidates) `impact_report(root, base_sha, task_ids=())`.
   - Pass the exact full commit and any provided task keys. The tool reads the current snapshot.
   - Old and new dependencies, deleted sources, and removed references all keep their reasons.
   - Candidates do not represent final business impact, severity, or confirmation. Still check non-canonical dependencies and unknown semantics as in steps 1 to 4.
   - The tool does not write back to rules or original results, and does not run VTs.

- Return: the changed items from step 1 and the affected items from step 4, with the rationale for any no-impact judgment.
- Record: the `unverified` applicability entries from step 6, and the confirmed and authorized updates from step 5.

<a id="runs"></a>
## Runs and records

Purpose: run only configured, authorized checks and record exactly what was observed. Only execution mode runs and records; in read-only review mode, list these steps as pending actions.

1. Following the [verification layers](../../../verification/README.md#layers), determine which objects can currently be run and the per-item criteria.
   - Without an application, application checks are not applicable to documentation tasks, and planned business/software VTs remain `not-run`.
   - When an application exists but the object, environment, or command is unavailable, mark the related checks `not-run` with the specific reason. Do not skip them by calling them not applicable.
2. Run only actually configured and authorized commands, cwd, or explicit manual steps.
3. Following the [execution guide](../../../verification/README.md#execution), check the actual scope, the discovered/executed/skipped counts, and the per-target observations.
   - Zero discovered tests, all skipped, missing evidence, or a zero exit code alone cannot establish acceptance success.
4. Append to the [VT actual run section](../../../_templates/items/verification-test.md#runs): the actual object/requirement/VT baselines, time, environment, steps, raw report, and per-item results.
   - Keep anything not run as `not-run`. Record skips as `skipped` with the reason.
   - When a report is inaccessible, state the limitation. Do not invent links or backfill results that were not observed.
5. Keep [standalone document checks](../../../docs/development.md#document-checks) separate. They use their own object, criteria, results, and baselines.
   - They may be recorded in a document-layer VT or an existing authorized check record.
   - Never enter them into a planned behavioral VT.
6. Do not derive business acceptance by aggregating software passes.
7. Use [record-handoff](../record-handoff/SKILL.md) to link the authoritative records, exact gaps, and remaining actions. The log does not copy result tables.

- Return: what was run, what stays `not-run` or `skipped` and why, and any report limitations.
- Record: the run entries from step 4 in the related VT, and the links from step 7 through record-handoff.

## Outputs

- Authorized records → `verification/README.md#coverage-index`, the target/run/applicability/gap sections of the related `verification/VT-NNN-<slug>.md`, and the actual report entry points.
- Necessary acceptance changes → back to their owners.
- Domain issues → as needed, the open-items section of the original artifact or the [formal location for BLs](../../../domain-model/README.md#strategic-forms).
- Read-only reviews and queries → return only locatable findings, inventory, evidence limitations, and suggested run items. They do not write files.
- Do not create a separate result or status mirror.

## Done when

You may report this check as complete, together with its scope, once all of these hold:

- All acceptance criteria have been checked.
- Dangling and uncovered items are explicit.
- Semantic impact has been traced.
- Actual evidence is locatable.
- Items not run are kept.

**Declare an acceptance criterion passed only when actual evidence for each target meets its criterion.**

## Stop conditions

- Stop the affected runs and pass declarations when:
  - the complete scope or a necessary source is unreadable;
  - the confirmation basis conflicts;
  - check prerequisites are missing;
  - a run fails;
  - authorization is insufficient.
- Then keep the known findings and next steps.
- Never delete scope, invent targets, or fill gaps with results from another layer.
