---
name: verify-change
description: Use when assessing acceptance coverage or domain and BC artifacts, querying the current inventory, reviewing open questions and backlog evidence, checking semantic impact and result applicability after a rule or baseline change, or recording authorized verification runs. Not for planning verification (use specify-feature) or handing off a task (use record-handoff).
---

# Verify acceptance, impact, and evidence

Use this method to check acceptance coverage, domain artifacts, open questions, semantic impact, and run evidence; record results only when authorized. **Start from the complete list of delivery acceptance criteria; never work backward from existing VTs to infer the scope.** Traceability, actual run, run success, and current applicability are separate conclusions (see [Keep conclusions separate](#conclusions)).

## Inputs

- General: the current task and complete delivery scope; the actual model, REQs, SRs, necessary design, and maintenance completion conditions; the Git branch, commit, and uncommitted scope; the requirement and VT baselines; all related VTs, existing runs, and raw reports; the check mode and authorization; the actual object and the [development configuration](../../../docs/development.md#project-registration), or what is missing from it.
- Per activity, in addition: domain review—the artifacts, sources, contexts, and open questions actually provided this time; query—an explicit root directory, object type, and filter scope; BL review—the original question and decision evidence.
- When applicable: governance/risk materials, only when provided and applicable.

<a id="review-mode"></a>
## Choose the mode first

Choose the mode before any activity below. The mode decides which steps you perform and which you only list.

1. Read the check mode and authorization from the task. If authorization for a step is insufficient, see Stop conditions.
2. Choose the mode:
   - Read-only review mode: the default for domain reviews, inventory queries, BL reviews, and BC reviews. Running anything or saving a report in these activities requires specific authorization for that task.
   - Execution mode: the only mode that performs the authorized checks and recording, following the activity steps below.
3. In read-only review mode, read existing materials, check evidence, and return findings. Treat every run and write step, including every "Record" line, as a pending action to list. **Do not run verification commands or tools. Do not modify VTs, the index, logs, or other output files.** Report what needs to be run and what is missing. Never fabricate results or approve on behalf of the authorizer.

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

- Locating a file and validating its structure are separate conclusions too; structural validation cannot authenticate identity.
- Never convert `contentState`, handling progress, actual run results, and current applicability into one another.

<a id="coverage"></a>
## Coverage check

Purpose: confirm that every delivery acceptance criterion in scope has a target able to judge it, and that every actual target traces back correctly.

1. Build the full acceptance inventory per the [acceptance inventory](../../../verification/README.md#coverage-check): every acceptance source in scope, including related UC/INV/QAS, REQs, SRs, necessary design, maintenance conditions, and targets without a VT. List each item's owner, full ID, source link, layer, and baseline. Do not skip it even if every VT has valid file links. Exclude an item only on a confirmed basis; never remove gaps by narrowing scope.
2. Match each item to its targets: search VT/scenario target fields for the item, and check that the method, preconditions, boundaries, and independent criterion can judge that acceptance criterion.
3. Trace back every actual target by metadata or `scope/id#anchor`. For old materials, use the original owner ID and stable links; do not migrate them just to look them up. Check that the file/anchor exists, the full ID and owner/item match, the layer is correct, and the criterion really covers the target.
4. Report identity problems separately, with exact IDs/locations: same-number-different-owner IDs, generic headings, omissions, and dangling targets. If the input gives no identity, list the available sources and gaps, and ask for them. Do not invent target numbers.
5. Keep each relationship in its formal location:
   - The upstream basis stays in the [SR](../../../software-requirements/README.md#traceability).
   - Target relationships stay in the [VT/scenario target declarations](../../../verification/README.md#domain-scenarios). With adopted metadata, `upstream` / `targets` belong in frontmatter and body criteria are located by `criterionAnchor`; old records keep their original fields.
   - The [verification index](../../../verification/README.md#coverage-index) only registers navigation, baselines, gaps, and reference differences. It copies no acceptance text, reverse mappings, or result table.
6. When authorized, call `trace_report(root, delivery_ids)` through the [actual coverage interface](../../utilities/README.md#traceability) with the complete step-1 list (never one rebuilt from VTs), tracing back all actual targets and keeping input errors and source locations. Its layer and criterion checks are a mechanical lower bound, not a replacement for steps 2 and 3 and not proof of execution.

- Return: the full inventory from step 1, the per-target findings from steps 2 to 4, and the exact gaps.
- Record: authorized results only, at the locations listed under Outputs.

<a id="domain-review"></a>
## Domain artifact review

Purpose: check domain artifacts against their sources and against each other, and return findings. Read-only by default (see [mode](#review-mode)).

1. Read the in-scope sources and current artifacts.
2. Inventory all applicable acceptance criteria first, as in [Coverage check](#coverage) step 1.
3. Then check, without forcing optional materials that were not adopted: term meanings and concept relationships; the basis linking rules to INVs; the facts owned or consumed by contexts; UC paths and QAS measures; adopted interface/tactical conventions.
4. List the confirmation basis, unknown facts, and model drift separately.
5. Write each finding with these fields (reused by the BC and BL reviews): actual source and file/line or section; object baseline; observation or inference; severity and rationale (impact only; do not assign clinical/regulatory levels on your own); affected artifacts/targets; decision or evidence needed; suggested action; any existing BL.
6. Handle what is missing: state each missing file, ID, accountable owner, or evidence item separately. With no BL, suggest creating one; do not pretend it has been created or resolved.
7. Do not confirm content as approved when it says "confirmed/approved" but lacks a named decision and an applicable baseline (see [Keep conclusions separate](#conclusions)).
8. For candidate interpretations of language/boundaries, use [knowledge crunching](../define-requirements/SKILL.md#distill). Actual changes still go back to an authorized task.
9. When a standalone record is needed, use the [review form](../../../_templates/items/review-record.md) and the [governance field guide](../../../docs/governance.md#ownership); for tool-use evaluation, also use the [tool record](../../../docs/ai-tooling.md#adoption) to locate version, configuration, inputs, evidence, and decision scope. In read-only mode, return only findings that match these fields; do not run checks or write forms. Run checks or save records only with authorization for this session. Keep actual decisions separate from VT results, and keep gaps for unknown risks or missing decisions rather than filling values to complete an export.
10. Do not automatically refactor, correct statuses, or declare the model healthy.

- Return: the findings, with the fields from step 5, and the residual gaps.
- Record: a standalone review or tool record from step 9, only when authorized.

<a id="query"></a>
## Query the actual inventory

Purpose: answer a question about which formal objects exist, from the actual files only. Read-only by default (see [mode](#review-mode)).

1. Read the actual files for the given root directory, object type, scope, and question. Do not infer objects from blank forms, directory names, or future files. A derived summary may be used only with its source and a checked baseline, and it never replaces the source text; without one, read the existing materials.
2. Sort the matches stably by path and full identity.
3. Report "no formal object" and "unreadable" as different conclusions.
4. For coverage questions, still start from [all acceptance criteria](#coverage). Querying one kind of inventory is not full acceptance coverage.
5. Run tools only when authorized; read-only review mode runs none. The [parser and formal artifact checker](../../utilities/README.md#artifact-checker) covers metadata, identity, structure, placeholders, and local links, separately from the coverage interface. When authorized, record the explicit root, complete current inventory, optional exact base, actual counts, and read-set digest. `empty` does not count as a pass. When separately authorized to derive or check the model, use the [model interface](../../utilities/README.md#model-export) and [optional local source manifest](../../contracts/README.md#model-sources); the nine views' source states are not business results. Write files only with explicit authorization for new output.
6. Do not generate a model, backfill artifacts, or create a persistent index.

- Return: the matches, the scope actually read and not read, counts, source versions, and exact gaps; plus the step-5 run details when tools ran under authorization.
- Record: no files by default; new output only under step 5.

<a id="bc-review"></a>
## BC derivation and implementation boundary review

Purpose: check that a BC's derived requirements, design, verification, and generated or maintained code stay within their sources and authorized boundaries. By default, follow [read-only mode](#review-mode); do not generate or run anything automatically.

1. Start from the [complete acceptance criteria](#coverage).
2. Read the actual SRs, optional US, ABB/ADR, VT/companion, SEQ/SWAS, and source baselines. Formal relationships and content state follow existing metadata; the body only explains sources and independent criteria. Do not forcibly migrate old lightweight materials.
3. Check requirements and slices:
   - Do the REQ/UC/INV/CAP/QAS sufficiently support the written software behavior, rejections/errors, and forbidden side effects?
   - Are unconfirmed sources, roles, metrics, and concurrency/failure policies still explicitly open?
   - Does the US only organize slices, rather than become a mandatory bridge?
   - Do ABB/VT depend only on their own required inputs?
4. Check architecture and code boundaries:
   - Do ABB/ADR contain only sourced structural constraints and real trade-offs?
   - For code-related reviews, explicitly read the [architecture](../../instructions/architecture.instructions.md), [coding](../../instructions/coding.instructions.md), [security](../../instructions/security.instructions.md), and applicable [test rules](../../instructions/tests.instructions.md), even if the actual directories do not match their `applyTo` patterns.
   - Distinguish a legitimate wiring entry point from a business-logic bypass. Do not infer permissions from boundary names.
5. Check verification:
   - Does each VT trace back, item by item, to the actual owner/anchor, an independent criterion, and the actual scenario/test location? Does the `.feature` file exclusively hold the scenario text?
   - Without an application, step implementations, a runner, or a report, keep `not-run`.
   - "Approved", test names, and parser success prove neither approval nor execution.
6. Check SEQ and SWAS:
   - Does the SEQ distinguish conceptual participants from actual ABBs/interfaces, and keep sourced directions and asynchronous contracts without inventing transport guarantees?
   - Is the readability of the SWAS's nine source categories checked against the source text/baselines?
   - When ABB/deployment/risk/release materials are missing, is the gap kept, rather than invented infrastructure or approval?
7. Check generation and maintenance:
   - Did initial generation go through the [generate-code preflight](../generate-code/SKILL.md#preflight), listing all exact paths, sources/acceptance criteria, and the authorized scope?
   - Does each non-empty conflict, path mismatch, or missing development input have the required blocker record? Skipping does not count as complete generation.
   - Does existing maintenance check the task/diff/reproduction, rather than overwrite with an initializer?
   - Are read-only sources and owner content preserved, as required?
8. Make actual changes or runs only with specific authorization. This section does not add a checker, security audit, or application pass verdict.

- Return: findings using the [existing finding fields](#domain-review): actual location, baseline, rationale, impact, and gaps.

<a id="backlog-review"></a>
## Open question and BL review

Purpose: classify open questions and BLs by their evidence, and recommend closure only where evidence supports it. Read-only by default (see [mode](#review-mode)).

1. Check each item against: the original question; conflicting sources; the impact/blocked scope; the actual accountable owner; the [decision evidence](../../../_templates/items/backlog-item.md#decision).
2. Report the findings in these categories: items still awaiting an answer; items decided but not yet implemented; items with insufficient evidence; items recommendable for closure. These describe this review's findings and do not replace the original status enumeration.
3. Recommend closure only on locatable and applicable decision/handling evidence. An expired date, a schedule, an implementation constant, complete links, or a self-declared "done" is not enough.
4. Using the [finding fields](#domain-review), list the residual impact and the acceptance criteria/VTs still to be checked.
5. State statistics for the scope actually inventoried this time. Do not count unknown items as resolved.
6. Update the original BL's handling progress, decision basis, and follow-up review only when authorized to modify it. Keep its history.

- Return: the categorized findings, the residual impact, the items still to be checked, and statistics with their scope.
- Record: the update to the original BL from step 6, only when authorized.

<a id="impact"></a>
## Semantic impact (before runs)

Purpose: before any run, trace what a change to rules, contexts, acceptance criteria, or baselines affects, and mark old results for re-review.

1. Compare the old and new rules, contexts, acceptance criteria, and baselines. List the actual changed IDs/locations, sources, and confirmation state.
2. Trace dependents by references and business meaning: dependent models, UC/INV, REQ/QAS, SRs, US, ABB/ADR, SEQ/SWAS, scenarios/VTs with their companions, and tasks. For boundary changes, also check CAP, the context map, Published Interfaces, and consumers. A value in one rule file can still affect the artifacts that reference it.
3. Include [incoming ADRs](../define-requirements/SKILL.md#incoming-adr), [Intended Use](../define-requirements/SKILL.md#intended-use), and governance/risk references only when actually provided and applicable. If a source is missing, state that the affected judgment cannot be completed. Do not make risk decisions on anyone's behalf.
4. Following the [impact guide](../../../verification/README.md#change-impact), list the affected items with their sources, rationale, severity, who needs to confirm what, and the suggested order. Give a rationale for any no-impact judgment. A suggested order is not a change that has been made.
5. Handle acceptance changes: clarify unconfirmed business changes first, and do not change rules or delete original acceptance criteria on your own. Update acceptance boundaries, error/forbidden side effects, and VT expectations only after confirmation and authorization. Keep regression scenarios that still hold.
6. Mark old results for re-review: keep old runs' actual results with their original object, requirement, and VT baselines, and append an `unverified` entry for the current baseline, with the impact rationale, to the original result's [applicability section](../../../_templates/items/verification-test.md#applicability). Never rewrite an old success as a new success or a historical failure; append new checks as separate records.
7. When authorized, use the [impact candidate interface](../../utilities/README.md#impact-candidates) `impact_report(root, base_sha, task_ids=())` with the exact full commit and any provided task keys; the tool reads the current snapshot. Old and new dependencies, deleted sources, and removed references keep their reasons. Candidates are not final business impact, severity, or confirmation, so still check non-canonical dependencies and unknown semantics per steps 1 to 4. The tool does not write back to rules or original results, and does not run VTs.

- Return: the changed items from step 1 and the affected items from step 4.
- Record: the `unverified` applicability entries from step 6, and the confirmed and authorized updates from step 5.

<a id="runs"></a>
## Runs and records

Purpose: run only configured, authorized checks and record exactly what was observed. Only execution mode runs and records (see [mode](#review-mode)).

1. Following the [verification layers](../../../verification/README.md#layers), determine which objects can currently be run and the per-item criteria. Without an application, application checks do not apply to documentation tasks, and planned business/software VTs remain `not-run`. When an application exists but the object, environment, or command is unavailable, mark the related checks `not-run` with the specific reason; do not call them not applicable.
2. Run only actually configured and authorized commands, cwd, or explicit manual steps.
3. Following the [execution guide](../../../verification/README.md#execution), check the actual scope, the discovered/executed/skipped counts, and the per-target observations. The exclusions listed for "Run succeeded" in [Keep conclusions separate](#conclusions) apply.
4. Append to the [VT actual run section](../../../_templates/items/verification-test.md#runs): the actual object/requirement/VT baselines, time, environment, steps, raw report, and per-item results. Keep anything not run as `not-run`; record skips as `skipped` with the reason. If a report is inaccessible, state the limitation; do not invent links or backfill results that were not observed.
5. Keep [standalone document checks](../../../docs/development.md#document-checks) separate, each with its own object, criteria, results, and baselines. They may be recorded in a document-layer VT or an existing authorized check record, never in a planned behavioral VT.
6. Do not derive business acceptance by aggregating software passes.
7. Use [record-handoff](../record-handoff/SKILL.md) to link authoritative records, exact gaps, and remaining actions; the log does not copy result tables.

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
